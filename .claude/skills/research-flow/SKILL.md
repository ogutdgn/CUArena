---
name: research-flow
description: Use at the start of a new app (e.g. when starting Sheets or Docs) to convert external help-doc corpora into a filtered, committed helper/ reference. Covers raw fetch, multi-pass AI filtering, final extraction, and gitignoring the raw sources.
---

# Research Flow

**Status: PLACEHOLDER — to be filled when we run the first research cycle for the second app (Sheets).**

This skill will document the protocol the user used to build `apps/figma/app-docs/helper/` so it can be repeated for Sheets and Docs.

## Expected outline (to be confirmed during first run)

1. **Pick the source**: official help docs (Figma Help, Google Sheets Help, Google Docs Help). Note license/usage constraints.
2. **Raw fetch**: download into a temporary local folder (NOT committed to git). Path convention: `apps/<app>/app-docs/helper/<source>_raw/` — added to `.gitignore` immediately.
3. **Multi-pass AI filtering**: review the raw corpus with the model multiple times to extract scope, features, functionality, UI specs, etc. into structured `.md` files.
4. **Final extraction**: produce the committed corpus under `apps/<app>/app-docs/helper/extracted/` and `apps/<app>/app-docs/helper/analysis/`. Each piece must trace back to its raw source via citations or section refs.
5. **Index**: write `apps/<app>/app-docs/helper/00-overview.md` as the single entry point. Every other helper file is reached through it. (See `helper-blind-read-prevent` skill.)
6. **Verify gitignore**: confirm raw paths are gitignored before any commit. The committed helper should be small enough to be useful as agent context.

The figma corpus is the working example: `apps/figma/app-docs/helper/00-overview.md` shows the final structure.
