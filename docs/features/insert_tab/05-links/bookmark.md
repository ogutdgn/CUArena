# Bookmark — Insert > Links

## What real Word does
`Insert > Links > Bookmark` opens the **Bookmark** dialog (assignable command `InsertBookmark`, commonly Ctrl+Shift+F5; no default ribbon hotkey). A bookmark marks a named location/range so hyperlinks and cross-references can target it. Dialog fields:

- **Bookmark name:** edit box (naming rules: must begin with a letter; letters/numbers/underscores only; no spaces).
- A selectable **list** of existing bookmarks.
- **Add** (creates it at the selection/caret), **Delete** (removes it), **Go To** (jumps to it).
- **Sort by:** `Name` (alphabetical) / `Location` (document order) radio.
- **Hidden bookmarks** checkbox — reveals auto-generated underscore-prefixed bookmarks (`_Ref########`, `_Toc…`, `_GoBack`, `_Hlk…`).
- **Close**.

**OOXML (oracle-verified, Word 16.0):** a paired `<w:bookmarkStart w:id="0" w:name="MyBookmark"/> … <w:bookmarkEnd w:id="0"/>` bracketing the run(s); a zero-length (point) bookmark places start and end adjacent. IDs must match start↔end. Bookmark brackets `[ ]` display only when *File > Options > Advanced > Show bookmarks* is on (display-only, never printed, not in the markup).

## Current clone state
**working (functionally complete)** — `H.bookmark → WC.Insert.bookmarkDialog()` (`src/renderer/public/js/insert-features.js:246`) opens a full dialog: name field + list with **Go To** / **Delete**. **Add** → `WC.PM.insertBookmark({name})` (`src/renderer/bridge/insert.ts:102`) inserts a **paired** `bookmarkStart`+`bookmarkEnd` in one transaction (end-first so the start insert doesn't shift the end; ids allocated by `nextBookmarkId`). list/goTo/remove map to `listBookmarks` / `goToBookmark` / `removeBookmark` (`insert.ts:125/135/154`) — all real doc mutations/reads. Minor gaps vs Word: no **Sort by Name/Location** toggle, no **Hidden bookmarks** checkbox, and spaces in names are coerced to underscores (`insert.ts:106`). Round-trips as real OOXML bookmarks.

## Can we build it in our engine?
**Verdict:** ✅ Already works
**Why:** The node types and converters are fully present and round-trip. `bookmarkStart` (`extensions/bookmarks/bookmark-start.js`) and `bookmarkEnd` carry `name`/`id` (plus `colFirst`/`colLast`/`displacedByCustomXml`), and the import/export handlers exist at `v3/handlers/w/bookmark-start/bookmark-start-translator.js` and `v3/handlers/w/bookmark-end/bookmark-end-translator.js` (with `w-name`/`w-id` attribute handlers). The bridge already inserts a correctly **paired** start+end. The only remaining gaps (sort toggle, "Hidden bookmarks" filter) are pure dialog conveniences with no engine or converter dependency — "Hidden bookmarks" is just a filter on `listBookmarks()` for `_`-prefixed names; the sort is a list ordering. Nothing needs a new node or handler.

## Required structures to build it
- **PM node/extension:** reuse `bookmarkStart` + `bookmarkEnd` (`extensions/bookmarks/`) — name/id paired markers.
- **Converter handler (super-converter):** exists at `v3/handlers/w/bookmark-start/` and `v3/handlers/w/bookmark-end/` (import + export of `w:bookmarkStart`/`w:bookmarkEnd`).
- **OOXML target:** `w:bookmarkStart w:id w:name` + matching `w:bookmarkEnd w:id`.
- **Bridge verb(s):** already complete — `insertBookmark` / `listBookmarks` / `goToBookmark` / `removeBookmark` / `renameBookmark` (`bridge/insert.ts:102–164`). Optional: have `listBookmarks` flag `_`-prefixed names so the dialog can show/hide them; add a sort option to the dialog only.
- **Fork edit?** none (NO-FORK).
- **Rough size:** S (only the optional Sort-by + Hidden-bookmarks dialog polish remains) • **Dependencies:** none; the cross-reference and hyperlink "Place in This Document" pickers consume the same `listBookmarks()`.

## Open questions for our discussion
- Add the two missing dialog conveniences (**Sort by Name/Location**, **Hidden bookmarks** filter), or leave as-is given it already round-trips?
- Do we ever surface auto/hidden bookmarks (e.g. `_Ref########` minted by a faithful cross-reference)? If so, the "Hidden bookmarks" filter becomes more than cosmetic.
- Keep coercing spaces → underscores silently, or validate the name (letter-first, no spaces) and warn the user the way Word does?

## Decision
**TBD — to be decided together.**
