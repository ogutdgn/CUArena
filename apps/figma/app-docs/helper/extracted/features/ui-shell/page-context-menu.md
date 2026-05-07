# Page context menu

- **Category:** ui-shell
- **One-line summary:** Right-click a page row in the Pages selector to show page-level actions (rename, duplicate, delete, etc.).

## Triggers
- Right-click on a page row in the expanded Pages selector.

## Preconditions
- Pages selector expanded (click the current page name to expand).

## Inputs
- Right-click → choose action from context menu.

## Behavior
Context menu entries (per Figma convention; corpus does not enumerate the exhaustive list, but the following are documented across `pages` related articles):
- **Rename** — toggles inline edit on the page row name.
- **Duplicate page** — creates a copy with all its layers (functional).
- **Delete page** — confirms then removes the page (functional; cannot delete the only page).
- **Set as thumbnail** — sets this page's preview as the file thumbnail (visual-only — covered by `set-custom-thumbnails-for-files`).
- **Copy link to page** — copies a deep-link URL (visual-only).
- **Move page** — drag/order alternative.

## Outputs
- **Scene graph changes:** depends on action (rename, duplicate, delete).
- **Selection changes:** depends.

## UI feedback
- Context menu floats anchored to cursor.

## Side effects
- Undo stack: depends on action.

## Related UI schema entries
- `regions/floating-overlays.md` → page-context-menu
- `regions/left-navigation.md` → pages-selector

## Semantic event(s) candidate
- `open_page_context_menu { page_id, position }`
- Per-action events: `rename_page`, `duplicate_page`, `delete_page`, `unsupported_feature_clicked` for visual-only entries.

## Source articles
- `set-custom-thumbnails-for-files`
- Existing per-action specs: `pages/rename-page.md`, `pages/delete-page.md`, etc.

## Notes / gaps
- Duplicate-page is implied by the existence of "duplicate" in the Figma keyboard shortcut set; treat as functional. If gaps in current pages/ specs, add a `pages/duplicate-page.md`.
