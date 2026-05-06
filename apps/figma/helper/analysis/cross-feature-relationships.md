# Cross-Feature Relationships

_Behavioral relationships between Figma Design features — what depends on what, what cascades through what, what shares state with what. Use this when designing engine ops, the right-panel state matrix, or the action-logger taxonomy: "if I implement X, what else must I think about?" Pair with `dependency-clusters.md` (article-level graph) and `figma-design-deep-index.md` (article catalog)._

## Conventions

- "**A → B**" means A depends on B (B must work for A to work).
- "**A ↔ B**" means A and B share state (changing one affects the other).
- "**A ⊕ B**" means A and B are mutually exclusive in some context (only one applies at a time).
- "**A ⇒ B**" means A triggers / causes B as a side effect.

---

## 1. Top-level dependency chains

Major feature chains visible in the corpus and the per-feature specs:

- **Selection chain**: hit-testing → scope (frame containment) → click-select / shift-click / marquee → right-panel state matrix → action bar visibility → keyboard ops (delete, copy, group, etc.).
- **Frame containment chain**: frame creation → reparent (canvas drag / panel drag) → enter/exit scope → select-all-in-scope → clip-content rendering → child constraints.
- **Color chain**: color picker → color models (Hex/RGB/HSB/HSL/CSS) → eyedropper / wheel / opacity / blend-mode → save-as-style / save-as-variable → libraries → mixed-selection-colors.
- **Fill chain**: fill section → add/remove/reorder/visibility/opacity → fill type (solid / linear / radial / angular / diamond / image / pattern) → per-type config → blend mode → paste-properties.
- **Image fill chain**: place-image (upload/drag/paste) → fill mode (Fill/Fit/Crop/Tile) → image adjustments (7 sliders) → rotate-image / crop-image (sub-mode).
- **Vector chain**: shape primitive → enter vector edit (`Enter`) → secondary toolbar (Move/Pen/Bend/Lasso/Cut/Paint/Variable-width/Shape-builder) → multi-point bbox → exit edit → flatten / convert / boolean ops.
- **Auto layout chain**: toggle auto layout → direction → padding/gap/alignment → resizing modes (Hug/Fill/Fixed/Min/Max) → wrap (horizontal) / grid → absolute-position children.
- **Constraints chain** (non-auto-layout): parent frame resize → child constraint per axis (Left/Right/Center/Scale/Both).
- **Component chain**: create-component → place-instance → component-properties (boolean/text/swap/variant) → variants → slots → publish library → consumer file enables → get updates.
- **Variables chain**: create-variable → collection → modes → apply-variable to property → variable-modes-in-prototypes → expressions in prototypes.
- **Styles chain**: create-style (color/text/effect/layout-grid) → apply-style → publish → libraries.
- **Prototype chain**: connect → trigger → action → animation (with easing/spring) → flows → device → play.
- **Branching chain**: create-branch → share → request-review → review → merge / incomplete-merges.

---

## 2. Per-cluster relationships

### Selection
- **Selection → Hit testing**: pointer click resolves through z-order; respects scope (current container).
- **Selection ↔ Right-panel state matrix**: panel sections render based on selection's type / count / sameness (see `state-matrix.md`).
- **Selection ⇒ Sub-header buttons (Mask / Component / Boolean / `…`)**: only render when selection non-empty.
- **Cmd/Ctrl-click → Deep select**: bypass scope rules.
- **Marquee select → Scope**: scoped to current container, not page-global (matches commit `4c6eb77`).
- **Selection ⇒ Selection bounding box, W×H label, alignment row**.
- **Selection ⇒ Parent-bounds dashed overlay** when selected layer is inside a frame.

### Frames (containment)
- **Frame → Z-order containment**: children render in order within parent; z-order ops are scoped to parent.
- **Frame ↔ Reparent-via-drag**: 50% overlap threshold (mock-specific — matches commits `4413ce0` / `74c4896`).
- **Frame → Clip Content**: independent per-frame; affects rendering only.
- **Frame ⇒ Layout guides, auto-layout, constraints, prototyping** become available (per `parent-child-and-sibling-relationships`: these are frame-only properties).
- **Frame-from-selection (`Opt+Cmd+G`) ⇒ wraps selection**, preserving on-canvas positions.
- **Ungroup frame ⇒ promotes children** to outer parent; frame-only properties (clip, layout-guides, fills) discarded.
- **Frame preset application ⇒ resize children per their constraints** (or leave unchanged if no constraints).
- **Top-level frame label rendered on canvas** above frame; nested frames don't render label.
- **Resize-to-fit ⇒ shrinks/grows frame** to children's bbox.

### Color picker
- **Color picker ↔ Fill / Stroke / Effect color / Page-bg / Selection-colors / Gradient stop**: same picker UI, same behaviors, swatch source determines target.
- **Color picker → Color models**: same color value, different rendering of input fields (Hex/RGB/HSB/HSL/CSS).
- **Eyedropper → Sample any pixel**: applies to current target; Shift = apply variable/style binding; Cmd-Shift = create style/variable.
- **Picker library tab ⇒ Apply style / variable** (binding).
- **Save-as-style ⇒ creates local style + binds the target**.

### Fill
- **Fill section → Fill row**: each row independently configurable (color, opacity, blend mode, visibility).
- **Fill type ⊕ alternative type**: switching type discards type-specific config (per `set-solid-fill.md` etc.).
- **Image fill → Fill mode**: Fill / Fit / Crop / Tile, persisting under resize.
- **Image fill → Crop sub-mode**: blue handles + reposition / rotate / resize on the image inside the layer.
- **Pattern fill → Source layer**: live-updates on source edits.
- **Gradient fill → Stops**: stops list per fill, `+/−`, drag to reposition, flip, rotate.
- **Paste-properties ⇒ replaces fills** (and other props) on target.

### Vector edit
- **Vector edit ⊕ Normal selection**: vector edit replaces toolbar with secondary toolbar.
- **Vector edit ⇒ Multi-point bbox**: appears with 2+ points selected; bbox supports resize/rotate with modifiers.
- **Shape primitive → vector network**: `Enter` enters edit mode; first non-primitive edit transitions the layer to a custom vector.
- **Variable-width tool restrictions**: not on dynamic / dashed strokes; not on branching networks (split-vector first).
- **Bend → Mirror handles**: per-point mirror mode controls handle behavior.
- **Paint tool → Closed-region fill list**: per-region fill list independent from layer-level fill.
- **Cut tool**: click splits, drag divides into a new layer.

### Boolean operations
- **Boolean ops ↔ Selection (2+ supported layers)**: shape, vector, text — not section/frame.
- **Boolean op ⇒ Group**: result is a non-destructive group containing originals.
- **Group's fill/stroke/effects**: from topmost (union/intersect/exclude) or bottommost (subtract).
- **Edit boolean group**: child geometry editable; child fill/stroke/effects are NOT editable (these are group-level).
- **Flatten ⊕ Boolean**: flatten is destructive; boolean is non-destructive.

### Auto layout
- **Auto-layout child ⊕ Constraint-based layout**: once a frame has auto-layout, its children use auto-layout sizing (Hug/Fill/Fixed); constraints apply only on absolute-positioned children or non-auto-layout frame children.
- **Hug → Fixed cascade**: a Hug-mode parent becomes Fixed on an axis if any child uses Fill on that axis.
- **Wrap (horizontal) ⊕ Grid**: mutually exclusive direction options.
- **Min/Max dimensions** are additional and combine with the base mode.
- **Toggle auto-layout** on non-frame layers wraps them in a new auto-layout frame.

### Constraints
- **Constraints → Resize parent**: child responds per its constraint mode (Left / Right / Both / Center / Scale).
- **Constraints + lock-aspect-ratio**: lock applies symmetrically.
- **Constraints not applicable**: on auto-layout-frame children (those use auto-layout's resizing).

### Components
- **Main component ⇒ Instances**: edits to main propagate (unless overridden).
- **Variants** = component-set with per-axis property values; instance UI exposes axis dropdowns.
- **Slots ⊕ Instance swap**: slots provide standardized swap with placeholder; instance-swap is a per-property type.
- **Detach** ⇒ severs main link; overrides become absolute values.
- **Component-properties** (boolean/text/swap/variant) live on main; instances expose them as form controls.

### Variables
- **Variable → Collection → Mode**: variable lives in collection; collection has modes; instance frame's `applied_modes` selects one mode per collection.
- **Variable apply → Property binding**: any property whose type matches the variable type can be bound.
- **Variables in prototypes**: `set variable` action; expressions reference variables.
- **Variable modes in prototypes**: switching modes is a prototype action (per `variable-modes-in-prototypes`).

### Styles
- **Style → Property**: applying style replaces literal value with binding; layer follows style updates.
- **Style → Library**: styles publish like components/variables; consumers see updates.
- **Style detach**: revert to literal value.

### Effects
- **Effects array → Per-effect row** (eye / drag / `…` / `-`).
- **Effect type drop-shadow / inner-shadow / layer-blur / background-blur / noise / texture / glass**: each has its own param set.
- **Background blur** requires partial transparency to be visible.
- **Effects don't rotate** with the layer (canvas rotate handle).

### Stroke
- **Stroke fill ⊕ stroke styles** (dashed, etc.): combinable.
- **Stroke alignment** (Inside / Center / Outside): affects rendering and constraint baselines.
- **Convert stroke to path** ⇒ outlines stroke as vector.
- **Variable width tool requires non-dynamic, non-dashed, non-branching stroke**.

### Text
- **Text edit mode ⊕ Canvas selection**: Cmd A behaves differently per mode.
- **Typography section** lives in right sidebar only when text is selected.
- **Text styles** carry typography settings as a binding.
- **Convert text to vector** ⇒ glyphs become vector paths; loses editability.
- **Variable fonts → axes**: weight/width/slant/optical sliders.
- **OpenType features → font-specific**: each font exposes different feature tags.

### Image
- **Image as fill ⊕ Image as layer**: Figma stores images as fills; "image layer" = rectangle with image fill.
- **Drag-drop file ⇒ creates layer or replaces fill**, depending on drop target.
- **Replace image preserves fill mode + crop**.

### Prototype
- **Prototype tab ⊕ Design tab**: tab switch swaps panel body.
- **Connection → trigger + action + animation**: each connection has exactly one trigger; action(s) chain (multiple-actions).
- **Conditionals + expressions**: action gating; references variables.
- **Smart animate**: tweens shared layers between frames automatically.
- **Flow start point ⇒ play entry**.

### Comments
- **Comment ↔ Position (canvas) or layer**: pin can attach to a layer (follows it) or to canvas coords.
- **Notifications**: mentions trigger emails/in-app notifications.
- **Comment thread → Resolved/Unread state**.

### Libraries
- **File → Subscribed libraries**: enables their assets in pickers.
- **Library publish ⇒ subscribed files see Updates**.
- **Library swap**: swap a library reference with another (e.g. theme A → theme B).

### Branches
- **Branch ⇒ isolated edit space**.
- **Merge → handles incomplete merges**.
- **Branch updates ↔ Main file**: updates from main can merge into branch (and vice versa).

### Pages
- **Page ↔ Scene root**: each page has its own root scene tree.
- **Switch page → load that page's scene**.
- **Page bg color ↔ Page-section in right sidebar**.

### Clipboard
- **Copy → Paste / Paste-here / Paste-over**: paste uses cursor or active scope; paste-here uses a specific position.
- **Copy-properties → Paste-properties**: separate clipboard slot.
- **Copy as PNG / SVG / link**: copy variants emit different clipboard formats.
- **Cut = copy + delete**.
- **Duplicate (`Cmd D`) ⇒ in-place clone with Alt-drag offset**.

### History (undo/redo)
- **Undo coalesces continuous gestures**: typing burst, drag, color-picker scrubbing each = one entry.
- **Version history ⊕ undo**: undo is in-session; version history is persistent snapshots.
- **Cross-frame undo**: covers all changes regardless of which frame.

### Layer panel
- **Panel rows ↔ Scene graph**: 1:1 mapping with order (top of panel = top of stack within parent).
- **Panel drag ⇒ Reparent / Reorder**: cross-parent drag supported (per commit `fe7b4c2`).
- **Panel padlock / eye → lock / visibility ↔ canvas**: same flag, accessible from both.
- **Find-replace takes over panel**: `Esc` returns to layers.

### Effects-and-fills shared
- **Color picker** is shared between fill / stroke / effect color / page bg / selection colors / gradient stops.
- **Blend mode** is shared between layer-level (Appearance section) and per-fill/per-effect.

---

## 3. Mutually exclusive feature contexts

Pairs / groups where only one applies at once:

- **Auto-layout child ⊕ Constraint-based layout** — constraints don't apply to auto-layout children.
- **Vector edit mode ⊕ Normal selection** — secondary toolbar replaces main toolbar.
- **Component main edit ⊕ Instance edit (limited)** — instances only show overridable properties.
- **Mask child ⊕ Normal layer** — different rendering rules within a mask group.
- **Boolean group children's fill/stroke/effects ⊕ Independent edit** — only group-level matters.
- **Flatten ⊕ Boolean** — flatten destroys; boolean preserves children.
- **Frame preset ⊕ Custom W/H** — selecting a preset overrides custom values.
- **Hug ⊕ Fill-on-child** — Hug parent becomes Fixed on an axis if any child uses Fill on that axis.
- **Crop tool active ⊕ Normal canvas tool** — Crop's blue handles replace selection handles.
- **Text edit mode ⊕ Canvas selection** — Cmd A meanings differ; click semantics differ.
- **Editable view ⊕ View-only / Ask-to-edit** — toolbar variants differ; edit features hidden.
- **Dev Mode ⊕ Design tab** — entirely different right-panel content (Dev Mode out of mock scope).
- **Branch active ⊕ Main file** — edits go to branch only.
- **Library subscriber ⊕ Library publisher** — depends on whether file is the library source.

---

## 4. Cascading side effects

When feature A fires, list features B that automatically update:

- **Move layer ⇒ Smart-snap guides recompute, alignment-row updates, position section updates, parent-bounds overlay updates, reparent decisions.**
- **Resize layer ⇒ Children's constraints fire, auto-layout recomputes, corner-radius re-renders if independent corners.**
- **Rename layer ⇒ Layer panel row updates, find-replace index updates, asset name updates.**
- **Apply variable to property ⇒ All consumers of that variable mode update.**
- **Edit main component ⇒ All instances re-render.**
- **Publish library ⇒ Consumers see "X has updates" badge.**
- **Switch variable mode ⇒ All variable-bound properties resolved with that mode update.**
- **Change pattern source layer ⇒ All pattern-fill consumers re-render.**
- **Reorder layer ⇒ Z-order recomputes; canvas re-render; layer panel reorder.**
- **Change fill color ⇒ Selection-colors section may re-aggregate; document-colors list updates.**
- **Lock parent frame ⇒ All children effectively locked.**
- **Frame clip-content toggle ⇒ Children outside bounds shown / hidden.**
- **Flatten ⇒ Children destroyed; selection moves to result.**
- **Boolean op ⇒ Children grouped; group fill/stroke from top/bottom layer.**

---

## 5. State-sharing islands

Groups of features that share an underlying state model:

- **Color picker, Fill, Stroke, Effects color, Page bg, Text fill, Selection colors, Gradient stops** — all share the color picker overlay & color value type (with optional alpha + variable/style binding).
- **Position, Rotation, Flip, Constraints, Alignment** — read/write the same layer transform.
- **Auto-layout settings (direction, padding, gap, alignment, hug/fill/fixed, wrap, absolute-position)** — share the auto-layout config object on the parent.
- **Variable, Variable-mode, Collection, Library** — one entity graph with cross-references.
- **Style (color/text/effect/layout-grid), Library, Variable** — all are publishable assets.
- **Layer visibility (eye in panel ↔ eye in Appearance section ↔ shortcut `Cmd Shift H`)** — same flag.
- **Layer lock (panel padlock ↔ shortcut `Cmd Shift L` ↔ context menu)** — same flag.
- **Find-replace text content + layer names** — single panel takeover.

---

## 6. CUA / logger implications

What these relationships mean for the action logger:

- **Coalescing**: continuous gestures (typing burst, color scrub, drag) emit one event per gesture (commit-on-release / commit-on-blur). Each gesture is one undo entry.
- **Trajectory disambiguation**: distinct events fire per trigger so CUA can distinguish:
  - Move via drag vs. move via arrow keys (`move_layer { trigger: "drag" }` vs `nudge_layer`).
  - Rename via inline panel edit vs. via bulk-rename modal (`rename_layer { trigger: "double_click_panel" | "modal" }`).
  - Delete from canvas vs. from panel (single `delete` event with `trigger` field).
  - Drag-into-frame (reparent) vs. canvas drag with `Space` modifier (no reparent).
- **Cascading**: side-effect cascades typically silent; the semantic event is the user's intent, not the cascade. (E.g. `apply_variable` does not emit individual property-update events for cascaded re-renders.)
- **Mutually-exclusive contexts**: events should carry a `context` field so events with the same name in different modes (e.g. `select_all` in canvas vs in text-edit) are distinguishable.
- **Library / cross-file events**: scope the event to the file id; cross-file effects (library publish → consumer file updates) are typically separate events on the consumer file.

---

## 7. How to use this doc

- When implementing a new feature, find its cluster in §2 and read the relationships before writing the engine op.
- When adding a new section to the right panel, check §1 (state-sharing islands) for what other features may share state.
- When adding a new event to the action logger, check §6 for coalescing / disambiguation precedent.
- When debugging a feature interaction (e.g. "why does my reparent break this?"), the side-effect cascades in §4 often surface the missing handler.
- When introducing a new mode (e.g. Dev Mode integration), §3 lists the mutually-exclusive contexts to consider.
