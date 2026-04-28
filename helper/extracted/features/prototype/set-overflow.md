# Set prototype overflow / scroll behavior

- **Category:** prototype
- **One-line summary:** Configure how a frame's content overflows in the running prototype — Vertical / Horizontal / Both / None.

## Triggers
- Frame selected → Prototype panel → **Overflow behavior** dropdown.

## Preconditions
- Frame selected; content extends beyond frame bounds.

## Inputs
- Dropdown: None / Horizontal / Vertical / Both.

## Behavior
1. At runtime, the frame becomes scrollable per the configured axes.
2. Combined with `preserve-scroll-position-in-prototypes` for cross-frame transitions.
3. Sticky / fixed scroll behaviors documented in `prototype-scroll-and-overflow-behavior`.

## Outputs
- **Scene graph changes:** frame's `overflow_behavior` updated.

## UI feedback
- Indicator on canvas (subtle).

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → prototype-section → overflow-dropdown

## Semantic event(s) candidate
- `set_prototype_overflow { frame_id, from, to, trigger }`

## Source articles
- `prototype-scroll-and-overflow-behavior`
- `preserve-scroll-position-in-prototypes`
