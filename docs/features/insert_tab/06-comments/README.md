# Insert > Comments — feasibility group index

The Insert tab's **Comments** group has a single control: **Comment**, a re-surfacing of the Review tab's New Comment command (idMso `ReviewNewComment`, Ctrl+Alt+M).

| Button | Verdict | Size | Required structure (one line) |
|--------|---------|------|-------------------------------|
| [Comment](comment.md) | ✅ Already works | S | Reuses the fork `comment` extension + `editor.doc.comments` API; import/export handlers (`commentRangeImporter`/`documentCommentsImporter` + v3 `comment-range-translator`; `commentsExporter` with extended/ids/extensible companion parts) all exist — NO-FORK. |
