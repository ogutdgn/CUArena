# Figma Design Documentation — AI Agent Guide

## Purpose

This is a scraped archive of Figma Design's help center (197 articles).
The goal is to analyze Figma's features, workflows, and UI patterns to build
a mock Figma application for CUA (Computer Use Agent) testing.

**You are working in phases.** The user will tell you which phase they are in.
Read ONLY the relevant phase file from `structure-helper/phases/` — do not load all phases at once.

## Phases

| Phase | File | Goal |
|-------|------|------|
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
    │   ├── phase1-discovery.md
    │   ├── phase2-scope.md
    │   ├── phase3-architecture.md
    │   └── phase4-implementation.md
    ├── figma_docs/              # Scraped documentation corpus
    │   ├── index.json           # 197 articles: id, title, slug, breadcrumb, labels (98KB)
    │   ├── graph.json           # Link graph: 197 nodes, 914 edges, 428 external links (211KB)
    │   ├── progress.json        # Scraper state (ignore)
    │   └── articles/
    │       └── <article-slug>/
    │           ├── content.md      # Full article as markdown
    │           ├── metadata.json   # URL, breadcrumb, images, videos, who_can_use, internal_links
    │           └── images/         # Downloaded images (822 total)
    └── fetch_script/            # Scraper source code
        ├── main.py
        ├── requirements.txt
        └── README.md
```

## How to Use This Data Efficiently

**Token budget matters.** Follow this lookup order:

1. **Start with `structure-helper/figma_docs/index.json`** — scan titles and breadcrumbs to find relevant articles.
   Do NOT read all 197 articles. Find the 2-5 that matter for your current question.

2. **Use `structure-helper/figma_docs/graph.json` for relationships** — find which articles link to each other.
   The `edges` array has `{source, target, link_text}`.
   The `external_links` array shows references outside this corpus.

3. **Read specific `structure-helper/figma_docs/articles/<slug>/content.md` files** — only when you need the actual content.
   Always read `metadata.json` first (smaller) to check if the article is relevant.

4. **Never read images** unless the user specifically asks about visual layout.

## Corpus Overview

| Domain | Articles | Description |
|--------|----------|-------------|
| Create designs | 68 | Layers, frames, shapes, vectors, fills, strokes, effects, auto layout, constraints |
| Build design systems | 41 | Components, variants, slots, variables, styles, libraries |
| Create prototypes | 27 | Triggers, actions, animations, flows, state management, expressions |
| Dev Mode | 19 | Inspect, code snippets, Code Connect, VS Code, handoff, branching |
| Work together | 18 | Comments, branching, merge, review, cursor chat, spotlight |
| Tour the interface | 15 | UI3 navigation, toolbar, sidebars, actions menu, AI tools, keyboard |
| Import and export | 6 | Sketch import, export formats, copy between tools |
| Figma Draw | 3 | Illustration tools, patterns, transforms |

## Graph Quick Reference

**Most referenced articles (core concepts):**
- Connect your prototype (21 incoming refs)
- Play your prototypes (20)
- Publish a library (16)
- Guide to prototyping (16)
- Guide to variables (16)
- Guide to Dev Mode (15)

**Most linking articles (hub/overview pages):**
- Navigating UI3 (25 outgoing refs)
- Right sidebar properties (24)
- Guide to prototyping (19)
- Guide to Dev Mode (18)

**Strongest cross-domain connections:**
- Tour the interface -> Create designs (44 links)
- Create prototypes -> Create designs (27)
- Build design systems -> Create designs (27)
- Create designs -> Build design systems (23)

## Rules

- When the user says "Phase N", read `structure-helper/phases/phaseN-*.md` for detailed instructions.
- Do not guess article content — read the file.
- Cite articles by title when referencing them.
- If a question spans multiple domains, check `structure-helper/figma_docs/graph.json` edges to find related articles.
- Prefer `metadata.json` over `content.md` when you only need links/breadcrumb/labels.
- All article paths follow: `structure-helper/figma_docs/articles/<slug>/content.md` and `structure-helper/figma_docs/articles/<slug>/metadata.json`.
