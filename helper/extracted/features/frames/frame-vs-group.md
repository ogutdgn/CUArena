# Frame vs Group (concept doc)

- **Category:** frames
- **One-line summary:** Frames and Groups both contain children, but differ in sizing, support for advanced features (auto-layout, constraints, prototyping), and how clicks resolve.

## Triggers
- N/A — conceptual reference. Decisions about which to use happen through the discrete features `group-selection.md`, `create-frame.md`, `frame-from-selection.md`.

## Preconditions
- N/A.

## Inputs
- N/A.

## Behavior

### Group
- Created with `Cmd G` / `Ctrl G`.
- Bounds are computed dynamically as the union of child bounds.
- Single-click selects the entire group; double-click selects a child.
- Cannot host: layout guides, auto layout, constraints, prototyping (these are frame-only).
- Ungroup: `Cmd Shift G` / `Ctrl Shift G`, or `Cmd Backspace` / `Ctrl Backspace`.

### Frame
- Created with the Frame tool (`F` / `A`), preset, or `Frame selection` (`Opt Cmd G` / `Ctrl Alt G`).
- Bounds are explicitly set by the user (W/H independent of children).
- Can host: corner radius, clip content, layout guides, auto layout, constraints (on its children), prototyping connections, fill/stroke/effects.
- Click + double-click rules same as group (single-click selects frame, double-click enters).
- Ungroup: same shortcuts as group.

### When to use which
- Use a **frame** when you need an explicit container with its own size, fill, or that needs to host one of the frame-only features (auto-layout, prototyping, layout guides, constraints).
- Use a **group** for a quick visual grouping without those features.

## Outputs
- N/A.

## UI feedback
- Layers panel: frame icon (grid) vs group icon (rectangle of dots).
- Frames render with optional fill and clip-content; groups have no fill of their own.

## Side effects
- N/A.

## Related UI schema entries
- `regions/right-properties.md` → layout-section (different fields shown based on type)
- `regions/left-navigation.md` → layers-tree (different icons)

## Semantic event(s) candidate
- N/A.

## Source articles
- `the-difference-between-frames-and-groups`
- `frames-in-figma-design`
- `parent-child-and-sibling-relationships`

## Notes / gaps
- "Convert group to frame" — Figma supports this via right-click → "Frame selection" or via the right-panel sub-header dropdown; document under `frame-from-selection.md`.
