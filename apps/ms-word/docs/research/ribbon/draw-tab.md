# Draw tab — Word ↔ LibreOffice

> **Status.** Word build: Microsoft 365 (target). **Word-side: web-sourced + LO-verified —
> screenshot-pending.** LO-side: high. Produced by the per-tab pipeline: 3 independent extractors →
> reconciled canonical → mapped to LO `.uno:` → verified against the LibreOffice source tree. The
> Word/idMso side was cross-checked against the official `wordcontrols.xlsx` (M365 Current Channel),
> against which the **core tab `TabDrawInk` is a 100% exact-match** (all 13 groups + 34 distinct
> idMso controls, correct types and parent nesting, zero invented idMsos). The LO command facts were
> checked against the vendored LO tree. **No owner screenshot exists for this tab yet** — and the
> Draw tab is itself **hidden by default in Word** (M365 / Office 2019+; enable via File > Options >
> Customize Ribbon > check Draw) and **stylus/touch-gated**, so the controls below are *web-sourced,
> unverified against a live build*. **No mapping carried a material LO-source correction** — every
> mapped LO command name and label is confirmed verbatim against the LO source, and the central
> thesis (LibreOffice has no ink/handwriting subsystem) is confirmed at three independent levels
> (see [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
Draw-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 57 catalogued Word Draw-tab controls, **none wire straight through** (Free = 0) and **none are
cut as cloud/AI/region product-choices** (Cut = 0). The largest band — 35 — is a genuine **Engine
gap**: every pen, pencil, highlighter, eraser, finger/touch-ink toggle, ink-to-shape, ink-to-math,
ink editor (Action Pen), ink replay, stop-inking and the notebook rule-lines feature, because
**LibreOffice has no digital-ink / handwriting / stylus engine at all** — zero `.uno:Ink*`
commands, zero touch/finger/stylus/pen commands, zero `SID_INK` slots. A thin **Behavior-shim**
band (9) exists where LO has an adjacent capability via UNO/dialog but no 1:1 ink control:
`.uno:SelectObject` (the three Select/Lasso rows), the window-chrome `.uno:Ruler`, page-background
formatting (`.uno:BackgroundDialog` / `.uno:BackgroundColor` + its More-Colors / Fill-Effects
sub-actions), and the ink Drawing Canvas (approximable via LO's draw layer). The remaining 13 are
the **ribbon group containers** — pure UI hosts (Our-layer UI).

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 0 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 13 | build the Word-faithful host; here, the ribbon group containers |
| **Behavior shim** | 9 | intercept/massage in our dispatch layer; LO's nearest capability differs |
| **Engine gap** | 35 | LO engine genuinely can't (no ink/handwriting); cut or accept reduced fidelity |
| **Cut** | 0 | out of scope by product choice (cloud/AI/M365, store add-ins, niche) |
| **Optional our-layer feature** | 0 | LO lacks it but it's app-state we could build |
| **Total** | **57** | |

**Decisive learning:** the Draw tab posts the **highest Engine gap of any tab so far — Engine
gap = 35 / 57 (~61%)** — and that gap is **genuine**: LO has no pen/ink/handwriting engine
whatsoever (confirmed three ways — no `.uno:Ink*`, no touch/finger/stylus/pen commands, no
`SID_INK` slots), so pens, erasers, finger-painting, ink-to-shape, ink-to-math, ink editor, ink
replay and stop-inking are all true capability gaps, not mere UI gaps. **Crucially, this high
engine-gap count does NOT threaten the core thesis**, because the **entire Draw tab is a
wholesale-cut candidate** under scoped parity: it is **optional, non-core, hidden by default even
in Word, and stylus/touch-only**. A CUA agent driving Writer with a keyboard and mouse never needs
it. So unlike Home or Insert (where engine gaps would force fidelity trade-offs in the core editing
surface), the Draw-tab engine gap is **safely out of scope by construction** — cut the tab,
accept zero ink parity, and the local-LO-via-LOK + scoped-parity decision is untouched. → still
supports **LO-via-LOK + scoped parity**, with the whole Draw/ink surface explicitly out of scope.

> **Recurring theme: the false friends.** LO ships several controls whose *names* collide with
> Word's ink controls but solve unrelated problems — and they are the trap to avoid when mapping.
> LO has a tab literally named **"Draw"** (in `notebookbar_cua.ui`), but it is a **vector-shape**
> tab (Text Box, Fontwork, Basic/Arrow/Star/Callout/Flowchart shapes, `.uno:InsertDraw`), not pen
> inking. `.uno:SelectObject` ("Select") is a draw-object selection cursor, not an ink-stroke
> selector. `.uno:Ruler` ("Rulers") toggles the window-chrome margin ruler, not a rotatable
> on-canvas straightedge. `.uno:BackColor` / `.uno:CharacterBackgroundPattern` highlight typed
> **text**, not ink. `.uno:Freeline_Unfilled` ("Freeform Line") draws a vector curve, not a
> pressure pen. None of these is a faithful ink analog — they are why the Behavior-shim band exists
> and why the rest is a clean Engine gap.

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none).
`work` is the bucket from the table above. Rows touched by the LO-source verification are marked
**✓ verified vs LO source** in the note.

### (tab root)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Draw (tab) | TabDrawInk | tab | — | LO-missing | Engine gap | The Draw ribbon tab itself, a permanent top-level Core Tab (Tab Set = 'None (Core Tab)'), not a contextual tab. All groups and controls below are its children. The tab is hidden by default and requires a Microsoft 365 subscription / Office 2019+; enable via File > Options > Customize Ribbon > check Draw. — **LO:** LibreOffice Writer has NO ink/Draw ribbon tab and no digital-ink subsystem at all. The catalog has zero `.uno:Ink*` commands (every 'ink' match is link/hyperlink). False friend: `ribbon`/notebookbar DOES define a tab literally named 'Draw', but it is a vector-shape tab (Basic/Symbol/Arrow/Star/Callout/Flowchart shapes, Connectors, Curves/Polygons, Select, Group, Text Box, Fontwork) — NOT pen/stylus inking. Word's whole Draw tab is built around handwriting ink; LO's same-named tab solves the unrelated problem of inserting editable vector drawing objects. No M365-style 'enable via Customize Ribbon' gating in LO either. ✓ verified vs LO source. |

### Group containers (as enumerated in the official file)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Input Mode group | GroupInputMode | group | — | LO-missing | Our-layer UI | Ribbon group container holding the pointer/input mode toggles (InkSelect, FingerPaintingMode, DrawInkMode). — **LO:** No pointer-input-mode concept in LO Writer. There is no ink/finger/draw-mode toggle subsystem, so this container has nothing to hold. (LO's nearest pointer toggle, `.uno:SelectObject`, is a one-shot draw-mode selection cursor, not a persistent ink-vs-select mode set.) |
| Write / Tools group | GroupWrite | group | — | LO-missing | Our-layer UI | Ribbon group container; in the modern M365 Word Draw tab this is the visible 'Tools' group surfacing select, eraser and lasso. — **LO:** Container for ink select/eraser/lasso, none of which exist in LO. Ribbon group containers are not addressable `.uno` commands anyway. |
| Drawing Tools group | GroupDrawingTools | group | — | LO-missing | Our-layer UI | Ribbon group container holding the consolidated InkToolboxWithEraserAndLasso composite control. — **LO:** Holds the InkToolboxWithEraserAndLasso composite; LO has no ink toolbox. (LO's 'Draw Functions' toolbox, `.uno:InsertDraw`, is a vector-shape toolbar, not an ink toolbox.) |
| Pens / OneNote pens group | GroupPensOneNote | group | — | LO-missing | Our-layer UI | Ribbon group container holding the OneNote-style InkToolbox composite control. — **LO:** OneNote-style ink pen toolbox container; LO has no pen instruments whatsoever. |
| Pens group | GroupPens2 | group | — | LO-missing | Our-layer UI | Ribbon group container for the pen gallery + ink color + thickness controls (PensGallery2, InkColorPicker2, LineThickness2). This is the 'Pens' group in modern Word. — **LO:** Container for the pen gallery + ink color + ink thickness; LO has none of these ink controls. LO does have generic shape line-width/line-color, but those format selected vector shapes, not an active pen. |
| Draw with Touch group | GroupDrawWithTouch | group | — | LO-missing | Our-layer UI | Ribbon group container holding the finger-painting (Draw with Touch) toggle. — **LO:** Touch/finger-painting toggle container; LO has no touch/finger/stylus inking commands (catalog search for touch/finger/stylus/pressure/tablet returns nothing ink-related). |
| Stencils group | GroupStencils | group | — | LO-missing | Our-layer UI | Ribbon group container holding the ruler/stencil toggle (ShowRulerStencil). — **LO:** Holds the on-canvas ruler/stencil for ink straight-edges. LO's `.uno:Ruler` is a window-chrome margin ruler, not a rotatable on-canvas drawing straightedge, so even the contained concept is absent. |
| Editing group | GroupEditingExcel | group | — | LO-missing | Our-layer UI | Ribbon group container (Excel-derived id) holding the page/background formatting dropdown surfaced on the Draw tab. — **LO:** Excel-derived container surfacing page/background formatting on the Draw tab. LO exposes page background/color via `.uno:BackgroundColor` and page-style dialogs, but on its Design tab (Page Background group), never on a Draw/ink context, and with no rule-lines feature. |
| Convert group | GroupInkConvertOneNote | group | — | LO-missing | Our-layer UI | Ribbon group container (OneNote-derived id) for ink conversion controls: Ink Editor split button, Diagramming (Ink to Shape), and ink-to-math conversion. This is the 'Convert' group in modern Word. — **LO:** Container for ink-to-shape / ink-to-math / ink editor. LO has a formula editor (Math) but no ink conversion, no ink-to-shape recognition, and no gesture ink editor, so the group has no analog. |
| Insert (Drawing Canvas) group | GroupInsertDrawingCanvas | group | — | LO-missing | Our-layer UI | Ribbon group container holding the Insert (Ink) Drawing Canvas button. — **LO:** Container for the ink Drawing Canvas. LO Writer has no drawing-canvas frame object concept — shapes anchor directly to page/paragraph/char, not into a bounded canvas unit. |
| Replay group | InkReplay | group | — | LO-missing | Our-layer UI | Ribbon group container for ink replay. The group container itself carries idMso 'InkReplay'; the playback toggle inside it is a separate idMso 'Replay'. — **LO:** Container for stroke-replay animation. LO has no stroke history to animate; no replay command exists. |
| Close group | GroupInkClose | group | — | LO-missing | Our-layer UI | Ribbon group container holding the stop-inking button (shown in reading view / on some builds). — **LO:** Container for Stop Inking. LO has no ink mode to stop; Esc simply deselects. |
| Help (Pen and Ink) group | GroupPenAndInkHelp | group | — | LO-missing | Our-layer UI | Ribbon group container holding the Pen and Ink help button. — **LO:** Pen-and-ink help container; no ink feature to document in LO. |

### Input Mode (GroupInputMode)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Select Objects / Ink Select | InkSelect | toggleButton | `.uno:SelectObject` | differs | Behavior shim | Switches the pointer into object/ink selection mode so you can click, move, and resize ink strokes, shapes, and text areas (useful for grabbing objects behind text); activating it deactivates the active pen. — **LO:** Closest LO analog is `.uno:SelectObject` (label 'Select', the arrow/pointer that selects drawing objects). It DIFFERS substantially: SelectObject selects vector shapes/frames/images, NOT ink strokes (LO has no ink strokes), it is not a persistent mode toggle paired with an active pen, and it has no 'grab objects behind text' lasso behavior. Closer match to Word's Lasso conceptually than to an ink-selection toggle. ✓ verified vs LO source. |
| Draw with Touch / Finger Painting Mode | FingerPaintingMode | toggleButton | — | LO-missing | Engine gap | Toggles finger/trackpad inking on/off; when on, finger gestures lay down ink with the active pen, when off they pan and select. Appears only on touch/trackpad-capable hardware. — **LO:** No finger/trackpad inking in LO. Catalog has no touch/finger/stylus/pressure command. ✓ verified vs LO source. |
| Draw / Ink Mode | DrawInkMode | toggleButton | — | LO-missing | Engine gap | Toggles drawing/ink input mode on the pointer. — **LO:** No ink-input pointer mode in LO. ✓ verified vs LO source. |

### Write / Tools (GroupWrite)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Select Objects / Ink Select | InkSelect | toggleButton | `.uno:SelectObject` | differs | Behavior shim | Selection-mode toggle surfaced in the Tools group; switches from inking to normal selection of ink, shapes, and text (useful for objects behind text). — **LO:** Same mapping/caveats as the GroupInputMode InkSelect: LO `.uno:SelectObject` selects vector objects only, is not an ink-vs-pen mode toggle, and does not select handwriting (none exists). ✓ verified vs LO source. |
| Draw with Touch / Finger Painting Mode | FingerPaintingMode | toggleButton | — | LO-missing | Engine gap | Touch/trackpad inking toggle surfaced in the Tools group. — **LO:** No touch/finger inking toggle in LO. ✓ verified vs LO source. |
| Draw / Ink Mode | DrawInkMode | toggleButton | — | LO-missing | Engine gap | Ink input-mode toggle surfaced in the Tools group. — **LO:** No ink-input mode toggle in LO. ✓ verified vs LO source. |
| Eraser (standalone) | InkEraser | toggleButton | — | LO-missing | Engine gap | Activates the ink eraser to remove ink. Shares the idMso InkEraser with the Stroke Eraser child of the InkEraserMenu split button. — **LO:** No ink eraser in LO. To remove a vector shape you select it and press Delete; there is no stroke/point eraser tool and no eraser command in the catalog. ✓ verified vs LO source. |
| Eraser (menu) | InkEraserMenu | splitButton | — | LO-missing | Engine gap | Split button: clicking the top half enters erase mode and dragging over ink removes it; the dropdown arrow exposes eraser-size/mode options. Word offers a Stroke Eraser (removes an entire stroke in one pass) and Point Erasers (erase only the portion the eraser passes over). — **LO:** No eraser split button or eraser-size options in LO. ✓ verified vs LO source. |
| Current Eraser | CurrentEraser | toggleButton | — | LO-missing | Engine gap | Child of the InkEraserMenu split button; selects/activates the last-used eraser. — **LO:** No eraser subsystem, so no last-used-eraser concept. ✓ verified vs LO source. |
| Stroke Eraser | InkEraser | toggleButton | — | LO-missing | Engine gap | Child of the InkEraserMenu split button; erases an entire ink stroke in a single pass. Carries the same idMso (InkEraser) as the standalone Eraser. — **LO:** No stroke eraser (there are no ink strokes in LO). ✓ verified vs LO source. |
| Small Point Eraser | PointEraserSmall | toggleButton | — | LO-missing | Engine gap | Child of the InkEraserMenu split button; small-radius pixel/point eraser for precise partial erasing. — **LO:** No point/pixel eraser of any size in LO. ✓ verified vs LO source. |
| Medium Point Eraser | PointEraserMedium | toggleButton | — | LO-missing | Engine gap | Child of the InkEraserMenu split button; medium-radius point eraser with a larger footprint than Small. — **LO:** No point eraser sizes in LO. ✓ verified vs LO source. |
| Lasso Select | LassoSelect | toggleButton | `.uno:SelectObject` | differs | Behavior shim | Activates free-form lasso selection: drag a loop around ink and everything fully enclosed becomes selected. Selects ink strokes/handwriting only — not standard typed text, shapes, or pictures. — **LO:** No free-form lasso in LO. The nearest behavior is `.uno:SelectObject`'s rubber-band marquee, but that is a rectangular drag-box over vector objects, not a free-form loop, and it selects shapes/frames rather than ink strokes. Functionally weaker and shape-only. ✓ verified vs LO source. |

### Drawing Tools (GroupDrawingTools)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Drawing Tools (combined toolbox) | InkToolboxWithEraserAndLasso | control | — | LO-missing | Engine gap | Composite/host-rendered inline control that surfaces the pen toolbox together with the eraser and lasso (Control Type 'control' in the official file — not a simple button). — **LO:** Composite host-rendered ink toolbox (pen+eraser+lasso). LO has no ink toolbox. The superficially similar `.uno:InsertDraw` ('Draw Functions') opens a vector-shape drawing toolbar, not an ink pen/eraser/lasso composite. ✓ verified vs LO source. |

### Pens / OneNote pens (GroupPensOneNote)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Pens (toolbox) | InkToolbox | control | — | LO-missing | Engine gap | Composite/inline pen toolbox control (OneNote-style), Control Type 'control' in the official file. — **LO:** OneNote-style composite ink pen toolbox; no LO equivalent (no pen instruments at all). |

### Pens (GroupPens2)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Pens (gallery) / Pen tiles | PensGallery2 | gallery | — | LO-missing | Engine gap | Gallery of available pens/highlighters/pencils (the pen picker). Each pen tile is a toggle that activates that pen for inking; re-clicking the selected pen opens its options flyout (Thickness, Color, Recent Colors, More Colors, Effects). Contains the 'Add Pen' favorite action. — **LO:** Pen/pencil/highlighter picker gallery; LO has no pen instruments and no pen gallery. |
| Pen (pen tile) | _(none)_ | toggleButton | — | LO-missing | Engine gap | A pen tile that activates that pen for inking; clicking an already-selected pen opens its options flyout. The flyout exposes five Thickness settings (0.25 mm to 3.5 mm), 16 solid colors plus More Colors, a Recent Colors row, and eight effect finishes (Rainbow, Galaxy, Lava, Ocean, Rose Gold, Gold, Silver, Bronze). — **LO:** No pen instrument. The closest freehand drawing in LO is `.uno:Freeline_Unfilled` ('Freeform Line'), but that draws a single editable VECTOR curve with the mouse — no pen pressure, no per-pen thickness/color flyout, no effect finishes, and it is a shape, not ink. Not a faithful pen. ✓ verified vs LO source. (Gallery-item row; idMso null in the official file — see QA flags.) |
| Pencil | _(none)_ | toggleButton | — | LO-missing | Engine gap | Activates a pencil-textured ink tool producing a softer, graphite-like stroke; re-clicking the selected pencil opens its options flyout for thickness/color. Compatible styluses also support tilt-based pencil shading. — **LO:** No pencil-textured ink tool; LO produces only flat vector strokes. No graphite/tilt-shading. (Gallery-item row; idMso null — see QA flags.) |
| Highlighter | _(none)_ | toggleButton | — | LO-missing | Engine gap | Activates a translucent highlighter for emphasizing sections; strokes are semi-transparent so underlying text/ink remains visible. Re-clicking the selected highlighter opens its options flyout (five thickness settings and multiple colors). — **LO:** No ink highlighter instrument. False friend: LO has `.uno:BackColor` 'Character Highlighting Color' / `.uno:CharacterBackgroundPattern` 'Highlight Color', but those highlight typed TEXT runs, not freehand ink strokes — a different feature. ✓ verified vs LO source. (Gallery-item row; idMso null — see QA flags.) |
| Add Pen / Add Pen (favorite) | PenAddFavorite | button | — | LO-missing | Engine gap | Child of PensGallery2. Adds a new customizable pen/pencil/highlighter preset to the gallery (favorites). The new tool appears as its own independently-customizable tile. — **LO:** No customizable pen presets/favorites in LO (no pens to favorite). |
| Color (ink color picker) | InkColorPicker2 | gallery | — | LO-missing | Engine gap | Ink color picker gallery for the selected pen: 16 solid colors plus a Recent Colors row and a 'More Colors...' launcher for a custom color. — **LO:** No active-pen ink color picker. LO has shape/line color pickers (`.uno:XLineColor` / `.uno:FillColor`) that recolor a SELECTED vector shape after the fact — not a pen color that arms the next stroke. Different model, so LO-missing for the ink-pen sense. ✓ verified vs LO source. |
| More Colors... (ink) | InkColorMoreColorsDialog | button | — | LO-missing | Engine gap | Child of InkColorPicker2; opens the More Colors dialog for choosing a custom ink color. — **LO:** No ink color picker, hence no ink More-Colors launcher. (LO's generic Custom Color dialog exists for shape fills but is not an ink control.) |
| Thickness (line thickness) | LineThickness2 | gallery | — | LO-missing | Engine gap | Gallery of pen/ink line thickness options (five settings ranging 0.25 mm to 3.5 mm); includes a line-styles dialog launcher. — **LO:** No active-pen thickness gallery. LO's `.uno:LineWidth` sets the line width of an already-selected vector shape, not the thickness of the next ink stroke — different workflow, so LO-missing for the pen sense. ✓ verified vs LO source. |
| Line Styles (dialog) | LineStylesDialog | button | — | LO-missing | Engine gap | Child of LineThickness2; opens the line styles dialog. — **LO:** No ink line-styles launcher. LO has a shape Line dialog (`.uno:FormatLine`) but it styles a selected vector object, not a pen. ✓ verified vs LO source. |
| Pen Effects | _(none)_ | gallery | — | LO-missing | Engine gap | Special ink textures/effect finishes for a pen: Rainbow, Galaxy, Lava, Ocean, Rose Gold, Gold, Silver, Bronze (eight effects). — **LO:** No special ink finishes (Rainbow/Galaxy/Lava/Ocean/metallics). LO vector shapes support gradient/pattern fills via dialogs, but there is no per-pen effect gallery and no ink to apply it to. (Inventory-only row; not a control in the official xlsx for GroupPens2 — see QA flags.) |

### Draw with Touch (GroupDrawWithTouch)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Draw with Touch / Finger Painting Mode | FingerPaintingMode | toggleButton | — | LO-missing | Engine gap | Touch/trackpad inking toggle surfaced in its own group variant; when on, finger/trackpad gestures lay down ink, when off they pan and select. — **LO:** No touch/trackpad inking in LO (duplicate of the same idMso elsewhere on Word's tab). ✓ verified vs LO source. |

### Stencils (GroupStencils)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Ruler | ShowRulerStencil | toggleButton | `.uno:Ruler` | differs | Behavior shim | Shows/hides an on-canvas ruler stencil so ink snaps to its edge to draw straight lines at any angle; rotate it via trackpad two-finger gesture, mouse scroll wheel, or Alt + arrow keys. Toggle off to hide. (Windows-only.) — **LO:** LO `.uno:Ruler` ('Rulers') exists but is fundamentally different: it shows/hides the document's horizontal margin/tab ruler in the window chrome (toggle, like View > Rulers). It is NOT a rotatable on-canvas straightedge that ink snaps to for drawing straight lines at arbitrary angles. Same word, unrelated feature. (`.uno:VRuler` is the vertical companion.) ✓ verified vs LO source. |

### Editing (GroupEditingExcel)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Format Background (dropdown) | FormatBackgroundDropdown | menu | `.uno:BackgroundDialog` | differs | Behavior shim | Dropdown menu grouping page/background formatting: rule lines, full-page rule lines, and page color (with More Colors and Fill Effects sub-actions). — **LO:** LO's nearest is the page background via `.uno:BackgroundDialog` / Page Style dialog (`.uno:PageDialog`), reached from Format > Page Style or the Design tab's Page Background group — never from a Draw/ink tab. It DIFFERS: it is a full page-style background (color/image/area) dialog, and it has no rule-lines submenu. Word groups this here only because the official file reuses an Excel-derived id. ✓ verified vs LO source. |
| Rule Lines (menu) | RuleLinesMenu | gallery | — | LO-missing | Engine gap | Child of FormatBackgroundDropdown; gallery of rule-line styles for the page. — **LO:** No rule-lines (notebook-line background) feature in LO Writer; this is a OneNote/Word inking-paper feature with no LO analog. |
| Rule Lines Full Page | RuleLineFullPage | toggleButton | — | LO-missing | Engine gap | Child of FormatBackgroundDropdown; toggles full-page rule lines. — **LO:** No full-page rule-lines toggle in LO. |
| Page Color (picker) | PageColorPicker | gallery | `.uno:BackgroundColor` | differs | Behavior shim | Child of FormatBackgroundDropdown; page background color picker with More Colors and Fill Effects sub-items. — **LO:** LO `.uno:BackgroundColor` ('Background Color') is wired in the CUA notebookbar to the Design tab's Page Background group as a color picker (argName BackgroundColor.Color) and sets the page background color. Concept overlaps but DIFFERS: it lives on Design (not a Draw/ink tab), and it is a single color picker without the Word picker's integrated More Colors + Fill Effects sub-actions in one dropdown (LO splits fill effects into separate Area/Page-Style dialogs). ✓ verified vs LO source. |
| More Colors... (page color) | PageColorMoreColorsDialog | button | — | LO-missing | Behavior shim | Child of PageColorPicker (under FormatBackgroundDropdown); opens the More Colors dialog for the page background. — **LO:** No dedicated page-color More-Colors launcher exposed as a command; LO reaches custom colors through the generic color-dropdown 'Custom Color' entry, not a discrete page-color dialog command. |
| Fill Effects... (page color) | PageColorFillEffects | button | — | LO-missing | Behavior shim | Child of PageColorPicker (under FormatBackgroundDropdown); opens the Fill Effects dialog for the page background. — **LO:** No page-color Fill Effects command. Gradient/pattern page backgrounds are set via the Page Style > Area dialog, not a discrete fill-effects command on a Draw tab. |

### Convert (GroupInkConvertOneNote)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Ink Editor / Action Pen (split button) | InkEditorSplitButton | splitButton | — | LO-missing | Engine gap | Split button enabling the ink-editing mode (now branded 'Action Pen') that lets pen gestures edit typed text instead of drawing ink: scratch/strike-through deletes, circling selects, a caret inserts space, a vertical line splits a word, a curve joins words, and a backwards-L moves text to a new line. Enable Track Changes first to keep an editable record. The dropdown holds enable toggle, mode toggle, and gesture help. — **LO:** No ink-gesture text editor (Action Pen) in LO — no scratch-to-delete, circle-to-select, caret-insert, etc. gesture recognition exists. ✓ verified vs LO source. |
| Ink Editor | InkEditor | toggleButton | — | LO-missing | Engine gap | Child of InkEditorSplitButton; toggles Ink Editor (Action Pen) mode on/off. — **LO:** No Ink Editor mode toggle in LO. |
| Enable Ink Editor | InkEditorEnable | toggleButton | — | LO-missing | Engine gap | Child of InkEditorSplitButton; enables/disables the Ink Editor feature. — **LO:** No Ink Editor feature to enable. |
| Ink Gesture Help | InkEditorInkGestureHelp | button | — | LO-missing | Engine gap | Child of InkEditorSplitButton; opens help describing the ink-editing gestures. — **LO:** No ink gestures, so no gesture help. |
| Ink to Shape / Diagramming | DiagrammingOnline | toggleButton | — | LO-missing | Engine gap | When enabled, freehand ink resembling a common geometric shape (rectangle, circle, triangle, arrow, etc.) is automatically snapped into a clean, editable Office shape as you draw. — **LO:** No ink-to-shape recognition in LO; freehand drawing yields a `.uno:Freeline` vector curve, never an auto-snapped clean rectangle/circle/arrow. No shape-recognition toggle exists. |
| Ink to Math | SelectionToMathConvert | button | `.uno:InsertObjectStarMath` | differs | Engine gap | Opens the Math Input Control dialog where you handwrite an equation with pen, finger, or mouse and see a live preview; clicking Insert converts the handwriting into a typed, editable math equation. — **LO:** No handwriting-to-math recognition in LO. The nearest is `.uno:InsertObjectStarMath` / `.uno:InsertMath` ('Formula Object...'), which embeds a LibreOffice Math OLE object you edit by TYPING markup (or via the elements panel). It DIFFERS sharply: no Math Input Control, no pen/finger handwriting, no live recognition — you type the formula, you don't ink it. (The handwriting/ink-recognition capability is a true engine gap; only the typed-Math fallback exists.) ✓ verified vs LO source. |

### Insert / Drawing Canvas (GroupInsertDrawingCanvas)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Drawing Canvas (Ink) | InsertInkDrawingCanvas | button | — | LO-missing | Behavior shim | Inserts a bounded drawing-canvas frame that groups ink and shapes as a single anchored, movable unit (with its own fill/outline and shape-insertion capabilities), so surrounding text reflows around it cleanly. — **LO:** LO Writer has no drawing-canvas frame object. Shapes are anchored directly (to page/paragraph/character/as-character); there is no bounded canvas unit that groups ink+shapes with its own fill/outline and reflow. (Catalog has no Insert*Canvas command; the shape-grouping intent is approximable via LO's draw layer / `.uno:InsertDraw`, but no 1:1 control.) |

### Replay (InkReplay)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Ink Replay | Replay | toggleButton | — | LO-missing | Engine gap | Animates the selected ink in the original order it was drawn, with pause/forward/rewind controls, so you can watch the strokes redraw. Used to demonstrate or review the sequence of handwritten annotations. — **LO:** No stroke-order capture and no replay/animation of drawing in LO Writer (the catalog `.uno:Repaint` 'Redraw' is just a screen-refresh, unrelated). No analog. ✓ verified vs LO source. |

### Close (GroupInkClose)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Stop Inking | InkStopInkingReadingView | button | — | LO-missing | Engine gap | Stops inking and exits ink/Drawing Tools mode (equivalent to pressing Esc); shown in reading view / on some builds. — **LO:** No ink mode to stop. In LO you simply press Esc / click away to deselect a drawing tool; there is no dedicated Stop-Inking command. |

### Help (GroupPenAndInkHelp)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Pen and Ink Help | PenAndInkHelp | button | — | LO-missing | Engine gap | Opens help for the pen and ink features. — **LO:** No pen-and-ink feature in LO, so no dedicated help entry (general `.uno:HelpIndex` exists but covers all help, not ink). ✓ verified vs LO source. |

---

## LO-source verification

These mappings were checked against the vendored LibreOffice tree at
`apps/ms-word/libreoffice-codebase/`. **No CORRECTED verdicts were warranted** — the LO-verify
pass found no factual errors in the loUno names, labels, slot mappings, or behavior claims (the
closest to a discrepancy is the cosmetic mnemonic '~' difference, e.g. mapping 'Rulers' vs source
'~Rulers', 'Background Color'/'Formula Object...' carrying the '~' mnemonic in source). The central
thesis — LibreOffice Writer has NO ink/handwriting subsystem — is confirmed at three independent
levels: (1) zero `.uno:Ink*` commands in officecfg (every 'ink' substring match is link/hyperlink);
(2) zero touch/finger/stylus/pressure/tablet/pen commands; (3) zero `SID_INK` slots in `svx/sdi` or
`sw/sdi`. The single **UNCERTAIN** item (the literal `ribbon.json` artifact) is noted but the
underlying command/slot facts it depends on are confirmed.

**Confirmed (CONFIRMED):**

- **Draw (tab) / overall ink thesis** — `loUno = null`, `LO-missing`, "no `.uno:Ink*`; every 'ink'
  match is link/hyperlink." A regex for `.uno:` commands containing 'ink' across all officecfg UI
  `.xcu` files returns ONLY link/hyperlink commands (EditLinks, PasteAsLink, ManageLinks,
  InsertHyperlink, EditHyperlink, RemoveHyperlink, LinkDialog, UpdateAllLinks, …) — zero
  ink/handwriting commands. No `SID_INK` / `SID_ATTR_INK` / `FN_INK` slots in `svx/sdi` or `sw/sdi`.
  The 'false friend' framing is exactly right. Evidence: `GenericCommands.xcu:3679,3821,3829,3840,3851`;
  `WriterCommands.xcu:379,723,1325,1834`; `CalcCommands.xcu:2511,2939`; empty grep for `.uno:Ink*`
  and `SID_INK`.
- **Draw (tab) — LO 'Draw' tab is a vector-shape tab, not ink.** The CUA notebookbar
  (`sw/uiconfig/swriter/ui/notebookbar_cua.ui`) defines a tab labelled '~Draw' (GtkLabel id=DrawLabel,
  style classes context-Draw / context-DrawLine). The actions there are vector/graphic commands:
  `.uno:DrawText` (Text Box), `.uno:FontworkGalleryFloater`, `.uno:BasicShapes(.rectangle/.ellipse)`,
  `.uno:InsertDraw`, plus shape-format commands (FormatLine, FillStyle, Extrusion*, group/align/wrap/
  bezier). No ink commands — a same-name false friend to Word's ink Draw tab. Evidence:
  `notebookbar_cua.ui:14067-14074` (DrawLabel '~Draw'); action-names at `5108` (`.uno:DrawText`),
  `5160/5584` (`.uno:FontworkGalleryFloater`), `5293/5303/5388` (`.uno:BasicShapes*`), `5652`
  (`.uno:InsertDraw`); `GenericCommands.xcu:4366` (`.uno:DrawText` label 'Text Box').
- **InkSelect / LassoSelect → `.uno:SelectObject`** (label 'Select', `differs`). Slot:
  `SfxBoolItem SelectObject SID_OBJECT_SELECT`. In Writer it activates a drawing-function
  (DrawSelection) and sets `m_nDrawSfxId`/`m_nFormSfxId` — the draw-mode object-selection cursor for
  vector shapes/frames/images; its 'toggled' state reflects the active draw function. Not an
  ink-stroke selector, not a persistent ink-vs-pen mode. Evidence: `GenericCommands.xcu:2970-2972`;
  `svx/sdi/svx.sdi:8956`; `sw/source/uibase/uiview/viewdraw.cxx:238-242`;
  `sw/source/uibase/uiview/viewstat.cxx:703-705`.
- **Drawing Tools (combined toolbox) / InsertDraw note.** `.uno:InsertDraw` has Label 'Draw
  Functions' (TooltipLabel 'Show Draw Functions'). Slot: `SfxBoolItem InsertDraw SID_INSERT_DRAW`.
  It toggles the vector drawing toolbar, not an ink pen/eraser/lasso composite. Evidence:
  `GenericCommands.xcu:4302-4308`; `svx/sdi/svx.sdi:2498`.
- **Pen (pen tile) — Freeline note.** `.uno:Freeline_Unfilled` has Label 'Freeform Line' (and
  `.uno:Freeline` = 'Freeform Line, Filled'). Vector-curve drawing commands, not pressure/ink pens.
  Evidence: `GenericCommands.xcu:5375-5378`; `:5367-5369`.
- **Highlighter — false-friend note.** `.uno:BackColor` Label = 'Character Highlighting Color';
  `.uno:CharacterBackgroundPattern` Label = 'Highlight Color'. Both highlight character/text runs,
  not freehand ink. Evidence: `WriterCommands.xcu:3133-3135`; `GenericCommands.xcu:1586-1588`.
- **Color (ink color picker) — false-friend note.** `.uno:XLineColor` Label = 'Line Color';
  `.uno:FillColor` Label = 'Fill Color'. Both apply to a selected object, not an armed pen color.
  Evidence: `GenericCommands.xcu:3647-3649`; `:3497-3499`.
- **Thickness — LineWidth note.** `.uno:LineWidth` Label = 'Line Thickness' — sets the line width of
  a selected shape. Evidence: `GenericCommands.xcu:3631-3634`.
- **Line Styles (dialog) — FormatLine note.** `.uno:FormatLine` exists with Label 'Line...'
  (mnemonic 'L~ine...') — the shape Line dialog. Evidence: `GenericCommands.xcu:3130-3133`.
- **Ruler → `.uno:Ruler`** (label '~Rulers', `differs`). Slot: `SfxBoolItem Ruler FN_RULER`, where
  `FN_RULER` is 'Horizontal ruler' — a boolean show/hide toggle of the window-chrome ruler, NOT a
  rotatable on-canvas straightedge. `.uno:VRuler` = 'Vertical Ruler'. The Writer view also has
  `SID_RULER_*` infrastructure slots confirming the document margin/tab ruler. (Minor: mapping cites
  'Rulers'; source string is '~Rulers'. A separate `.uno:RulerMenu` '~Rulers' menu wrapper exists,
  distinct from `.uno:Ruler`.) Evidence: `WriterCommands.xcu:3063-3065`; `:3152-3154`;
  `sw/sdi/swriter.sdi:5507`; `sw/inc/cmdid.h:160`; `sw/sdi/_viewsh.sdi:338-355,939`;
  `GenericCommands.xcu:4329`.
- **Format Background (dropdown) → `.uno:BackgroundDialog`** (+ `.uno:PageDialog`).
  `.uno:BackgroundDialog` Label = 'Background' (Writer); `.uno:PageDialog` Writer Label =
  '~Page Style...'. Both reached from Format menu / Design-tab Page Background, never from a
  Draw/ink context. Evidence: `WriterCommands.xcu:1566-1568`; `:1571-1573`.
- **Page Color (picker) → `.uno:BackgroundColor`** (label 'Background Color', argName
  BackgroundColor.Color). Slot: `SvxColorItem BackgroundColor SID_BACKGROUND_COLOR` with arg item
  named 'BackgroundColor' (UNO property `.Color`), so the argName is consistent with the slot. The
  'wired to the Design tab Page Background group' claim is corroborated by the CUA notebookbar
  (GtkMenuToolButton action-name `.uno:BackgroundColor`). Evidence: `GenericCommands.xcu:3797-3799`;
  `svx/sdi/svx.sdi:456-457`; `notebookbar_cua.ui:3839-3841`.
- **Ink to Math → `.uno:InsertObjectStarMath`** (label '~Formula Object...'; also `.uno:InsertMath`).
  These embed a LibreOffice Math OLE object; there is no handwriting/ink recognition command. Matches
  the `differs` verdict. Evidence: `WriterCommands.xcu:1111-1113`; `GenericCommands.xcu:3869-3871`;
  `CalcCommands.xcu:6-8`.
- **Ink Replay — Repaint note.** `.uno:Repaint` Label = 'Redraw' — a screen-refresh, unrelated to
  stroke-order replay. No replay/animation command exists. Evidence: `GenericCommands.xcu:6234-6236`.
- **Pen and Ink Help row.** `.uno:HelpIndex` Label = '%PRODUCTNAME ~Help' — general product help, not
  an ink-specific entry. Evidence: `GenericCommands.xcu:1782-1784`.
- **All touch/finger/stylus/pen/eraser/ink-editor/ink-canvas/replay/stop-inking rows (LO-missing).**
  A regex over all officecfg UI `.xcu` for `.uno:(Touch|Finger|Stylus|Pressure|Tablet|Pen)*` returns
  no real matches (only a 'Table'-prefixed false positive). Combined with the zero `.uno:Ink*` and
  zero `SID_INK` results, LO Writer has no touch/finger/stylus inking, no pen instruments, no eraser
  tool, no ink editor, no ink drawing-canvas, no stroke replay, and no stop-inking command. Every
  LO-missing verdict for these rows is upheld. Evidence: empty/false-positive grep for
  `.uno:(Touch|Finger|Stylus|Pressure|Tablet|Pen)*`; empty grep for `.uno:Ink*`; empty grep for
  `SID_INK` in `svx/sdi` + `sw/sdi`.
- **Default keyboard shortcuts (all rows).** `Accelerators.xcu` contains no accelerator entries for
  `.uno:SelectObject`, `.uno:Ruler`, `.uno:InsertDraw`, `.uno:Freeline*`, or any `.uno:Ink*` command.
  No default shortcuts exist for any control in this mapping. Evidence: `Accelerators.xcu` — empty
  grep for SelectObject, uno:Ruler, InsertDraw, Freeline, uno:Ink.

**Uncertain (UNCERTAIN) — not treated as authoritative:**

- **`ribbon.json` artifact referenced in the Page Color / BackgroundColor and 'Draw'-tab notes.**
  No file literally named `ribbon.json` exists anywhere under `apps/ms-word/` — the ribbon
  comparison is maintained as per-tab markdown (`apps/ms-word/docs/research/ribbon/{home,insert,
  references,mailings,review}-tab.md`), and this `draw-tab.md` is the previously-missing entry. The
  DOWNSTREAM facts those notes rely on are independently confirmed against the LO source (a 'Draw'
  tab exists in `notebookbar_cua.ui`; `.uno:BackgroundColor` is bound there; the argName `.Color` is
  consistent with the `SvxColorItem` slot). So the commands/behaviors are CONFIRMED; only the
  existence of an artifact literally named `ribbon.json` is UNCERTAIN. Evidence: Glob `**/ribbon.json`
  → no files; `apps/ms-word/docs/research/ribbon/` contains only README.md + the per-tab markdown files.

---

## Conditional / version-sensitive controls

There is **no owner screenshot for the Draw tab yet**, so the following are flagged
**expected-conditional, unverified against a live build** — a screenshot sweep would confirm
whether (and how) they surface. The Draw tab as a whole is itself conditional:

- **The entire Draw tab is hidden by default** in Word (M365 / Office 2019+) and must be enabled via
  File > Options > Customize Ribbon > check Draw. Without that, none of these controls appear.
- **Stylus/touch-gated controls** — several controls only render on touch/trackpad/pen-capable
  hardware: **Draw with Touch / Finger Painting Mode** (`FingerPaintingMode`; label varies by
  platform — 'Draw with Trackpad' on Mac, 'Draw with Touch' on Windows/touch), and pencil
  tilt-shading. On a mouse-only machine they are absent.
- **Ruler** (`ShowRulerStencil`) — Windows-only on the Word side.
- **Stop Inking** (`InkStopInkingReadingView`) — shown in reading view / on some builds only ('not
  all builds show it').
- **Layout-variant groups** — Word ships several group layouts for the same physical tab
  (GroupInputMode vs GroupWrite vs GroupDrawingTools; GroupPensOneNote vs GroupPens2;
  GroupDrawWithTouch). Which one renders is build-dependent, which is why some idMsos (InkSelect,
  FingerPaintingMode, DrawInkMode, InkEraser) appear in multiple groups in the official file. A live
  screenshot would confirm which variant the target build shows.
- **Ink Editor / Action Pen** (`InkEditorSplitButton`) — branding ('Ink Editor' vs 'Action Pen') and
  group placement (Convert vs Pens) vary across builds and sources; a screenshot would settle the
  current label and home.

---

## Out of scope

- **The entire Draw tab is a wholesale-cut candidate (the decisive scope call).** It is optional,
  non-core, hidden by default even in Word, and stylus/touch-only. A CUA agent driving Writer with
  keyboard and mouse never needs ink. Cutting the whole tab is the recommended scoped-parity stance,
  and it is *why* the ~61% engine gap below does not threaten the core thesis.
- **Engine gap — the ink/handwriting engine (35 controls, the true blockers).** Every pen, pencil,
  highlighter, eraser (stroke + point sizes), finger/touch-ink toggle, ink-mode toggle, the combined
  ink toolboxes, ink-to-shape recognition, ink-to-math handwriting, the Ink Editor (Action Pen)
  gesture engine, ink replay, stop-inking, and the OneNote rule-lines paper feature. LibreOffice has
  **no digital-ink subsystem at all** (no `.uno:Ink*`, no touch/finger/stylus/pen commands, no
  `SID_INK` slots). These cannot be shimmed — they would require a new ink engine. Cut, or accept
  zero fidelity.
- **Behavior shim — adjacent LO capability, no 1:1 ink control (9 controls).** `.uno:SelectObject`
  (the two InkSelect rows + Lasso Select — vector-object selection, not ink-stroke selection),
  `.uno:Ruler` (window-chrome margin ruler, not on-canvas straightedge), page-background formatting
  (`.uno:BackgroundDialog` / `.uno:BackgroundColor` + its More-Colors / Fill-Effects children), and
  the ink Drawing Canvas (shape-grouping approximable via LO's draw layer / `.uno:InsertDraw`). All
  live on non-Draw surfaces in LO and differ in behavior; only relevant if the Draw tab were kept.
- **No Cloud / AI / M365 cut items and no niche/region cut items on this tab.** Unlike Insert, the
  Draw tab has no Loop / Office.js / online-media / region-locked controls — its out-of-scope mass is
  the ink engine itself, not product-choice cloud features.

---

## QA flags & resolutions

From `result.qa`. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
(M365 Current Channel; 5638 control rows parsed). For the **core tab `TabDrawInk`, coverage is
verifiably 100% complete and correct** — exact set match on idMsos, groups, control types, and
parent nesting (empty diff both directions). The flags below are **scoping / completeness** notes,
not factual errors in the included rows. Because there is **no owner screenshot for this tab**,
several structural items remain **screenshot-pending**.

| QA flag | Status | Resolution |
|---|---|---|
| Are the included `TabDrawInk` rows correct? | **Resolved (source set-diff)** | Yes — all idMso names, groups, control types, and parent nesting match the official xlsx exactly; LO mappings hold per the LO-source pass. 'Correctness' of included rows is CONFIRMED; the only issue is whole-feature completeness. |
| Tab idMso `TabDrawInk` correct? | **Resolved (source)** | Correct (verified in xlsx). User-visible name is 'Draw'; internal idMso is TabDrawInk. No correction needed. |
| Second ink tab `TabInkToolsPens` (Tab Set TabSetInkTools) missing? | **Open (scoping gap)** | A real contextual ink tab in the same xlsx, wholly absent from this inventory. It carries the genuine named pen idMsos `InkBallpointPen` / `InkHighlighter` / `InkFeltTipPen` and groups GroupPensWrite/GroupPens/GroupInkSelect/GroupInkFormat/GroupInkPens. Out of scope here (this doc is `TabDrawInk`), but it is the biggest single completeness miss. Buckets unaffected (all would be Engine gap). |
| Named pen idMsos vs the gallery-tile null idMsos? | **Open (clarification)** | The 'Pen'/'Pencil'/'Highlighter' tiles in GroupPens2 legitimately have **idMso:null** (they are gallery items). But real pen idMsos (InkBallpointPen/InkFeltTipPen/InkHighlighter) DO exist — on the contextual `TabInkToolsPens` tab, not as TabDrawInk tiles. The blanket framing 'Word has no addressable pen commands' would be misleading; the null is correct only for the gallery tiles. |
| 'Pen Effects' (GroupPens2, idMso:null) a real ribbon control? | **Open (screenshot-pending)** | Does NOT correspond to any control in the official xlsx for GroupPens2 (which has only PensGallery2/PenAddFavorite/InkColorPicker2/InkColorMoreColorsDialog/LineThickness2/LineStylesDialog). Pen Effects (Rainbow/Galaxy/…) are pen-property finishes, not a ribbon control — likely a fabricated/mislabeled row. Flagged inventory-only in the row note; screenshot required. Bucket (Engine gap) unaffected. |
| 'Pen'/'Pencil'/'Highlighter' tile rows verifiable? | **Open (screenshot-pending)** | Gallery-item rows with no backing idMso; their existence/label/count cannot be confirmed from the command-id list. A screenshot of the expanded Pens gallery is the only confirmation. |
| Missing 'Ink to Text' concept? | **Open (screenshot-pending)** | The Convert group lists Ink-to-Shape and Ink-to-Math but no Ink-to-Text, yet `InkToTextAnalysis` exists in Word (context menus ContextMenuInk / ContextMenuObjectsGroup), plus InkCopyAsText and InkEditorGallery. A screenshot of the live Ink-to-Text affordance would clarify ribbon vs context-menu placement. Would be LO-missing → Engine gap. |
| `InkEquation` (dedicated handwriting-math idMso) cross-reference? | **Open (scoping)** | 'Ink to Math' was mapped only to `SelectionToMathConvert`; the dedicated `InkEquation` idMso (on TabInsert>GroupInsertSymbols and TabEquationToolsDesign) is the closer 'Math Input Control' analog and should at least be cross-referenced. Bucket (Engine gap) unaffected. |
| `InkSelect` vs `ObjectsSelect` → `.uno:SelectObject`? | **Open (screenshot-pending)** | Two different idMsos (InkSelect on TabDrawInk; ObjectsSelect on TabInkToolsPens + TabHome) both plausibly map to `.uno:SelectObject`; only InkSelect was considered. A screenshot showing both select tools in context would confirm the better LO analog. |
| Other off-tab ink controls (Review/Conflicts `GroupInk`, not-in-ribbon ink commands)? | **Open (scoping)** | `InkingStart` + `InkDeleteAll` on TabReviewWord>GroupInk and TabConflicts>GroupInk, plus QAT-addable InkDrawingAndWriting / InkToolsClose / InkDeleteAllInk, are outside this tab's scope. Round out Word's full ink command surface; lower priority. |
| `ribbon.json` artifact cited in LO notes? | **Resolved → UNCERTAIN (artifact only)** | No `ribbon.json` exists in the tree; the ribbon mapping is per-tab markdown and this `draw-tab.md` is the new entry. The underlying LO command/slot facts (Draw tab in notebookbar_cua.ui; `.uno:BackgroundColor` binding; `.Color` arg) are independently CONFIRMED — only the literal artifact is UNCERTAIN. |
| Overall completeness confidence | **HIGH (included scope) / MODERATE-LOW (whole feature)** | For the literal `TabDrawInk` tab, the inventory is essentially complete and exactly correct (parsed against the authoritative OfficeDev `wordcontrols.xlsx`). For 'Word's whole ink/Draw command surface', several real controls are missing (the `TabInkToolsPens` pen instruments and the Ink-to-Text concept being the biggest). LO-side: HIGH — every present-command fact confirmed at the slot level; the all-ink-absent thesis confirmed three ways. |
