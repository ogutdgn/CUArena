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

1. **Phase 2.3 — icon theme decision** (pending owner visual review).
   Open question: is current `sifr_dark` close enough to Word M365,
   or do we fork a `cua_word` icon theme? Owner needs to visually
   review the V2.1 palette on WSLg first.
   - If `sifr_dark` adequate → skip 2.3 entirely.
   - If not → 2.3b spec in [`ui/ui-plan.md`](ui/ui-plan.md) §5.3:
     50-100 SVG replacements from Fluent UI / Lucide, plus
     `configure.ac` `WITH_THEMES` allow-list edit and
     `postprocess/CustomTarget_images.mk` confirm.
2. **Phase 3 — comfort + optional depth.** All three items optional;
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

Phase 2.3 and Phase 3 can run in parallel — icon work doesn't share
files with DSL / watcher / paint patches.

## Doc gaps surfaced 2026-05-24

- **View → User Interface picker hardcoded.**
  `cui/source/dialogs/uipickerdlg.cxx` lists 7 built-in modes as
  fixed radio buttons (Standard Toolbar / Tabbed / Single Toolbar /
  Sidebar / Tabbed Compact / Groupedbar Compact / Contextual Single);
  custom XCU variants (like our CUA) **do not appear** in the
  picker, and the dialog defaults its radio selection to the first
  entry ("Standard Toolbar") when the active variant isn't
  recognized. **Caveat:** clicking "Apply to Writer" or "Apply to
  All" in this picker with CUA active will silently overwrite the
  CUA default. This should be added to [`USAGE.md`](USAGE.md)
  troubleshooting and the risks table in
  [`ui/ui-plan.md`](ui/ui-plan.md) §9. (Verification of active
  variant: terminal — `grep ActiveWriter ~/.config/libreoffice/4/user/registrymodifications.xcu`,
  empty result = using XCU shipped default = `notebookbar_cua.ui`.)

## Open decisions

- ~~Light + dark palette both or only dark?~~ — **dark only**
  (decided 2026-05-22).
- Existing icon theme first (`sifr_dark` / `colibre_dark`) or
  build `cua_word` from scratch? — **pending owner visual review
  of Phase 2.1 on WSLg**.
- Hide vanilla LO menubar to match Word M365 (which has no menubar
  above the ribbon)? — **open**, owner noticed during 2026-05-24
  visual review. Trivial flip in `ToolbarMode.xcu` CUA entry
  (`HasMenubar=false`) if accepted.

## Future (from ROADMAP)

- **Phase 5** — Calc logger + UI redesign (→ Excel).
- **Phase 6** — Impress logger + UI redesign (→ PowerPoint).
- **Phase 7** — Docker multi-stage distribution image.
