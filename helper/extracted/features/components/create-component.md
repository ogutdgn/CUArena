# Create component

- **Category:** components
- **One-line summary:** Convert a layer (or selection) into a reusable main component.

## Triggers
- Selection + shortcut: `⌥ ⌘ K` (Mac) / `Ctrl Alt K` (Win).
- Right sidebar sub-header → **Create component** icon.
- Right-click → **Create component**.

## Preconditions
- One or more layers selected.

## Inputs
- Shortcut OR menu choice.

## Behavior
1. Selected layers become a single main component (multi-select wraps in a frame first if not already a frame/group).
2. Component icon (rhombus) replaces the layer's standard icon in the Layers panel.
3. Component receives a default name; can be renamed.
4. Subsequent instances of this component reflect changes made to the main.

## Outputs
- **Scene graph changes:** layer type changes to `component` (or new component frame wraps selection).
- **Selection changes:** selection = the new component.

## UI feedback
- Layer icon swap; right sidebar shows Component section.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → component-section
- `regions/right-properties.md` → sub-header → create-component icon

## Semantic event(s) candidate
- `create_component { source_layer_ids, new_component_id, trigger }`

## Source articles
- `create-components-to-reuse-in-designs`
- `guide-to-components-in-figma`
