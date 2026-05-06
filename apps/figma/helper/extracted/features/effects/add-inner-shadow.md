# Add inner shadow

- **Category:** effects
- **One-line summary:** Add an inner-shadow effect; same parameters as drop shadow but composited inside the layer.

## Triggers
- Right sidebar **Effects** section → `+` → **Inner shadow**.

## Preconditions / Inputs / Behavior / Outputs / UI feedback / Side effects
- Same as `add-drop-shadow.md` with `type: "inner_shadow"`.

## Related UI schema entries
- `regions/right-properties.md` → effects-section

## Semantic event(s) candidate
- `add_effect { layer_ids, type: "inner_shadow", default_params, trigger }`

## Source articles
- `apply-effects-to-layers`
