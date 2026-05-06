# Insert link in text

- **Category:** text
- **One-line summary:** Attach a URL to a selected text range so it renders as a link.

## Triggers
- In edit mode with a range selected → click **Create link** in Properties panel.
- Keyboard shortcut: `Cmd/Ctrl Shift U`.
- Paste a URL from clipboard while a range is selected (`Cmd/Ctrl V`) → URL becomes a link on the selected range.
- Paste twice: first paste inserts URL as text, second turns it into a link.

## Preconditions
- In text-edit mode on a text layer.
- A character range is selected (links can target the whole layer or a subrange).

## Inputs
- Trigger as above; then a small input box appears above the range. Type or paste URL → press Enter.
- Modifier: `Cmd/Ctrl Shift V` pastes URL as plain text (no link).

## Behavior
1. Input modal appears anchored above selection.
2. On Enter: range gains a `link` attribute pointing to the URL.
3. Linked text is auto-styled with underline by default. Underline can be toggled off (Cmd/Ctrl U) without removing the link.

## Outputs
- **Scene graph changes:** range run gains `link: { href: "..." }`. Default underline applied (`textDecoration.underline = true`).
- **Selection changes:** none.

## UI feedback
- Linked text shows underline.
- Properties panel shows link state.
- Hovering the link in non-edit mode shows preview / opens in new tab on click.

## Side effects
- Undo stack: one entry per insertion.
- Link styles are inherited like any other text style — link follows text style of the range.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → link-button
- `regions/canvas-overlays.md` → link-input-popover

## Semantic event(s) candidate
- `insert_link { layer_id, range, href, trigger: "button" | "shortcut" | "paste" }`

## Source articles
- `add-links-to-text`

## Notes / gaps
- mailto: links not supported per corpus.
- Image / vector links not supported (only via prototype hotspots, out of scope).
- Cmd/Ctrl click to follow link is documented; non-edit-mode click also follows.
