# Text Box — Insert > Text

## What real Word does
Insert > Text > **Text Box** is a split/gallery control. The dropdown shows a **Built-in gallery** of ~18 pre-formatted floating text-box building blocks (Simple Text Box, Austin Quote, Banded Sidebar, Ion, Retrospect, Whisp, ViewMaster, …), plus **Draw Text Box** (crosshair → click-drag an arbitrary-size empty box at that location), an optional **Draw Vertical Text Box**, a **More Text Boxes from Office.com** link, and **Save Selection to Text Box Gallery**. Selecting a built-in inserts a floating shape anchored to a paragraph with placeholder text you type over. Selecting a shape raises the **Shape Format (Drawing Tools)** contextual tab (Shape Fill/Outline/Effects, WordArt Styles, Text Direction, Create Link, Arrange, Size).

OOXML: a floating text box is `w:drawing > wp:anchor > a:graphic > a:graphicData(uri=…/wordprocessingShape) > wps:wsp` with `wps:txbx > w:txbxContent` holding the runs, wrapped in `mc:AlternateContent` (Choice `wps` / Fallback `w:pict > v:shape > v:textbox`). Gallery entries themselves persist as `w:docPart` (gallery `w:val='txtBox'`) in a glossary document.

## Current clone state
**shallow** — A real, editable text box inserts, but there is no gallery and no draw gesture. Menu (`commands.js:496-501`) shows only "Simple Text Box" + "Draw Text Box", **both** call `H.textBox()` → `WC.PM.xeTextBox('')` → `editor.commands.insertTextBox({text:'Text'})` (`bridge/insert-exotica.ts:178-179`; fork node `extensions/shape-textbox/shape-textbox.js:86`). The node exports real VML `<w:pict><v:shape type="#_x0000_t202"><v:textbox><w:txbxContent>` (`core/super-converter/v3/handlers/w/pict/helpers/translate-shape-textbox.js`), so it round-trips and is editable in-app. Missing: the ~18-item gallery, real Draw Text Box (rubber-band), vertical text box, Save-to-Gallery, and the Shape Format contextual tab.

## Can we build it in our engine?
**Verdict:** 🟡 Buildable with additive fork edits
**Why:** The core engine is already there — `shapeTextbox` is a real PM node with a working VML import (`handle-shape-textbox-import.js`) AND export (`translate-shape-textbox.js`), and `insertTextBox` is a live fork command. So the **insert** path needs no fork edit; a styled built-in gallery and a rubber-band Draw gesture are pure UI/bridge work. The additive-fork part is only for higher fidelity: (a) the inserted box is **inline/anchored-at-caret VML**, not a `wp:anchor` floating `wps:wsp` with arbitrary x/y from a draw rectangle — true floating placement + per-box position needs the anchor encoder (`v3/handlers/wp/anchor/`) wired to the textbox; (b) the **Shape Format contextual tab** is absent — `state-sync.ts:282-285` only matches `selection.node.type.name === 'image'`, so a `shapeTextbox`/`vectorShape` NodeSelection surfaces no tab. Building-block galleries persist as `w:docPart` in a glossary part the fork does not author, so "Save Selection to Text Box Gallery" is a separate (XL) subsystem; the built-in gallery can be faked client-side with prebuilt shapes (NO-FORK).

## Required structures to build it
- **PM node/extension:** reuse `shapeTextbox` (+ `shapeContainer`, `vector-shape` for warp). For floating placement, reuse the anchor attrs the image node already carries.
- **Converter handler (super-converter):** exists — import `v3/handlers/w/pict/helpers/handle-shape-textbox-import.js`, export `translate-shape-textbox.js`. Additive: route textbox export through `v3/handlers/wp/anchor/` for a true floating `wp:anchor` (currently VML-only / caret-anchored).
- **OOXML target:** `w:pict/v:shape/v:textbox/w:txbxContent` (today) → optionally `w:drawing/wp:anchor/a:graphicData(wordprocessingShape)/wps:wsp/wps:txbx` (true Word default).
- **Bridge verb(s):** keep `WC.PM.xeTextBox`; add `xeTextBoxStyled(presetId)` for gallery presets and `xeDrawTextBox({x,y,w,h})` for the draw rectangle; add a Shape-Format-tab path in `state-sync.ts`.
- **Fork edit?** none for insert/gallery/draw-into-caret; **additive** for floating-anchor export + contextual-tab detection.
- **Rough size:** M (gallery + draw + tab) • **Dependencies:** rides the existing `shapeTextbox`/`shapeContainer` engine; floating placement shares the image anchor encoder.

## Open questions for our discussion
- Gallery scope: ship a small **curated set** of CSS-faithful built-ins (like the WordArt 6-cell approach) or attempt all ~18? Quotes vs sidebars vs simple?
- Is **Draw Text Box** (rubber-band placement) worth the floating-anchor export work now, or keep caret-inserted boxes for v1?
- Do we want the **Shape Format contextual tab** in this slice (it unblocks fill/outline/arrange for text boxes AND WordArt at once), or defer it to a dedicated "shape tools" feature?
- **Save Selection to Text Box Gallery** needs a glossary `w:docPart` subsystem — keep out of scope / remove from ribbon?

## Decision
**TBD — to be decided together.**
