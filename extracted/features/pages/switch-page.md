# Switch page

- **Category:** pages
- **One-line summary:** Change the active page that the canvas displays.

## Triggers
- Left-panel Pages selector: click any page row in the expanded pages list.
- Keyboard (per some docs): `Page Up` / `Page Down` navigate between pages — not explicitly confirmed in corpus.

## Preconditions
- File has more than one page.
- Target page is different from the currently-active page.

## Inputs
- The click target OR keyboard direction.

## Behavior
1. Save current page's viewport state (zoom + x + y).
2. Load the target page's last-known viewport state (or default to Zoom-to-fit if it's the first visit).
3. Re-render canvas with target page's scene graph.
4. Clear selection (or restore target-page's last selection — engine decision).

## Outputs
- **File-level changes:** `activePageId` updated.
- **Canvas state:** scene + viewport reloaded for the target page.
- **Selection changes:** cleared OR restored per engine decision.

## UI feedback
- Left panel: target page row highlighted; previous page unhighlighted; layers tree reflects the new page's layers.
- Canvas: content swaps.
- Right panel: sections update per new selection state.

## Side effects
- Undo stack: **no entry** (page navigation is typically not undoable in Figma).
- Clipboard: untouched.

## Related UI schema entries
- `regions/left-navigation.md` → pages-selector

## Semantic event(s) candidate
- `switch_page { from_page_id, to_page_id, trigger: "pages_list_click" | "keyboard" }`

## Source articles
- `view-layers-and-pages-in-the-left-sidebar`

## Notes / gaps
- Whether the selection carries across pages or clears: real Figma clears on page switch. Follow that default.
