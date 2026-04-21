"""
Figma Help Center Scraper (Multi-Product)
==========================================
Fetches articles from the Figma help center for multiple products:
  - Figma Design (category 360002042553)
  - Figma Draw   (section  31830768959511)
  - Dev Mode     (section  15023066873239)
  - Projects     (section  13148624530967)

Converts them to markdown and saves them locally under
  figma_docs/articles/<Product Name>/<article-slug>/
together with images, metadata, and a link graph.

Usage:
    python main.py                  # Full scrape (resume supported)
    python main.py --discover-only  # Discover links only, don't fetch articles
    python main.py --dry-run        # Preview what would be done, write nothing
"""

import argparse
import json
import logging
import re
import shutil
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

# Products to scrape. Order matters: section-type (narrower) products are
# processed first so that their sections are claimed before the broader
# category-type products pick up the rest. This prevents an article from
# being assigned to a broader product when a narrower one owns it.
PRODUCTS: list[dict] = [
    {"name": "Figma Draw",   "type": "section",  "id": "31830768959511"},
    {"name": "Dev Mode",     "type": "section",  "id": "15023066873239"},
    {"name": "Projects",     "type": "section",  "id": "13148624530967"},
    {"name": "Figma Design", "type": "category", "id": "360002042553"},
]

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "figma_docs"
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
    category_id: int | None = None


@dataclass
class ArticleMeta:
    id: int
    title: str
    html_url: str
    section_id: int
    updated_at: str
    labels: list[str] = field(default_factory=list)
    product_name: str = ""


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

def fetch_section(section_id: str) -> dict | None:
    """Fetch a single section's metadata."""
    data = api_get(f"{API_BASE}/sections/{section_id}.json")
    return data.get("section") if data else None


def discover_sections_in_category(category_id: str) -> list[SectionInfo]:
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
                category_id=s.get("category_id"),
            ))

        url = data.get("next_page")
        params = None  # next_page URL already includes params

    return sections


def discover_sections_for_product(product: dict) -> list[SectionInfo]:
    """Discover all sections that belong to a product.

    For a category-type product, returns every section under that category.
    For a section-type product, returns the root section plus every section
    transitively rooted at it (descendants) within the same category.
    """
    if product["type"] == "category":
        sections = discover_sections_in_category(product["id"])
        log.info(f"[{product['name']}] {len(sections)} sections in category {product['id']}")
        return sections

    if product["type"] == "section":
        root = fetch_section(product["id"])
        if not root:
            log.warning(f"[{product['name']}] Could not fetch section {product['id']}")
            return []

        root_section = SectionInfo(
            id=root["id"],
            name=root["name"],
            html_url=root["html_url"],
            parent_section_id=root.get("parent_section_id"),
            category_id=root.get("category_id"),
        )

        result: list[SectionInfo] = [root_section]

        # Walk descendants using the parent_section_id graph within the same category.
        if root_section.category_id:
            siblings = discover_sections_in_category(str(root_section.category_id))
            # BFS for descendants of root_section.id
            to_visit = [root_section.id]
            visited = {root_section.id}
            while to_visit:
                current_id = to_visit.pop()
                for s in siblings:
                    if s.parent_section_id == current_id and s.id not in visited:
                        visited.add(s.id)
                        result.append(s)
                        to_visit.append(s.id)

        log.info(f"[{product['name']}] {len(result)} sections rooted at {product['id']}")
        return result

    log.error(f"Unknown product type: {product['type']}")
    return []


def discover_articles_for_sections(
    sections: list[SectionInfo],
    product_name: str,
) -> list[ArticleMeta]:
    """Fetch article list from all sections, tagged with product name."""
    articles: list[ArticleMeta] = []
    seen_ids: set[int] = set()

    for section in tqdm(sections, desc=f"[{product_name}] articles", unit="section"):
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
                        product_name=product_name,
                    ))

            url = data.get("next_page")
            params = None

    return articles


def discover_all_products() -> tuple[list[SectionInfo], list[ArticleMeta], dict[int, str]]:
    """Discover sections and articles across all products, with narrower
    products (section-type) claiming their sections before broader
    category-type products see them.

    Returns (sections, articles, section_to_product) where section_to_product
    maps each owned section_id to its owning product name.
    """
    all_sections: list[SectionInfo] = []
    all_articles: list[ArticleMeta] = []
    section_to_product: dict[int, str] = {}
    claimed_section_ids: set[int] = set()
    seen_article_ids: set[int] = set()

    for product in PRODUCTS:
        log.info(f"[{product['name']}] discovery start")
        sections = discover_sections_for_product(product)

        # Exclude sections already claimed by a narrower product.
        own_sections = [s for s in sections if s.id not in claimed_section_ids]
        for s in own_sections:
            claimed_section_ids.add(s.id)
            section_to_product[s.id] = product["name"]

        all_sections.extend(own_sections)

        articles = discover_articles_for_sections(own_sections, product["name"])
        added = 0
        for a in articles:
            if a.id not in seen_article_ids:
                seen_article_ids.add(a.id)
                all_articles.append(a)
                added += 1

        log.info(f"[{product['name']}] owns {len(own_sections)} sections, {added} articles")

    return all_sections, all_articles, section_to_product


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


def article_dir_for(product_name: str, slug: str) -> Path:
    """Target directory for an article under its product."""
    return OUTPUT_DIR / "articles" / product_name / slug


def process_article(
    article_meta: ArticleMeta,
    section_cache: SectionCache,
    dry_run: bool = False,
) -> dict | None:
    """Fetch, process, and save a single article. Returns an index entry."""

    data = api_get(f"{API_BASE}/articles/{article_meta.id}.json")
    if not data:
        return None

    article = data["article"]
    title = article["title"]
    body_html = article.get("body", "") or ""

    if not body_html.strip():
        log.warning(f"Empty body: {title} ({article_meta.id})")
        return None

    soup = BeautifulSoup(body_html, "html.parser")
    markdown_content = html_to_markdown(body_html)
    images = extract_images(soup)
    videos = extract_videos(soup)
    who_can_use = extract_who_can_use(soup)
    internal_links = extract_internal_links(soup)
    breadcrumb = section_cache.get_breadcrumb(article["section_id"])

    slug = make_slug(title)
    target_dir = article_dir_for(article_meta.product_name, slug)

    if dry_run:
        log.info(f"[DRY RUN] Would process: {title} -> {target_dir}")
        return None

    target_dir.mkdir(parents=True, exist_ok=True)

    (target_dir / "content.md").write_text(markdown_content, encoding="utf-8")

    image_map: list[dict] = []
    if images:
        img_dir = target_dir / "images"
        img_dir.mkdir(exist_ok=True)

        for i, img in enumerate(images, 1):
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

    metadata = {
        "article_id": article_meta.id,
        "title": title,
        "url": article["html_url"],
        "product": article_meta.product_name,
        "section_id": article["section_id"],
        "breadcrumb": breadcrumb,
        "images": image_map,
        "videos": videos,
        "who_can_use": who_can_use,
        "internal_links": internal_links,
        "labels": article.get("label_names", []),
        "updated_at": article["updated_at"],
    }
    (target_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "id": article_meta.id,
        "title": title,
        "slug": slug,
        "url": article["html_url"],
        "product": article_meta.product_name,
        "section_id": article["section_id"],
        "breadcrumb_path": " > ".join(b["name"] for b in breadcrumb),
        "labels": article.get("label_names", []),
        "updated_at": article["updated_at"],
        "image_count": len(images),
        "video_count": len(videos),
        "internal_link_count": len(internal_links),
        "has_who_can_use": who_can_use is not None,
    }


# ── Migration (old flat structure → per-product structure) ─────────────────

def migrate_existing_articles(articles_by_id: dict[int, ArticleMeta]) -> int:
    """Move any article directories still at the old flat path
    (articles/<slug>/) into the new per-product path
    (articles/<Product>/<slug>/). Returns number of folders moved.

    Folders that cannot be mapped to a discovered article (e.g. deleted
    upstream) are left in place and logged, so nothing is destroyed silently.
    """
    articles_root = OUTPUT_DIR / "articles"
    if not articles_root.exists():
        return 0

    product_names = {p["name"] for p in PRODUCTS}
    moved = 0

    for item in list(articles_root.iterdir()):
        if not item.is_dir():
            continue
        if item.name in product_names:
            continue  # already a product bucket

        slug = item.name
        metadata_path = item / "metadata.json"
        if not metadata_path.exists():
            log.warning(f"Orphan folder without metadata, leaving in place: {item}")
            continue

        try:
            meta = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception as e:
            log.warning(f"Bad metadata in {item}: {e}; leaving in place")
            continue

        article_id = meta.get("article_id")
        article_meta = articles_by_id.get(article_id) if article_id is not None else None
        if not article_meta:
            log.warning(f"Article {article_id} ({slug}) not in any current product, leaving in place")
            continue

        new_dir = article_dir_for(article_meta.product_name, slug)
        if new_dir.exists():
            log.warning(f"Target already exists: {new_dir}; removing duplicate source {item}")
            shutil.rmtree(item)
            continue

        new_dir.parent.mkdir(parents=True, exist_ok=True)
        item.rename(new_dir)

        # Stamp product into the migrated metadata so downstream reads pick it up.
        new_meta_path = new_dir / "metadata.json"
        try:
            m = json.loads(new_meta_path.read_text(encoding="utf-8"))
            m["product"] = article_meta.product_name
            new_meta_path.write_text(
                json.dumps(m, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            log.warning(f"Could not stamp product into {new_meta_path}: {e}")

        moved += 1

    if moved:
        log.info(f"Migrated {moved} article folders into per-product structure")
    return moved


# ── Internal Link Enrichment ───────────────────────────────────────────────

_ARTICLE_PATH_RE = re.compile(r"/hc/en-us/articles/(\d+)")
_SECTION_PATH_RE = re.compile(r"/hc/en-us/sections/(\d+)")


def enrich_internal_links(
    articles_by_id: dict[int, ArticleMeta],
    section_to_product: dict[int, str],
) -> int:
    """Walk every scraped metadata.json and stamp each internal_link with
    (target_type, target_id, target_product) so cross-product references are
    explicit. Idempotent: re-running only rewrites files whose resolution
    actually changed. Returns number of files updated."""
    articles_root = OUTPUT_DIR / "articles"
    if not articles_root.exists():
        return 0

    updated = 0
    for product_dir in articles_root.iterdir():
        if not product_dir.is_dir():
            continue
        for article_dir in product_dir.iterdir():
            if not article_dir.is_dir():
                continue
            meta_path = article_dir / "metadata.json"
            if not meta_path.exists():
                continue

            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception as e:
                log.warning(f"Bad metadata {meta_path}: {e}")
                continue

            links = meta.get("internal_links", [])
            if not links:
                continue

            changed = False
            for link in links:
                path = urlparse(link.get("url", "")).path
                target_type: str = "external"
                target_id: int | None = None
                target_product: str | None = None

                am = _ARTICLE_PATH_RE.search(path)
                if am:
                    aid = int(am.group(1))
                    art = articles_by_id.get(aid)
                    if art:
                        target_type = "article"
                        target_id = aid
                        target_product = art.product_name

                if target_product is None:
                    sm = _SECTION_PATH_RE.search(path)
                    if sm:
                        sid = int(sm.group(1))
                        prod = section_to_product.get(sid)
                        if prod:
                            target_type = "section"
                            target_id = sid
                            target_product = prod

                if (
                    link.get("target_type") != target_type
                    or link.get("target_id") != target_id
                    or link.get("target_product") != target_product
                ):
                    link["target_type"] = target_type
                    link["target_id"] = target_id
                    link["target_product"] = target_product
                    changed = True

            if changed:
                meta_path.write_text(
                    json.dumps(meta, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                updated += 1

    return updated


# ── Graph Builder ──────────────────────────────────────────────────────────

def build_graph(index_entries: list[dict]) -> dict:
    """Build an article relationship graph from internal links."""
    url_to_id: dict[str, int] = {}
    for entry in index_entries:
        url_to_id[entry["url"]] = entry["id"]
        parsed = urlparse(entry["url"])
        path = parsed.path
        match = re.match(r"(/hc/en-us/articles/\d+)", path)
        if match:
            short_url = f"{parsed.scheme}://{parsed.netloc}{match.group(1)}"
            url_to_id[short_url] = entry["id"]

    nodes = []
    edges = []
    external_links = []

    for entry in index_entries:
        nodes.append({
            "id": entry["id"],
            "title": entry["title"],
            "product": entry.get("product", ""),
            "breadcrumb_path": entry["breadcrumb_path"],
        })

        meta_path = article_dir_for(entry.get("product", ""), entry["slug"]) / "metadata.json"
        if not meta_path.exists():
            continue

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for link in meta.get("internal_links", []):
            target_url = link["url"]
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
    parser = argparse.ArgumentParser(description="Figma Help Center Scraper (Multi-Product)")
    parser.add_argument("--discover-only", action="store_true", help="Discover links only, don't fetch articles")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be done, write nothing")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    progress = ProgressTracker(PROGRESS_FILE)

    # ── Step 1: Discovery (all products) ───────────────────────────────
    log.info("=" * 60)
    log.info("STEP 1: Discovering sections and articles across products")
    log.info("=" * 60)

    all_sections, all_articles, section_to_product = discover_all_products()

    section_cache = SectionCache(all_sections)
    articles_by_id: dict[int, ArticleMeta] = {a.id: a for a in all_articles}

    progress.set_discovered([a.id for a in all_articles])

    # Per-product tally
    per_product: dict[str, int] = {}
    for a in all_articles:
        per_product[a.product_name] = per_product.get(a.product_name, 0) + 1
    log.info(f"Total: {len(all_articles)} articles across {len(PRODUCTS)} products")
    for name, n in per_product.items():
        log.info(f"  {name}: {n}")
    log.info(f"Already completed: {len(progress.data['completed'])}")
    log.info(f"Remaining: {len(progress.remaining)}")

    if args.discover_only:
        discovery_index = [asdict(a) for a in all_articles]
        INDEX_FILE.write_text(
            json.dumps(discovery_index, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info(f"Discovery index saved to {INDEX_FILE}")
        return

    # ── Step 1b: Migrate existing flat-structure articles ──────────────
    if not args.dry_run:
        migrate_existing_articles(articles_by_id)

    # ── Step 2: Process Articles ───────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 2: Processing articles")
    log.info("=" * 60)

    remaining_ids = progress.remaining
    index_entries: list[dict] = []

    # Load index entries for previously completed articles.
    for aid in progress.data["completed"]:
        article_meta = articles_by_id.get(aid)
        if not article_meta:
            continue
        slug = make_slug(article_meta.title)
        meta_path = article_dir_for(article_meta.product_name, slug) / "metadata.json"
        if not meta_path.exists():
            # File not at new path yet (e.g. migration failed) — will be re-fetched if removed from completed.
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        index_entries.append({
            "id": aid,
            "title": article_meta.title,
            "slug": slug,
            "url": article_meta.html_url,
            "product": article_meta.product_name,
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

        article_meta = articles_by_id.get(article_id)
        if not article_meta:
            log.warning(f"Article {article_id} has no discovered metadata, skipping")
            continue

        try:
            entry = process_article(article_meta, section_cache, dry_run=args.dry_run)
            if entry:
                index_entries.append(entry)
                progress.mark_completed(article_id)
                log.info(f"OK [{entry['product']}]: {entry['title']}")
            else:
                error_msg = "Empty or failed"
                progress.mark_failed(article_id, error_msg)
                log_error(article_id, error_msg)

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            progress.mark_failed(article_id, error_msg)
            log_error(article_id, error_msg)
            log.error(f"FAILED article {article_id}: {error_msg}")

    # ── Step 2b: Enrich internal_links with target product ─────────────
    if not args.dry_run:
        log.info("=" * 60)
        log.info("STEP 2b: Enriching internal_links with target product")
        log.info("=" * 60)
        touched = enrich_internal_links(articles_by_id, section_to_product)
        log.info(f"Updated {touched} metadata.json files with target_product tags")

    # ── Step 3: Build Index & Graph ────────────────────────────────────
    if not args.dry_run:
        log.info("=" * 60)
        log.info("STEP 3: Building index and graph")
        log.info("=" * 60)

        INDEX_FILE.write_text(
            json.dumps(index_entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info(f"Index: {len(index_entries)} entries -> {INDEX_FILE}")

        graph = build_graph(index_entries)
        GRAPH_FILE.write_text(
            json.dumps(graph, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info(f"Graph: {graph['stats']['node_count']} nodes, {graph['stats']['edge_count']} edges -> {GRAPH_FILE}")

    # ── Summary ─────────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("DONE")
    log.info(f"  Products: {', '.join(p['name'] for p in PRODUCTS)}")
    log.info(f"  Completed: {len(progress.data['completed'])}")
    log.info(f"  Failed: {len(progress.data['failed'])}")
    log.info(f"  Output: {OUTPUT_DIR}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
