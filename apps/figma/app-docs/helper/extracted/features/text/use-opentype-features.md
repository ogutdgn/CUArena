# Use OpenType features

- **Category:** text
- **One-line summary:** Toggle font-specific OpenType features (ligatures, fractions, stylistic alternates, etc.) per the font's exposed feature set.

## Triggers
- Type-settings panel (`…` in Typography section) → **Details** tab → OpenType section.

## Preconditions
- Text selected.
- Font exposes one or more OpenType features (varies per font).

## Inputs
- Toggle clicks for each feature.

## Behavior
1. Features available depend on the font; common ones include:
   - Standard ligatures (e.g. `fi`, `fl`).
   - Discretionary ligatures.
   - Stylistic alternates (`salt`).
   - Stylistic sets (`ss01`–`ss20`).
   - Character variants (`cv01`–`cv99`).
   - Number style (lining/oldstyle, tabular/proportional).
   - Fractions, ordinals, superscripts, subscripts.
2. Toggling a feature updates the rendering of the glyphs that use it.

## Outputs
- **Scene graph changes:** text run(s) `opentype_features` map updated.
- **Selection changes:** none.

## UI feedback
- Type-settings panel shows on-state per feature; canvas redraws.

## Side effects
- Undo stack: per-toggle entries.

## Related UI schema entries
- `regions/floating-overlays.md` → type-settings panel → details tab

## Semantic event(s) candidate
- `set_opentype_feature { layer_ids, range?, feature_tag, to_state, trigger }`

## Source articles
- `use-opentype-features`
- `explore-text-properties`
