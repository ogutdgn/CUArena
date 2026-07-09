# pixel — ElementFromPoint hit-testing + pixel sampling for owner-drawn surfaces

> Evidence paths below refer to the MS-Word crawler this was distilled from
> (mirrored in `references/word-crawler/`).

## Purpose

Some surfaces are **owner-drawn**: the app paints them as pixels and exposes little or nothing
to UIA tree walks (Office ribbon flyouts return an empty container; color-palette swatches have
NO per-cell UIA element at all). Two recovery tools work together: **`ElementFromPoint`
grid sampling** (ask "what element is at this screen point?" across the surface) and **pixel
sampling from the screenshot** (read what the API cannot name — e.g. swatch colors and grid
geometry).

## How to use

**Grid-sample a popup with `ElementFromPoint`** (`crawler/capture.py::_sample_popup`):

```python
iuia = IUIA().iuia                      # raw IUIAutomation
y = top + 4
while y < bottom - 3:
    x = left + 5
    while x < right - 5:
        el = iuia.ElementFromPoint(POINT(x, y))
        ct, name, rect = el.CurrentControlType, el.CurrentName, el.CurrentBoundingRectangle
        enabled = el.CurrentIsEnabled
        ...                             # dedupe, see below
        x += 8
    y += 6
```

Dedupe correctly: **menu items by NAME** (distinct labels), but **gallery/color cells by
rounded GEOMETRY** — owner-drawn cells share an empty Name, so a (type, name) key collapses ~70
swatches into one (`crawler/capture.py` module docstring).

**Read colors from the screenshot, not the API** — there is no reliable UIA color property:

```python
r, g, b = Image.open(png).convert("RGB").getpixel((cx, cy))   # -> "#RRGGBB"
```

(`crawler/shots.py::sample_rgb`)

**Detect color-grid geometry from pixels** (`crawler/capture.py::_detect_color_grids`):
sample the background color at a corner (2,2); a swatch ROW is a y where ≥4 evenly-spaced
probes are non-background; cluster rows into bands; find column centers on the densest scanline
by splitting on background gaps OR large color jumps (handles both gapped grids and contiguous
theme grids); find row centers as the transpose, taking the **median row-set across all
columns** (robust to one noisy column). Assign grid coordinates (column = theme slot,
row = tint) by center ranking (`::_assign_grid_pos`).

## Known traps

- **Don't trust header rectangles inside owner-drawn surfaces:** section header elements span
  the swatch rows below them, so `header.bottom` is useless for band boundaries — pixels decide
  (`crawler/capture.py::_detect_color_grids` docstring).
- **Skip container hits.** `ElementFromPoint` frequently returns the popup's own Pane — filter
  by control type before recording (`crawler/capture.py::_sample_popup`).
- **A NAMED cell inside a color picker is a command, not a swatch** ("Automatic", "No Color") —
  route named cells through the normal item path, blank-named ones through the swatch path
  (`crawler/capture.py::capture_popup`).
- **Owner-drawn lists can be scrollable:** point sampling only sees the visible window. Mark
  such captures `dynamic` (an honest sample, not a false-complete enumeration) — e.g. a font
  list showing the machine's installed fonts (`crawler/capture.py::capture_popup` comment).
- **Chasing per-variant pixel perfection regresses siblings.** After the main color-picker fix,
  two pickers kept a residual duplicate row/col; further per-picker CV tuning broke other
  pickers. The project stopped, documented the residual, and moved on — swatches carry real RGB
  either way (`crawler/capture.py::_detect_color_grids` comment "#3").

## Lessons learned

- 2026-07-09 — **"Invisible to the tree" ≠ "invisible to UIA".** The tree walk shows an empty
  container, yet `ElementFromPoint` resolves real items at those coordinates — always try
  point-probing before declaring a surface unreadable.
  (learned from `crawler/capture.py` module docstring, `::_sample_popup`)
- 2026-07-09 — **The dedup key must match the surface's drawing model.** Name-keyed dedup for
  labeled items; geometry-keyed dedup for anonymous painted cells. Getting this wrong collapses
  or duplicates content silently.
  (learned from `crawler/capture.py::_sample_popup`)
- 2026-07-09 — **Pixels are a first-class data source, not a fallback of last resort:** swatch
  RGB values, grid row/column detection, and screenshot-hash dedup (see `screenshot.md`) are
  all pixel-derived facts the APIs simply do not carry.
  (learned from `crawler/shots.py::sample_rgb`, `crawler/capture.py::_detect_color_grids`,
  `crawler/emit.py::_shot_sig`)
- 2026-07-09 — **Sample step sizes matter less than dedupe + ordering:** the crawler probes
  every 8px horizontally / 6px vertically, then sorts unique hits top-to-bottom, left-to-right
  to reconstruct reading order.
  (learned from `crawler/capture.py::_sample_popup`)
