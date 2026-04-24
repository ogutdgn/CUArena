# Figma Mock for CUA Testing

This project builds a mock Figma Design application for Computer Use Agent (CUA) testing. The CUA interacts with the app via screen pixels — clicking buttons, reading labels, and verifying state changes. The mock replicates Figma's UI structure (toolbar, sidebars, panels, menus) and core workflows without real canvas rendering, providing a deterministic test environment for agent evaluation.

## Getting Started

```bash
# 1. Generate the documentation corpus
cd helper/fetch_script
pip install -r requirements.txt
python3 main.py

# 2. Work with AI using the phase system
# Open CLAUDE.md for instructions on each phase:
#   Phase 1 — Discovery: Analyze Figma features and workflows
#   Phase 2 — Scope: Define what the mock app will include
#   Phase 3 — Architecture: Technical design
#   Phase 4 — Implementation: Build the mock app
```

## Project Structure

```
.
├── CLAUDE.md                    # AI agent instructions (phase-based)
├── README.md                    # This file
└── helper/
    ├── phases/                  # Phase-specific AI prompts
    ├── fetch_script/            # Documentation scraper (Python)
    ├── figma_docs/              # Generated after running fetch script
    └── analysis/                # Generated from documentations
```
