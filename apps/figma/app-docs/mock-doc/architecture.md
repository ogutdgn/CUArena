# test-app architecture

Current state of the Figma mock application. Read this before touching engine or UI code.

---

## 1. Stack

| Concern | Choice |
|---|---|
| Framework | React 18 + TypeScript |
| Build | Vite 5 |
| Store | Zustand + Immer |
| Canvas | SVG (shapes, vectors, handles) + HTML overlays (text edit, panels) |
| Font | `@fontsource/inter` (bundled, 400–700) |
| Icons | `lucide-react` |

SVG over Canvas2D: pen tool, vector edit, text editing, hit-testing, and corner-radius are simpler at mock scale (<1k nodes).

---

## 2. State buckets

| Bucket | Lives in | Undo |
|---|---|---|
| **Scene graph** (Document → Pages → Layers) | `store.document` | yes |
| **Viewport** (pan + zoom, per-page) | `store.viewport` | no |
| **Selection** (per-page layer ids) | `store.selection` | snapshot restored on undo |
| **Mode** (activeTool, editMode, focusContextId, productMode) | `store.mode` | no |
| **Clipboard** | `store.clipboard` | no |
| **UI ephemeral** (hover, drag preview, toasts, dropdowns) | local component state | no |
| **Logger** (raw + semantic, append-only) | `logger/buffer.ts` | undo emits `undo` event; originals stay |

---

## 3. Op set — all scene-graph mutation goes through ops

UI never writes scene state directly. Every change is dispatched through `engine/dispatch.ts`.

| Op | Undoable | Purpose |
|---|---|---|
| `create_node` | yes | shape/frame/text/image/vector creation, paste, duplicate |
| `delete_nodes` | yes | delete, cut |
| `set_property` | yes | fills, strokes, effects, opacity, corner radius, visibility, flip, constraints, rename |
| `set_transform` | yes | move, resize, rotate |
| `scale_uniform` | yes | scale tool (K) — recursively scales children |
| `reparent` | yes | group/ungroup, frame nesting, cross-parent drag |
| `reorder_z` | yes | send to front/back |
| `mutate_text_runs` | yes | text typing (coalesced) |
| `mutate_vector_network` | yes | pen tool anchors, vector edits |
| `create_page` / `delete_page` | yes | page lifecycle |
| `set_selection` | no | selection changes |
| `set_focus_context` | no | enter/exit frame or group |
| `set_viewport` | no | pan, zoom |
| `set_tool` | no | tool activation |
| `set_edit_mode` | no | text-edit, vector-edit, pen-creation mode |
| `switch_page` | no | page switch |
| `set_clipboard` | no | copy, cut |

---

## 4. Transaction / undo model

One user gesture = one undo entry. Micro-mutations from a drag are coalesced.

```
open()   → snapshot selection + focusContext, buffer ops
commit() → apply buffered ops as one merged undo entry
abort()  → discard ops, revert any preview
```

Coalescing rules:
- **Drag** (move/resize/rotate/scale) — open on `pointerdown`, commit on `pointerup`
- **Color picker scrub** — open when picker opens, commit when it closes
- **Text typing** — 500ms inactivity or caret-jump commits
- **Pen path** — first anchor opens, close-path / Esc / Enter / tool-change commits

Undo stack: 1000 entries.

---

## 5. Implemented features

**Shapes & tools:**
- Rectangle, Ellipse, Polygon, Star, Line, Arrow, Text, Frame, Section, Group, Slice, Image, Vector
- Pen tool (anchor placement, Bezier handles, close path)
- Pencil tool (freehand stroke → vector)
- Scale tool (`K`) — proportional stroke/radius/font scaling, recursive children

**Frame system:**
- Double-click to enter frame scope
- Shapes created inside focused frame auto-nest
- Drag-to-nest (50% overlap auto-reparent)
- Layers panel cross-parent drag-drop
- Copy/paste preserves full nested subtree
- Frame resize reflows children via constraints

**Properties (right panel):**
- Position, size, rotation, flip (H/V)
- Fills (multi-fill list, per-fill opacity, alpha-composited via Porter-Duff source-over)
- Strokes (multi-stroke list, single shared weight per layer, per-stroke opacity, alpha-composited)
- Opacity, **per-corner cornerRadius** (rectangle/image: `[tl,tr,br,bl]` tuple; polygon/star: uniform only; frame: ignored at render), visibility
- Effects: drop shadow, layer blur (`+` adds drop shadow + opens floating popover; type switcher inside)
- Appearance section unifies opacity + corner radius + per-corner toggle + polygon Count + star Count/Ratio
- Text: font, size, weight, alignment, line height, letter spacing
- Constraints (H/V per layer), aspect-ratio lock (Layout)
- Prototype panel (Design/Prototype tab, `Shift+E`)

**Prototype:**
- Hotspot-to-frame connections with trigger + action + animation
- Flow starting points on top-level frames
- Prototype preview / play
- Connection arrows rendered on canvas

**Editing:**
- Undo/redo
- Copy / Cut / Paste / Duplicate (`Cmd+D`, Alt-drag)
- Select all (scoped to hierarchy level)
- Send to front / Send to back
- Group / Ungroup
- Enter group / Exit group (`Esc`)
- Rename (inline, modal, context menu)
- Multiple pages

**Canvas:**
- Pan (Space+drag, hand tool, trackpad), Zoom (scroll, pinch, `Cmd++/-/0`)
- Snap to pixel, snap guides
- Hover outline, selection bbox + handles
- Context menu, action bar

---

## 6. Logger — 3 streams

Full field reference: `project-documents/app-docs/logging-documentation.md`

| Stream | Source | Capacity |
|---|---|---|
| **raw** | DOM events (pointer, keyboard, wheel, clipboard) | Ring buffer 500k |
| **semantic** | Engine dispatch — every meaningful operation | Ring buffer 10k |
| **outcome** | Live snapshot: full document + shapeCounts | Single object, overwritten each flush |

All three sync to `sessionStorage` on a 250ms throttle (`logger/persist.ts`).

**Export:** `window.__exportLog()` in dev mode (`main.tsx`) downloads a single combined JSON:
`figma-mock-log-<sessionId>.json` — this is what `test-verifier` reads.

---

## 7. Folder structure

```
test-app/src/
├── main.tsx                    entry — installs logger, exposes __exportLog in dev
├── App.tsx                     top-level layout
├── types/
│   ├── scene.ts                DocumentNode, Page, Layer union, Paint/Stroke/Effect
│   ├── ops.ts                  op union (17 ops)
│   └── events.ts               semantic event registry (~60 event types)
├── engine/
│   ├── store.ts                Zustand store (6 buckets)
│   ├── ops.ts                  apply + inverse per op
│   ├── dispatch.ts             central entrypoint: op → apply → undo → semantic
│   ├── selectors.ts            derived state (active page, selected layers, hit-test)
│   ├── commands.ts             shape creation entry points
│   ├── alignmentCommands.ts    align + distribute selection
│   ├── hierarchyCommands.ts    group/ungroup, z-order, reparent, rename
│   ├── imageCommands.ts        place image
│   ├── framePresetCommands.ts  create/apply frame presets
│   ├── pageCommands.ts         create/delete/switch page
│   ├── propertyCommands.ts     fills, strokes, effects, opacity, corner radius
│   ├── textCommands.ts         font, size, weight, alignment
│   ├── transformCommands.ts    flip, zoom, scale
│   ├── coordinates.ts          screen ↔ scene coordinate transforms
│   ├── snap.ts                 pixel snap + snap guide logic
│   └── styleDefaults.ts        default fills/strokes per shape type
├── logger/
│   ├── buffer.ts               ring buffer
│   ├── raw.ts                  DOM event capture
│   ├── semantic.ts             pushSemantic() + event types
│   ├── outcome.ts              buildOutcomeSnapshot()
│   ├── persist.ts              sessionStorage sync (250ms throttle)
│   └── export.ts               exportLog() + downloadLogAsJson()
├── ui/
│   ├── chrome/
│   │   ├── Toolbar.tsx         tool buttons
│   │   ├── ToolbarDropdown.tsx
│   │   ├── LeftPanel.tsx       layers tree + pages list
│   │   ├── LeftRail.tsx        icon rail (assets, variables…)
│   │   ├── RightPanel.tsx      design/prototype tabs + panel sections
│   │   └── noopClick.ts        toast emitter for unimplemented buttons
│   ├── canvas/
│   │   ├── CanvasView.tsx      SVG root + viewport transform
│   │   └── NodeRenderer.tsx    per-type SVG renderer
│   ├── overlays/
│   │   ├── SelectionOverlay.tsx    bbox + resize/rotate handles
│   │   ├── ActionBar.tsx           floating action bar on selection
│   │   ├── ColorPicker.tsx         color wheel + hex/rgb inputs
│   │   ├── ConnectionArrows.tsx    prototype connection lines
│   │   ├── ContextMenu.tsx         right-click menu
│   │   ├── FlowBadges.tsx          prototype flow badges
│   │   ├── HoverOutline.tsx        layer hover ring
│   │   ├── InsertionCrosshair.tsx  tool cursor
│   │   ├── InteractionModal.tsx    prototype connection editor
│   │   ├── ParentBoundsOverlay.tsx frame scope indicator
│   │   ├── PenPreview.tsx          live pen path preview
│   │   ├── PencilPreview.tsx       freehand stroke preview
│   │   ├── PrototypePreview.tsx    prototype play mode overlay
│   │   ├── RenameModal.tsx         rename dialog
│   │   ├── RotateReadout.tsx       angle tooltip during rotate
│   │   ├── TextEditor.tsx          inline text editing
│   │   ├── Toasts.tsx              unsupported-feature toasts
│   │   └── VectorEditOverlay.tsx   vertex handles for vector edit
│   └── panels/
│       ├── LayersTree.tsx          layers panel
│       ├── PageSection.tsx         page background color
│       ├── PositionSection.tsx     x/y/w/h/rotation/flip inputs
│       ├── AppearanceSection.tsx   opacity
│       ├── FillSection.tsx         fill list + color picker trigger
│       ├── StrokeSection.tsx       stroke list
│       ├── EffectsSection.tsx      drop shadow + layer blur
│       ├── TypographySection.tsx   font/size/weight/align
│       ├── ConstraintsControl.tsx  H/V constraint dropdowns
│       ├── LayoutSection.tsx       frame layout settings
│       ├── FramePresetBrowser.tsx  frame preset category + size list
│       ├── AlignmentRow.tsx        align + distribute buttons
│       ├── ExportSection.tsx       export stub (noop)
│       ├── PrototypePanel.tsx      prototype connections + flows
│       ├── NumericInput.tsx        scrubable number input
│       └── sectionShell.tsx        collapsible section wrapper
└── util/
    ├── id.ts                   nanoid wrapper
    ├── keymap.ts               keyboard shortcut routing
    ├── geometry.ts             bbox, hit-test, bounds math
    ├── prototypeDevices.ts     prototype device list
    └── framePresets.ts         frame preset list (right sidebar)
```

---

## 8. Coordinate spaces and transform invariants

| Space | Description | Used in |
|---|---|---|
| **Screen** | Browser pixel coords (`clientX/Y`) | Raw events |
| **Canvas** | Screen adjusted for pan/zoom | Hit-testing, snap |
| **Scene** | Parent-relative coords in layer `x/y/w/h` | outcome.document, semantic events |

`coordinates.ts` provides `screenToScene()` and `sceneToScreen()`.

### Rendered world geometry

Layer `x/y/w/h` is stored in parent space, but canvas rendering, hit-testing, hover, selection, prototype handles, smart-snap, and frame nesting need rendered world geometry. These paths must use the matrix-aware helpers in `engine/coordinates.ts`:

- `layerToWorldMatrix`
- `parentToWorldMatrix`
- `localPointToWorld`
- `worldPointToLayerLocal`
- `worldToParentLocal`
- `worldOrientedCornersOfLayer`
- `worldAABBOfLayer`

Do not add parent offsets by hand for nested layers. That offset-only pattern ignores ancestor rotation and flip.

### Reparent invariant

`reparent` preserves the visual world transform of the moved layer. When a layer enters or exits a frame/group/section, its local transform is re-expressed under the new parent so the user does not see a jump.

Frame containment uses shared overlap logic in `engine/frameContainment.ts`. Canvas drag and right-panel X/Y/W/H transforms must both use this helper so a layer entering or exiting a frame updates both its visual transform and its scene-graph parent.

Canvas drag and panel scrub can combine `set_transform` and `reparent` in one transaction. Panel scrub defers the containment check until pointer-up so the panel value does not change coordinate reference mid-gesture; the final `reparent` still lands in the same undo transaction. Panel transforms use the shared overlap calculation with a more responsive exit threshold than live canvas drag, because no mid-drag reparent jitter can occur.

### Smart-snap invariant

Smart-snap compares visual bounds, not raw stored rectangles.

- Candidate siblings and frames are cached as transformed `worldAABBOfLayer` rectangles.
- Moving selections snapshot transformed visual AABBs at drag start and use their union as the moving bbox.
- Snap guide lines and distance measures are transient UI feedback; they do not mutate document state.

### Line and arrow invariant

Lines and arrows are two-point geometry. Their visual segment is represented by `p1` and `p2`, while `x/y/w/h` stores the normalized parent-space bbox. Selection and endpoint drag should use line-specific geometry helpers instead of the normal eight-handle rectangle model.

### Position coordinate invariant

Stored layer geometry remains rect-based: `x/y` is the parent-local top-left of the layer bbox. User-facing Position panel X/Y is a different engine-level concept:

- The canvas viewport is center-origin: with `viewport = { x: 0, y: 0, zoom: 1 }`, world `{ x: 0, y: 0 }` renders at the visible canvas center.
- Top-level layer Position X/Y is the layer visual center relative to the page/world origin `{ x: 0, y: 0 }`, which is the visible canvas center at the default viewport.
- Nested layer Position X/Y is the layer visual center relative to its parent container's visual center.
- Setting Position X/Y converts that center-origin value back to stored parent-local `x/y`.
- Panel width/height changes preserve the current center-origin Position value.

Use `engine/positionCoordinates.ts` for Position value conversion and `engine/viewportCoordinates.ts` for screen/world conversion. Do not read or write `layer.x/layer.y` directly when implementing user-facing Position behavior.

### Paint compositing invariant

Multi-fill and multi-stroke render via Porter-Duff source-over compositing. The fill / stroke list is top-down (index 0 is on top); compositing walks the array bottom-up so each upper paint is laid over the accumulator. Per-paint alpha drives how much of the layer below shows through. Single helpers in `NodeRenderer.tsx` (`paintToFill`, `strokeAttrs`) own this math — shapes do not iterate paints themselves.

Strokes additionally maintain a single-weight invariant per layer: every stroke entry must share the same `weight` and `dash` value. `setStrokeWeight` writes the entire `strokes` array in one op, and `addSolidStroke` inherits weight from `strokes[0]`. The renderer uses `strokes[0].weight` and `strokes[0].dash` to draw the composited line.

### Corner radius invariant

`cornerRadius` is polymorphic at the type level:
- **Rectangle / Image** carry `number | [topLeft, topRight, bottomRight, bottomLeft]`. Rendering uses the path helper `rectCornerPath(w, h, cr)` (NOT `<rect rx>`) so 4-tuples render correctly. Image clip paths use the same helper.
- **Polygon / Star** carry an optional uniform `cornerRadius?: number`. The vertex-rounding helper `roundedPolygonPath(points, radius)` replaces each vertex with a circular arc tangent to both adjacent edges (tangent length `t = r/tan(angle/2)`, clamped to half-edge to prevent overlap, collinear vertices skipped). When the radius reaches the inscribed-ellipse threshold, `PolygonEl` falls back to `<ellipse>` so polygons morph cleanly into circles at max radius.
- **Frame** carries `cornerRadius` in the model but `GroupEl` overrides it to `rx=0` at render. Frames are always flat regardless of the stored value. The model field is preserved so existing tools that set or read it don't crash.
