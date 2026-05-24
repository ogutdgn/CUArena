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

## On feature branches, pending PR / merge

- **Phase 4 V2 — UI flexibility foundation** (branch
  `feat/libreoffice-ui-phase1`, 2026-05-22). Owner-iterable ribbon
  via fork + hot-reload. See [`docs/ui/`](ui/README.md) and
  [`docs/ui/ui-plan.md`](ui/ui-plan.md).
  - Ribbon anatomy map ([`docs/ui/ribbon-anatomy.md`](ui/ribbon-anatomy.md)) —
    every Home-tab button → file:line + UNO command + icon/label
    source. Other tabs at group-level.
  - Hot-reload workflow — `scripts/sync-ui.sh` (with user-profile
    shadow check) + USAGE.md "Ribbon iteration" section. Edit
    `.ui` + sync + restart = ~5s loop, no rebuild.
  - CUA notebookbar variant — `notebookbar_cua.ui` forked from
    vanilla (17,349 lines). Registered in `ToolbarMode.xcu` as
    `Applications/Writer/Modes/CUA`, set as Writer default. Build
    integration via `sw/UIConfig_swriter.mk` +
    `solenv/sanitizers/ui/modules/swriter.{false,suppr}` mirrors.
  - WSL smoke test green: `make` RC=0, instdir packaged
    notebookbar_cua.ui, xcd registry has CUA entry, soffice launches
    with CUA default (functional verified; visual screenshot
    deferred due to xvfb/soffice GTK render compatibility).

- **Phase 4 V2.1 — CUA Word Dark palette** (branch
  `feat/libreoffice-ui-phase2`, branched off phase1, 2026-05-23).
  New `Office.UI/ColorScheme` named `COLOR_SCHEME_CUA_WORD_DARK`,
  set as the default `CurrentColorScheme`. Vanilla schemes
  (AUTOMATIC / LIGHT / DARK) preserved. Built by idempotent
  generator script [`scripts/build-cua-palette.py`](scripts/build-cua-palette.py);
  32 high-impact ThemeColors keys pinned (ribbon `#2B2B2B`,
  AccentColor `#2B5797` Word blue, ActiveColor `#4A9EFF`, etc.).
  Full palette table in [`docs/ui/word-palette.md`](ui/word-palette.md).
  Affects both VCL paint and GTK paint (via
  `custom-theme.cxx`'s auto-flow from `ThemeColors`).
  WSL smoke test green; xcd registry has CUA scheme + AccentColor
  int; soffice loads with our scheme as default.

## Current branch

`feat/libreoffice-ui-phase2` — Phase 4 V2.1 dark palette on top of
phase1, pending owner PR review of phase1 first (phase2 branches
off phase1, so merge order matters).

## Code touchpoints (last shipped change on `main`)

- `apps/libreoffice/libreoffice-codebase/vcl/unx/gtk3/gtkframe.cxx`
- `apps/libreoffice/libreoffice-codebase/vcl/source/control/tabctrl.cxx`
