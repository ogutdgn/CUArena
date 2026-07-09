# enrich — LLM/agent-knowledge descriptions as a pipeline stage

> Evidence paths below refer to the MS-Word crawler this was distilled from
> (mirrored in `references/word-crawler/`).

## Purpose

Some captured commands carry no self-description: owner-drawn popup items have no tooltip
(no UIA FullDescription), so "what does this do?" cannot be read off the live control. The fix
is an **enrichment stage**: an agent writes 1–2 sentence descriptions from its own knowledge of
the app, those land in a curated fixture file, and the emitter stamps them onto matching items
on **every** rebuild. Descriptions become regenerable pipeline data — never hand-edits of
output.

## How to use

**Curated fixture, keyed by (surface-stem, normalized label)**
(`fixtures/feature_descriptions.json` in the source project):

```json
{"popup": "selectmenu", "label": "Select All",
 "description": "Selects the entire document contents (equivalent to Ctrl+A)…"}
```

**Emitter stamps at rebuild time** (`crawler/enrich.py::apply_to_popup`, called from
`crawler/emit.py::emit`): only onto `feature`/`toggles` LEAVES — an item that opens a surface
is documented as that surface, not as a leaf blurb.

**Label normalization is part of matching:** strip trailing dots/ellipsis and casefold —
UI labels vary by context ("Sentence case." gallery tile vs "Sentence case")
(`crawler/enrich.py::_norm`).

## Known traps

- **Enrich only true leaves.** The source project's reviewer proved 7 of 21 candidate "leaves"
  actually opened submenus/panes/dialogs — describing those as terminal features would have
  baked misclassifications into the KB. Classify first (press-and-observe), enrich second
  (`docs/DEPTH_REVIEW.md` cluster 4/5 of the source project).
- **A missing fixture must be a no-op, not an error** — enrichment is additive
  (`crawler/enrich.py::load_descriptions`).
- **Ribbon-level controls usually don't need this**: their tooltip (FullDescription) already is
  the description. Target the enrichment at the tooltip-less tail only
  (`crawler/uia.py::_props`, `docs/DEPTH.md` §4 of the source project).

## Lessons learned

- 2026-07-09 — **Prefer the app's own words, fall back to agent knowledge, web-search last.**
  ~80% of controls carried a usable tooltip in FullDescription; the policy reserves web search
  for genuinely obscure controls only — and in practice every Home-tab fixture entry is plain
  agent-written knowledge.
  (learned from `docs/DEPTH.md` §4 + `fixtures/feature_descriptions.json` of the source project)
- 2026-07-09 — **Make enrichment idempotent and regenerable** — a fixture the emitter re-applies
  each run survives full re-crawls; text patched into output files does not.
  (learned from `crawler/enrich.py` module docstring)
