# Logging Documentation

This document describes the three log streams the mock app produces (`raw`, `semantic`, `outcome`), their storage layout, and every field they contain.

The streams exist to let an offline evaluator score CUA agent runs against task rubrics. Each rubric reads from the stream that has the data it needs:

| Rubric | Reads from | What it looks at |
|---|---|---|
| **Fundamentals** (correct primitives used) | `outcome` | `summary.shapeCounts` or walks `document` and counts by `type` |
| **Alignment** (geometric relationships) | `outcome` | `document` → per-node `x`, `y`, `w`, `h`, `rotation` |
| **Efficiency** (turn count) | `semantic` | event count vs. per-task target |

`raw` is the low-level forensic stream — no rubric reads it directly, but it's the source of truth for "exactly what input did the agent generate" and it cross-references into semantic events via `rawEventIdRange`.

---

## Storage

All three streams are mirrored from in-memory ring buffers + the live store into `sessionStorage` on a 250ms throttle ([`mock/src/logger/persist.ts`](mock/src/logger/persist.ts)).

**Key naming:** `${YYYY-MM-DD}_${stream}_${sessionId}_data`

| Key | Holds |
|---|---|
| `2026-04-29_raw_session_xxx_data` | `RawEvent[]` — JSON array, oldest-to-newest order |
| `2026-04-29_semantic_session_xxx_data` | `SemanticEvent[]` — JSON array, oldest-to-newest order |
| `2026-04-29_outcome_session_xxx_data` | `OutcomeSnapshot` — single JSON object, overwritten each flush |

**Lifecycle:**
- Keys are seeded at app load with empty arrays (raw/semantic) or the initial document state (outcome).
- Every semantic/raw event triggers a 250ms-throttled re-flush of all three keys.
- `beforeunload` forces an immediate final flush so the last state survives a tab close.
- On page refresh, any keys from a prior session matching `*_raw_*_data` / `*_semantic_*_data` / `*_outcome_*_data` are swept before new ones are seeded — exactly one set per stream lives in storage at a time.

**Capacities** (in-memory ring buffers; oldest events drop when full):
- `raw`: 500 000 events
- `semantic`: 10 000 events

The `outcome` stream is not a buffer — it's a single snapshot rebuilt from store state on every flush.

**Export:** [`mock/src/logger/export.ts`](mock/src/logger/export.ts) bundles all three into one JSON file (`figma-mock-log-${sessionId}.json`) for offline scoring.

---

## Raw stream

Captures every relevant DOM input event before any handler can stop it. Source: [`mock/src/logger/raw.ts`](mock/src/logger/raw.ts).

### `RawEvent` schema

| Field | Type | Description |
|---|---|---|
| `eventId` | `string` | Unique id (`raw_<timestamp36>_<counter>_<rand>`). Referenced by `semantic.rawEventIdRange`. |
| `type` | `string` | DOM event name (see table below). |
| `timestamp` | `number` | `performance.now()` at capture (monotonic ms since page load). |
| `sessionTime` | `number` | `timestamp - sessionStartedAt`; ms since the raw capture installed. |
| `fields` | `Record<string, unknown>` | Per-type payload (see below). |
| `targetId` | `string \| null` | `data-id` of nearest ancestor of `event.target` (set on chrome elements + canvas nodes). `null` if the event was on an element without one. |
| `modifiers` | `{ alt, shift, ctrl, meta: boolean }` | Keyboard modifier state at capture. |

### Captured `type`s and their `fields`

| `type` | `fields` keys |
|---|---|
| `pointerdown` | `clientX`, `clientY`, `button`, `buttons`, `pointerType`, `pointerId` |
| `pointermove` | same as pointerdown — coalesced to **one event per animation frame** |
| `pointerup` | same as pointerdown |
| `click` | `clientX`, `clientY`, `button` |
| `dblclick` | `clientX`, `clientY`, `button` |
| `contextmenu` | `clientX`, `clientY` |
| `keydown` | `key`, `code`, `repeat`, `targetTag` |
| `keyup` | `key`, `code` |
| `wheel` | `deltaX`, `deltaY` — accumulated and flushed once per ~16ms |
| `copy` | `{}` |
| `cut` | `{}` |
| `paste` | `kinds`: array of `"<kind>/<mime>"` strings from the clipboard items |
| `resize` | `innerWidth`, `innerHeight` |
| `visibilitychange` | `visibilityState` |

`clientX`/`clientY` are screen-relative pixel coords (DOM mouse-event coords), **not** scene coords.

---

## Semantic stream

User-intent events emitted by the engine when a meaningful operation happens (e.g. shape created, layer moved, undo, page switch). Source: [`mock/src/types/events.ts`](mock/src/types/events.ts), emission via [`mock/src/logger/semantic.ts`](mock/src/logger/semantic.ts).

### Base fields (every semantic event)

| Field | Type | Description |
|---|---|---|
| `schemaVersion` | `1` | Bumped only on payload-breaking changes. |
| `sessionId` | `string` | Same id used in storage keys + `outcome.sessionId`. |
| `eventId` | `string` | Unique id (`sem_…`). |
| `timestamp` | `number` | `performance.now()` at emission. |
| `pageId` | `string \| null` | Active page when the event was emitted. |
| `rawEventIdRange` | `[string, string] \| null` | `[firstRawIdSinceLastSemantic, mostRecentRawId]` — lets you slice the raw stream that caused this semantic event. `null` if no raw events have been captured yet. |
| `name` | string literal | Discriminator; see below. |

Each event's full payload = base fields + the `name`-specific fields below.

### Tool / mode / selection

| `name` | Extra fields |
|---|---|
| `tool_change` | `before`, `after`: tool ids; `trigger`: `shortcut` \| `toolbar_click` \| `auto_revert_after_create` \| `space_temp_hand` |
| `mode_change` | `before`, `after`: mode strings |
| `selection_change` | `before`, `after`: layer-id arrays; `triggerMethod` (see `SelectionTriggerMethod`); `cause`: `{ eventId }` of the event that caused this implicit change, else `null` |
| `click_select` | `targetLayerId`, `pointer: { x, y }` (scene coords), `source`: `canvas` \| `layers_panel` |
| `shift_click_add_selection` | `targetLayerId`, `pointer`, `source` |
| `shift_click_remove_selection` | `targetLayerId`, `pointer`, `source` |
| `drag_box_select` | `start`, `end` (scene coords); `layerIds`; `modifier`: `none` \| `shift_additive` \| `alt_enclosure` |
| `select_all` | `scope`: `page` \| `parent_group` \| `parent_frame`; `layerIds` |
| `deselect` | `trigger`: `escape` \| `click_empty_canvas` \| `shortcut` |

### Layer creation

All creation events share `layerId`, `parentId`, and `trigger`. Geometry payload differs:

| `name` | Extra fields |
|---|---|
| `create_rectangle` | `x`, `y`, `w`, `h`; `modifiers: { shift, alt }`; `trigger`: `shortcut_R` \| `toolbar` \| `click_default_size` |
| `create_ellipse` | `x`, `y`, `w`, `h`; `modifiers`; `trigger`: `shortcut_O` \| `toolbar` \| `click_default_size` |
| `create_polygon` | `x`, `y`, `w`, `h`, `sides`; `modifiers`; `trigger` |
| `create_star` | `x`, `y`, `w`, `h`, `points`, `innerRatio`; `modifiers`; `trigger` |
| `create_line` | `p1: { x, y }`, `p2: { x, y }`; `modifiers`; `trigger`: `shortcut_L` \| `toolbar` |
| `create_arrow` | `p1`, `p2`; `modifiers`; `trigger`: `shortcut_shift_L` \| `toolbar` |
| `create_frame` | `x`, `y`, `w`, `h`; `mode`: `drag` \| `preset` \| `wrap`; `trigger`: `shortcut_F` \| `toolbar` \| `preset` \| `wrap_selection` |
| `create_section` | `x`, `y`, `w`, `h`; `trigger`: `shortcut_shift_S` \| `toolbar` \| `wrap_selection` |
| `create_slice` | `x`, `y`, `w`, `h`; `trigger`: `shortcut` \| `toolbar` |
| `create_text` | `x`, `y`, `w`, `h`, `resizingMode`: `auto_width` \| `auto_height` \| `fixed`; `trigger`: `shortcut_T` \| `toolbar` |
| `place_image` | `layerIds`, `source`: `file_picker` \| `drag_drop` \| `clipboard_paste`; `filenames` |

### Text editing

| `name` | Extra fields |
|---|---|
| `type_characters` | `layerId`, `length` (chars typed in this batch — content not stored to keep payload small) |
| `commit_text` | `layerId`, `content` (final text after commit) |

### Vector editing

| `name` | Extra fields |
|---|---|
| `create_vector_with_pen` | `layerId`, `closed`, `pointCount` |
| `create_vector_with_pencil` | `layerId`, `pointCount` |
| `add_vector_point` | `layerId`, `index`, `position: { x, y }` |
| `move_vector_point` | `layerId`, `index`, `before: { x, y }`, `after: { x, y }` |
| `delete_vector_point` | `layerId`, `index` |

### Transform & layout

| `name` | Extra fields |
|---|---|
| `move_layer` | `layerIds`; `before`/`after`: `Record<layerId, { x, y }>` in world-space origin terms for drag; `trigger`: `drag` \| `arrow_key` \| `panel_input`; `modifiers: { shift, alt, ctrl }` |
| `resize_layer` | `layerIds`; `before`/`after`: `Record<layerId, { x, y, w, h }>`; `handle`: `n`/`s`/`e`/`w`/`ne`/`nw`/`se`/`sw`; `trigger`; `modifiers` |
| `resize_line_endpoint` | `layerId`; `endpoint`: `p1` \| `p2`; `before`/`after`: `{ transform, p1, p2 }`; `trigger`: `drag` |
| `rotate_layer` | `layerIds`; `before`/`after`: `Record<layerId, degrees>`; `trigger`: `drag` \| `panel_input` \| `panel_button` |
| `flip_layer` | `layerIds`, `axis`: `horizontal` \| `vertical`; `trigger`: `shortcut` \| `context_menu` \| `main_menu` \| `panel_button` |
| `scale_layer` | `layerIds`, `factor: { sx, sy }`, `anchor: { x, y }`; `trigger`: `drag` |
| `align_layers` | `layerIds`, `axis`: `left` \| `center-x` \| `right` \| `top` \| `center-y` \| `bottom`; `trigger`: `panel_button` \| `shortcut` |
| `distribute_layers` | `layerIds`, `axis`: `horizontal` \| `vertical`; `trigger` |
| `reorder_layer` | `layerIds`; `before`/`after`: `{ parentId, index }[]`; `trigger`: shortcut bracket variants \| `panel_drag` \| `canvas_drag` |

Notes:
- `flip_layer.axis` is user-facing. Internal scale toggles may differ so the visual action matches the Position panel label.
- Position panel X/Y values are center-origin user coordinates. Top-level layer values are relative to the page/world origin, which renders at the visible canvas center in the default viewport; nested layer values are relative to the parent visual center. The stored `outcome.document` geometry remains parent-local bbox geometry.
- `move_layer` with `trigger: "panel_input"` records these user-facing Position values in `before`/`after`.
- A canvas drag that crosses a frame boundary emits `move_layer` for the drag and `reorder_layer` with `trigger: "canvas_drag"` for the parent/index transition.
- Smart-snap guides are transient UI feedback. They do not emit semantic events unless the drag commits a document mutation.

### Edit operations

| `name` | Extra fields |
|---|---|
| `delete` | `layerIds`; `trigger`: `keyboard_canvas` \| `keyboard_panel` \| `context_menu_canvas` \| `context_menu_panel` \| `main_menu` |
| `copy` | `layerIds`; `trigger`: `shortcut` \| `context_menu` \| `main_menu` |
| `cut` | same as copy |
| `paste` | `newLayerIds`; `placement`: `viewport_center` \| `into_frame` \| `at_cursor` \| `from_origin`; `trigger` |
| `duplicate` | `sourceLayerIds`, `newLayerIds`, `offset: { dx, dy }`; `trigger`: `shortcut_cmd_d` \| `alt_drag` |

### Property changes

| `name` | Extra fields |
|---|---|
| `set_property` | `layerIds`, `path` (dot-path into the layer, e.g. `fills.0.color`, `strokes`, `strokes/${i}/paint/visible`); `before`/`after`: `Record<layerId, unknown>`; `trigger`: `panel_input` \| `color_picker` \| `context_menu` \| `shortcut`. **Note**: stroke-weight edits replace the full `strokes` array (path `"strokes"`) so every stroke in the stack stays at the same weight. `removeStroke` also writes path `"strokes"`; `toggleStrokeVisibility` writes path `"strokes/${i}/paint/visible"`. |
| `set_fill_color` | `layerIds`, `fillIndex`; `before`/`after`: `{ r, g, b, a }` (0..1) |
| `add_fill` / `remove_fill` | `layerIds`, `fillIndex` |
| `toggle_layer_visibility` / `toggle_fill_visibility` / `toggle_stroke_visibility` / `toggle_effect_visibility` | `layerIds`, optional `index`, `after: boolean` |
| `set_layer_opacity` | `layerIds`; `before`/`after`: `Record<layerId, number>` (0..1); `trigger`: `slider_scrub` \| `panel_input` |
| `set_corner_radius` | `layerIds`; `before`/`after`: `Record<layerId, number \| [n,n,n,n]>`; `trigger` |
| `rename_layer` | `layerId`, `before`, `after`; `trigger`: `inline_panel` \| `rename_modal` \| `context_menu` |
| `set_page_background` | `targetPageId`; `before`/`after`: `{ r, g, b, a }` (0..1); `trigger`: `color_picker` \| `panel_input` |
| `set_page_background_opacity` | `targetPageId`; `before`/`after`: alpha number (0..1); `trigger`: `slider_scrub` \| `panel_input` |
| `toggle_page_background_hidden` | `targetPageId`; `before`/`after`: boolean; `trigger`: `panel_button` |
| `set_polygon_sides` | `layerIds`; `before`/`after`: `Record<layerId, number>`; `trigger`: `panel_input` |
| `set_star_points` | `layerIds`; `before`/`after`: `Record<layerId, number>`; `trigger`: `panel_input` |
| `set_star_inner_ratio` | `layerIds`; `before`/`after`: `Record<layerId, number>` (clamped to `[0.1, 1.0]` — UI hides values below 10%); `trigger`: `panel_input` |

### Grouping

| `name` | Extra fields |
|---|---|
| `group_selection` / `ungroup` | `layerIds`, optional `groupId`; `trigger` |
| `enter_group` / `exit_group` | `groupId` |

### Viewport

| `name` | Extra fields |
|---|---|
| `pan_canvas` | `delta: { dx, dy }`; `before`/`after`: `{ x, y }`; `trigger`: `space_drag` \| `hand_tool_drag` \| `trackpad` \| `arrow_key` \| `middle_mouse` |
| `zoom_canvas` | `before`/`after`: zoom factors; `anchor: { x, y }`; `trigger`: `scroll` \| `pinch` \| `keyboard` \| `input_field` \| `dropdown_entry` \| `magic_mouse` |
| `viewport_change` | `before`/`after`: `{ x, y, zoom }`; `reasons`: subset of `["pan", "zoom"]` |
| `zoom_to_fit` | `contentBounds: { x, y, w, h } \| null`; `trigger`: `keyboard` \| `dropdown_entry` \| `initial_load` |
| `zoom_to_100` | `trigger`: `keyboard` \| `input_field` |
| `zoom_to_selection` | `selectionBounds: { x, y, w, h }`, `layerIds`; `trigger` |

### Pages

| `name` | Extra fields |
|---|---|
| `create_page` | `newPageId`, `pageIndex`; `trigger`: `panel_button` \| `context_menu` |
| `switch_page` | `beforePageId`, `afterPageId`; `trigger`: `panel_click` \| `shortcut` \| `implicit_after_create` |
| `rename_page` | `targetPageId`, `before`, `after` |
| `rename_file` | `before`, `after`; `trigger`: `inline_edit` \| `file_menu` |
| `delete_page` | `targetPageId`, `pageIndex`; `trigger`: `context_menu` \| `shortcut` |

### Undo / redo

| `name` | Extra fields |
|---|---|
| `undo` | `revertedOpKind`, `revertedOpId` |
| `redo` | `reappliedOpKind`, `reappliedOpId` |

### Session

| `name` | Extra fields |
|---|---|
| `session_start` | `userAgent`, `viewport: { width, height }` |
| `session_end` | (no extra fields) |
| `noop_click` | `elementId`, `pointer: { x, y }` — emitted when the user clicks a not-yet-implemented control |

### Prototype

| `name` | Extra fields |
|---|---|
| `prototype_tab_switch` | `before`/`after`: `design` \| `prototype`; `trigger`: `tab_click` \| `shortcut_shift_e` |
| `add_prototype_flow` | `flowId`, `flowName`, `frameId` |
| `remove_prototype_flow` | `flowId`, `frameId` |
| `rename_prototype_flow` | `flowId`, `before`, `after` |
| `set_prototype_device` | `before`, `after` (device id strings or `null`) |
| `set_overflow_scrolling` | `layerId`, `before`, `after` |
| `set_scroll_position` | `layerId`, `before`, `after` |
| `open_prototype_preview` | `trigger`: `play_button` |
| `close_prototype_preview` | `trigger`: `close_button` \| `play_button_toggle` |
| `navigate_prototype_preview` | `direction`: `prev` \| `next`; `fromIndex`, `toIndex` |
| `create_prototype_connection` | `connectionId`, `sourceLayerId`, `trigger` (string), `action` (string) |
| `delete_prototype_connection` | `connectionId`, `sourceLayerId` |
| `update_prototype_connection` | `connectionId`, `field`: `trigger` \| `action` \| `destinationFrameId` \| `animation` \| `delayMs` \| `url`; `before`, `after` |
| `navigate_prototype_connection` | `connectionId`, `sourceLayerId`, `destinationFrameId` |

---

## Outcome stream

A single snapshot of "what got built" — the live document plus a small precomputed summary. Overwritten on every flush; **no history kept**. Source: [`mock/src/logger/outcome.ts`](mock/src/logger/outcome.ts).

### Top-level

| Field | Type | Description |
|---|---|---|
| `schemaVersion` | `1` | Bumped on payload-breaking changes. |
| `sessionId` | `string` | Same id used in keys + semantic events. |
| `capturedAt` | `number` | `Date.now()` at flush time. |
| `activePageId` | `string` | Page the user/agent was on. |
| `summary` | `OutcomeSummary` | Precomputed aggregates, see below. |
| `document` | `DocumentNode` | Full scene tree, see below. |

### `summary`

| Field | Type | Description |
|---|---|---|
| `semanticEventCount` | `number` | `logger.semanticEvents.length` at flush time — direct input for the **Efficiency** rubric. |
| `shapeCounts` | `Partial<Record<NodeType, number>>` | Total count per `type` across **all** pages, recursing into containers. Containers count themselves AND their children get counted independently. Direct input for the **Fundamentals** rubric. |

`NodeType` is one of: `rectangle`, `ellipse`, `polygon`, `star`, `line`, `arrow`, `text`, `vector`, `image`, `frame`, `section`, `group`, `slice`.

### `document` — full scene

Type: `DocumentNode` from [`mock/src/types/scene.ts`](mock/src/types/scene.ts).

```
document
├─ id (string)
├─ schemaVersion (number)
├─ name (string)
└─ pages: Page[]
   ├─ id, name, type: "page"
   ├─ backgroundColor: { r, g, b, a }   (0..1)
   ├─ backgroundHidden: boolean
   ├─ prototypeSettings, prototypeFlows, prototypeConnections (optional)
   └─ children: Layer[]                  (recursive into containers)
```

Every layer has the **`LayerBase` block**:

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique layer id (referenced by every semantic event that touches this layer). |
| `type` | `NodeType` | Discriminator; selects which extra fields apply (see per-type table below). |
| `name` | `string` | Display name in the Layers panel. |
| `parentId` | `string` | Page id at root, or container layer id when nested. |
| `x`, `y` | `number` | Top-left of axis-aligned bounding box, in **parent space** (scene coords). |
| `w`, `h` | `number` | Width and height in parent space. |
| `rotation` | `number` | Degrees, clockwise positive. |
| `scaleX`, `scaleY` | `1 \| -1` | Mirror flags only — fractional scale lives in `w`/`h`. |
| `visible` | `boolean` | Layer-level visibility toggle. |
| `locked` | `boolean` | Editing lock; UI-only, doesn't affect rubrics. |
| `opacity` | `number` | 0..1 multiplicative. |
| `constraints` | `{ horizontal, vertical }` | Resize-reflow rules; values listed below. |
| `scrollPosition` | `"scroll_with_parent" \| "fixed" \| "sticky"` | Optional, prototype-related. |

**`Constraints` values:**
- `horizontal`: `left` \| `right` \| `center` \| `stretch` \| `scale`
- `vertical`: `top` \| `bottom` \| `center` \| `stretch` \| `scale`

### Per-type extras

`Color` everywhere is `{ r, g, b, a }` with each channel 0..1.

#### `Paint` (used inside `fills`)
- `SolidPaint`: `{ kind: "solid", color, opacity, visible }`
- `ImagePaint`: `{ kind: "image", src, fit: "fill"|"fit"|"crop"|"tile", rotation, opacity, visible }`
- (gradient/pattern/video kinds reserved in `PaintKind` but not currently emitted)

#### `Stroke`
`{ paint: Paint, weight: number, alignment: "inside"|"center"|"outside", dash: { dash, gap } | null }`

#### `Effect`
- `{ kind: "drop_shadow", x, y, blur, spread, color, visible }`
- `{ kind: "layer_blur", radius, visible }`

#### Per-`type` payload

| `type` | Extra fields |
|---|---|
| `rectangle` | `cornerRadius` (number or 4-tuple), `fills: Paint[]`, `strokes: Stroke[]`, `effects: Effect[]` |
| `ellipse` | `fills`, `strokes`, `effects`, `arcStartAngle`, `arcEndAngle`, `innerRadius` |
| `polygon` | `sides`, optional `cornerRadius?: number` (uniform-only — never a 4-tuple), `fills`, `strokes`, `effects` |
| `star` | `points`, `innerRatio` (clamped to `[0.1, 1.0]`), optional `cornerRadius?: number` (uniform-only), `fills`, `strokes`, `effects` |
| `line` | `p1: { x, y }`, `p2: { x, y }`, `strokes`, `effects` |
| `arrow` | `p1`, `p2`, `strokes`, `effects`, `endCapStart`/`endCapEnd`: `none`\|`arrow` |
| `text` | `content` (full string), `runs: TextRun[]`, `fontFamily`, `fontWeight`, `fontSize`, `lineHeight: { type: auto\|px\|percent, value? }`, `letterSpacing: { type: px\|percent, value }`, `hAlign`, `vAlign`, `fills`, `strokes`, `effects`, `resizingMode`. `TextRun` = `{ range: [start,end], fontFamily?, fontWeight?, fontSize?, letterSpacing?, lineHeight?, fills? }` |
| `vector` | `network: { vertices, segments, closed }`, `fills`, `strokes`, `effects`. `vertices[i]` = `{ x, y, handleType: corner\|mirror\|mirror_angle\|independent }`. `segments[i]` = `{ fromIndex, toIndex, handleFrom: { dx, dy }\|null, handleTo: { dx, dy }\|null }` |
| `image` | `cornerRadius`, `imageFill: { src, naturalWidth, naturalHeight, fit, rotation, opacity, visible }`, `fills`, `strokes`, `effects` |
| `frame` | `fills`, `strokes`, `effects`, `cornerRadius` (carried in the model but **render-side override forces `0`** — frames always render flat regardless of stored value; rubrics that judge visual outcome should treat frames as having `cornerRadius=0`), `clipsContent: boolean`, `children: Layer[]` (recurse), `overflowScrolling`: `none`\|`horizontal`\|`vertical`\|`both` |
| `section` | `fills`, `clipsContent: false`, `children: Layer[]`, `devStatus`: `null`\|`ready_for_dev` |
| `group` | `effects`, `children: Layer[]` |
| `slice` | (no extras beyond `LayerBase`) |

---

## Cross-stream relationships

- `outcome.sessionId` === `semantic[i].sessionId` === sessionStorage key `${sessionId}`. Tying the three streams together is one string compare.
- `semantic[i].rawEventIdRange = [from, to]` slices the **raw** events that belong to that semantic event. Use it to replay exactly what input produced an action.
- `semantic[i].pageId` lets you filter the semantic stream to the page that ended up in `outcome.activePageId`, in case multi-page sessions mix events.
- Layer ids stay stable across the session: a `layerId` mentioned in a semantic event will exist somewhere in `outcome.document.pages[*].children` (recursively) unless a later `delete` event removed it.

---

## Conventions / gotchas

- **Coordinate spaces:** raw events use **screen pixels** (`clientX`/`clientY`). Semantic events that mention `pointer`/`start`/`end`/`anchor` use **scene coords**. `outcome.document` `x`/`y`/`w`/`h` are always **parent-space scene coords**.
- **Color range is 0..1**, not 0..255. Convert on the evaluator side if your rubric expects 0..255.
- `before`/`after` payloads on bulk events are **keyed by `layerId`** (`Record<string, …>`) so a multi-select op tells you per-layer what changed.
- `outcome` is a snapshot, not a log. If the agent finishes and immediately undoes everything, the snapshot reflects the post-undo state.
- `semantic.eventCount` includes EVERY semantic event — `tool_change`, `selection_change`, `pan_canvas`, etc. If a rubric defines "turns" more narrowly (e.g. "only creation/transform events"), the rubric is responsible for filtering before counting.
- Ring-buffer caps: very long sessions may drop the oldest raw events (cap 500 000) or semantic events (cap 10 000). Outcome is unaffected because it's a live snapshot.

---

## Right-panel overhaul (2026-05) — payload changes evaluators should know

The figma/ui session reshaped the right panel and its engine commands. No new event names were introduced; existing events carry slightly different payloads:

- **`set_corner_radius`** payload may be a 4-tuple `[topLeft, topRight, bottomRight, bottomLeft]` for `rectangle` / `image`. Polygon and star always use a uniform `number`. Frames carry the value but render-side ignores it.
- **`set_property` `path` for strokes**: `setStrokeWeight` now writes the full `strokes` array via `path: "strokes"` (was `"strokes/0/weight"`); `removeStroke` writes `path: "strokes"`; `toggleStrokeVisibility` writes `path: "strokes/${i}/paint/visible"`.
- **`set_star_inner_ratio`** values are clamped to `[0.1, 1.0]` (UI minimum is 10%).
- **Live-drag scrubs**: `NumericInput` and the per-fill/stroke/effect opacity scrubbers fire their commit on every pointermove tick. One drag gesture produces dozens of `set_property` / `set_fill_color` / `set_stroke_color` / `set_effect_color` semantic events. Rubrics counting "turns" should consider deduplicating consecutive same-target events with timestamp deltas under ~100ms before scoring efficiency.
- **Multi-fill / multi-stroke compositing** is rendering-only (Porter-Duff source-over). Per-paint `outcome.document.<layer>.fills[i]` and `strokes[i]` are unchanged — checks reading individual paint data are unaffected.
- **Removed UI `data-id`s** (raw stream surface only, semantic events unchanged): `effects.add.drop-shadow`, `effects.add.layer-blur` (Drop Shadow now added directly via `effects.add`), `polygon.sides.input`, `star.points.input`, `star.ratio.input` (Polygon and Star sections were merged into Appearance).
- **New UI `data-id`s**: `appearance.corner-radius.per-corner-toggle`, `fill.row.<i>.opacity`, `layout.lock-aspect-ratio`.
