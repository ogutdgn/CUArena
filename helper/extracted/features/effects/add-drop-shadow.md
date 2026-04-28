# Add drop shadow

- **Category:** effects
- **One-line summary:** Add a drop-shadow effect to a layer; configure offset / blur / spread / color / blend-mode.

## Triggers
- Right sidebar **Effects** section → `+` → choose **Drop shadow**.

## Preconditions
- A layer selected.

## Inputs
- After add: per-effect row exposes:
  - X offset, Y offset (px)
  - Blur radius (px)
  - Spread radius (px)
  - Color (with opacity, picker)
  - Blend mode (Normal, Multiply, etc.)
  - Visibility eye

## Behavior
1. Effect appended to layer's `effects` array with `type: "drop_shadow"`.
2. Renderer composites the shadow under the layer's geometry.

## Outputs
- **Scene graph changes:** `effects` array gains entry.
- **Selection changes:** none.

## UI feedback
- Effect row in Effects section; canvas re-renders.

## Side effects
- Undo stack: one entry per change.

## Related UI schema entries
- `regions/right-properties.md` → effects-section

## Semantic event(s) candidate
- `add_effect { layer_ids, type: "drop_shadow", default_params, trigger }`
- `set_effect_property { layer_ids, effect_index, property, from, to, trigger }`

## Source articles
- `apply-effects-to-layers`
- `apply-blend-modes-to-layers-fills-and-effects`
