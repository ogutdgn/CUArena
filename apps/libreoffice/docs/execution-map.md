# LibreOffice — Execution Map

> What's queued. **What we're going to do next** — nothing else.
> Auto-maintained by the `update-execution-map` skill.

Last updated: 2026-05-22

---

## Next

**Active effort: Writer UI flexibility (3-week plan).** Full plan
and per-phase detail in [`ui/ui-plan.md`](ui/ui-plan.md). Phase
status tracked in [`ui/README.md`](ui/README.md).

**Phase 1 verified in source + WSL build green (2026-05-22):**

1. **Phase 1.1 — Ribbon anatomy map** — done. See
   [`ui/ribbon-anatomy.md`](ui/ribbon-anatomy.md).
2. **Phase 1.2 — Hot-reload workflow** — done.
   `scripts/sync-ui.sh` written with user-profile shadow check,
   `USAGE.md` "Ribbon iteration" section added.
3. **Phase 1.3 — CUA notebookbar variant fork** — done with 3
   build-system fixes surfaced by smoke test:
   - `notebookbar_cua.ui` fork (17,349 lines)
   - `ToolbarMode.xcu` CUA ModeEntry + `ActiveWriter`/`Active`
     defaults flipped
   - `sw/UIConfig_swriter.mk` registers `notebookbar_cua` for
     build packaging (was missed in v1 plan)
   - `solenv/sanitizers/ui/modules/swriter.false` +696 mirror
     lines for a11y fatals (was missed in v1 plan)
   - `solenv/sanitizers/ui/modules/swriter.suppr` +8 mirror
     lines (was missed in v1 plan)
   - **Smoke test result:** `make` RC=0 in 17s; soffice launches
     with CUA default (rllogger captured 2 sessions, profile
     `registrymodifications.xcu` created normally with no
     fallback-variant indicator); screenshot deferred due to
     xvfb/soffice render compatibility (functional verification
     deemed sufficient — owner can visual-verify on next launch).

After Phase 1 verify: Phase 2 (Word palette via
`Office.UI/ColorScheme` overrides + GTK CSS auto-flow + icon
strategy decision), then Phase 3 (DSL transpiler, watcher,
optional VCL paint patches).

Open decisions blocking Phase 2 start (see [`ui/ui-plan.md`](ui/ui-plan.md) §13):

- ~~Light + dark palette both or only dark?~~ — **dark only** (decided 2026-05-22)
- Existing icon theme first (`sifr_dark` / `colibre_dark`) or
  build `cua_word` from scratch?

## Future (from ROADMAP)

- **Phase 5** — Calc logger + UI redesign (→ Excel).
- **Phase 6** — Impress logger + UI redesign (→ PowerPoint).
- **Phase 7** — Docker multi-stage distribution image.
