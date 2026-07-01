# Insert > Links — feasibility index

Button-by-button feasibility for the **Insert > Links** ribbon group, grounded in the
SuperDoc-fork engine (`src/renderer/core/superdoc-fork/`) and the `WC.PM` bridge
(`src/renderer/bridge/*.ts`). Each verdict reflects what the fork **actually** supports
(node types + super-converter handlers), not what the ribbon merely shows.

| Button | Verdict | Size | Required structure (one line) |
|--------|---------|------|-------------------------------|
| [Link (Hyperlink)](link.md) | ✅ Buildable NO-FORK | M | `link` mark + `w/hyperlink` translator already round-trip; dialog/bridge only needs to forward ScreenTip (`tooltip`) + internal `anchor` |
| [Bookmark](bookmark.md) | ✅ Already works | S | `bookmarkStart`/`bookmarkEnd` nodes + `w/bookmark-start`+`w/bookmark-end` translators already paired & round-trip; only optional Sort/Hidden dialog polish |
| [Cross-reference](cross-reference.md) | 🟡 Buildable with additive fork edits | M | `crossReference`+`pageReference` nodes & `sd/crossReference`+`sd/pageReference` translators exist; additive `crossref-wrappers.ts` branch to emit PAGEREF/NOTEREF + fix BUG-013 `\p`, plus a wider dialog |

## Key findings
- **No new subsystems and no external runtimes are needed for any Links button.** All three OOXML constructs (`w:hyperlink`, `w:bookmarkStart`/`End`, the REF/PAGEREF/NOTEREF field) have both a PM node/mark and a working super-converter import+export handler.
- **Link** and **Bookmark** are engine-complete; their gaps are dialog/UX (four-rail link dialog, ScreenTip, Place-in-This-Document picker, bookmark Sort/Hidden filters).
- **Cross-reference** is the only one needing a fork touch — and it's purely **additive**: the PAGEREF/NOTEREF nodes and translators already exist; the plan-engine wrapper just hard-creates a `crossReference` node for every display mode and mis-emits `\p` for page numbers (**BUG-013**, `crossref-wrappers.ts:229`).

## Decision
All three buttons: **TBD — to be decided together.**
