# Feature Specs Index

**Purpose:** Top-level index of every per-feature spec under `extracted/features/`. Each file follows the standard template (Triggers, Preconditions, Inputs, Behavior, Outputs, UI feedback, Side effects, Related UI schema entries, Semantic event(s), Source articles, Notes / gaps).

This index reflects the **expanded spec set** — significantly broader than the original 65 specs. Specs cover every functional category in Figma Design (canvas, color, fills, frames, vector, text, components, variables, styles, prototyping, comments, sharing, libraries, etc.). Some specs document features that may not be implemented in the mock; they document the design surface as if everything will be implemented (per project goal of full documentation coverage).

For top-level analysis (article-level summaries, cross-feature relationships) see `helper/analysis/`.

---

## Categories (alphabetical)

### ai (1)
- [use-ai-tools](ai/use-ai-tools.md) — Figma AI tools (Make designs, Make image, Rename layers AI, etc.)

### alignment (9)
- [align-left](alignment/align-left.md) · [align-horizontal-centers](alignment/align-horizontal-centers.md) · [align-right](alignment/align-right.md) · [align-top](alignment/align-top.md) · [align-vertical-centers](alignment/align-vertical-centers.md) · [align-bottom](alignment/align-bottom.md)
- [distribute-horizontal-spacing](alignment/distribute-horizontal-spacing.md) · [distribute-vertical-spacing](alignment/distribute-vertical-spacing.md)
- [tidy-up](alignment/tidy-up.md)

### auto-layout (9)
- [toggle-auto-layout](auto-layout/toggle-auto-layout.md) · [set-direction](auto-layout/set-direction.md) · [set-padding](auto-layout/set-padding.md) · [set-gap](auto-layout/set-gap.md) · [set-alignment](auto-layout/set-alignment.md) · [set-resizing](auto-layout/set-resizing.md) · [set-wrap](auto-layout/set-wrap.md) · [set-absolute-position](auto-layout/set-absolute-position.md) · [set-grid-properties](auto-layout/set-grid-properties.md)

### boolean (5)
- [union](boolean/union.md) · [subtract](boolean/subtract.md) · [intersect](boolean/intersect.md) · [exclude](boolean/exclude.md) · [edit-boolean-group](boolean/edit-boolean-group.md)

### branching (1)
- [create-branch](branching/create-branch.md)

### canvas-navigation (7)
- [pan-canvas](canvas-navigation/pan-canvas.md) · [zoom-in-out](canvas-navigation/zoom-in-out.md) · [zoom-to-fit](canvas-navigation/zoom-to-fit.md) · [zoom-to-100](canvas-navigation/zoom-to-100.md) · [zoom-to-selection](canvas-navigation/zoom-to-selection.md)
- [measure-distances](canvas-navigation/measure-distances.md) · [change-canvas-bg](canvas-navigation/change-canvas-bg.md)

### clipboard (5)
- [copy](clipboard/copy.md) · [cut](clipboard/cut.md) · [paste](clipboard/paste.md) · [duplicate](clipboard/duplicate.md) · [delete](clipboard/delete.md)

### color (14)
- [open-color-picker](color/open-color-picker.md)
- [set-color-hex](color/set-color-hex.md) · [set-color-rgb](color/set-color-rgb.md) · [set-color-hsb](color/set-color-hsb.md) · [set-color-css](color/set-color-css.md)
- [use-color-wheel](color/use-color-wheel.md) · [set-color-opacity](color/set-color-opacity.md) · [use-eyedropper](color/use-eyedropper.md)
- [recent-colors-history](color/recent-colors-history.md) · [document-colors](color/document-colors.md)
- [save-as-color-style](color/save-as-color-style.md) · [apply-color-style](color/apply-color-style.md) · [library-colors-browser](color/library-colors-browser.md)
- [view-mixed-selection-colors](color/view-mixed-selection-colors.md)

### comments (2)
- [add-comment](comments/add-comment.md) · [manage-comment-thread](comments/manage-comment-thread.md)

### components (7)
- [create-component](components/create-component.md) · [place-instance](components/place-instance.md) · [swap-instance](components/swap-instance.md) · [detach-instance](components/detach-instance.md) · [edit-main-component](components/edit-main-component.md) · [component-properties](components/component-properties.md) · [create-variants](components/create-variants.md)

### effects (6)
- [add-drop-shadow](effects/add-drop-shadow.md) · [add-inner-shadow](effects/add-inner-shadow.md) · [add-layer-blur](effects/add-layer-blur.md) · [add-background-blur](effects/add-background-blur.md) · [add-noise-texture-glass](effects/add-noise-texture-glass.md) · [manage-effects](effects/manage-effects.md)

### exports (1)
- [export-config](exports/export-config.md)

### fills (21)
- [add-fill](fills/add-fill.md) · [remove-fill](fills/remove-fill.md) · [reorder-fill](fills/reorder-fill.md) · [toggle-fill-visibility](fills/toggle-fill-visibility.md) · [set-fill-opacity](fills/set-fill-opacity.md) · [set-fill-blend-mode](fills/set-fill-blend-mode.md)
- [set-solid-fill](fills/set-solid-fill.md)
- [set-linear-gradient-fill](fills/set-linear-gradient-fill.md) · [set-radial-gradient-fill](fills/set-radial-gradient-fill.md) · [set-angular-gradient-fill](fills/set-angular-gradient-fill.md) · [set-diamond-gradient-fill](fills/set-diamond-gradient-fill.md) · [edit-gradient-stop](fills/edit-gradient-stop.md)
- [set-image-fill](fills/set-image-fill.md) · [set-image-fill-mode](fills/set-image-fill-mode.md) · [set-image-tile-scale](fills/set-image-tile-scale.md) · [adjust-image-properties](fills/adjust-image-properties.md) · [replace-image](fills/replace-image.md) · [rotate-image-fill](fills/rotate-image-fill.md) · [crop-image](fills/crop-image.md)
- [set-pattern-fill](fills/set-pattern-fill.md)
- [paste-properties](fills/paste-properties.md)

### find-replace (1)
- [find-and-replace](find-replace/find-and-replace.md)

### frames (18)
- [enter-frame](frames/enter-frame.md) · [exit-frame](frames/exit-frame.md)
- [frame-from-selection](frames/frame-from-selection.md) · [frame-clip-content](frames/frame-clip-content.md) · [frame-presets](frames/frame-presets.md) · [duplicate-frame-quick-add](frames/duplicate-frame-quick-add.md) · [resize-to-fit](frames/resize-to-fit.md) · [ungroup-frame](frames/ungroup-frame.md) · [frame-resize-with-children](frames/frame-resize-with-children.md)
- [reparent-via-canvas-drag](frames/reparent-via-canvas-drag.md) · [reparent-via-layer-panel](frames/reparent-via-layer-panel.md) · [drop-shape-into-frame](frames/drop-shape-into-frame.md) · [drop-out-of-frame](frames/drop-out-of-frame.md)
- [select-frame-with-children](frames/select-frame-with-children.md) · [parent-bounds-overlay](frames/parent-bounds-overlay.md) · [nested-frame-rendering](frames/nested-frame-rendering.md) · [frame-children-z-order](frames/frame-children-z-order.md) · [frame-vs-group](frames/frame-vs-group.md)

### history (2)
- [undo](history/undo.md) · [redo](history/redo.md)

### image (2)
- [place-image-bulk](image/place-image-bulk.md) · [drag-drop-image](image/drag-drop-image.md)

### imports (1)
- [import-sketch](imports/import-sketch.md)

### layers (11)
- [group-selection](layers/group-selection.md) · [ungroup](layers/ungroup.md) · [enter-group](layers/enter-group.md) · [exit-group](layers/exit-group.md)
- [reorder-layer](layers/reorder-layer.md) · [rename-layer](layers/rename-layer.md) · [bulk-rename-modal](layers/bulk-rename-modal.md) · [delete-layer-from-panel](layers/delete-layer-from-panel.md)
- [lock-layer](layers/lock-layer.md) · [toggle-layer-visibility](layers/toggle-layer-visibility.md) · [view-layer-outlines](layers/view-layer-outlines.md)

### libraries (3)
- [publish-library](libraries/publish-library.md) · [enable-library](libraries/enable-library.md) · [get-library-updates](libraries/get-library-updates.md)

### pages (4)
- [create-page](pages/create-page.md) · [switch-page](pages/switch-page.md) · [rename-page](pages/rename-page.md) · [delete-page](pages/delete-page.md)

### properties (8)
- [set-fill](properties/set-fill.md) — stub redirecting to fills/* and color/*
- [set-stroke](properties/set-stroke.md)
- [set-effects](properties/set-effects.md) — see effects/* for per-effect specs
- [set-opacity](properties/set-opacity.md)
- [set-corner-radius](properties/set-corner-radius.md) · [set-corner-smoothing](properties/set-corner-smoothing.md)
- [set-constraints](properties/set-constraints.md)
- [set-visibility](properties/set-visibility.md) — see also layers/toggle-layer-visibility.md

### prototype (7)
- [create-connection](prototype/create-connection.md) · [set-trigger](prototype/set-trigger.md) · [set-action](prototype/set-action.md) · [set-animation](prototype/set-animation.md) · [manage-flows](prototype/manage-flows.md) · [set-overflow](prototype/set-overflow.md) · [play-prototype](prototype/play-prototype.md)

### region-tools (6)
- [create-frame](region-tools/create-frame.md) · [create-section](region-tools/create-section.md) · [use-section](region-tools/use-section.md) · [use-slice-tool](region-tools/use-slice-tool.md)
- [add-layout-guide](region-tools/add-layout-guide.md) · [add-canvas-guide](region-tools/add-canvas-guide.md)

### selection (6)
- [click-select](selection/click-select.md) · [shift-click-add-to-selection](selection/shift-click-add-to-selection.md) · [shift-click-remove-from-selection](selection/shift-click-remove-from-selection.md) · [drag-box-select](selection/drag-box-select.md) · [select-all](selection/select-all.md) · [deselect](selection/deselect.md)

### shape-creation (7)
- [create-rectangle](shape-creation/create-rectangle.md) · [create-line](shape-creation/create-line.md) · [create-arrow](shape-creation/create-arrow.md) · [create-ellipse](shape-creation/create-ellipse.md) · [create-polygon](shape-creation/create-polygon.md) · [create-star](shape-creation/create-star.md) · [place-image](shape-creation/place-image.md)

### sharing (1)
- [version-history](sharing/version-history.md)

### styles (3)
- [create-text-style](styles/create-text-style.md) · [create-effect-style](styles/create-effect-style.md) · [create-layout-grid-style](styles/create-layout-grid-style.md) · (color styles handled under color/save-as-color-style.md and color/apply-color-style.md)

### text (29)
- [create-text](text/create-text.md) · [edit-text](text/edit-text.md) · [double-click-to-edit-text](text/double-click-to-edit-text.md) · [select-text-range](text/select-text-range.md) · [select-all-in-text](text/select-all-in-text.md) · [keyboard-caret-navigation](text/keyboard-caret-navigation.md) · [commit-text](text/commit-text.md)
- [select-font-family](text/select-font-family.md) · [set-font-weight-style](text/set-font-weight-style.md) · [set-font-size](text/set-font-size.md)
- [set-line-height](text/set-line-height.md) · [set-letter-spacing](text/set-letter-spacing.md) · [set-paragraph-spacing](text/set-paragraph-spacing.md) · [set-paragraph-style](text/set-paragraph-style.md)
- [set-text-alignment](text/set-text-alignment.md) · [set-text-decoration](text/set-text-decoration.md) · [set-text-case](text/set-text-case.md)
- [set-text-resizing-mode](text/set-text-resizing-mode.md) · [set-vertical-trim](text/set-vertical-trim.md) · [set-truncate-text](text/set-truncate-text.md)
- [insert-emoji](text/insert-emoji.md) · [insert-link-in-text](text/insert-link-in-text.md)
- [use-rtl-text](text/use-rtl-text.md) · [use-cjk-text](text/use-cjk-text.md) · [use-icon-fonts](text/use-icon-fonts.md) · [use-opentype-features](text/use-opentype-features.md) · [use-variable-fonts](text/use-variable-fonts.md)
- [bulk-edit-text](text/bulk-edit-text.md)
- [set-text-properties](text/set-text-properties.md) — overview / index for typography section

### transform (11)
- [move-layer](transform/move-layer.md) · [resize-layer](transform/resize-layer.md) · [rotate-layer](transform/rotate-layer.md) · [scale-with-scale-tool](transform/scale-with-scale-tool.md) · [flip](transform/flip.md)
- [nudge-with-arrow-keys](transform/nudge-with-arrow-keys.md) · [set-nudge-values](transform/set-nudge-values.md)
- [lock-aspect-ratio](transform/lock-aspect-ratio.md)
- [snap-to-objects](transform/snap-to-objects.md)
- [rotate-via-canvas-handle](transform/rotate-via-canvas-handle.md) · [change-rotation-origin](transform/change-rotation-origin.md)

### ui-shell (13)
- [unsupported-feature-toast](ui-shell/unsupported-feature-toast.md) — fallback toast for not-yet-implemented buttons
- [share-button](ui-shell/share-button.md) · [present-button](ui-shell/present-button.md) · [export-button](ui-shell/export-button.md) · [actions-menu](ui-shell/actions-menu.md) · [avatar-stack](ui-shell/avatar-stack.md) · [zoom-percentage-display](ui-shell/zoom-percentage-display.md)
- [file-name-rename](ui-shell/file-name-rename.md) · [page-context-menu](ui-shell/page-context-menu.md) · [switch-file-assets-tab](ui-shell/switch-file-assets-tab.md) · [minimize-ui](ui-shell/minimize-ui.md) · [panel-scroll](ui-shell/panel-scroll.md) · [cursor-chat](ui-shell/cursor-chat.md)

### variables (4)
- [create-variable](variables/create-variable.md) · [apply-variable](variables/apply-variable.md) · [variable-modes](variables/variable-modes.md) · [variable-collections](variables/variable-collections.md)

### vector (24)
- [enter-vector-edit-mode](vector/enter-vector-edit-mode.md) · [exit-vector-edit-mode](vector/exit-vector-edit-mode.md) · [shape-to-vector](vector/shape-to-vector.md)
- [use-pen-tool](vector/use-pen-tool.md) · [use-pencil-tool](vector/use-pencil-tool.md) · [use-arc-tool](vector/use-arc-tool.md)
- [add-vector-point](vector/add-vector-point.md) · [move-vector-point](vector/move-vector-point.md) · [delete-vector-point](vector/delete-vector-point.md) · [toggle-vector-handle](vector/toggle-vector-handle.md) · [edit-vector-mirror-handles](vector/edit-vector-mirror-handles.md) · [close-open-vector-path](vector/close-open-vector-path.md) · [multi-point-bounding-box](vector/multi-point-bounding-box.md)
- [use-bend-tool](vector/use-bend-tool.md) · [use-paint-tool](vector/use-paint-tool.md) · [use-cut-tool](vector/use-cut-tool.md) · [use-lasso-select](vector/use-lasso-select.md) · [use-shape-builder](vector/use-shape-builder.md) · [use-variable-width](vector/use-variable-width.md)
- [convert-stroke-to-path](vector/convert-stroke-to-path.md) · [convert-text-to-vector](vector/convert-text-to-vector.md) · [flatten-to-vector](vector/flatten-to-vector.md) · [simplify-path](vector/simplify-path.md) · [offset-path](vector/offset-path.md)

### z-order (4)
- [bring-to-front](z-order/bring-to-front.md) · [bring-forward](z-order/bring-forward.md) · [send-backward](z-order/send-backward.md) · [send-to-back](z-order/send-to-back.md)

---

## Totals (per category)

| Category | Count |
|---|---|
| ai | 1 |
| alignment | 9 |
| auto-layout | 9 |
| boolean | 5 |
| branching | 1 |
| canvas-navigation | 7 |
| clipboard | 5 |
| color | 14 |
| comments | 2 |
| components | 7 |
| effects | 6 |
| exports | 1 |
| fills | 21 |
| find-replace | 1 |
| frames | 18 |
| history | 2 |
| image | 2 |
| imports | 1 |
| layers | 11 |
| libraries | 3 |
| pages | 4 |
| properties | 8 |
| prototype | 7 |
| region-tools | 6 |
| selection | 6 |
| shape-creation | 7 |
| sharing | 1 |
| styles | 3 |
| text | 29 |
| transform | 11 |
| ui-shell | 13 |
| variables | 4 |
| vector | 24 |
| z-order | 4 |
| **total** | **~250** |

---

## Cross-cutting concerns (carried over from earlier index)

1. **Undo granularity / coalescing** — typing bursts, color-picker scrubbing, drag operations.
2. **Multi-trigger semantic events** — most features emit one event name with a `trigger` field.
3. **Drag vs Alt-drag** — distinct events for CUA trajectory testing.
4. **Delete from canvas vs from panel** — single `delete` event with `trigger` field.
5. **Viewport state vs scene-graph state** — clear engine-model boundary.
6. **Coalesced undo during continuous input** — rotation drag, resize drag, color-picker scrubbing, typing.
7. **Visual-only click behavior** — handled via `ui-shell/unsupported-feature-toast.md`.
8. **Nested frame scope** — `select-all`, click hit-testing, paste-here all scope to active frame.
9. **Paste-properties cross-cuts fills/strokes/effects/typography** — see `fills/paste-properties.md`.
10. **Style / variable apply** — multiple categories share the picker UI.

---

## Relationship to upstream / downstream

- **Upstream**: each spec sources its behavior from the `helper/figma_docs/articles/Figma Design/<slug>/content.md` listed in its **Source articles** section. Where corpus is silent, **Notes / gaps** flags the gap explicitly.
- **Downstream**: implementer reads the spec for that feature, then realizes it in `test-app/`. The spec's **Semantic event(s)** drives the action logger taxonomy.

For top-level analysis (article-level summaries, dependency clusters, cross-feature relationships) see `helper/analysis/`.

For UI chrome / region descriptions (toolbar, sidebars, overlays) see `helper/extracted/ui-schema/`.
