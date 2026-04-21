# Figma Documentation — AI Agent Guide

## Purpose

This is a scraped archive of Figma's help center, organized by product. Four
products are covered:

- **Figma Design** — the main design tool
- **Figma Draw** — illustration / vector drawing workflows
- **Dev Mode** — handoff, inspect, code generation, Code Connect
- **Projects** — sample projects / project organization content

The goal is to analyze Figma's features, workflows, and UI patterns to build a
mock Figma application for CUA (Computer Use Agent) testing.

**You are working in phases.** The user will tell you which phase they are in.
Read ONLY the relevant phase file from `structure-helper/phases/` — do not load
all phases at once.

## Phases

| Phase | File | Goal |
|-------|------|------|
| 0 - Alignment | `structure-helper/phases/phase0-learn.md` | Architectural decisions log (top 3 locked, pending, tabled) |
| 1 - Discovery | `structure-helper/phases/phase1-discovery.md` | Analyze features, workflows, dependencies |
| 2 - Scope | `structure-helper/phases/phase2-scope.md` | Define what the mock app will include |
| 3 - Architecture | `structure-helper/phases/phase3-architecture.md` | Technical design for the mock app |
| 4 - Implementation | `structure-helper/phases/phase4-implementation.md` | Build the mock app |

## File Structure

```
.
├── CLAUDE.md                    # This file
└── structure-helper/
    ├── phases/                  # Phase-specific instructions
    │   ├── phase0-learn.md
    │   ├── phase1-discovery.md
    │   ├── phase2-scope.md
    │   ├── phase3-architecture.md
    │   └── phase4-implementation.md
    ├── figma_docs/              # Scraped documentation corpus
    │   ├── index.json           # All articles across all products: id, title, slug, product, breadcrumb, labels
    │   ├── graph.json           # Link graph: nodes (with product), edges, external_links
    │   ├── progress.json        # Scraper state (ignore)
    │   └── articles/
    │       ├── Figma Design/
    │       │   └── <article-slug>/
    │       │       ├── content.md      # Full article as markdown
    │       │       ├── metadata.json   # URL, product, breadcrumb, images, videos, who_can_use, internal_links
    │       │       └── images/         # Downloaded images
    │       ├── Figma Draw/
    │       │   └── <article-slug>/...
    │       ├── Dev Mode/
    │       │   └── <article-slug>/...
    │       └── Projects/
    │           └── <article-slug>/...
    └── fetch_script/            # Scraper source code
        ├── main.py
        ├── requirements.txt
        └── README.md
```

## How to Use This Data Efficiently

**Token budget matters.** Follow this lookup order:

1. **Start with `structure-helper/figma_docs/index.json`** — scan titles,
   breadcrumbs, and the `product` field to find relevant articles across all
   four products. Do NOT read every article. Find the 2-5 that matter for
   your current question.

2. **Use `structure-helper/figma_docs/graph.json` for relationships** — find
   which articles link to each other.
   - `nodes[]` has `{id, title, product, breadcrumb_path}`
   - `edges[]` has `{source, target, link_text}` — resolve target's product
     via `nodes[target].product`
   - `external_links[]` — references outside this corpus

3. **Read specific `structure-helper/figma_docs/articles/<Product>/<slug>/content.md`**
   — only when you need the actual content. Always read `metadata.json` first
   (smaller); its `internal_links[]` entries are pre-tagged with:
   - `target_type`: `"article"` / `"section"` / `"external"`
   - `target_id`: article_id or section_id (null for external)
   - `target_product`: `"Figma Design"` / `"Figma Draw"` / `"Dev Mode"` /
     `"Projects"` / `null`

4. **Never read images** unless the user specifically asks about visual layout.

## Products and Cross-Product References

Articles frequently link across products (e.g. a Figma Design article linking
to a Dev Mode article). Use the `target_product` field in each article's
`internal_links[]` to see where a reference goes without opening the target
file.

When answering cross-product questions, prefer reading `index.json` +
`graph.json` over loading multiple `content.md` files — the graph already
carries per-node product info.

## Rules

- When the user says "Phase N", read `structure-helper/phases/phaseN-*.md` for
  detailed instructions.
- Do not guess article content — read the file.
- Cite articles by title and product (e.g. *"Guide to Dev Mode"* [Dev Mode]).
- If a question spans multiple products, check `structure-helper/figma_docs/graph.json`
  edges + node product tags to find related articles.
- Prefer `metadata.json` over `content.md` when you only need
  links/breadcrumb/labels/product.
- Article paths follow:
  `structure-helper/figma_docs/articles/<Product>/<slug>/content.md` and
  `structure-helper/figma_docs/articles/<Product>/<slug>/metadata.json`.
  The `<Product>` segment is one of: `Figma Design`, `Figma Draw`, `Dev Mode`,
  `Projects`.
