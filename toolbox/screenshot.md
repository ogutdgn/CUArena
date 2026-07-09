# screenshot — surface captures, crops, and geometry that stays truthful

> Evidence paths below refer to the MS-Word crawler this was distilled from
> (mirrored in `references/word-crawler/`).

## Purpose

Screenshots serve three distinct jobs: (1) the visual record of every captured surface (a human
or reviewer agent can check the JSON against the picture), (2) the source for icon/preview
crops, and (3) a **surface identity signal** (byte-hash) when structure alone can't distinguish
dialogs. The cardinal invariant: every recorded `bounds` must be a pixel rect **inside the
owning surface's screenshot** — geometry that doesn't match the picture is worse than no
geometry.

## How to use

**Grab by screen rect, multi-monitor aware** (`crawler/shots.py::grab`):

```python
ImageGrab.grab(bbox=rect, all_screens=True).save(out)   # all_screens: bbox is virtual-desktop
```

**One screenshot per surface; per-tab shots for multi-tab dialogs** (filename carries the tab:
`dialogs__font@advanced.png`) (`crawler/capture.py::capture_dialog`).

**Crop icons/previews from the surface shot you already took** — never re-grab the screen for a
sub-rect; the surface may have moved or closed (`crawler/shots.py::crop_from`,
`crawler/capture.py::_crop_preview`).

**Control icons = one surface screenshot + N crops.** The crawler never screenshots buttons
individually: it grabs the whole ribbon ONCE, then crops each control's rect out of that image
(`icon__<control-id>.png`), gates each crop through the quality check, and records the
control's `bounds` with an `in: <ribbon screenshot>` back-reference so the geometry stays
verifiable against the source image (`crawler/run_p0.py::icon_and_bounds`). Gallery tile
previews reuse the same idiom against the popup's screenshot
(`crawler/capture.py::_crop_preview`).

**Gate crop quality:** reject crops under 4×4 px and single-color crops (blank tile = the crop
missed) (`crawler/shots.py::quality_ok`).

**Record geometry RELATIVE to the surface** so it stays valid inside the screenshot:

```python
def rel_bounds(control_rect, surface_rect):
    l, t, r, b = control_rect; sl, st, _, _ = surface_rect
    return {"x": l - sl, "y": t - st, "w": r - l, "h": b - t}
```

**Screenshot byte-hash as identity for structure-poor surfaces:** two captures of the same
physical dialog render identical pixels; two different zero-field alert boxes differ visually.
Hash the tab screenshots (sha256) and merge only on identical hashes
(`crawler/emit.py::_shot_sig`).

## Known traps

- **A coordinate grab photographs whatever is at those coordinates** — not "the surface you
  meant". When a disabled item was pressed and no dialog opened, the capture screenshotted the
  still-open flyout and shipped it as the dialog's picture. The screenshot is only as truthful
  as your "what is open right now?" evidence (`docs/DEPTH_REVIEW.md` cluster 7 of the source
  project).
- **Scrolling breaks the bounds↔screenshot contract.** The pane screenshot is taken before
  scrolling; items enumerated after a scroll have on-screen rects that map to the WRONG pixels
  of that screenshot (and can collide with rects of items recorded earlier). Items collected
  post-scroll carry `scrolled: true` and **no bounds** (`crawler/capture.py::capture_pane::_collect`
  docstring).
- **Overlapping chrome corrupts geometry too:** a pane's footer controls are painted OVER the
  last list rows, so those clipped rows report bounds colliding with the footer. Drop the bounds
  of any listitem overlapping a non-listitem control >40% and flag it `occluded`
  (`crawler/capture.py::_drop_occluded_bounds`).
- **Icon crops silently go blank** when the source rect was wrong — the single-color quality
  gate catches most of these (`crawler/shots.py::quality_ok`).

## Lessons learned

- 2026-07-09 — **Keep the screenshot and the JSON as a verifiable pair.** The most effective
  review the source project ran was agents comparing "what the JSON claims" against "what the
  screenshot shows" — it caught duplicated dialogs, stale submenu content, and wrong-window
  captures that no schema check could see.
  (learned from `docs/DEPTH_REVIEW.md` findings of the source project)
- 2026-07-09 — **When structure can't identify a surface, pixels can.** Field-rich dialogs
  dedup by (title + field names + buttons); field-poor panels (empty title, zero fields) dedup
  by screenshot byte-hash — and different alerts stay separate because their message text
  renders differently.
  (learned from `crawler/emit.py::_dlg_sig`/`::_shot_sig`)
- 2026-07-09 — **Geometry must degrade honestly.** If you can't guarantee a rect maps onto the
  surface screenshot (scrolled-in, occluded), omit the rect and say why (`scrolled`/`occluded`
  flags) — downstream consumers doing click-replay or visual judging depend on it.
  (learned from `crawler/capture.py::capture_pane`, `::_drop_occluded_bounds`)
