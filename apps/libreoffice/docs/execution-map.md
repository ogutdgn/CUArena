# LibreOffice — Execution Map

> What's queued. **What we're going to do next** — nothing else.
> Auto-maintained by the `update-execution-map` skill.

Last updated: 2026-05-22

---

## Next

1. **CSD paint pipeline** — Make the document HeaderBar background
   and the notebookbar tab strip respond to colour overrides.
   Targets: HeaderBar `#1F1F1F`, tab strip `#2B2B2B`, File tab blue
   button `#2B5797`, active tab 2 px underline `#4A9EFF`, hover
   `rgba(255,255,255,0.05)`, close-button hover red `#E81123`.
   Run `GtkInspector` (`GTK_DEBUG=interactive` + Ctrl-Shift-I)
   against a live LO window FIRST to identify the actual paint
   path — earlier blind CSS attempts didn't land.
2. **Home tab ribbon — Word M365 pixel styling.** Detailed colour /
   spacing / font / dialog-launcher tuning on top of the Phase 4
   V1 group structure. Independent of #1 (different paint layer:
   tab BODY, not tab strip / titlebar).

## Future (from ROADMAP)

- **Phase 5** — Calc logger + UI redesign (→ Excel).
- **Phase 6** — Impress logger + UI redesign (→ PowerPoint).
- **Phase 7** — Docker multi-stage distribution image.
