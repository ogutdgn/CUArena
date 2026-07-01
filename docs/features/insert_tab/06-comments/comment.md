# Comment — Insert > Comments

## What real Word does
The Insert tab's **Comments** group holds exactly one button, **Comment** — a re-surfacing of the Review tab's **New Comment** command (idMso `ReviewNewComment`, legacy `InsertAnnotation`); shortcut **Ctrl+Alt+M**. Behavior, shortcut and saved OOXML are identical regardless of which tab launches it.

Flows:
- **Comment on a selection** — select text (or place the caret), invoke Comment. Word wraps the target range and opens an empty modern-comment **card** (inline, *not* a Ribbon contextual tab) near the anchor (Contextual view) or in the **Comments pane** (List view), with author name/avatar and an editable box. Type, optionally **@mention** / tick **Assign to** (task), then **Post comment** / **Ctrl+Enter** to commit.
- **Comment at the insertion point** — with a collapsed caret, Word anchors to a single point (range start == end).
- **Reply / Resolve / Edit / Delete** — threads support Reply (Ctrl+Enter), Resolve (toggles `w15:done`), Edit (pencil), and Delete (card "…" → Delete thread; Review > Delete dropdown also offers Delete-All).

OOXML produced: in `document.xml` the range is delimited by `<w:commentRangeStart w:id="N"/>` … `<w:commentRangeEnd w:id="N"/>` plus a `<w:r><w:commentReference w:id="N"/></w:r>` mark; the body lives in `word/comments.xml` as `<w:comment w:id author initials date>` with `<w:p w14:paraId w14:textId>`. Modern companion parts: `word/commentsExtended.xml` (`<w15:commentEx w15:paraId w15:paraIdParent w15:done>` — thread/resolve), `word/commentsIds.xml` (`<w16cid:commentId w16cid:paraId w16cid:durableId>`), `word/commentsExtensible.xml` (`<w16cex:commentExtensible w16cex:durableId w16cex:dateUtc>`), optional `word/people.xml`. Relationships + `[Content_Types].xml` register each part.

## Current clone state
**working** — full end-to-end chain verified. `H.comment` re-dispatches to `newComment` (`src/renderer/public/js/commands.js:429`) → `WC.CommentsUI.compose()` (`src/renderer/bridge/comments-ui.ts:153`) opens the in-margin composer card; `composerPost()` (`comments-ui.ts:165`) calls `pm.cmd('addComment', text)` → `addComment` (`src/renderer/bridge/review.ts:296`) → `editor.doc.comments.create({ text, target })` (`review.ts:302`), a real Document API write that mutates the doc and exports to `word/comments.xml`. Installed at boot via `installCommentsUI(editor)` (`src/renderer/bridge/index.ts:701`). Docs (`docs/INSERT_TAB.md:42`) mark it ✅ — accurate.

## Can we build it in our engine?
**Verdict:** ✅ Already works
**Why:** Every layer the feature needs already exists in the fork. The PM side has a dedicated **comment extension** (`src/renderer/core/superdoc-fork/extensions/comment/` — `comment.js`, `comments-marks.js`, `comments-plugin.js`, helpers) plus a live **Document comments API** (`editor.doc.comments.create/patch`) the bridge already drives. The converter has both directions: **import** via `v2/importer/commentRangeImporter.js` + `documentCommentsImporter.js` and a **v3 range translator** at `core/super-converter/v3/handlers/w/commentRange/comment-range-translator.js`; **export** via `v2/exporter/commentsExporter.js`, which writes not only `comments.xml` but the full modern companion set — `updateCommentsExtendedXml` (`w15:commentEx` / `w15:paraId` / `w15:paraIdParent` / `w15:done`, `commentsExporter.js:186`) and `updateCommentsIdsAndExtensible` (`w16cid:commentId`/`durableId` + `w16cex:commentExtensible`/`dateUtc`, `commentsExporter.js:258`), conditionally emitting `word/commentsExtended.xml` / `commentsIds.xml` / `commentsExtensible.xml` (`commentsExporter.js:314-316`). The clone goes beyond the single Insert button: reply (`review.ts:308`), resolve (`review.ts:319`), and edit (`review.ts:331`) are all wired and survive export.

## Required structures to build it
- **PM node/extension:** reuse the existing `comment` extension (`superdoc-fork/extensions/comment/`) and its comments mark — no new node.
- **Converter handler (super-converter):** exists — import `commentRangeImporter.js` + `documentCommentsImporter.js` + v3 `commentRange/comment-range-translator.js`; export `v2/exporter/commentsExporter.js` (incl. extended/ids/extensible companion parts).
- **OOXML target:** `w:commentRangeStart` / `w:commentRangeEnd` / `w:commentReference` + `word/comments.xml`; companions `w15:commentEx` (commentsExtended), `w16cid:commentId` (commentsIds), `w16cex:commentExtensible` (commentsExtensible).
- **Bridge verb(s):** existing `WC.PM.addComment` / `replyComment` / `resolveComment` / `editComment` (`review.ts`) + the `WC.CommentsUI` composer (`comments-ui.ts`). None to add.
- **Fork edit?** none (NO-FORK) — already supported.
- **Rough size:** S (only optional polish) • **Dependencies:** none — self-contained on the comment extension + comments exporter.

## Open questions for our discussion
- **Entry-flow parity:** Word inserts an empty balloon and lets you type in place; the clone opens a margin composer card and refuses empty text / a caret not in/next to a word (`review.ts:297-298`). Match Word's empty-balloon flow, or keep the (arguably cleaner) composer-first flow?
- **Stale-code cleanup:** `commands.js:430-433` still claims `H.newComment` is "a guarded no-op until WC.CommentsUI lands" — stale since `CommentsUI` shipped. Worth the one-line comment fix (`task_55c214e5`)?
- **@mention / Assign-to:** modern Word supports `@mention` + task assignment (`people.xml`). Out of scope for a desktop clone, or a future enhancement?

## Decision
**TBD — to be decided together.**
