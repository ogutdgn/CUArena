# Add layer blur

- **Category:** effects
- **One-line summary:** Apply a Gaussian blur to a layer's content (and its children if a frame).

## Triggers
- Right sidebar **Effects** section → `+` → **Layer blur**.

## Preconditions
- A layer selected.

## Inputs
- Blur radius (px).
- Visibility eye.

## Behavior
1. Effect blurs the layer (and children for frames) by the given radius.
2. Layer extent may grow visually due to blur halo.

## Outputs
- **Scene graph changes:** `effects` gains `{ type: "layer_blur", radius }`.
- **Selection changes:** none.

## UI feedback
- Canvas re-renders blurred.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → effects-section

## Semantic event(s) candidate
- `add_effect { layer_ids, type: "layer_blur", default_params, trigger }`

## Source articles
- `apply-effects-to-layers`
