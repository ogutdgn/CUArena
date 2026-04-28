# Set vertical trim

- **Category:** text
- **One-line summary:** Toggle vertical trim — crop the extra space above and below text so the bounding box matches cap-height / baseline.

## Triggers
- Open Type-settings → **Basics** tab → Vertical trim toggle.

## Preconditions
- A text layer is selected.

## Inputs
- Click toggle (boolean).

## Behavior
1. When ON: bounding box vertical extent is trimmed to cap-height / baseline.
2. When OFF (default): bounding box includes typeface's intrinsic ascender / descender padding.
3. The setting does not change the layer's measurement values directly, but changes how the parent layout sees the text's box (corpus: "may change the final dimensions of its parent layer").

## Outputs
- **Scene graph changes:** `verticalTrim: bool` on layer.
- **Selection changes:** none.

## UI feedback
- Toggle reflects state.
- Canvas: bounding-box visual adjusts on next layout.
- Dev Mode: emits `leading-trim: both;` CSS hint.

## Side effects
- Undo stack: one entry per toggle.
- Layout side effect: parent auto-layout frame may re-pack.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → type-settings-popover → vertical-trim-toggle

## Semantic event(s) candidate
- `set_text_property { layer_id, range: null, property: "vertical_trim", from: bool, to: bool, trigger: "click_button" }`

## Source articles
- `explore-text-properties`

## Notes / gaps
- Visual rendering of trim is metric-driven — engine must read font's cap-height / baseline. [gap: which metrics to use exactly] — pick a sensible default.
