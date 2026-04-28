# Figma Design Feature Inventory — Deep

_Per-feature reference for every distinct user-facing feature documented in the 175 Figma Design help-center articles. Pair with `feature-inventory.md` (broad/shallow, all four products) and per-feature specs in `helper/extracted/features/`. This document **maps each feature to its detailed spec** — the spec contains the full Triggers / Inputs / Outputs / Edge cases / Source articles fields. Read both together: this for an at-a-glance "what's in scope?", the specs for "how does it work?"._

## Conventions

- "Feature" = a user-triggerable action that changes scene-graph, viewport, selection, panel state, or persistent file state.
- For each feature: lists **spec path** + main **triggers** + main **source articles** + **status** in mock.
  - `[FN]` = currently functional / in-scope
  - `[VO]` = visual-only stub (route to `unsupported-feature-toast.md`)
  - `[DEF]` = deferred / nice-to-have, document but don't build first

---

## 1. Tour the interface

| Feature | Spec | Main triggers | Status |
|---|---|---|---|
| Toolbar — Move tools dropdown (Move/Hand/Scale) | various transform/* | `V` / `H` / `K`; spacebar = temp Hand | [FN] |
| Toolbar — Region tools (Frame/Section/Slice) | region-tools/* | `F` / `Shift S` / Slice action | [FN] |
| Toolbar — Shape tools (Rect/Line/Arrow/Ellipse/Polygon/Star/Image) | shape-creation/* | `R` / `L` / `O` / `Shift+Cmd+K` | [FN] |
| Toolbar — Creation tools (Pen/Pencil) | vector/use-pen-tool, vector/use-pencil-tool | `P` | [FN] |
| Toolbar — Text tool | text/create-text | `T` | [FN] |
| Toolbar — Comment tools (Comment/Annotation/Measurement) | comments/, canvas-navigation/measure-distances | `C`, `Shift T`, `Shift M` | [FN comment basic, VO annotations] |
| Toolbar — Actions menu (`Cmd K`) | ui-shell/actions-menu | toolbar icon, `Cmd K` | [VO — stub] |
| Toolbar — Mode switcher (Design / Prototype / Dev Mode) | (Dev mode out of scope) | `Shift D`, `Shift E` | [VO Prototype/Dev — Design only] |
| Right panel — header (zoom/view-options) | ui-shell/zoom-percentage-display | click % | [FN core] |
| Right panel — Share button | ui-shell/share-button | click | [VO] |
| Right panel — Present button | ui-shell/present-button | click | [VO] |
| Right panel — avatar stack | ui-shell/avatar-stack | click | [VO] |
| Right panel — tabs (Design / Prototype) | (state-matrix) | tab click, `Shift E` | [VO Prototype] |
| Right panel — sub-header (Mask / Component / Boolean / `…`) | boolean/access-boolean-menu, components/create-component | click | [Mixed] |
| Left panel — file-name dropdown | ui-shell/file-name-rename | dropdown | [FN rename, VO others] |
| Left panel — minimize-UI | ui-shell/minimize-ui | `Shift \` | [FN] |
| Left panel — File / Assets tabs | ui-shell/switch-file-assets-tab | `Opt 1/2`, click | [FN File, VO Assets] |
| Left panel — pages selector | pages/* | click page name | [FN] |
| Left panel — find/replace | find-replace/find-and-replace | `Cmd F`, sidebar icon | [FN] |
| Bottom toolbar mode toggle (Figma Draw entry) | (out of scope) | click | [VO] |

## 2. Canvas navigation

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Pan canvas | canvas-navigation/pan-canvas | space-drag, middle-drag | [FN] |
| Zoom in / out | canvas-navigation/zoom-in-out | wheel-with-modifier, `+`/`-` | [FN] |
| Zoom to fit | canvas-navigation/zoom-to-fit | `Shift 1` | [FN] |
| Zoom to selection | canvas-navigation/zoom-to-selection | `Shift 2` | [FN] |
| Zoom to 100% | canvas-navigation/zoom-to-100 | `Shift 0` | [FN] |
| Custom zoom % | ui-shell/zoom-percentage-display | type into % | [FN] |
| Measure distances | canvas-navigation/measure-distances | hold Alt + hover | [FN] |
| Change canvas bg | canvas-navigation/change-canvas-bg | Page section | [FN] |
| View layer outlines | layers/view-layer-outlines | `Cmd Shift O` | [FN] |
| Pixel preview / pixel grid / snap-to-pixel | (in zoom-view-options) | view-options dropdown | [VO most] |
| Layout-guides toggle visibility | (zoom-view-options) | view-options | [VO] |

## 3. Selection

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Click to select | selection/click-select | pointer click | [FN] |
| Shift-click add | selection/shift-click-add-to-selection | shift+click | [FN] |
| Shift-click remove | selection/shift-click-remove-from-selection | shift+click on selected | [FN] |
| Marquee / drag-box select | selection/drag-box-select | pointer drag empty | [FN] |
| Select all (scoped) | selection/select-all | `Cmd A` | [FN — scoped per commit `4c6eb77`] |
| Deselect | selection/deselect | `Esc` / click empty | [FN] |
| Cmd-click deep select | frames/select-frame-with-children | `Cmd`+click | [FN] |
| Tab / Shift-Tab sibling traverse | frames/select-frame-with-children | `Tab` / `Shift Tab` | [FN] |
| Enter / Shift-Enter scope traverse | frames/enter-frame, frames/exit-frame | `Enter` / `Shift Enter` | [FN] |
| Smart selection pink handles | (covered in alignment/tidy-up) | tidy-up activates them | [DEF] |
| Lasso (vector edit only) | vector/use-lasso-select | `Q` in vector edit | [FN] |
| Select layer via right-click | (covered in layers/lock-layer) | right-click → Select layer (locked) | [FN] |

## 4. Shape creation

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Rectangle | shape-creation/create-rectangle | `R` | [FN] |
| Line | shape-creation/create-line | `L` | [FN] |
| Arrow | shape-creation/create-arrow | toolbar | [FN] |
| Ellipse | shape-creation/create-ellipse | `O` | [FN] |
| Polygon | shape-creation/create-polygon | toolbar | [FN] |
| Star | shape-creation/create-star | toolbar | [FN] |
| Image / video place | shape-creation/place-image, image/place-image-bulk | `Shift+Cmd+K` | [FN image, VO video] |
| Drag-drop image | image/drag-drop-image | OS drag-drop | [FN] |
| Arc (from ellipse) | vector/use-arc-tool | drag arc handles | [FN] |

Modifiers during drag (covered in each spec): `Shift` proportional, `Alt` from-center, `Space` lock-parent.

## 5. Region tools

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Frame creation (drag/preset/duplicate) | region-tools/create-frame, frames/frame-presets, frames/duplicate-frame-quick-add | `F` / `A` / preset / `+` button | [FN] |
| Frame from selection | frames/frame-from-selection | `Opt+Cmd+G` | [FN] |
| Section | region-tools/create-section, region-tools/use-section | `Shift S` | [FN] |
| Slice tool | region-tools/use-slice-tool | toolbar | [VO export-only] |
| Layout guide on frame | region-tools/add-layout-guide | Layout guide section `+` | [FN basic, DEF advanced] |
| Canvas guide (ruler-drag) | region-tools/add-canvas-guide | drag from ruler | [FN] |

## 6. Frame system / containment

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Enter frame | frames/enter-frame | double-click / `Enter` | [FN] |
| Exit frame | frames/exit-frame | `Shift Enter` / `Esc` | [FN] |
| Clip content toggle | frames/frame-clip-content | layout panel toggle | [FN] |
| Reparent via canvas drag | frames/reparent-via-canvas-drag | drag (50% overlap) | [FN — matches commit `4413ce0`/`74c4896`] |
| Reparent via Layers panel | frames/reparent-via-layer-panel | drag in panel | [FN — matches commit `fe7b4c2`] |
| Drop shape into frame on creation | frames/drop-shape-into-frame | tool drag inside frame | [FN] |
| Drop out of frame | frames/drop-out-of-frame | drag outside bounds | [FN] |
| Resize frame with children | frames/frame-resize-with-children | drag handle / W-H input | [FN] |
| Resize-to-fit | frames/resize-to-fit | `Opt+Shift+Cmd+R` | [FN] |
| Frame presets | frames/frame-presets | preset list | [FN] |
| Ungroup frame | frames/ungroup-frame | `Cmd Shift G` | [FN] |
| Frame children z-order | frames/frame-children-z-order | (rendering contract) | [FN] |
| Parent-bounds overlay | frames/parent-bounds-overlay | (visual feedback) | [FN — matches commit `20a05a4`] |
| Nested frame rendering | frames/nested-frame-rendering | (rendering contract) | [FN] |
| Frame vs Group concept | frames/frame-vs-group | (concept doc) | [FN — informs both group-* and frame-* implementations] |

## 7. Transform

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Move | transform/move-layer | drag / arrow keys | [FN] |
| Resize | transform/resize-layer | drag handles / W-H | [FN] |
| Rotate (panel input) | transform/rotate-layer | rotation field | [FN] |
| Rotate (canvas handle) | transform/rotate-via-canvas-handle | drag near corner | [FN] |
| Change rotation origin | transform/change-rotation-origin | `Opt R` + drag | [FN] |
| Scale tool | transform/scale-with-scale-tool | `K` | [FN] |
| Flip horizontal/vertical | transform/flip | toolbar / shortcut | [FN] |
| Nudge | transform/nudge-with-arrow-keys | arrow keys (+ Shift) | [FN] |
| Set nudge values | transform/set-nudge-values | preferences | [VO — preferences modal stub] |
| Lock aspect ratio | transform/lock-aspect-ratio | toggle / Shift drag | [FN] |
| Snap to objects / pixel grid | transform/snap-to-objects | (default-on) | [FN] |

## 8. Z-order / Layer ordering

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Bring to front | z-order/bring-to-front | `Opt+Cmd+]` | [FN] |
| Bring forward | z-order/bring-forward | `Cmd ]` | [FN] |
| Send backward | z-order/send-backward | `Cmd [` | [FN] |
| Send to back | z-order/send-to-back | `Opt+Cmd+[` | [FN] |
| Reorder via panel drag | layers/reorder-layer | drag panel rows | [FN] |

## 9. Layers (organization)

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Group | layers/group-selection | `Cmd G` | [FN] |
| Ungroup | layers/ungroup | `Cmd Shift G` | [FN] |
| Enter group | layers/enter-group | double-click / `Enter` | [FN] |
| Exit group | layers/exit-group | `Shift Enter` / `Esc` | [FN] |
| Rename layer (inline) | layers/rename-layer | double-click row name | [FN] |
| Bulk rename modal | layers/bulk-rename-modal | `Cmd R` | [FN — basic + DEF regex] |
| Lock / unlock layer | layers/lock-layer | `Cmd Shift L` / panel padlock | [FN] |
| Toggle layer visibility | layers/toggle-layer-visibility, properties/set-visibility | `Cmd Shift H` / panel eye | [FN] |
| View layer outlines | layers/view-layer-outlines | `Cmd Shift O` | [FN] |
| Delete layer (panel) | layers/delete-layer-from-panel | `Backspace` / right-click | [FN] |

## 10. Pages

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Create page | pages/create-page | pages selector `+` | [FN] |
| Switch page | pages/switch-page | click page in list | [FN] |
| Rename page | pages/rename-page | double-click | [FN] |
| Delete page | pages/delete-page | right-click → Delete | [FN] |
| Duplicate page | (referenced in ui-shell/page-context-menu) | right-click → Duplicate | [DEF] |
| Page context menu | ui-shell/page-context-menu | right-click | [FN core, VO some entries] |

## 11. Clipboard

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Copy | clipboard/copy | `Cmd C` | [FN] |
| Cut | clipboard/cut | `Cmd X` | [FN] |
| Paste (cursor-pos) | clipboard/paste | `Cmd V` | [FN] |
| Duplicate | clipboard/duplicate | `Cmd D` / Alt-drag | [FN] |
| Delete | clipboard/delete | `Backspace` / `Delete` | [FN] |
| Copy properties | fills/paste-properties (cross-cut) | `Opt+Cmd+C` | [FN] |
| Paste properties | fills/paste-properties | `Opt+Cmd+V` | [FN] |
| Copy as PNG / SVG / link | (cross-cuts copy + clipboard) | right-click → Copy as | [DEF] |

## 12. History

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Undo | history/undo | `Cmd Z` | [FN] |
| Redo | history/redo | `Cmd Shift Z` | [FN] |
| Version history | sharing/version-history | dropdown | [VO] |
| Viewer history (file analytics) | (see-viewer-history-for-your-files) | menu | [VO] |

## 13. Color (picker, models, libraries, history)

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Open color picker | color/open-color-picker | swatch click | [FN] |
| Set hex | color/set-color-hex | type | [FN] |
| Set RGB | color/set-color-rgb | type | [FN] |
| Set HSB / HSL | color/set-color-hsb | type | [FN] |
| Set CSS | color/set-color-css | type | [FN basic CSS] |
| Color wheel + hue slider | color/use-color-wheel | drag | [FN] |
| Set opacity | color/set-color-opacity | slider / input | [FN] |
| Eyedropper | color/use-eyedropper | `I` / picker icon | [FN canvas-only] |
| Recent colors | color/recent-colors-history | swatch click | [FN] |
| Document colors | color/document-colors | swatch click | [FN] |
| Save as color style | color/save-as-color-style | `+` in picker | [FN basic] |
| Apply color style | color/apply-color-style | swatch click in libraries tab | [FN] |
| Library colors browser | color/library-colors-browser | Libraries tab | [FN basic, VO multi-team libs] |
| View mixed-selection colors | color/view-mixed-selection-colors | Selection colors section | [FN] |

## 14. Fill

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Add fill | fills/add-fill | `+` | [FN] |
| Remove fill | fills/remove-fill | `-` / menu | [FN] |
| Reorder fill | fills/reorder-fill | drag handle | [FN] |
| Toggle fill visibility | fills/toggle-fill-visibility | eye icon | [FN] |
| Set fill opacity | fills/set-fill-opacity | input | [FN] |
| Set fill blend mode | fills/set-fill-blend-mode | dropdown | [FN] |
| Set solid fill | fills/set-solid-fill | picker | [FN] |
| Linear gradient | fills/set-linear-gradient-fill | picker | [FN] |
| Radial gradient | fills/set-radial-gradient-fill | picker | [FN] |
| Angular gradient | fills/set-angular-gradient-fill | picker | [FN] |
| Diamond gradient | fills/set-diamond-gradient-fill | picker | [FN] |
| Edit gradient stop | fills/edit-gradient-stop | drag / `+` / Delete | [FN] |
| Image fill | fills/set-image-fill | picker | [FN] |
| Image fill mode (Fill/Fit/Crop/Tile) | fills/set-image-fill-mode | dropdown | [FN] |
| Image tile scale | fills/set-image-tile-scale | slider | [FN] |
| Image adjustments (7 sliders) | fills/adjust-image-properties | sliders | [FN basic] |
| Replace image | fills/replace-image | drag-drop / picker | [FN] |
| Rotate image fill 90° | fills/rotate-image-fill | rotate button | [FN] |
| Crop image (Crop tool) | fills/crop-image | double-click on image / panel button | [FN] |
| Pattern fill | fills/set-pattern-fill | picker → Select source | [FN basic] |
| Paste properties | fills/paste-properties | `Opt+Cmd+V` | [FN] |

## 15. Stroke

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Set stroke | properties/set-stroke | Stroke section | [FN] |
| Add / remove / reorder / visibility | (covered in set-stroke and equivalent fills patterns) | panel | [FN] |
| Convert stroke to vector path | vector/convert-stroke-to-path | menu | [FN] |
| Variable width tool | vector/use-variable-width | vector edit secondary toolbar | [FN] |
| Stroke alignment / cap / join / dashed | (advanced controls in panel) | panel | [FN basic, DEF advanced] |

## 16. Effects

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Drop shadow | effects/add-drop-shadow | Effects `+` | [FN] |
| Inner shadow | effects/add-inner-shadow | Effects `+` | [FN] |
| Layer blur | effects/add-layer-blur | Effects `+` | [FN] |
| Background blur | effects/add-background-blur | Effects `+` | [FN] |
| Noise / texture / glass | effects/add-noise-texture-glass | Effects `+` | [DEF] |
| Manage effects (eye / drag / `…` / `-`) | effects/manage-effects | per-row | [FN] |

## 17. Corner radius

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Uniform corner radius | properties/set-corner-radius | input | [FN] |
| Independent corners | properties/set-corner-radius | toggle | [FN] |
| Corner smoothing (squircle) | properties/set-corner-smoothing | slider | [FN] |

## 18. Constraints

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Set constraints (Left/Right/Center/Scale) | properties/set-constraints | constraints picker | [FN] |
| Combine layout-guides + constraints | (combine-layout-guides-and-constraints) | (rendering) | [FN] |

## 19. Text

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Create text | text/create-text | `T` + click/drag | [FN] |
| Edit text | text/edit-text, text/double-click-to-edit-text | double-click / Enter | [FN] |
| Select text range | text/select-text-range | drag in text | [FN] |
| Select-all text | text/select-all-in-text | `Cmd A` in edit mode | [FN] |
| Caret nav | text/keyboard-caret-navigation | arrow keys | [FN] |
| Commit text | text/commit-text | Esc / outside-click | [FN] |
| Font family | text/select-font-family | typography section | [FN] |
| Font weight / style | text/set-font-weight-style | dropdown | [FN] |
| Font size | text/set-font-size | input | [FN] |
| Line height | text/set-line-height | input | [FN] |
| Letter spacing | text/set-letter-spacing | input | [FN] |
| Paragraph spacing | text/set-paragraph-spacing | type-settings | [FN] |
| Paragraph indentation | (in set-text-properties) | type-settings | [DEF] |
| Text alignment H / V | text/set-text-alignment | alignment row | [FN] |
| Text decoration | text/set-text-decoration | type-settings | [FN basic] |
| Text case | text/set-text-case | type-settings | [FN] |
| Text resizing mode | text/set-text-resizing-mode | Layout section | [FN] |
| Vertical trim | text/set-vertical-trim | type-settings | [DEF] |
| Truncate text | text/set-truncate-text | type-settings | [DEF] |
| Bullet / numbered lists | text/set-paragraph-style | type-settings | [DEF] |
| Insert link | text/insert-link-in-text | menu / shortcut | [DEF] |
| Insert emoji | text/insert-emoji | `:` + name | [DEF] |
| RTL text | text/use-rtl-text | type | [FN bidi] |
| CJK text | text/use-cjk-text | IME input | [FN passthrough] |
| Icon fonts | text/use-icon-fonts | font picker | [FN] |
| OpenType features | text/use-opentype-features | type-settings details | [DEF] |
| Variable fonts | text/use-variable-fonts | type-settings variable | [DEF] |
| Bulk edit text | text/bulk-edit-text | multi-select + type-settings | [FN] |
| Find & replace | find-replace/find-and-replace | `Cmd F` | [FN basic] |
| Apply text style | styles/create-text-style | style-picker | [DEF] |

## 20. Vector

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Pen tool | vector/use-pen-tool | `P` | [FN] |
| Pencil tool | vector/use-pencil-tool | toolbar | [FN] |
| Enter / exit vector edit | vector/enter-vector-edit-mode, vector/exit-vector-edit-mode | `Enter` / Esc | [FN] |
| Shape to vector edit | vector/shape-to-vector | `Enter` on shape | [FN] |
| Add / move / delete vector point | vector/add-vector-point, vector/move-vector-point, vector/delete-vector-point | various | [FN] |
| Toggle vector handle | vector/toggle-vector-handle | per-point | [FN] |
| Mirror handle modes | vector/edit-vector-mirror-handles | sidebar | [FN] |
| Close / open path | vector/close-open-vector-path | per-point | [FN] |
| Multi-point bbox | vector/multi-point-bounding-box | multi-select | [FN] |
| Bend tool | vector/use-bend-tool | secondary toolbar | [FN] |
| Paint tool | vector/use-paint-tool | `Shift B` in vector edit | [FN] |
| Cut tool | vector/use-cut-tool | `X` in vector edit | [FN] |
| Lasso select | vector/use-lasso-select | `Q` in vector edit | [FN] |
| Shape builder | vector/use-shape-builder | secondary toolbar | [FN] |
| Variable width | vector/use-variable-width | secondary toolbar | [FN basic] |
| Arc tool (ellipse handles) | vector/use-arc-tool | drag arc handles | [FN] |
| Convert stroke to path | vector/convert-stroke-to-path | menu | [FN] |
| Convert text to vector | vector/convert-text-to-vector | menu | [FN] |
| Flatten | vector/flatten-to-vector | `Opt+Shift+F` | [FN] |
| Simplify path | vector/simplify-path | menu | [FN basic] |
| Offset path | vector/offset-path | menu | [FN basic] |

## 21. Boolean operations

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Union | boolean/union | `Opt+Shift+U` | [FN] |
| Subtract | boolean/subtract | `Opt+Shift+S` | [FN] |
| Intersect | boolean/intersect | `Opt+Shift+I` | [FN] |
| Exclude | boolean/exclude | `Opt+Shift+E` | [FN] |
| Edit boolean group | boolean/edit-boolean-group | (children stay editable) | [FN] |

## 22. Image

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Place image bulk | image/place-image-bulk | `Shift+Cmd+K` | [FN] |
| Drag-drop image | image/drag-drop-image | OS drag-drop | [FN] |
| Image fill (full chain) | fills/* | (see Fill section) | [FN] |
| Crop image | fills/crop-image | double-click / panel | [FN] |

## 23. Mask

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Use as mask | (masks article) | sub-header Mask icon | [DEF] |

## 24. Auto layout

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Toggle auto layout | auto-layout/toggle-auto-layout | `Shift A` | [FN] |
| Set direction | auto-layout/set-direction | dir icons | [FN] |
| Set padding | auto-layout/set-padding | inputs | [FN] |
| Set gap | auto-layout/set-gap | input / Auto | [FN] |
| Set alignment 3×3 | auto-layout/set-alignment | cell click | [FN] |
| Set resizing (Hug/Fill/Fixed/Min/Max) | auto-layout/set-resizing | dropdowns / shortcuts | [FN] |
| Wrap | auto-layout/set-wrap | toggle | [FN] |
| Absolute position child | auto-layout/set-absolute-position | toggle | [FN] |
| Grid auto-layout properties | auto-layout/set-grid-properties | grid controls | [DEF — beta] |

## 25. Components

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Create component | components/create-component | `Opt+Cmd+K` | [FN] |
| Place instance | components/place-instance | drag from Assets | [FN basic] |
| Swap instance | components/swap-instance | dropdown | [FN] |
| Detach instance | components/detach-instance | `Opt+Cmd+B` | [FN] |
| Edit main component | components/edit-main-component | navigate | [FN] |
| Component properties (boolean/text/swap/variant) | components/component-properties | `+` in props | [FN basic] |
| Create variants | components/create-variants | combine-as-variants | [FN basic] |
| Slots | (use-slots-to-build-flexible-components-in-figma) | property type | [DEF] |

## 26. Variables

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Create variable | variables/create-variable | `+` in modal | [FN basic] |
| Apply variable to property | variables/apply-variable | apply-variable icon | [FN basic] |
| Variable modes | variables/variable-modes | mode dropdown | [FN basic] |
| Variable collections | variables/variable-collections | `+` collection | [FN basic] |
| Use variables in prototypes | (use-variables-in-prototypes) | prototype actions | [DEF] |
| Variable expressions | (use-expressions-in-prototypes) | action params | [DEF] |

## 27. Styles

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Create color style | color/save-as-color-style | picker `+` | [FN] |
| Apply color style | color/apply-color-style | libraries tab | [FN] |
| Create text style | styles/create-text-style | typography `+` | [FN basic] |
| Create effect style | styles/create-effect-style | effects `+` | [FN basic] |
| Create layout-grid style | styles/create-layout-grid-style | layout-guide `+` | [FN basic] |
| Manage / share styles | (manage-and-share-styles) | local-styles section | [DEF] |

## 28. Layout guides / Grids

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Add layout guide on frame | region-tools/add-layout-guide | layout-guide section `+` | [FN basic] |
| Add canvas guide | region-tools/add-canvas-guide | drag from ruler | [FN] |
| Combine guides + constraints | (combine-layout-guides-and-constraints) | (auto) | [FN] |

## 29. Prototyping

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Create connection | prototype/create-connection | drag from connector dot | [DEF] |
| Set trigger | prototype/set-trigger | dropdown | [DEF] |
| Set action | prototype/set-action | dropdown | [DEF] |
| Set animation | prototype/set-animation | params | [DEF] |
| Manage flows | prototype/manage-flows | flow-start `+` | [DEF] |
| Set overflow | prototype/set-overflow | dropdown | [DEF] |
| Play prototype | prototype/play-prototype | play triangle | [DEF] |
| Multiple actions / conditionals / expressions | (covered in set-action) | params | [DEF] |
| Smart animate | (smart-animate-layers-between-frames) | animation type | [DEF] |
| Easing / spring | (prototype-easing-and-spring-animations) | animation params | [DEF] |
| Overlay (open/swap/close) | (create-overlays-in-your-prototypes) | action types | [DEF] |
| Scroll position preserve | (preserve-scroll-position-in-prototypes) | overflow + property | [DEF] |
| Sections in prototyping | (use-sections-in-prototyping) | section as scope | [DEF] |
| Use animated GIFs / videos | (use-animated-gifs-in-prototypes / use-videos-in-prototypes) | image/video fills | [DEF] |
| Variables in prototypes | (use-variables-in-prototypes) | actions | [DEF] |
| Variable modes in prototypes | (variable-modes-in-prototypes) | actions | [DEF] |
| Accessible prototypes | (accessible-prototypes-in-figma) | settings | [DEF] |
| Mobile preview | (view-prototypes-on-a-mobile-device) | mobile mode | [DEF] |
| Offline present | (present-prototypes-offline) | menu | [DEF] |
| Device + bg settings | (set-prototype-device-and-background-settings) | prototype panel | [DEF] |
| View connections | (view-prototype-connections) | sidebar | [DEF] |
| Comments on prototypes | (comment-on-prototypes) | comment in play | [DEF] |

## 30. Sharing & Collaboration

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Share modal | ui-shell/share-button | header click | [VO] |
| Avatar stack / multiplayer follow | ui-shell/avatar-stack | click | [VO] |
| Cursor chat | ui-shell/cursor-chat | `/` | [VO] |
| Spotlight | (present-to-collaborators-using-spotlight) | menu | [VO] |
| Viewer history | (see-viewer-history-for-your-files) | analytics | [VO] |
| Version history | sharing/version-history | menu | [VO] |
| Set custom file thumbnail | (set-custom-thumbnails-for-files) | menu | [VO] |

## 31. Comments

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Add comment | comments/add-comment | `C` + click | [FN basic] |
| Manage thread | comments/manage-comment-thread | per-thread | [FN basic] |
| Mark unread / resolve | (in manage-comment-thread) | menu | [FN basic] |
| Email notifications | (manage-email-notifications-for-comments-on-files) | settings | [VO] |
| Annotation tool | (toolbar Annotation) | `Shift T` | [VO — full-seat] |
| Measurement tool | canvas-navigation/measure-distances | `Shift M` | [FN ephemeral, DEF persistent] |

## 32. Imports

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Import Sketch | imports/import-sketch | file browser | [VO] |
| Import file | (import-files-to-the-file-browser) | file browser | [VO] |
| Copy assets between tools | (copy-assets-between-design-tools) | menu | [VO] |
| UI kits | (start-designing-with-ui-kits, get-started-with-apples-ui-kit) | enabled libraries | [VO] |

## 33. Exports

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Export config | exports/export-config | Export section `+` | [FN config, VO trigger] |
| Export from Figma Design (full) | (export-from-figma-design) | Export button | [VO] |
| Export formats / settings | (export-formats-and-settings) | dropdown | [VO] |
| Optimize for handoff | (optimize-design-files-for-developer-handoff) | menu | [VO — Dev Mode] |

## 34. AI / Smart features

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Actions menu (Cmd K) | ui-shell/actions-menu | `Cmd K` | [VO stub] |
| AI tools | ai/use-ai-tools | actions menu / specific entries | [VO] |
| Make/edit image with AI | (in fills/set-image-fill) | picker | [VO] |
| Smart symbols (auto-replace) | text/insert-emoji | typing | [DEF] |
| Find similar designs | (in actions menu) | `Cmd K` | [VO] |
| Identify matching objects | (identify-matching-objects) | menu | [VO] |
| Check designs in Figma | (check-designs-in-figma) | menu | [VO] |

## 35. Find & Replace

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Find / replace text + layer names | find-replace/find-and-replace | `Cmd F` / sidebar icon | [FN basic] |

## 36. Misc canvas controls

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Set nudge values | transform/set-nudge-values | preferences | [VO] |
| Use Figma keyboard | (use-figma-products-with-a-keyboard) | (full sheet) | [reference only] |
| Set custom thumbnail | (set-custom-thumbnails-for-files) | menu | [VO] |

## 37. Libraries

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Publish library | libraries/publish-library | menu | [VO] |
| Enable library | libraries/enable-library | Assets tab modal | [VO] |
| Get / accept updates | libraries/get-library-updates | badge → modal | [VO] |
| Swap libraries | (swap-libraries) | modal | [VO] |
| Hide assets when publishing | (hide-styles-components-and-variables-when-publishing) | per-asset toggle | [VO] |
| Library descriptions | (add-descriptions-to-styles-components-and-variables) | per-asset | [VO] |

## 38. Branching

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Create branch | branching/create-branch | menu | [VO] |
| Share / review / merge / incomplete merges | (per articles) | menu | [VO] |

## 39. Cursor chat / Multiplayer

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Cursor chat | ui-shell/cursor-chat | `/` | [VO] |
| Spotlight | (present-to-collaborators-using-spotlight) | menu | [VO] |
| Multiplayer presence | ui-shell/avatar-stack | (passive) | [VO] |
| Multiplayer cursors | (in zoom-view-options) | toggle | [VO] |

## 40. View-only / Accessibility

| Feature | Spec | Triggers | Status |
|---|---|---|---|
| Ask to edit | (mentioned in `frames-in-figma-design`, `navigating-ui3`) | view-only toolbar | [VO — never entered] |
| Accessible prototypes | (accessible-prototypes-in-figma) | prototype settings | [DEF] |
| Keyboard support | (use-figma-products-with-a-keyboard) | (full sheet) | [FN core, DEF advanced] |

---

## Cross-section notes

- **`[FN]` count**: ~150 features across selection, shape creation, frames, transform, color/fill (full coverage), vector (full), boolean, basic auto-layout, basic components/variables/styles, text (broad coverage), comments (basic), prototype (specs only — `[DEF]`).
- **`[VO]` count**: ~30 features mostly in collaboration / libraries / branching / exports / AI surfaces.
- **`[DEF]` count**: ~40 features that are spec'd but slated as deferred (advanced text settings, prototyping advanced, slots, smart-animate, etc.).

For each `[VO]` feature, the click target should route through `ui-shell/unsupported-feature-toast.md` (not silent — surface a toast naming the feature). This is a robustness requirement: every clickable surface should respond.

---

## Coverage gaps vs. corpus

The 175 Figma Design articles cover all the above. Articles that are documented in this inventory but not represented as a per-feature spec because they are pure-concept / overview / reference (no actionable user trigger):

- `layers-101-get-started-with-layers`, `layers-101-explore-layer-types`, `layers-101-combine-layers` — concept only.
- `the-difference-between-frames-and-groups` — concept (covered as `frames/frame-vs-group.md`).
- `the-difference-between-variables-and-styles` — concept (text-only article).
- `the-difference-between-slots-instance-swaps-and-variants` — concept.
- `parent-child-and-sibling-relationships` — concept (cross-cuts every container feature).
- `vector-networks` — concept (cross-cuts vector edit features).
- `about-color-models` — concept (cross-cuts color/* specs).
- `guide-to-text-in-figma-design`, `guide-to-fills`, `guide-to-auto-layout`, `guide-to-prototyping-in-figma`, `guide-to-components-in-figma`, `guide-to-variables-in-figma`, `guide-to-libraries-in-figma`, `guide-to-comments-in-figma`, `guide-to-branching`, `guide-to-imports-in-figma-design` — umbrella / TOC articles (their content is split across the per-feature specs).
- `navigating-ui3`, `explore-design-files`, `access-design-tools-from-the-toolbar`, `view-layers-and-pages-in-the-left-sidebar`, `design-prototype-and-explore-layer-properties-in-the-right-sidebar` — UI3 chrome / orientation (covered in `helper/extracted/ui-schema/`).

These articles inform multiple per-feature specs. They do not need their own spec files.
