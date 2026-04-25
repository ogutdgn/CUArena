# Rename page

- **Category:** pages
- **One-line summary:** Change the name of a page.

## Triggers
- Left-panel Pages selector: double-click a page row → inline edit input.
- Right-click a page row → Rename.

## Preconditions
- Target is an existing page.
- File is in edit-access mode.

## Inputs
- Typed new name.

## Behavior
1. Double-click: row label becomes editable input with current name pre-selected.
2. Type new name.
3. Enter commits; Esc cancels.

## Outputs
- **File-level changes:** page's `name` updated.
- **Selection changes:** none.

## UI feedback
- Left panel: row label updates.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/left-navigation.md` → pages-selector

## Semantic event(s) candidate
- `rename_page { page_id, from_name, to_name, trigger: "double_click" | "context_menu" }`

## Source articles
- `view-layers-and-pages-in-the-left-sidebar`

## Notes / gaps
- Empty-name behavior: real Figma likely keeps the old name or uses a placeholder. Pick a sensible default (disallow empty; revert on empty commit).
