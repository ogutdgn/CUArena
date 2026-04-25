# Set constraints

- **Category:** properties
- **One-line summary:** Define how a child layer resizes relative to its parent frame when the parent is resized — horizontal + vertical constraints.

## Triggers
- Right-sidebar Position section: constraints icon next to X / Y inputs. Clicking opens a constraint-picker with two dropdowns (horizontal, vertical) + visual thumbnail.
- Keyboard shortcuts for specific constraint modes not explicitly listed in corpus.

## Preconditions
- Selection is a direct child of a frame (constraints apply only to children of frames, and only when the parent frame is not auto-layout).

## Inputs
- Horizontal constraint selection: Left / Right / Center / Left and right (stretch) / Scale.
- Vertical constraint selection: Top / Bottom / Center / Top and bottom / Scale.

## Behavior
1. Set child layer's `constraints.horizontal` and `constraints.vertical`.
2. Behavior applies when the parent frame is later resized — the child reflows per the constraint.

## Outputs
- **Scene graph changes:** selected layer's `constraints` updated.

## UI feedback
- Panel: constraint icon + thumbnail update to reflect new mode.
- Canvas: no immediate visual change until parent frame is resized.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → position-section (constraints icon)

## Semantic event(s) candidate
- `set_constraints { layer_ids, horizontal: "...", vertical: "...", trigger: "panel_picker" }`

## Source articles
- `apply-constraints-to-define-how-layers-resize`
- `combine-layout-guides-and-constraints`

## Notes / gaps
- Constraints only apply when the parent frame is resized by the user. Our mock rarely resizes parent frames during CUA tests, so the computed-reflow behavior is infrequent; still implement it for correctness.
- Scale mode (entire child scales including strokes) is essentially the Scale tool semantic applied during parent resize.
