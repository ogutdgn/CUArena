# Create page

- **Category:** pages
- **One-line summary:** Add a new blank page to the file.

## Triggers
- Left-panel Pages selector: `+` button at the header of the expanded pages list.
- Right-click on a page row → "New page" (reported in some docs).

## Preconditions
- File is in edit-access mode.

## Inputs
- Just the trigger.

## Behavior
1. Append a new page to the file's pages list.
2. Default name: "Page N" (N increments from existing count).
3. New page has its own empty canvas + its own viewport state.
4. Switch active page to the new one (see `switch-page.md`).

## Outputs
- **File-level changes:** new page appended.
- **Active page:** switched to the new page.
- **Selection changes:** cleared (new page is empty).

## UI feedback
- Left panel: new page row appears in pages list, highlighted as active.
- Canvas: empty page, background per page-level default.
- Right panel: no-selection view (Page section + Local styles + Export page).

## Side effects
- Undo stack: one entry (creating a page is typically undoable).

## Related UI schema entries
- `regions/left-navigation.md` → pages-selector

## Semantic event(s) candidate
- `create_page { page_id, page_name, trigger: "panel_plus_button" | "context_menu" }`

## Source articles
- `view-layers-and-pages-in-the-left-sidebar`

## Notes / gaps
- Whether create-page is undoable: real Figma treats page creation as undoable in many contexts; confirm behavior at build time.
