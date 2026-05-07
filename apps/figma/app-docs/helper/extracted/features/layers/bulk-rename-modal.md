# Bulk rename modal

- **Category:** layers
- **One-line summary:** Open the Rename Layers modal to rename multiple selected layers at once with patterns (current name, ascending/descending number, prefixes, regex).

## Triggers
- Multi-selection + shortcut:
  - Mac: `⌘ R`
  - Windows: `Ctrl R`
- Right-click on layers in the panel → **Rename**.

## Preconditions
- One or more layers selected.

## Inputs
The modal exposes:
- **Match** field (optional): substring or regex (`/regex/` mode) to identify which part of the layer's name to update.
- **Rename to** field: the replacement template; supports tokens.
- **Token buttons** that insert codes into the Rename-to field:
  - **Current name** — insert the layer's existing name.
  - **Number ↑** — insert an ascending counter; **Start ascending from** field appears.
  - **Number ↓** — insert a descending counter; **Stop descending at** field appears.
- **Preview** list on the left: shows the post-rename names live as the user types.
- **Rename** button to apply.

## Behavior
1. Modal opens centered above canvas (rendered in `regions/floating-overlays.md`).
2. Selected layers' names are listed in the preview.
3. Editing **Match** + **Rename to** updates the preview live.
4. Match field supports plain substring (default) or regex.
5. Replace field supports `$1`, `$2`, `$&`, `$\``, `$'`, `$n`, `$nnn`, `$NNN` tokens (regex backrefs + counters).
6. **Rename** applies; modal closes; all names commit in one undo step.

## Outputs
- **Scene graph changes:** every selected layer's `name` updated per the pattern.
- **Selection changes:** none.

## UI feedback
- Modal with two columns: preview + form.
- Live preview updates per keystroke.

## Side effects
- Undo stack: one entry covering the whole bulk rename.

## Related UI schema entries
- `regions/floating-overlays.md` → rename-modal

## Semantic event(s) candidate
- `bulk_rename_layers { layer_ids: [...], match_pattern, replace_template, options: { ascending_start?, descending_stop? }, applied_names: { id: new_name }, trigger: "modal" }`

## Source articles
- `rename-layers`
- `edit-objects-on-the-canvas-in-bulk`

## Notes / gaps
- Regex syntax is JavaScript regex (per article's link to MDN replace docs).
- Modal exact layout (button positions, label wording) per the article's screenshot.
