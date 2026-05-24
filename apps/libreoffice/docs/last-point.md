# LibreOffice — Last Point

> Current state of the cua-bench LibreOffice fork. **What's shipped on
> `main`** — nothing else. Auto-maintained by the `update-last-point`
> skill.

Last updated: 2026-05-24

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
- **Phase 4 V2 — UI flexibility foundation** (PR #58, merged
  2026-05-24, `be3303759`). Owner-iterable ribbon via fork +
  hot-reload. See [`docs/ui/`](ui/README.md) and
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
- **Phase 4 V2.1 — CUA Word Dark palette** (PR #59, merged
  2026-05-24, `5b2d935f2`).
  New `Office.UI/ColorScheme` named `COLOR_SCHEME_CUA_WORD_DARK`,
  set as the default `CurrentColorScheme`. Vanilla schemes
  (AUTOMATIC / LIGHT / DARK) preserved. Built by idempotent
  generator script [`scripts/build-cua-palette.py`](../scripts/build-cua-palette.py);
  32 high-impact ThemeColors keys pinned (ribbon `#2B2B2B`,
  AccentColor `#2B5797` Word blue, ActiveColor `#4A9EFF`, etc.).
  Full palette table in [`docs/ui/word-palette.md`](ui/word-palette.md).
  Affects both VCL paint and GTK paint (via
  `custom-theme.cxx`'s auto-flow from `ThemeColors`).

## On feature branches, pending PR / merge

_(none — between phases on `main`)_

## Current branch

`main` — Phase 4 V2 and V2.1 both shipped. Next feature work branches
off `main`. Current open item: owner visual review of V2.1 palette on
WSLg to decide whether to fork a `cua_word` icon theme (Phase 2.3) or
keep `sifr_dark`.

## Code touchpoints (last shipped change on `main`)

- `apps/libreoffice/libreoffice-codebase/officecfg/registry/data/org/openoffice/Office/UI.xcu` (CUA Word Dark scheme + `CurrentColorScheme` flip)
- `apps/libreoffice/scripts/build-cua-palette.py` (idempotent palette generator)
