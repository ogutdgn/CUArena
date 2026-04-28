# Flatten to vector

- **Category:** vector
- **One-line summary:** Merge selected layers (or a container) into a single vector layer — destructive; cannot be re-separated except via undo.

## Triggers
- Selection non-empty + shortcut:
  - Mac: `⌥ ⇧ F`
  - Windows: `Alt Shift F`
- Right-click → **Flatten**.
- Right sidebar sub-header → Boolean ops dropdown → **Flatten** (the entry combines current selection's geometry into one vector).

## Preconditions
- One or more layers selected.

## Inputs
- Shortcut OR menu choice.

## Behavior
1. **Selection of vector layers:** merges them into one complex vector path.
2. **Selection of a text layer:** flattens text glyphs into a vector path (allows custom typeface adjustments for logos / wordmarks).
3. **Selection of a container** (frame/section/group): merges children's geometry into a single vector layer; the container is removed.
4. **Destructive** — the resulting vector cannot be re-separated except via undo or version history (per `flatten-layers`).
5. Resulting layer takes a single fill/stroke/effect (typically resolved from the previous topmost layer's properties — confirm in implementation).

## Outputs
- **Scene graph changes:** original layers replaced by one new vector layer.
- **Selection changes:** selection = the new vector layer.

## UI feedback
- Layers panel: original rows disappear; new vector row appears.
- Canvas: same visual result rendered as one vector.

## Side effects
- Undo stack: one entry. Subsequent edits cannot un-flatten without undo.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu → Flatten
- `regions/right-properties.md` → sub-header → boolean-ops dropdown → Flatten

## Semantic event(s) candidate
- `flatten_to_vector { layer_ids: [...], result_id, trigger: "shortcut" | "context_menu" | "menu" }`

## Source articles
- `flatten-layers`
- `boolean-operations`

## Notes / gaps
- Flatten differs from boolean ops: boolean creates a non-destructive group whose children remain editable; flatten destroys the children.
- Flattened text loses its typography settings — only the glyph outlines remain.
