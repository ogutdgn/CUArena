# Link (Hyperlink) — Insert > Links

## What real Word does
`Insert > Links > Link` is a split/dropdown button (Ctrl+K). The dropdown shows **Insert Link** (opens the dialog) and a **Recent Items** MRU of recently opened files/locations. The **Insert/Edit Hyperlink** dialog has a four-entry **"Link to:"** rail down the left:

- **Existing File or Web Page** (default) — `Address:` box + a `Look in:` file browser with side buttons (Current Folder / Browsed Pages / Recent Files), `Browse for File…`, `Browse the Web`, and a `Bookmark…` button to point at a bookmark/heading inside the target.
- **Place in This Document** — a tree of `Top of the Document`, `Headings` (every Heading 1–9 paragraph), and `Bookmarks`; produces an internal anchor.
- **Create New Document** — name + `Change…` path + an "edit now / edit later" radio pair.
- **E-mail Address** — `E-mail address:` (auto `mailto:` prefix) + `Subject:` + a recently-used list.

Shared across all four: a **Text to display:** box (greyed when an object like a picture is selected) and a **ScreenTip…** button (sub-dialog with a single "ScreenTip text:" box). In edit mode the dialog is titled **Edit Hyperlink** and shows a **Remove Link** button; right-click gives Edit/Open/Copy/Select/Remove Hyperlink.

**OOXML (oracle-verified, Word 16.0):** `<w:hyperlink>` wraps the run(s). External target → `r:id` into `word/_rels/document.xml.rels` with `Type=.../hyperlink TargetMode="External"`; internal target → `w:anchor="bookmarkname"` (no relationship). Optional `w:tooltip` (ScreenTip), `w:tgtFrame`, `w:history="1"`, `w:docLocation`. The linked run carries `<w:rStyle w:val="Hyperlink"/>`. Example: `<w:hyperlink r:id="rId4" w:tooltip="…" w:history="1"><w:r><w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr><w:t>Click me</w:t></w:r></w:hyperlink>`.

## Current clone state
**working (shallow vs Word)** — the primary action mutates the doc and round-trips. `H.link → WC.Dialogs.insertLink()` (`src/renderer/public/js/dialogs.js:45`) collects **Text to display** + **Address** only (lines 52–53), then calls `WC.PM.insertLink({href,text})` (`src/renderer/bridge/insert.ts:31`) → `editor.chain().setLink({href,text})`, a real fork mark command (`src/renderer/core/superdoc-fork/extensions/link/link.js:185`) that inserts/marks text, auto-adds underline, and allocates the docx relationship id. The split-button dropdown items "Insert Link…" / "Recent Items" (`ribbon-data.js:729–730`) are decorative — no handler, no MRU. The dialog has none of Word's four "Link to:" categories, no **ScreenTip**, no **Place in This Document** anchor picker, no mailto/new-document tabs.

## Can we build it in our engine?
**Verdict:** ✅ Buildable NO-FORK
**Why:** Both the PM mark and the converter handler already exist and already model nearly everything Word emits. The `link` mark (`extensions/link/link.js`) carries `href`, `anchor`, `docLocation`, `tooltip`, `target` (tgtFrame), `history`, and `rId` attributes; the export translator `core/super-converter/v3/handlers/w/hyperlink/hyperlink-translator.js` writes `w:hyperlink` with `r:id`/`w:anchor`/`w:tooltip`/`w:tgtFrame`/`w:history` and creates the external `Relationship` (`TargetMode=External`) — and the import path resolves both `r:id` and `#anchor`. Every gap (ScreenTip, internal anchor target, mailto/new-doc, Recent Items) is a **UI/bridge** gap, not a missing node or handler. The only wrinkle: `setLink` today only accepts `{href, text}` and does not pass `tooltip`/`anchor` through, so the bridge/command needs a thin pass-through (the mark already stores them).

## Required structures to build it
- **PM node/extension:** reuse `link` mark (`extensions/link/link.js`) — already has `tooltip`, `anchor`, `docLocation`, `target`, `history` attrs.
- **Converter handler (super-converter):** exists at `v3/handlers/w/hyperlink/hyperlink-translator.js` (export + import); writes `w:hyperlink`/`r:id`/`w:anchor`/`w:tooltip`/`w:tgtFrame`/`w:history` + the external `Relationship`.
- **OOXML target:** `w:hyperlink` (+ `word/_rels/document.xml.rels` Relationship for external; `w:anchor` for internal) + `w:rStyle w:val="Hyperlink"` on the run.
- **Bridge verb(s):** extend `WC.PM.insertLink` (`bridge/insert.ts:31`) to accept `{ href?, anchor?, text?, tooltip?, target? }` and pass them into a widened `setLink` (or a new `addMark` path) so ScreenTip + "Place in This Document" anchors reach the mark; `removeLink` already exists.
- **Fork edit?** none (NO-FORK) for the round-trip; widening `setLink`'s option object to forward `tooltip`/`anchor` is an additive edit *inside the fork extension* but is low-risk and purely additive (or it can be done bridge-side via `editor.chain().command(addMark…)` to stay strictly NO-FORK).
- **Rough size:** M (mostly the four-rail dialog + ScreenTip + anchor/heading picker; the engine work is small) • **Dependencies:** "Place in This Document" reuses the existing `listBookmarks()` and heading scan already written for Cross-reference; Recent Items needs a host-side MRU.

## Open questions for our discussion
- How faithful should the dialog be — full four-rail Word dialog, or just add **ScreenTip** + **Place in This Document** (the two highest-value, fully engine-backed gaps) and skip Create-New-Document / mailto / Recent Items?
- Do we want the **Recent Items** MRU at all? It needs main-process file-history state and has zero document-fidelity value.
- Should we forward `tooltip`/`anchor` by widening the fork's `setLink` (tiny additive fork edit) or keep it strictly NO-FORK via a bridge-side `addMark`?
- Wire up the dead split-button dropdown items now, or remove them from `ribbon-data` until the dialog grows?

## Decision
**TBD — to be decided together.**
