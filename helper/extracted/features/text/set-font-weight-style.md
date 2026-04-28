# Set font weight / style

- **Category:** text
- **One-line summary:** Pick a weight (Thin/Light/Regular/Medium/Bold/...) and italic / non-italic from the secondary typography dropdown.

## Triggers
- Right sidebar **Typography** section → click weight/style dropdown.

## Preconditions
- Text selected.
- Selected font supports multiple weights/styles (else dropdown shows only the available variants).

## Inputs
- Click → choose weight/style.

## Behavior
1. Dropdown lists the variants the font family exposes.
2. Selecting a variant applies it.
3. Multi-text-layer selection: applies to all selected.

## Outputs
- **Scene graph changes:** text run(s) `font_weight` and `font_style` updated.
- **Selection changes:** none.

## UI feedback
- Canvas redraws with new weight/style.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → weight-dropdown

## Semantic event(s) candidate
- `set_font_weight { layer_ids, range?, from_weight, to_weight, trigger }`
- `set_font_style { layer_ids, range?, from_style, to_style, trigger }`  // italic vs not

## Source articles
- `explore-text-properties`
- `browse-and-apply-fonts`
