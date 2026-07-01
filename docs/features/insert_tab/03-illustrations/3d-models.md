# 3D Models — Insert > Illustrations

## What real Word does
3D Models is a split/menu button: **This Device…** (file-open for `.fbx / .obj / .3mf / .ply
/ .stl / .glb / .gltf`) and **Stock 3D Models…** (an online 3D content picker with categories
and animated models). The inserted object shows an on-object 3D rotation control for free
360°/tilt manipulation and raises the **3D Model** contextual tab (Adjust → 3D Model Views
gallery / Pan & Zoom / Reset 3D Model; Accessibility; Arrange; Size). It is stored as a
DrawingML picture carrying a `model3d` extension: `w:drawing > wp:inline > a:graphic >
a:graphicData(.../picture)` with `a:extLst > am3d:model3D`, the 3D binary in `word/media`
(e.g. `.glb`), plus a generated 2D preview `pic:blipFill` PNG. Animated stock models add
scene/animation data and a Scenes gallery. KeyTips Alt, N, 3.

## Current clone state
**stub** — `H['3dModels']` (`src/renderer/public/js/commands.js:442`) is a single
`WC.toast("3D models require a 3D model viewer/runtime — not available in this clone.",
"See docs/NOT_IMPLEMENTED.md")`. The split-dropdown items "This Device"/"Stock 3D Models"
have no separate handler; the whole control just toasts. No bridge verb, no node, no
converter handler. `ribbon-data` marks `feasible: "no"`.

## Can we build it in our engine?
**Verdict:** ⛔ Needs an external runtime we don't have
**Why:** There is no `model3d` node, no `am3d:model3D` import/export handler anywhere in the
fork (grep finds zero hits), and — decisively — rendering and rotating a 3D mesh requires a
**WebGL/glTF runtime** (a model loader + 3D viewport) that the document core does not have and
that is wholly outside the ProseMirror/paged-render architecture. The paged
PresentationEditor paints 2D page sheets; it has no 3D viewport concept. A *degraded* path is
technically possible — accept a `.glb/.gltf`, render a static 2D preview PNG, and insert it as
a plain `image` (the existing `insertImage` path) — but that is "insert a screenshot of a 3D
model", not a real, rotatable 3D object, and it would NOT round-trip as `am3d:model3D` without
a new export handler. True fidelity is gated on a 3D runtime we deliberately don't ship.

## Required structures to build it
- **PM node/extension:** would need a NEW `model3d` node (atom/inline) under `extensions/` — does not exist.
- **Converter handler (super-converter):** would need a NEW import/export handler for `a:extLst/am3d:model3D` + the model binary part + preview PNG — does not exist.
- **OOXML target:** `w:drawing/wp:inline/a:graphic/a:graphicData(.../picture)` + `a:extLst/am3d:model3D` → `word/media/*.glb`.
- **Bridge verb(s):** a new `WC.PM.insert3DModel` (+ a WebGL viewport NodeView).
- **Fork edit?** non-additive + external runtime (a glTF/WebGL viewer subsystem).
- **Rough size:** XL • **Dependencies:** a 3D model loader + WebGL viewport (e.g. three.js / `<model-viewer>`) — an external runtime outside the document engine.

## Open questions for our discussion
- Keep the honest stub as-is (recommended given the runtime cost), or build the degraded "static-preview-as-image" path so the button at least inserts *something*?
- If we ever pursue it: is bundling a WebGL viewer (three.js / model-viewer) acceptable for a "faithful Word clone", or does it bloat the engine beyond the project's intent?
- Remove "3D Models" from the ribbon as honestly out-of-scope, or leave it visible with the documented stub?

## Decision
**TBD — to be decided together.**
