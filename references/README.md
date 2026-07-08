# References — inspire, never dictate

These are **donated example scripts** from earlier, manual replication work. They are here as
**base examples only** — reading material, not runnable pipeline parts.

The rules (same law as harvested docs):

1. **The pipeline must figure out how to drive each app itself.** These examples show *one way*
   it was once done for *one app*. They are not the way.
2. **Read for patterns, never copy as templates.** Useful ideas (journaling, snapshot-diff
   classification, depth-first dialog draining, resumable harvesting) have already been promoted
   into the design spec. App-specific mechanics (ribbon locators, dialog-class lists, COM document
   hashing, Zendesk API shapes) must never leak into general pipeline code.
3. **Never trust as facts.** These scripts are unverified and were written against specific app
   versions. Nothing in them counts as knowledge about any app.

## Contents

- `word-crawler/` — Python crawler that walked Microsoft Word's ribbon UI on Windows:
  UIA enumeration, press-observe-classify-restore probing, snapshot-diff outcome classification,
  depth-first dialog draining, ElementFromPoint grid sampling for owner-drawn flyouts,
  append-only JSONL journal, reconciling emitter. Includes its unit tests.
- `docs-harvester/` — Python harvester that extracted a help-center documentation site
  (Zendesk API) into per-article markdown + images + metadata, with a cross-article link graph
  and resumable progress tracking. Includes the methodology notes written alongside it.
