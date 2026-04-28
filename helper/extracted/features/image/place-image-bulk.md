# Place image / video (bulk)

- **Category:** image
- **One-line summary:** Bulk-import images/videos with shortcut `⇧⌘K` / `Shift+Ctrl+K` and place each on canvas (or onto existing layers).

## Triggers
- Toolbar **Image/video** entry under Shape tools.
- Shortcut: Mac `⇧ ⌘ K` / Win `Shift Ctrl K`.

## Preconditions
- Editor view active.

## Inputs
- File picker selects one or more images/videos.
- After selection, cursor displays a counter badge showing the number of remaining placements.

## Behavior
1. Cursor enters "place" mode.
2. **Click on canvas** — places image as a new rectangle layer with that image as fill, at original dimensions.
3. **Click on an existing layer** — replaces that layer's fill with the image.
4. **Place all** button — drops all assets at one location stacked.
5. **Delete** discards remaining unplaced assets.
6. Repeat until all assets placed or discarded.

## Outputs
- **Scene graph changes:** new layers OR existing layers' fills updated.
- **Selection changes:** typically last placed item.

## UI feedback
- Cursor with image preview + counter badge.

## Side effects
- Undo stack: one entry per placed item (or one bulk entry — implementer choice).

## Related UI schema entries
- `regions/canvas-overlays.md` → image-place-cursor

## Semantic event(s) candidate
- `place_image_bulk { asset_ids, placement_actions: [...], trigger: "shortcut" | "toolbar" }`

## Source articles
- `add-images-and-videos-to-designs`
