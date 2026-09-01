# Figma Docs Fetch Script

Scrapes the Figma Design help center via the Zendesk API and produces a local
documentation corpus with markdown articles, images, metadata, and a link graph.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Full scrape (~18 min, 197 articles, resume supported)
python figma_docs_fetch_script.py

# Discover articles only (no content fetch)
python figma_docs_fetch_script.py --discover-only

# Preview what would be done
python figma_docs_fetch_script.py --dry-run
```

## Output

```
figma_docs/
  index.json          # Article index (id, title, slug, breadcrumb, labels)
  graph.json          # Link graph (nodes, edges, external_links)
  progress.json       # Resume state
  articles/
    <article-slug>/
      content.md      # Article body as markdown
      metadata.json   # URL, breadcrumb, images, videos, who_can_use, internal_links
      images/         # Downloaded images
```

## Configuration

Edit constants at the top of `figma_docs_fetch_script.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `CATEGORY_ID` | `360002042553` | Figma Design category (change to scrape other categories) |
| `OUTPUT_DIR` | `figma_docs` | Output directory |
| `REQUEST_DELAY` | `1.0` | Seconds between API calls |
| `IMAGE_DELAY` | `0.5` | Seconds between image downloads |
| `MAX_RETRIES` | `3` | Retry count on failure |
