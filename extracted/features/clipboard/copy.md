# Copy

- **Category:** clipboard
- **One-line summary:** Copy the current selection to the application clipboard.

## Triggers
- Keyboard: `Cmd C` (Mac) / `Ctrl C` (Windows).
- Right-click → Copy.
- Main menu → Edit → Copy (if rendered).

## Preconditions
- Selection is non-empty.
- Canvas has focus (not in a text input field — that would copy text instead).

## Inputs
- Just the trigger.

## Behavior
1. Serialize the current selection — every selected layer and its full subtree — into the app clipboard.
2. Also write a parallel representation to the system clipboard in Figma-HTML format (a special HTML payload Figma uses for cross-instance copy). This allows paste in another file / tab to retain fidelity.
3. No scene graph change.
4. Selection unchanged.

## Outputs
- **Scene graph changes:** none.
- **Clipboard state:** app clipboard now holds the serialized selection; system clipboard holds the HTML representation.

## UI feedback
- No visible change on canvas.
- A subtle toast may appear ("Copied" — `visual-only` for our mock; `plan/03` decides whether to emit it).

## Side effects
- Undo stack: no entry.
- Focus: unchanged.

## Related UI schema entries
- `regions/floating-overlays.md` → right-click-context-menu (Copy entry — functional)

## Semantic event(s) candidate
- `copy { layer_ids: [...], trigger: "shortcut" | "context_menu" | "main_menu" }`

## Source articles
- `copy-and-paste-objects`
- `copy-assets-between-design-tools`

## Notes / gaps
- Figma-HTML clipboard format: see `open-source-example/open-pencil/packages/core/src/editor/clipboard.ts` for reference on producing a Figma-compatible clipboard payload.
- "Copy as SVG / PNG / CSS / iOS / Android" entries are visual-only (plan/00 §3 — export-adjacent).
- Multi-type copy (copying an image layer copies pixel data? or just the layer reference?): real Figma copies the whole layer including embedded image blob. Same approach here.
