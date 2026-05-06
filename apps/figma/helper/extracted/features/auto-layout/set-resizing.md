# Set resizing (Hug / Fill / Fixed / Min / Max)

- **Category:** auto-layout
- **One-line summary:** Per-axis sizing rule for an auto-layout frame or one of its children — Hug contents, Fill container, Fixed, plus optional Min / Max.

## Triggers
- Layout / Auto layout section → Width or Height dropdown → choose Hug / Fill / Fixed / Min / Max.
- Shortcut: double-click an edge of the bbox → Hug; `Alt`/`Option` + double-click edge → Fill.
- Type a numeric value into W or H → automatically becomes Fixed.

## Preconditions
- For Hug: layer is an auto-layout frame.
- For Fill: layer is a child of an auto-layout frame (not top-level).
- Fixed: any layer.
- Min/Max: optional with any of the above.

## Inputs
- Dropdown choice OR shortcut.

## Behavior

| Mode | Applies to | Behavior |
|---|---|---|
| **Hug contents** | Auto-layout frame | Frame shrinks/grows to fit children + padding |
| **Fill container** | Child of auto-layout frame | Layer expands to fill remaining axis space |
| **Fixed** | Any | Size stays absolute; manual resize sets this automatically |
| **Min width / height** | Any | Floor on dimension |
| **Max width / height** | Any | Ceiling on dimension |

- If a child of a Hug frame is set to Fill, the parent becomes Fixed on that axis.
- Min/Max are additional and combine with the base mode.

## Outputs
- **Scene graph changes:** layer's `width_mode` / `height_mode` updated; optional `min_width` / `max_width` / `min_height` / `max_height`.
- **Selection changes:** none.

## UI feedback
- W/H field icons reflect mode (e.g. Hug shows arrows-toward-center, Fill shows arrows-away).
- Hovering over a mode shows on-canvas preview lines.

## Side effects
- Undo stack: per-change.

## Related UI schema entries
- `regions/right-properties.md` → layout-section / auto-layout-section → W/H dropdowns

## Semantic event(s) candidate
- `set_resizing_mode { layer_id, axis: "w" | "h", from_mode, to_mode, trigger: "dropdown" | "shortcut" | "manual_resize" }`
- `set_min_max_dimension { layer_id, axis, kind: "min" | "max", from, to }`

## Source articles
- `guide-to-auto-layout`
- `apply-constraints-to-define-how-layers-resize` (cross)
