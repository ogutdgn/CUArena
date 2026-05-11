# Figma Mock Feature Behavior Review

This document describes the mock application's features from the point of view requested by product review: do not explain what an obvious button visually suggests. Instead, document the parts that are not obvious at first glance: when a control appears, what state it depends on, what it changes, how multi-selection behaves, and what hidden side effects matter for undo, logging, selection, tool mode, or page/frame context.

## Reading rule for this document

If a normal user can infer the basic action from the icon or label, this document skips that explanation. For example, a rotate icon does not need "this rotates the layer." The useful documentation is: it only appears after selection, can affect multiple selected layers, normalizes angles, keeps the layer center fixed, emits a rotation event, and participates in undo.

## Global state model

The mock is driven by a few user-visible state buckets:

- Active page: every selection, viewport, page background, and layer operation is scoped to the current page.
- Selection: right-sidebar layer controls appear only when the active page has selected layers. No selection shows page controls instead.
- Active tool: toolbar tools change how canvas pointer input is interpreted. Most creation tools automatically return to Move after creating an object.
- Edit mode: text editing, vector editing, and pen creation suppress normal selection handles or change keyboard behavior until the user exits the mode.
- Focus context: entering a frame, section, or group scopes hit-testing, select-all, and object creation to that container.
- Prototype tab: the right sidebar swaps from Design controls to Prototype controls. Frame tool presets are a stronger sidebar state and appear when the Frame tool is active.

Most real edits go through undoable operations. Selection, viewport, tool switches, focus context, and some UI-only states are tracked separately. Semantic logging records the user's meaningful action in addition to the final document state.

## Canvas and selection

### Selecting objects

Selection is page-specific. Selecting an object on one page does not carry to another page. A click selects one visible, unlocked layer; Shift-click adds or removes layers from the current selection. Clicking empty canvas clears the active page selection.

The non-obvious behavior is that selection controls the entire right sidebar. With no selection, the sidebar shows Page controls. With a selection, it switches to layer controls such as Position, Layout, Appearance, Fill, Stroke, Effects, and type-specific controls.

### Marquee selection

Dragging on empty canvas creates a selection box. The selected objects are chosen inside the current page or the current focused container. In a frame or group context, the marquee does not select siblings outside that context.

### Hover and selection outline

Hover outlines and selection outlines follow transformed geometry, including rotation and flip. During text edit, vector edit, pen creation, or prototype preview-related modes, normal resize/rotate handles may be suppressed so the edit mode can own the pointer interaction.

### Double-clicking containers

Double-clicking a frame, section, or group enters that container as a focused workspace. Once focused, object creation and hit-testing are scoped inside it. Escape exits the current focus context one level at a time; if there is no focus context, Escape clears selection and returns to Move.

## Toolbar tools

### Move tool

Move is the default canvas tool. It owns normal selection, dragging, resizing, rotate handles, alt-drag duplication, and marquee selection. The important hidden behavior is that many other tools return to Move automatically after creating an object, so the next click usually selects or moves instead of creating another object.

### Hand tool and temporary pan

The Hand tool pans the viewport. Holding Space temporarily enters pan behavior even if another tool is active. Releasing Space restores the previous tool state.

### Scale tool

Scale is separate from normal resize. It is activated from the Move tools menu or with `K`. Unlike regular resize, scaling is intended to scale child content and visual properties together, including nested layers, stroke weights, corner radii, and text sizing.

It still depends on selection. With no selected layer, scale handles have nothing to act on. With selected layers, dragging handles scales the selected bounds; Shift and Alt modify the resize behavior.

## Shape and object creation

### Rectangle, ellipse, polygon, star, frame, section, and slice creation

These tools share the same creation flow. After the tool is active, the user can click once to create a default-size object or drag to define its bounds. Shift-drag forces a square bounding box for tools that use the shared bounding-box creation flow.

After creation, the new object becomes selected automatically. This is important because the right sidebar immediately switches from page state to layer state, and type-specific controls may appear without any extra click. The active tool normally returns to Move after the object is created.

### Polygon creation and side count

Polygon starts with 3 sides. Creating a polygon automatically selects it, so the Appearance section exposes Count immediately. Count is shown only when the current selection is entirely polygons. If multiple polygons are selected and they have different side counts, the field enters a Mixed state.

Changing Count clamps the value to the supported range and applies the new side count to all selected polygons. The polygon keeps its position and size; only its generated vertex count changes. The action is undoable and emits a polygon-side semantic event.

### Star creation, point count, and ratio

Star works like polygon creation, but its type-specific state includes Count and Ratio. These controls appear only when the selection is entirely stars. Count changes the number of star points. Ratio changes the inner radius percentage, which alters how deep the star valleys are.

In multi-selection, matching values show normally; different values show Mixed. A committed value applies to all selected stars.

### Line and arrow creation

Line and arrow use endpoint geometry rather than a normal rectangle-like shape. The non-obvious behavior is that after creation the endpoint data is what matters for resizing, hit testing, and rendering. Later handle edits can move a line endpoint instead of resizing a box.

Arrow is a line-like layer with arrow cap data. The visible arrow head is part of the layer's geometry state, not a separate child object.

### Text creation

The Text tool has two creation modes. Clicking creates auto-width text at the click point. Dragging creates fixed-width text using the dragged rectangle. After creation, the new text layer is selected and the app enters text edit mode so typing edits the text content immediately.

The Text tool also returns to Move after creation. That means a second click after creating text will not create another text layer unless the user activates Text again.

### Pen and vector creation

The Pen tool enters a creation/editing mode rather than producing a complete object from a single drag. Clicking adds corner vertices. Click-drag adds a vertex with mirrored Bezier handles. While the path is being built, the app keeps a live vector preview and a pen-creation edit mode.

Enter or Escape can finish or abort the active pen path depending on current creation state. When a vector exists and is edited, selection handles behave differently because vertex handles need the pointer interaction.

### Pencil creation

Pencil records a freehand stroke and turns it into a vector layer. The created vector is selected automatically and the tool returns to Move. The hidden state is the temporary pencil preview: until pointer-up, the shape is not yet a normal editable layer.

### Image placement

Image placement is available through the image file picker shortcut. It creates image layers from chosen files and selects the new image layers after placement. Image layers support corner radius, fills/strokes/effects, and image fill data, but image import depends on browser file input rather than a normal canvas drag tool.

## Position and layout controls

### Position section visibility

Position controls appear only when at least one layer is selected and the right sidebar is in Design mode. They disappear when nothing is selected, when Prototype mode is active, or when the Frame tool is showing frame presets.

### X and Y fields

X and Y show the selected layer position in the active coordinate context. For nested layers, the value is interpreted through the layer's parent/frame coordinate logic rather than as a raw screen coordinate. Multi-selection shows a value only when all selected layers share the same value; otherwise it shows Mixed. Committing a value moves all selected layers.

### Rotation field and rotate button

Rotation appears in Position after selection. The numeric field normalizes committed values into the canonical degree range, so negative or very large values become the equivalent visible angle. Multi-selection with different rotations shows Mixed; committing a value makes every selected layer use that value.

The rotate button adds 90 degrees clockwise to each selected layer. It rotates each layer around its own center and does not move the layer's X/Y position. The action is undoable and logged as a rotation action.

### Flip horizontal and vertical

Flip controls appear in Position after selection. They work on all selected layers, not only one. The app mirrors by changing transform scale state, so the layer keeps its stored position and size while rendering mirrored around its own center.

Shortcut flip is also supported with Shift+H and Shift+V. Both panel and shortcut routes emit flip semantic events.

### Width, height, and aspect ratio lock

Layout appears after selection. Width and height values show Mixed when selected layers disagree. Committing W or H resizes every selected layer. Values are clamped to at least 1.

The aspect-ratio lock is UI state, not a layer property. When enabled, editing width also derives height from the original displayed ratio, and editing height derives width. Because the lock is shared UI state, it affects the next size edit until toggled off.

Panel resizing can also trigger frame-containment handling after the resize completes, so a layer that is resized into or out of a frame may be re-evaluated for nesting.

## Alignment

Alignment controls live inside the Position section, so they follow the same visibility rules as Position: they are visible only for a layer selection in Design mode. With two or more layers selected, alignment uses the selected bounds. With exactly one layer selected, alignment is enabled only if that layer sits inside a non-page container such as a frame or group; in that case the container bounds are the alignment target.

Disabled alignment buttons can be visually present but do not perform the operation until the required selection/container state exists.

Alignment mutates layer transforms, so it is undoable and logged as a layout operation.

## Appearance controls

### Opacity

Opacity appears for selected layers. Multi-selection shows Mixed when values differ. Committing opacity applies the value to all selected layers and clamps the user-facing percent range.

### Visibility

The eye control in Appearance toggles layer visibility for all selected layers. If every selected layer is visible, the next click hides them; otherwise it shows them. Hidden layers are skipped by normal hit testing, which means hiding a selected layer can make it harder to reselect from the canvas and may require the layers panel.

### Locking

Locking is exposed from the context menu rather than the main right-sidebar Appearance section. It requires a current selection. If every selected layer is locked, the context menu offers unlock behavior; otherwise it locks the selected layers. Locked layers are skipped by normal canvas hit testing, so the layers panel or undo may be needed to recover them easily.

### Corner radius

Corner radius is always visually allocated in the Appearance area, but it is enabled only for supported layer types. Rectangles and images support per-corner editing. Polygons and stars support uniform corner radius only. Other types keep the field disabled.

When per-corner mode is opened for rectangles or images, individual corner fields appear. Uniform edits can collapse or overwrite per-corner differences depending on the committed value.

### Polygon Count in Appearance

For polygon-only selection, Appearance includes a Count field. It is another surface for the same polygon sides state described above. It appears only when every selected layer is a polygon.

### Star Count and Ratio in Appearance

For star-only selection, Appearance includes Count and Ratio. These fields are hidden for mixed layer selections and for non-star selections.

## Fill controls

Fill appears only when the selected layer type has fills. It shows the fills of the first selected layer. Adding, removing, toggling, or editing a fill targets selected fill-capable layers through the property command layer, but the visible row list is based on the first selected layer's fill list.

Opening a fill swatch opens the color picker. Hex input edits color while preserving alpha. The opacity scrubber edits alpha. Fill visibility is separate from removing the fill; hiding a fill preserves its color and opacity.

The current implementation exposes solid fill editing through the picker. The data model can represent more paint kinds, but this UI path opens the picker only for solid fills.

## Stroke controls

Stroke appears only when the selected layer type supports strokes. Like Fill, the visible stroke rows come from the first selected layer. Stroke color can be edited by swatch or hex input, stroke alpha by opacity scrubber, and visibility by the row eye control.

Stroke weight appears only when at least one stroke exists. A single weight field is shown from the first stroke and committing it applies through the selected stroke-capable layers. Removing a stroke is different from hiding it; hiding preserves the stroke data.

## Effects controls

Effects appear for selected layers that support effects. Pressing plus adds a Drop shadow by default and immediately opens its detail popover. The user can switch that effect to Layer blur inside the popover.

Drop shadow exposes position, blur, spread, and color. Layer blur exposes radius. The popover is anchored outside the right panel and flips upward if it would overflow the viewport bottom. Effects can be hidden without being removed.

Switching an effect type is implemented as remove-and-add, so it behaves differently from editing a field in place. This matters for undo and for whether the detail popover remains open.

## Typography and text editing

Typography appears only when the first selected layer is text. It does not appear for mixed selections whose first layer is not text. The visible controls edit the selected text layer's font family, weight, size, and horizontal alignment.

Text edit mode is separate from text selection. Creating text or entering text edit mode opens the inline editor overlay. While editing, keyboard input goes to the text editor instead of global shortcuts. Committing text records text content changes and exits or updates edit state according to the editor flow.

The current text property controls apply to the selected text layer as a whole. Range-aware text styling is represented in the data model but is not the primary panel flow documented here.

## Frame, section, group, and nesting

### Frame tool presets

When the Frame tool is active, the right sidebar shows frame preset categories instead of the normal Design selection/page panels. Choosing a preset creates a frame of that size and selects it. This sidebar state is based on active tool, not current selection.

### Manual frame and section creation

Frame and Section can be created from the toolbar or shortcuts. They use the shared bounding-box creation flow and select the created container automatically. Once selected, they can be moved, resized, renamed, grouped, or entered as focus context.

### Focused frame workspace

Entering a frame makes it act like a scoped workspace. New shapes created while focused are placed inside that frame when their creation point resolves to the focused container. Select-all also becomes scoped to the focused container instead of the whole page.

### Drag-to-nest

Moving layers can reparent them into frames when the frame containment threshold is met. This is not visually obvious from the toolbar: a normal drag can become a hierarchy change if the moved layer overlaps a frame enough. The layer's parent changes, and subsequent X/Y values are interpreted in the new parent context.

### Layers panel drag and nesting

The layers panel supports reordering and reparenting. Dropping above or below changes z-order within a parent. Dropping inside a frame, section, or group moves the layer into that container. The command protects against cycles, so a parent cannot be moved inside its own descendant.

### Group and ungroup

Grouping requires selected layers with a common parent. Mixed-parent grouping is intentionally blocked. After grouping, the new group becomes the selection. Ungrouping selects the former children after moving them back to the parent.

## Layer ordering, copy, paste, and deletion

### Context menu state

The context menu is selection-aware. Copy, cut, duplicate, delete, layer ordering, group, flip, lock, and visibility actions are disabled when there is no selection. Paste is disabled until the internal clipboard has a layer payload. Rename requires exactly one selected layer. Ungroup requires exactly one selected group.

Disabled context-menu rows still exist visually and can emit no-op feedback, which is useful for evaluating unsupported or unavailable actions separately from missing UI.

### Z-order commands

Send forward, send backward, send to front, and send to back operate on the current selection. If selected layers have different parents, the operation is grouped by parent and applied within each parent separately.

### Copy, cut, paste, and duplicate

Copy stores a deep clone of the selected layer subtree, including nested children. Cut writes the same clipboard payload and deletes the selected layers. Paste creates fresh ids for all pasted layers and selects the pasted result.

Paste placement depends on context. It may preserve origin offset, offset by a small amount, or place into a frame depending on current state and source placement logic. Duplicate offsets the clone and selects the duplicated layers.

### Alt-drag duplicate

With the Move tool, Alt-drag duplicates the selection and drags the duplicate instead of the original. The new duplicated layers become selected. This can combine with frame containment, so an alt-drag duplicate can also become nested if dropped into a frame.

### Delete

Delete removes the selected layers and clears selection. In vector edit mode, Delete can remove a selected vector point instead of deleting the whole layer.

### Rename layer

Layer rename requires exactly one selected layer. It can be reached through the context menu or rename modal shortcut. The rename changes the layer's name property without affecting hierarchy, selection, geometry, or visual style.

## Pages and document controls

### Page list

Pages live in the left panel. Creating a page also switches the active page to the new page. Selection is page-specific, so switching page changes which selection and viewport are active.

### Page rename and delete

Page rename can be triggered from inline editing or context menu. Deleting a page is blocked when there is only one page left. If the active page is deleted, the app falls back to a neighboring page.

### Page background

When nothing is selected in Design mode, the right sidebar shows Page background controls. Background color, hex input, opacity, and hidden state are separate behaviors. Hiding the background does not destroy the stored color or alpha.

Dragging the page opacity scrubber is coalesced into one undo transaction. Color picker drags are also coalesced so one continuous color drag does not flood undo history.

### Document rename

The file/document name can be renamed from the left panel header. This is separate from page rename and layer rename.

## Prototype features

### Design and Prototype tabs

The right sidebar tab state is global UI state. Clicking Prototype or pressing Shift+E switches the sidebar from Design controls to Prototype controls. This does not change the selected layer, but it changes which controls are visible and which canvas overlays are relevant.

### Prototype preview

The Preview button toggles a prototype preview overlay. Opening and closing preview is UI state and is logged semantically. The preview starts from available prototype flow state and can also be toggled by keyboard shortcut.

### Prototype device settings

With no selection in Prototype mode, the panel shows prototype-level settings such as device choice. Device state belongs to the page's prototype settings, not to a layer.

### Frame prototype state

When a frame is selected in Prototype mode, the panel exposes frame-related prototype controls such as flow starting points and connections. Prototype behavior is frame-centric: destination targets are frames, and flow starts are associated with top-level frames.

### Prototype connections

Connections are created from a source layer/frame to a destination frame. The connection stores trigger, action, destination, animation, delay, and URL-like fields depending on action type. Updating the modal fields emits individual connection update events only for fields that actually changed.

Deleting a connection removes it from the active page's prototype connection list. Connection arrows are canvas overlays derived from prototype state and selected frame/layer context.

### Scroll position inside prototype

When an item inside a frame is selected in Prototype mode, the panel can expose scroll-position behavior for that layer. This state belongs to the selected layer and determines how it behaves relative to its parent frame during prototype playback.

## Vector editing

Vector edit mode is different from selecting a vector layer. In vector edit mode, vertices and handles become editable targets. A selected vector point can be deleted with Delete without deleting the whole layer.

Normal selection handles are suppressed or changed while vector editing is active, because pointer events are routed to vertex/handle manipulation. Exiting vector edit returns the layer to normal selection behavior.

## Color picker behavior

Color picker popovers are opened from page background, fill, stroke, effect color, and similar swatches. The swatch tells the user a color can be changed, but the non-obvious behavior is transaction coalescing and alpha preservation:

- Hex input edits RGB and preserves current alpha.
- Opacity controls edit alpha without replacing RGB.
- Continuous picker drags can be treated as one undo step.
- Invalid hex drafts are discarded and reset to the current color.

## Viewport and zoom

Zoom and pan are page-scoped viewport state, not document content. Zoom commands do not create undo entries. Zoom to fit uses page content bounds. Zoom to selection requires a current selection and does nothing when no selection exists.

The UI can be hidden with the keyboard shortcut for presentation-like canvas work. This hides panels and toolbar but does not modify the document.

## Unsupported or inert surfaces

Some visible UI surfaces intentionally do not perform a full feature. Inert clicks should be documented as such if they are part of a task surface:

- Some left rail surfaces are placeholders and emit unsupported/no-op feedback.
- Some advanced menu entries exist for parity but do not mutate the document.

The important review rule is to document these only when a normal user might expect them to work. If a disabled/inert surface is visually obvious as disabled, the useful note is what feedback or log event occurs when it is clicked, if any.

## Logging and verification relevance

For verifier work, every feature should be considered in two layers:

- Final document state: what changed in `outcome.document`, such as transform, fills, effects, text, prototype connections, page count, or hierarchy.
- Semantic stream: what meaningful action was taken, such as create polygon, set polygon sides, rotate layer, flip layer, create prototype connection, or switch page.

When documenting a feature, include both only when they are not obvious from UI. For example, "polygon Count changes side count" is obvious after using it; "it appears only for polygon-only selection and logs `set_polygon_sides` with before/after per layer" is the part worth preserving.
