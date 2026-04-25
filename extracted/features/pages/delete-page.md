# Delete page

- **Category:** pages
- **One-line summary:** Remove a page and all its content from the file.

## Triggers
- Right-click a page row → Delete.
- Keyboard: Delete while a page row is focused (behavior may differ; corpus doesn't fully confirm).

## Preconditions
- File has more than one page (cannot delete the last remaining page).
- Target page is not read-only / locked.

## Inputs
- Just the trigger.
- Optionally, a confirmation dialog — real Figma may prompt if the page has content. Per `plan/03`, confirmation can be omitted for simplicity.

## Behavior
1. Remove the target page and all its content from the file.
2. If the deleted page was the active page: switch active page to an adjacent one (previous if exists, else next).

## Outputs
- **File-level changes:** page removed.
- **Active page:** possibly changed.
- **Selection changes:** cleared.

## UI feedback
- Left panel: page row removed; if active, the adjacent page becomes highlighted.
- Canvas: content for the new active page loads.

## Side effects
- Undo stack: one entry; undo restores the page with all its content.

## Related UI schema entries
- `regions/left-navigation.md` → pages-selector

## Semantic event(s) candidate
- `delete_page { page_id, was_active, fallback_page_id, trigger: "context_menu" | "keyboard" }`

## Source articles
- `view-layers-and-pages-in-the-left-sidebar`

## Notes / gaps
- Confirmation dialog: real Figma may require confirmation. `plan/03` decides whether to render one.
- "Last page cannot be deleted" invariant: enforce in engine.
