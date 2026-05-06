# Add noise / texture / glass effects

- **Category:** effects
- **One-line summary:** Apply additional effect types — Noise, Texture, Glass — listed in the Effects picker.

## Triggers
- Right sidebar **Effects** section → `+` → choose **Noise**, **Texture**, or **Glass**.

## Preconditions
- A layer selected.

## Inputs
- Per-effect parameters (varies). Per `apply-effects-to-layers`:
  - **Noise**: density, size, opacity, blend mode.
  - **Texture**: pattern type, scale.
  - **Glass**: refraction / bevel-like settings.

## Behavior
1. Effect appended to layer.
2. Renderer composites accordingly.

## Outputs
- **Scene graph changes:** `effects` gains entry.

## UI feedback
- Effect row + canvas redraws.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → effects-section

## Semantic event(s) candidate
- `add_effect { layer_ids, type: "noise" | "texture" | "glass", default_params, trigger }`

## Source articles
- `apply-effects-to-layers`

## Notes / gaps
- Exact parameter list per effect is not exhaustively reproduced in the article excerpt — refer to `apply-effects-to-layers` for full controls.
