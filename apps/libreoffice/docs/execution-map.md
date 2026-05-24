# LibreOffice — Execution Map

> What's queued. **What we're going to do next** — nothing else.
> Auto-maintained by the `update-execution-map` skill.

Last updated: 2026-05-24

---

## Next

**Active effort: Writer UI flexibility (3-week plan).** Full plan
and per-phase detail in [`ui/ui-plan.md`](ui/ui-plan.md). Phase
status tracked in [`ui/README.md`](ui/README.md).

**Shipped to `main` 2026-05-24** (PR #58 + #59): Phase 1.1–1.3
(ribbon anatomy + hot-reload + CUA notebookbar variant) and
Phase 2.1–2.2 (CUA Word Dark palette + auto-flow to GTK). See
[`last-point.md`](last-point.md) for the full shipped feature set.

**Queued (in priority order):**

1. **Phase 3 — comfort + optional depth.** All three items optional;
   pick what hurt during Phases 1+2:
   - **3.1 DSL transpiler** — YAML/TS → `notebookbar_cua.ui` XML
     generator. Skip unless structural edits felt painful at raw-XML
     level.
   - **3.2 File watcher daemon** — `inotifywait` + auto-sync +
     soffice restart. Skip unless manual `sync-ui.sh` loop is a
     friction point.
   - **3.3 Targeted VCL paint patches** — border radius / focus
     ring / padding (C++ rebuild, scoped per change). Only if
     V2.1 visual review surfaces specific gaps the CUA agent will
     notice.

**Deferred (revisit after Phase 3):**

- **Phase 2.3 — icon theme decision.** Owner decision 2026-05-24:
  ship as-is on `sifr_dark`, revisit after Phase 3 work lands so
  the visual review can happen against the more complete UI (incl.
  whatever VCL paint patches end up in 3.3). Open question
  unchanged: is `sifr_dark` close enough to Word M365, or do we
  fork a `cua_word` icon theme? Spec for the fork path lives in
  [`ui/ui-plan.md`](ui/ui-plan.md) §5.3 (50-100 SVG replacements
  from Fluent UI / Lucide, plus `configure.ac` `WITH_THEMES`
  allow-list edit and `postprocess/CustomTarget_images.mk`
  confirm).

## Open decisions

- ~~Light + dark palette both or only dark?~~ — **dark only**
  (decided 2026-05-22).
- ~~Existing icon theme first (`sifr_dark` / `colibre_dark`) or
  build `cua_word` from scratch?~~ — **deferred to post-Phase-3**
  (decided 2026-05-24, see "Deferred" above).
- ~~Hide vanilla LO menubar to match Word M365?~~ — **yes, hide**
  (decided + shipped on main 2026-05-24: `ToolbarMode.xcu` CUA
  entry `HasMenubar=false`).
- ~~`View → User Interface` picker overwrites CUA — document the
  risk?~~ — **documented 2026-05-24** in [`USAGE.md`](USAGE.md)
  "Important caveat" section.

## Future (from ROADMAP)

- **Phase 5** — Calc logger + UI redesign (→ Excel).
- **Phase 6** — Impress logger + UI redesign (→ PowerPoint).
- **Phase 7** — Docker multi-stage distribution image.
