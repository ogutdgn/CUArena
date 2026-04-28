# Find & replace (cross-canvas text + layer names)

- **Category:** find-replace
- **One-line summary:** Search across the current page (or entire file) for matching text content or layer names and optionally replace.

## Triggers
- Shortcut:
  - Mac: `⌘ F`
  - Windows: `Ctrl F`
- Left sidebar Find/Replace icon (also opens the panel — takes over the panel contents per `view-layers-and-pages-in-the-left-sidebar`).

## Preconditions
- Editor view active.

## Inputs
- **Find** field — query string.
- **Replace** field — replacement string.
- Match scope: current page or entire file (file-scope toggle).
- Match-type sub-options (typically): match case, match whole word, regex.
- **Find next**, **Find previous**, **Replace**, **Replace all** buttons.

## Behavior
1. Opening Find/Replace replaces the left sidebar's current contents (Layers / Assets) with the Find UI.
2. Pressing `Esc` returns to the previous panel content.
3. Typing a query updates a result list (matching text layers + matching layer-name rows).
4. Result list is selectable; clicking an entry selects it on canvas + zooms to it.
5. Replace updates the matched substring in the targeted entity.

## Outputs
- **Scene graph changes:** matched text contents updated (Replace), or layer names updated. None for find-only.
- **Selection changes:** clicking a result selects that layer / text-range.

## UI feedback
- Panel takeover with find/replace form.
- Results list under the form.
- Canvas zoom moves to the selected result.

## Side effects
- Undo stack: one entry per replace operation (Replace = single match; Replace all = one entry covering all matches).

## Related UI schema entries
- `regions/left-navigation.md` → find-replace-takeover

## Semantic event(s) candidate
- `find_text { query, scope: "page" | "file", trigger: "shortcut" | "panel_icon" }`
- `replace_text { query, replacement, layer_ids: [...], scope, mode: "single" | "all", trigger: "panel_button" }`

## Source articles
- `find-and-replace-in-figma`
- `view-layers-and-pages-in-the-left-sidebar`

## Notes / gaps
- Whether matching layer names is integrated with text-content matching in one panel or two panels is per the article — they share the panel.
