# CUA Word-Dark Palette

> Color scheme `COLOR_SCHEME_CUA_WORD_DARK` injected into
> `officecfg/.../Office/UI.xcu` by
> [`scripts/build-cua-palette.py`](../../scripts/build-cua-palette.py).
> Generated 2026-05-23 (Phase 2.1).
>
> **What this is:** a `ThemeColors` color scheme set as the default
> `CurrentColorScheme`. Affects VCL paint (ribbon, menus, dialogs,
> sidebar) and — via `vcl/unx/gtk3/custom-theme.cxx` — GTK paint
> surfaces (HeaderBar, scrollbar, file picker).
>
> **What this is NOT:** an icon theme. The active icon theme is still
> `sifr_dark` from Phase 4 V1; Phase 2.3 will decide if we switch.

## Why a new scheme instead of editing vanilla DARK

Per `ui-plan.md` §3 principle "vanilla preserved", we add a new node
alongside the existing `COLOR_SCHEME_LIBREOFFICE_AUTOMATIC` /
`_LIGHT` / `_DARK` rather than mutating `_DARK`. Owner who selects
"LibreOffice Dark" from Tools → Options → Application Colors still
gets vanilla behavior. The Tools dropdown will show four schemes
total, with CUA Word Dark as the default `CurrentColorScheme`.

## Word M365 dark palette mapping

The palette aims for Microsoft Word's dark mode look (Office 2021 /
M365). 32 keys are pinned in the new scheme; the rest are left as
`<value xsi:nil="true"/>` (system-fallback, same as vanilla DARK).

### Group General — document chrome

| Key | Hex | Int | Role |
|---|---|---|---|
| `DocColor` | `#FFFFFF` | 16777215 | Document body (paper stays white in dark mode) |
| `AppBackground` | `#1F1F1F` | 2039583 | Area behind doc / Calc gridless area |
| `FontColor` | `#F0F0F0` | 15790320 | Default UI text fallback |

### Group Application — VCL widget paint

| Key | Hex | Int | Role |
|---|---|---|---|
| `WindowColor` | `#2B2B2B` | 2829099 | Ribbon body, dialogs, menu bg |
| `WindowTextColor` | `#F0F0F0` | 15790320 | Text on WindowColor |
| `BaseColor` | `#1F1F1F` | 2039583 | Input fields / list views bg |
| `ButtonColor` | `#2B2B2B` | 2829099 | Toolbar / push button bg |
| `ButtonTextColor` | `#F0F0F0` | 15790320 | Text on buttons |
| `AccentColor` | `#2B5797` | 2840471 | Word classic blue (selection, focus) |
| `ActiveColor` | `#4A9EFF` | 4889855 | Active tab underline / hover accent |
| `DisabledColor` | `#3A3A3A` | 3815994 | Disabled button bg |
| `DisabledTextColor` | `#888888` | 8947848 | Disabled text |
| `ShadowColor` | `#1A1A1A` | 1710618 | Drop shadow |
| `SeparatorColor` | `#3A3A3A` | 3815994 | Toolbar / menu separators |
| `FaceColor` | `#2B2B2B` | 2829099 | Generic 3D face |

### Menus

| Key | Hex | Int | Role |
|---|---|---|---|
| `MenuColor` | `#2B2B2B` | 2829099 | Popup menu bg |
| `MenuTextColor` | `#F0F0F0` | 15790320 | Menu item text |
| `MenuBarColor` | `#2B2B2B` | 2829099 | Top menubar bg |
| `MenuBarTextColor` | `#F0F0F0` | 15790320 | Top menubar text |
| `MenuBarHighlightColor` | `#2B5797` | 2840471 | Top menubar hover |
| `MenuBarHighlightTextColor` | `#FFFFFF` | 16777215 | Top menubar hover text |
| `MenuHighlightColor` | `#2B5797` | 2840471 | Popup menu item hover |
| `MenuHighlightTextColor` | `#FFFFFF` | 16777215 | Popup menu item hover text |
| `MenuBorderColor` | `#1A1A1A` | 1710618 | Popup menu border |

### Inactive states

| Key | Hex | Int | Role |
|---|---|---|---|
| `InactiveColor` | `#3A3A3A` | 3815994 | Inactive window bg |
| `InactiveTextColor` | `#888888` | 8947848 | Inactive text |
| `InactiveBorderColor` | `#3A3A3A` | 3815994 | Inactive border |

### Writer-specific

| Key | Hex | Int | Role |
|---|---|---|---|
| `WriterFieldShadings` | `#3A4A60` | 3820128 | Field hint background |
| `WriterHeaderFooterMark` | `#4A4A4A` | 4868154 | Header / footer separator mark |
| `WriterPageBreaks` | `#666666` | 6710886 | Page break line |
| `WriterIdxShadings` | `#3A4A60` | 3820128 | Index / TOC background hint |
| `WriterSectionBoundaries` | `#3A3A3A` | 3815994 | Section boundary line |

## What's NOT pinned

The CUA scheme inherits ~50 other keys as `<value xsi:nil="true"/>`,
deferring to the schema / system. Notable groups left at nil:

- **Author1-Author9** — comment-author identification colors. Default
  rotating palette is fine.
- **BASICEditor / SQL\*** — internal editor highlighting. Irrelevant
  for typical Writer use.
- **CalcGrid / CalcCellFocus / Calc\*** — Calc-specific (no Calc UI
  work yet — Phase 5).
- **DrawGrid** — Impress / Draw.
- **HTMLSGML / HTMLComment / HTMLKeyword / HTMLUnknown** — HTML
  editor (not exposed in our stripped Writer build).
- **Links / LinksVisited / Spell / Grammar / SmartTags / Shadow** —
  document content overlay markers. Default colors are reasonable.

If any of these become a visual gap, add to `WORD_PALETTE` in
`scripts/build-cua-palette.py` and re-run.

## Regenerating

Idempotent — re-run anytime:

```sh
python apps/libreoffice/scripts/build-cua-palette.py
make sw postprocess   # or `make` for full incremental
```

The script removes the existing `COLOR_SCHEME_CUA_WORD_DARK` block
(if present) before re-injecting, so palette edits are non-additive.

## How values flow at runtime

1. `Office.UI/CurrentColorScheme` → `COLOR_SCHEME_CUA_WORD_DARK`
2. `svtools::ColorConfig_Impl` reads `ColorScheme/ColorSchemes/COLOR_SCHEME_CUA_WORD_DARK/<Key>/Color` for each key (`svtools/source/config/colorcfg.cxx:137-181,356-393`)
3. Values copied into the `ThemeColors` singleton in `LoadThemeColorsFromRegistry()` (`colorcfg.cxx:356-393`)
4. VCL widgets read from `Application::GetSettings().GetStyleSettings()` which is fed by `ThemeColors`
5. GTK CSS provider (`vcl/unx/gtk3/custom-theme.cxx:CreateStyleString()`) regenerates GTK CSS from `ThemeColors` on every theme change

So setting `Office.UI/...` cascades through both VCL and GTK paint paths.

## Decisions deferred

- **Light variant** — `COLOR_SCHEME_CUA_WORD_LIGHT` not built (owner
  decision 2026-05-22: dark only for now).
- **Icon theme** — Phase 2.3, separate from palette. Currently
  `sifr_dark` (inherited from Phase 4 V1).
