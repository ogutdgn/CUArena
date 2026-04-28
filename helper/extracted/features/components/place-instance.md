# Place component instance

- **Category:** components
- **One-line summary:** Drop an instance of a component onto the canvas.

## Triggers
- Drag from **Assets** tab in left sidebar onto the canvas.
- Shortcut palette (`Cmd K` actions menu) → search for component → enter.
- Copy-paste an existing instance.

## Preconditions
- Component is available (in current file or via enabled libraries).

## Inputs
- Pointer drag-drop, OR command palette, OR clipboard paste.

## Behavior
1. Instance created at drop location.
2. Instance's `main_id` references the source component.
3. Updates to the main propagate to all instances (unless overridden).

## Outputs
- **Scene graph changes:** new instance node.
- **Selection changes:** selection = new instance.

## UI feedback
- Layers panel: instance with diamond icon.
- Right sidebar shows Instance section (with property controls).

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/left-navigation.md` → assets-tab
- `regions/right-properties.md` → component-section

## Semantic event(s) candidate
- `place_instance { source_component_id, new_instance_id, position, trigger: "asset_drag" | "actions_menu" | "paste" }`

## Source articles
- `create-and-insert-component-instances`
- `guide-to-components-in-figma`
