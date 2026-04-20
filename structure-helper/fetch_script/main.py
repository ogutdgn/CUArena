"""
Figma Design Help Center Scraper
==================================
Fetches all articles from the Figma Design help center category via the
Zendesk API, converts them to markdown, and saves them locally with
images, metadata, and a link graph.

Usage:
    python figma_docs_fetch_script.py                  # Full scrape (resume supported)
    python figma_docs_fetch_script.py --discover-only  # Discover links only, don't fetch articles
    python figma_docs_fetch_script.py --dry-run        # Preview what would be done, write nothing
"""

import argparse
import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm import tqdm

# ── Configuration ──────────────────────────────────────────────────────────

BASE_URL = "https://help.figma.com"
API_BASE = f"{BASE_URL}/api/v2/help_center/en-us"
CATEGORY_ID = "360002042553"  # Figma Design

OUTPUT_DIR = Path("figma_docs")
PROGRESS_FILE = OUTPUT_DIR / "progress.json"
ERROR_LOG = OUTPUT_DIR / "errors.log"
INDEX_FILE = OUTPUT_DIR / "index.json"
GRAPH_FILE = OUTPUT_DIR / "graph.json"

REQUEST_DELAY = 1.0         # Seconds between API calls
IMAGE_DELAY = 0.5           # Seconds between image downloads
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0        # Exponential backoff multiplier
PER_PAGE = 100              # Zendesk API max per_page

USER_AGENT = "FigmaDocScraper/1.0 (documentation-archival)"


# ── Logging Setup ──────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scraper")


# ── Data Classes ───────────────────────────────────────────────────────────

@dataclass
class SectionInfo:
    id: int
    name: str
    html_url: str
    parent_section_id: int | None = None


@dataclass
class ArticleMeta:
    id: int
    title: str
    html_url: str
    section_id: int
    updated_at: str
    labels: list[str] = field(default_factory=list)


# ── HTTP Session ───────────────────────────────────────────────────────────

session = requests.Session()
session.headers.update({
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
})


def api_get(url: str, params: dict | None = None) -> dict | None:
    """Rate-limited, retrying API GET request."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, params=params, timeout=30)

            if resp.status_code == 429:
                wait = BACKOFF_FACTOR ** attempt
                log.warning(f"Rate limited (429), waiting {wait:.0f}s... (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
                continue

            if resp.status_code != 200:
                log.error(f"HTTP {resp.status_code} for {url}")
                if attempt < MAX_RETRIES:
                    time.sleep(BACKOFF_FACTOR ** attempt)
                    continue
                return None

            time.sleep(REQUEST_DELAY)
            return resp.json()

        except requests.RequestException as e:
            log.error(f"Request failed: {e} (attempt {attempt}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_FACTOR ** attempt)
            else:
                return None

    return None


def download_file(url: str, dest: Path) -> bool:
    """Download a file (image etc). Skips if already exists."""
    if dest.exists() and dest.stat().st_size > 0:
        return True

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=30, stream=True)
            if resp.status_code == 200:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                time.sleep(IMAGE_DELAY)
                return True
            else:
                log.warning(f"Download HTTP {resp.status_code}: {url}")
                if attempt < MAX_RETRIES:
                    time.sleep(BACKOFF_FACTOR ** attempt)
        except requests.RequestException as e:
            log.warning(f"Download failed: {e} (attempt {attempt})")
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_FACTOR ** attempt)

    return False


# ── Progress Management ────────────────────────────────────────────────────

class ProgressTracker:
    """Manages progress.json for resume support."""

    def __init__(self, path: Path):
        self.path = path
        self.data: dict = {"completed": [], "failed": [], "discovered": []}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                log.warning("Corrupt progress.json, starting fresh")

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def is_completed(self, article_id: int) -> bool:
        return article_id in self.data["completed"]

    def mark_completed(self, article_id: int):
        if article_id not in self.data["completed"]:
            self.data["completed"].append(article_id)
            self.save()

    def mark_failed(self, article_id: int, error: str):
        entry = {"id": article_id, "error": error}
        # Replace existing entry if present
        self.data["failed"] = [
            f for f in self.data["failed"] if f.get("id") != article_id
        ]
        self.data["failed"].append(entry)
        self.save()

    def set_discovered(self, article_ids: list[int]):
        self.data["discovered"] = article_ids
        self.save()

    @property
    def remaining(self) -> list[int]:
        completed = set(self.data["completed"])
        return [aid for aid in self.data["discovered"] if aid not in completed]


# ── Link Discovery ─────────────────────────────────────────────────────────

def discover_sections(category_id: str) -> list[SectionInfo]:
    """Fetch all sections under a category (with pagination)."""
    sections: list[SectionInfo] = []
    url = f"{API_BASE}/categories/{category_id}/sections.json"
    params = {"per_page": PER_PAGE}

    while url:
        data = api_get(url, params)
        if not data:
            break

        for s in data.get("sections", []):
            sections.append(SectionInfo(
                id=s["id"],
                name=s["name"],
                html_url=s["html_url"],
                parent_section_id=s.get("parent_section_id"),
            ))

        url = data.get("next_page")
        params = None  # next_page URL already includes params

    log.info(f"Discovered {len(sections)} sections")
    return sections


def discover_articles(sections: list[SectionInfo]) -> list[ArticleMeta]:
    """Fetch article list from all sections."""
    articles: list[ArticleMeta] = []
    seen_ids: set[int] = set()

    for section in tqdm(sections, desc="Discovering articles", unit="section"):
        url = f"{API_BASE}/sections/{section.id}/articles.json"
        params = {"per_page": PER_PAGE}

        while url:
            data = api_get(url, params)
            if not data:
                break

            for a in data.get("articles", []):
                if a["id"] not in seen_ids and not a.get("draft", False):
                    seen_ids.add(a["id"])
                    articles.append(ArticleMeta(
                        id=a["id"],
                        title=a["title"],
                        html_url=a["html_url"],
                        section_id=a["section_id"],
                        updated_at=a["updated_at"],
                        labels=a.get("label_names", []),
                    ))

            url = data.get("next_page")
            params = None

    log.info(f"Discovered {len(articles)} unique articles")
    return articles


# ── Content Extraction ─────────────────────────────────────────────────────

def fix_images_in_headings(soup: BeautifulSoup) -> BeautifulSoup:
    """Move img tags out of heading/strong wrappers.

    Figma docs sometimes wrap images as <h4><strong><img></strong></h4>.
    markdownify loses the image in this case and renders alt text as heading.
    This function moves the img before the heading element.
    """
    for img in soup.find_all("img"):
        parent = img.parent
        if parent and parent.name in ("strong", "b", "em", "i"):
            grandparent = parent.parent
            if grandparent and grandparent.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                grandparent.insert_before(img)
                if not parent.get_text(strip=True):
                    parent.decompose()
                if grandparent and not grandparent.get_text(strip=True):
                    grandparent.decompose()
        elif parent and parent.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            parent.insert_before(img)
            if not parent.get_text(strip=True):
                parent.decompose()
    return soup


def html_to_markdown(html: str) -> str:
    """Convert HTML body to clean markdown."""
    soup = BeautifulSoup(html, "html.parser")
    soup = fix_images_in_headings(soup)
    return md(
        str(soup),
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
    )


def extract_images(soup: BeautifulSoup) -> list[dict]:
    """Extract image URLs from the HTML body."""
    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if src:
            if src.startswith("/"):
                src = urljoin(BASE_URL, src)
            images.append({"src": src, "alt": img.get("alt", "")})
    return images


def extract_videos(soup: BeautifulSoup) -> list[dict]:
    """Extract video URLs (URL only, does not download)."""
    videos = []
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if src:
            videos.append({"type": "iframe", "src": src})
    for video in soup.find_all("video"):
        src = video.get("src", "")
        source = video.find("source")
        if source:
            src = source.get("src", "")
        if src:
            videos.append({"type": "video", "src": src})
    return videos


def extract_who_can_use(soup: BeautifulSoup) -> dict | None:
    """Parse the 'Who can use this feature' metadata box."""
    for tag in soup.find_all(["h2", "h3", "h4", "strong", "b", "p"]):
        text = tag.get_text(strip=True).lower()
        if "who can use" in text:
            info = {"header": tag.get_text(strip=True), "details": []}
            for sibling in tag.find_next_siblings():
                sibling_text = sibling.get_text(strip=True)
                if not sibling_text:
                    continue
                if sibling.name in ["h1", "h2", "h3"]:
                    break
                info["details"].append(sibling_text)
                if len(info["details"]) >= 5:
                    break
            return info
    return None


def extract_internal_links(soup: BeautifulSoup) -> list[dict]:
    """Collect internal links to other Figma help center articles."""
    links = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/hc/en-us/articles/" in href or "/hc/en-us/sections/" in href:
            if href.startswith("/"):
                href = urljoin(BASE_URL, href)
            # Normalize: strip fragment and query
            parsed = urlparse(href)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if normalized not in seen:
                seen.add(normalized)
                links.append({"url": normalized, "text": a.get_text(strip=True)})
    return links


# ── Breadcrumb Builder ─────────────────────────────────────────────────────

class SectionCache:
    """Caches section info for breadcrumb construction."""

    def __init__(self, sections: list[SectionInfo]):
        self._cache: dict[int, SectionInfo] = {s.id: s for s in sections}

    def get_breadcrumb(self, section_id: int) -> list[dict]:
        breadcrumb = []
        current_id: int | None = section_id

        while current_id and current_id in self._cache:
            section = self._cache[current_id]
            breadcrumb.insert(0, {
                "id": section.id,
                "name": section.name,
                "url": section.html_url,
            })
            current_id = section.parent_section_id

        return breadcrumb


# ── Article Processor ──────────────────────────────────────────────────────

def make_slug(title: str) -> str:
    """Create a filesystem-friendly slug from an article title."""
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:80].strip("-")


def process_article(
    article_id: int,
    section_cache: SectionCache,
    dry_run: bool = False,
) -> dict | None:
    """Fetch, process, and save a single article. Returns an index entry."""

    # Fetch article from API
    data = api_get(f"{API_BASE}/articles/{article_id}.json")
    if not data:
        return None

    article = data["article"]
    title = article["title"]
    body_html = article.get("body", "") or ""

    if not body_html.strip():
        log.warning(f"Empty body: {title} ({article_id})")
        return None

    # Parse content
    soup = BeautifulSoup(body_html, "html.parser")
    markdown_content = html_to_markdown(body_html)
    images = extract_images(soup)
    videos = extract_videos(soup)
    who_can_use = extract_who_can_use(soup)
    internal_links = extract_internal_links(soup)
    breadcrumb = section_cache.get_breadcrumb(article["section_id"])

    slug = make_slug(title)
    article_dir = OUTPUT_DIR / "articles" / slug

    if dry_run:
        log.info(f"[DRY RUN] Would process: {title} -> {article_dir}")
        return None

    article_dir.mkdir(parents=True, exist_ok=True)

    # Write content.md
    (article_dir / "content.md").write_text(markdown_content, encoding="utf-8")

    # Download images
    image_map: list[dict] = []
    if images:
        img_dir = article_dir / "images"
        img_dir.mkdir(exist_ok=True)

        for i, img in enumerate(images, 1):
            # Extract extension from URL
            parsed = urlparse(img["src"])
            ext = Path(parsed.path).suffix or ".png"
            filename = f"img_{i:02d}{ext}"
            dest = img_dir / filename

            success = download_file(img["src"], dest)
            image_map.append({
                "original_url": img["src"],
                "local_path": f"images/{filename}",
                "alt": img["alt"],
                "downloaded": success,
            })

    # Write metadata.json
    metadata = {
        "article_id": article_id,
        "title": title,
        "url": article["html_url"],
        "section_id": article["section_id"],
        "breadcrumb": breadcrumb,
        "images": image_map,
        "videos": videos,
        "who_can_use": who_can_use,
        "internal_links": internal_links,
        "labels": article.get("label_names", []),
        "updated_at": article["updated_at"],
    }
    (article_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Return index entry
    return {
        "id": article_id,
        "title": title,
        "slug": slug,
        "url": article["html_url"],
        "section_id": article["section_id"],
        "breadcrumb_path": " > ".join(b["name"] for b in breadcrumb),
        "labels": article.get("label_names", []),
        "updated_at": article["updated_at"],
        "image_count": len(images),
        "video_count": len(videos),
        "internal_link_count": len(internal_links),
        "has_who_can_use": who_can_use is not None,
    }


# ── Graph Builder ──────────────────────────────────────────────────────────

def build_graph(index_entries: list[dict]) -> dict:
    """Build an article relationship graph from internal links."""
    # Article URL -> ID mapping
    url_to_id: dict[str, int] = {}
    for entry in index_entries:
        url_to_id[entry["url"]] = entry["id"]
        # Also map the short URL variant (without trailing slug)
        parsed = urlparse(entry["url"])
        path = parsed.path
        match = re.match(r"(/hc/en-us/articles/\d+)", path)
        if match:
            short_url = f"{parsed.scheme}://{parsed.netloc}{match.group(1)}"
            url_to_id[short_url] = entry["id"]

    nodes = []
    edges = []
    external_links = []  # Links pointing outside this corpus

    for entry in index_entries:
        nodes.append({
            "id": entry["id"],
            "title": entry["title"],
            "breadcrumb_path": entry["breadcrumb_path"],
        })

        # Read internal_links from metadata.json
        meta_path = OUTPUT_DIR / "articles" / entry["slug"] / "metadata.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            for link in meta.get("internal_links", []):
                target_url = link["url"]
                # Normalize URL
                parsed = urlparse(target_url)
                match = re.match(r"(/hc/en-us/articles/\d+)", parsed.path)
                if match:
                    short = f"{parsed.scheme}://{parsed.netloc}{match.group(1)}"
                    target_id = url_to_id.get(short) or url_to_id.get(target_url)
                else:
                    target_id = url_to_id.get(target_url)

                if target_id and target_id != entry["id"]:
                    edges.append({
                        "source": entry["id"],
                        "target": target_id,
                        "link_text": link["text"],
                    })
                elif not target_id:
                    # Link to an article outside this corpus (FigJam, Admin, etc.)
                    external_links.append({
                        "source": entry["id"],
                        "target_url": target_url,
                        "link_text": link["text"],
                    })

    return {
        "nodes": nodes,
        "edges": edges,
        "external_links": external_links,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "external_link_count": len(external_links),
        },
    }


# ── Error Logger ───────────────────────────────────────────────────────────

def log_error(article_id: int, error: str):
    """Append error to errors.log."""
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | article {article_id} | {error}\n")


# ── Main Pipeline ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Figma Design Help Center Scraper")
    parser.add_argument("--discover-only", action="store_true", help="Discover links only, don't fetch articles")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be done, write nothing")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    progress = ProgressTracker(PROGRESS_FILE)

    # ── Step 1: Discovery ──────────────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 1: Discovering sections and articles")
    log.info("=" * 60)

    sections = discover_sections(CATEGORY_ID)
    section_cache = SectionCache(sections)

    articles = discover_articles(sections)
    progress.set_discovered([a.id for a in articles])

    log.info(f"Total: {len(articles)} articles to process")
    log.info(f"Already completed: {len(progress.data['completed'])}")
    log.info(f"Remaining: {len(progress.remaining)}")

    if args.discover_only:
        # Write discovery results to index.json
        discovery_index = [asdict(a) for a in articles]
        INDEX_FILE.write_text(
            json.dumps(discovery_index, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info(f"Discovery index saved to {INDEX_FILE}")
        return

    # ── Step 2: Process Articles ───────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 2: Processing articles")
    log.info("=" * 60)

    remaining_ids = progress.remaining
    index_entries: list[dict] = []

    # Load index entries for previously completed articles
    for aid in progress.data["completed"]:
        article_meta = next((a for a in articles if a.id == aid), None)
        if article_meta:
            slug = make_slug(article_meta.title)
            meta_path = OUTPUT_DIR / "articles" / slug / "metadata.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                index_entries.append({
                    "id": aid,
                    "title": article_meta.title,
                    "slug": slug,
                    "url": article_meta.html_url,
                    "section_id": article_meta.section_id,
                    "breadcrumb_path": " > ".join(b["name"] for b in meta.get("breadcrumb", [])),
                    "labels": meta.get("labels", []),
                    "updated_at": meta.get("updated_at", ""),
                    "image_count": len(meta.get("images", [])),
                    "video_count": len(meta.get("videos", [])),
                    "internal_link_count": len(meta.get("internal_links", [])),
                    "has_who_can_use": meta.get("who_can_use") is not None,
                })

    for article_id in tqdm(remaining_ids, desc="Processing articles", unit="article"):
        if progress.is_completed(article_id):
            continue

        try:
            entry = process_article(article_id, section_cache, dry_run=args.dry_run)
            if entry:
                index_entries.append(entry)
                progress.mark_completed(article_id)
                log.info(f"OK: {entry['title']}")
            else:
                error_msg = "Empty or failed"
                progress.mark_failed(article_id, error_msg)
                log_error(article_id, error_msg)

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            progress.mark_failed(article_id, error_msg)
            log_error(article_id, error_msg)
            log.error(f"FAILED article {article_id}: {error_msg}")

    # ── Step 3: Build Index & Graph ────────────────────────────────────
    if not args.dry_run:
        log.info("=" * 60)
        log.info("STEP 3: Building index and graph")
        log.info("=" * 60)

        # index.json
        INDEX_FILE.write_text(
            json.dumps(index_entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info(f"Index: {len(index_entries)} entries -> {INDEX_FILE}")

        # graph.json
        graph = build_graph(index_entries)
        GRAPH_FILE.write_text(
            json.dumps(graph, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info(f"Graph: {graph['stats']['node_count']} nodes, {graph['stats']['edge_count']} edges -> {GRAPH_FILE}")

    # ── Summary ─────────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("DONE")
    log.info(f"  Completed: {len(progress.data['completed'])}")
    log.info(f"  Failed: {len(progress.data['failed'])}")
    log.info(f"  Output: {OUTPUT_DIR}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
