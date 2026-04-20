# Figma Documentation Corpus

This directory contains scraped Figma Design help center articles.
The data is **not included in the repository** — you generate it locally by running the fetch script.

## How to Generate

```bash
cd structure-helper/fetch_script
pip install -r requirements.txt
python3 main.py
```

The script will create the following structure here:

```
figma_docs/
├── index.json              # 197 articles: id, title, slug, breadcrumb, labels
├── graph.json              # Link graph: nodes, edges, external links
├── progress.json           # Resume state (auto-generated)
└── articles/
    └── <article-slug>/
        ├── content.md      # Full article as markdown
        ├── metadata.json   # URL, breadcrumb, images, videos, internal_links
        └── images/         # Downloaded screenshots
```

## Notes

- First run takes ~10 minutes (197 articles + 822 images)
- If interrupted, re-run the script — it resumes from where it left off
- No authentication required (public Zendesk API)
- Requires Python 3.8+
