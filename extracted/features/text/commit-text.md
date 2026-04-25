# Commit text

- **Category:** text
- **One-line summary:** Exit text-edit mode; optionally discard empty text layers.

## Triggers
- `Esc` while in text-edit.
- Click outside the text layer on canvas.
- Select a different tool (e.g., press `V`).
- Select a different layer via Layers panel.

## Preconditions
- User is in text-edit mode.

## Inputs
- Just the trigger.

## Behavior
1. Exit text-edit mode; caret disappears.
2. Text layer's `content` is committed to the scene graph (if not already, depending on per-keystroke vs batch update engine choice).
3. **If content is empty:** the text layer is deleted (real Figma's default to avoid empty layers cluttering the file).
4. Selection = the text layer (unless it was deleted; then cleared).

## Outputs
- **Scene graph changes:** possibly deletes an empty text layer. Otherwise none beyond whatever was committed from editing.
- **Mode state change:** exits text-edit mode.

## UI feedback
- Canvas: caret disappears; layer shows as a static text block.
- Right panel: switches back to non-edit text view (Typography applies layer-wide).

## Side effects
- Undo stack: if an empty-layer deletion occurred, one entry. Otherwise the commit is part of the `edit-text` session's undo coalescing.

## Related UI schema entries
- `regions/right-properties.md` → typography-section

## Semantic event(s) candidate
- `commit_text { layer_id, content, was_empty, layer_deleted, trigger: "escape" | "click_outside" | "tool_switch" | "panel_select" }`

## Source articles
- `explore-text-properties`

## Notes / gaps
- Click-outside behavior: real Figma commits; some editors require explicit Enter. Figma's click-outside-to-commit is documented implicitly.
