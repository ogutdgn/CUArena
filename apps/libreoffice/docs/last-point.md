# LibreOffice — Last Point

> Current state of the cua-bench LibreOffice fork. **What's shipped on
> `main`** — nothing else. Auto-maintained by the `update-last-point`
> skill.

Last updated: 2026-05-22

---

## Shipped on `main`

- **Phase 0** — Vanilla build verified.
- **Phase 1** — Module deletions, 7 groups (1A–1G).
- **Phase 3** — Writer logger V1.1 (raw / semantic / outcome streams,
  always-on, `~/.lo-rl-logs/<session>/`).
- **Phase 4 V1** — Writer UI redesign: Tabbed notebookbar default,
  Word tab order (File / Home / Insert / Design / Layout / References
  / Mailings / Review / View / Help), dark theme, `sifr_dark` icons,
  Home tab restructured to Word's 8 groups, sidebar suppressed.
- **lo/ui-improve** (squash-merged `5d5d6db39`) —
  - GTK Client-Side Decoration: `GtkHeaderBar` titlebar on every
    document workspace toplevel (Writer / Calc / Impress).
  - Quick Access Toolbar in the HeaderBar: Save / Undo / Redo
    GtkButtons dispatching through `comphelper::dispatchCommand`.
  - HeaderBar decoration layout forced to
    `:minimize,maximize,close`, no subtitle slot.
  - Tab-strip hamburger menu (`m_pOpenMenu`) and in-tab-strip
    shortcuts ToolBox (`m_pShortcuts`) hidden; tab row reclaims the
    full strip.

## Current branch

`main` — clean.

## Code touchpoints (last shipped change)

- `apps/libreoffice/libreoffice-codebase/vcl/unx/gtk3/gtkframe.cxx`
- `apps/libreoffice/libreoffice-codebase/vcl/source/control/tabctrl.cxx`
