# Feature Inventory

_Source: synthesized from 216 articles across 4 Figma products. See `analysis/_partial/` for raw per-domain extracts._

## Figma Design

### Tour the interface

- **Feature:** Move tools menu (Move / Hand / Scale)
  - Domain: Explore
  - UI Location: Toolbar (bottom of editor), leftmost group
  - Trigger: Click move-tool icon dropdown, or shortcuts `V` / `H` / `K`; spacebar = temporary Hand
  - Inputs: Pointer/keyboard
  - Outputs: Active tool changes; cursor changes
  - Related: Selection, panning
  - Article: Access design tools from the toolbar

- **Feature:** Region tools menu (Frame / Section / Slice)
  - Domain: Explore
  - UI Location: Toolbar (bottom), Region group
  - Trigger: Toolbar icon dropdown, or `F` / `Shift S` / Slice action
  - Inputs: Click-drag on canvas; or pick frame preset from properties panel
  - Outputs: New frame/section/slice node; presets exposed in right panel when frame tool is active
  - Article: Access design tools from the toolbar

- **Feature:** Shape tools menu (Rectangle, Line, Arrow, Ellipse, Polygon, Star, Image/video)
  - Domain: Explore
  - UI Location: Toolbar (bottom), Shape group; Rectangle is default
  - Trigger: Dropdown arrow, or `R` for rectangle, `O` for ellipse, `Shift Cmd K` for image
  - Inputs: Click-drag on canvas; Place Image opens file picker
  - Outputs: New shape layer; image becomes a fill on a shape
  - Article: Access design tools from the toolbar

- **Feature:** Creation tools menu (Pen / Pencil)
  - Domain: Explore
  - UI Location: Toolbar (bottom), Creation group
  - Trigger: Dropdown, `P` for pen
  - Inputs: Click points (Pen) or freehand drag (Pencil); Pencil applies smoothing
  - Outputs: Vector network layer
  - Article: Access design tools from the toolbar

- **Feature:** Text tool
  - Domain: Explore
  - UI Location: Toolbar (bottom)
  - Trigger: Click `T` icon, or shortcut `T`
  - Inputs: Click (auto-grow) or click-drag (fixed size) on canvas, then keyboard typing
  - Outputs: New text layer
  - Article: Access design tools from the toolbar

- **Feature:** Comment tools menu (Comment / Annotation / Measurement)
  - Domain: Explore
  - UI Location: Toolbar (bottom), Comments group; Annotation & Measurement are Full-seat only
  - Trigger: Dropdown
  - Inputs: Click on canvas to drop pin / annotation / measurement endpoints
  - Outputs: Comment thread, annotation marker, or measurement guideline
  - Article: Access design tools from the toolbar

- **Feature:** Actions menu (command palette + AI hub)
  - Domain: Explore / File utilities
  - UI Location: Toolbar (bottom), to the right of creation tools; opens floating overlay
  - Trigger: Toolbar icon, or `Cmd K` / `Ctrl K`
  - Inputs: Free-text search; click action; pick AI tool / plugin / widget / asset search
  - Outputs: Triggers a Figma command, AI flow, plugin run, or asset insert
  - Related: AI tools, plugins, widgets, find similar designs
  - Article: Use the actions menu in Figma Design

- **Feature:** Dev Mode toggle
  - Domain: Explore
  - UI Location: Toolbar, right end (mode switcher)
  - Trigger: Click toggle, or `Shift D`
  - Inputs: Click
  - Outputs: Switches editor into Dev Mode interface (different right panel)
  - Article: Access design tools from the toolbar / Navigating UI3

- **Feature:** Figma Draw entry
  - Domain: Explore
  - UI Location: Toolbar `Draw` button
  - Trigger: Click
  - Outputs: Activates Figma Draw illustration toolset within the editor
  - Article: Access design tools from the toolbar

- **Feature:** Find and replace
  - Domain: File utilities
  - UI Location: Left sidebar (search icon); will move to new left nav bar in UI3 rollout
  - Trigger: `Cmd F` / `Ctrl F`, or sidebar icon
  - Inputs: Query string, optional filter (text/frame/shape/widget/slice/other), scope (page/all pages); Replace mode adds replacement text
  - Outputs: Filtered list of matching layers; selection of one or many; bulk text replace
  - Notes: Multi-select via Cmd/Ctrl-click and Shift-click ranges; Replace All scopes to current page; Esc returns to Layers panel
  - Article: Find and replace in Figma

- **Feature:** Zoom controls + custom percentage entry
  - Domain: File utilities
  - UI Location: Top-right corner of right sidebar; current zoom is shown there; click to open Zoom/view options menu
  - Trigger: Click percentage; shortcuts `Shift +`, `Shift -`, `Shift 1` (fit), `Shift 2` (selection); pinch / Cmd+scroll
  - Outputs: Canvas viewport scale change; zoom-to-fit/-selection
  - Article: Adjust your zoom and view options

- **Feature:** Pixel preview (1x / 2x / Disabled)
  - Domain: File utilities
  - UI Location: Zoom/view options menu (right sidebar header)
  - Trigger: Menu select; `Ctrl P` (Mac) / `Ctrl Alt P` (Win)
  - Outputs: Canvas renders vectors as rasterized pixels at chosen density; toast confirms
  - Article: Adjust your zoom and view options

- **Feature:** Pixel grid + Snap to pixel grid
  - Domain: File utilities
  - UI Location: Zoom/view options menu
  - Trigger: Menu toggles; `Cmd '` and `Cmd Shift '`
  - Outputs: Visible pixel grid (only at >=400% zoom); placement/move snapping; frames/sections/components always snap regardless
  - Article: Adjust your zoom and view options

- **Feature:** Layout guides toggle
  - Domain: File utilities
  - UI Location: Zoom/view options menu
  - Trigger: Menu, `Ctrl G` (Mac) / `Ctrl Shift 4` (Win)
  - Outputs: Show/hide all layout guides in file
  - Article: Adjust your zoom and view options

- **Feature:** Multiplayer cursors toggle
  - Domain: File utilities
  - UI Location: Zoom/view options menu
  - Trigger: Menu, `Opt Cmd \\` / `Ctrl Alt \\`
  - Outputs: Show/hide collaborator cursors on canvas
  - Article: Adjust your zoom and view options

- **Feature:** Property labels toggle
  - Domain: File utilities
  - UI Location: Zoom/view options menu (next to 100% zoom in properties panel)
  - Trigger: Menu select
  - Outputs: Adds text labels to property-panel sections (renames to "Additional labels" once new nav bar ships)
  - Article: Adjust your zoom and view options / Navigating UI3

- **Feature:** Prototyping flows view (view-only users)
  - Domain: File utilities
  - UI Location: Zoom/view options menu (only appears for view-only access; editors switch tab instead)
  - Trigger: Menu toggle
  - Outputs: Renders prototype connection arrows on the canvas
  - Article: Adjust your zoom and view options

- **Feature:** Show outlines (x-ray view)
  - Domain: File utilities
  - UI Location: Zoom/view options menu > Outlines
  - Trigger: Menu, `Cmd Shift O` / `Ctrl Shift O`
  - Inputs: Sub-toggles `Include hidden layers`, `Include object bounds`
  - Outputs: Renders all layers as outlines for selecting hidden/clipped/behind layers
  - Article: View layer outlines in Figma Design

- **Feature:** Set custom thumbnail
  - Domain: File utilities
  - UI Location: Right-click context menu on a frame in canvas
  - Trigger: `Right-click frame > Set as thumbnail` (frames only); `Restore default thumbnail` to undo
  - Outputs: File card in browser uses chosen frame; custom-thumbnail icon appears next to that frame
  - Article: Set custom thumbnails for files

- **Feature:** Adjust nudge amount
  - Domain: File utilities
  - UI Location: Main menu > Preferences > Nudge amount...
  - Trigger: Menu open
  - Inputs: Small nudge (default 1) and Big nudge (default 10), in resolution-independent points
  - Outputs: Arrow-key step distances change for layer position
  - Article: Set small and big nudge values

- **Feature:** Add canvas/frame guides (rulers)
  - Domain: File utilities
  - UI Location: Rulers must first be enabled via Main menu > View > Rulers; then drag from horizontal/vertical ruler onto canvas
  - Trigger: Drag from ruler; `Opt`/`Alt`-drag from existing guide to clone; `Opt`/`Alt`-drag while top-level frame is selected = redline (distance) measurement
  - Outputs: Canvas-level or frame-level guide; ruler highlighted blue when frame selected; redline distances shown in pixels
  - Removal: Drag back to ruler / select + Delete / right-click > Remove guide
  - Article: Add guides to the canvas or frames

- **Feature:** Hide/Show UI (toggle whole chrome)
  - Domain: File utilities
  - UI Location: Actions menu, or shortcut
  - Trigger: `Cmd \\` (Mac) / `Ctrl \\` (Win); also Actions menu item
  - Outputs: Hides toolbar + both sidebars; toggle restores
  - Article: View layers and pages in the left sidebar

- **Feature:** Minimize UI (collapse panels only)
  - Domain: Explore
  - UI Location: Top of left navigation panel (Minimize UI button)
  - Trigger: Click button, or `Shift \\`
  - Outputs: Collapses left + right panels; if you select an object the right panel temporarily expands; with new nav bar rollout this also collapses the nav bar
  - Article: Navigating UI3 / View layers and pages in the left sidebar

- **Feature:** Background color of canvas (per page)
  - Domain: Explore
  - UI Location: Right properties panel > Page section (visible only when nothing is selected)
  - Trigger: Click color swatch; enter hex; opacity input; eye icon hides background
  - Outputs: Page background changes for everyone in file (defaults: light `#F5F5F5`, dark `#1E1E1E`); new pages inherit; not changeable in Dev Mode
  - Article: Change the background color of the canvas

- **Feature:** AI tools surface (First Draft, Find assets/designs, Replace content, Add interactions, Rename layers, Rewrite/translate/shorten text, Text suggestions, Make/edit images, Remove background, Boost resolution, Expand image, Isolate/erase objects, Vectorize images)
  - Domain: Explore (File utilities)
  - UI Location: All exposed via Actions menu (toolbar)
  - Trigger: Open Actions; pick AI tool
  - Inputs: Text prompts, image selections, layer selection
  - Outputs: New/edited layers; AI-generated images; rewritten text; auto-named layers; uses shared AI credit pool
  - Article: Use AI tools in Figma Design

- **Feature:** Search assets (Assets tab + AI search)
  - Domain: Explore
  - UI Location: Left sidebar Assets tab; search field; AI mode in Actions menu
  - Trigger: Switch to Assets tab (`Opt 2` / `Alt 2`); type query; or "Find more like" with selection
  - Outputs: List of matching components from current file + accessible libraries
  - Article: Use the actions menu in Figma Design / View layers and pages

- **Feature:** Keyboard box selection tool
  - Domain: File utilities
  - UI Location: Activated by shortcut; pink cursor renders on canvas
  - Trigger: `Opt Space` (Mac) / `Ctrl Space` (Win); `Esc` exits
  - Inputs: Arrow keys to move pink cursor; `Return` to select; `Tab` / `Shift Tab` to descend into children; `Cmd`/`Ctrl` + arrows to draw selection box; `Shift` to enlarge step
  - Outputs: Layer selection without mouse
  - Article: Use Figma products with a keyboard

- **Feature:** Adapt content for screen readers
  - Domain: File utilities
  - UI Location: Main menu > Preferences > Accessibility settings; or Actions menu "Screen reader"
  - Trigger: Toggle
  - Outputs: Canvas content adapted for assistive tech
  - Article: Use Figma products with a keyboard

- **Feature:** Keyboard shortcuts panel
  - Domain: File utilities
  - UI Location: Floating panel along bottom of screen; opened from Help and resources (bottom-right) > Keyboard shortcuts, Actions menu, or shortcut
  - Trigger: `Ctrl Shift ?` (Mac) / `Ctrl Shift ?` (Win)
  - Inputs: Tabs by category, plus Layout tab to select keyboard layout
  - Outputs: Live highlight of shortcuts as you press them
  - Article: Use Figma products with a keyboard

### Create designs

- **Feature:** Frame tool / create frame
  - Domain: Create and edit layers
  - UI Location: toolbar, right sidebar (presets), shortcut
  - Trigger: click toolbar / `F` / `A` shortcut / click on canvas / click-and-drag / `+` quick-add on hover / `⌥⌘G` (Mac) / `Ctrl+Alt+G` (Win) for frame-around-selection
  - Inputs: cursor position, drag rectangle, optional preset (Phone/Tablet/Desktop/Watch/Paper/etc.), selection
  - Outputs: new frame layer (top-level or nested), bolded name in Layers panel for top-level
  - Related: Group, Section, Auto layout, Constraints, Layout guides
  - Article: Frames in Figma Design

- **Feature:** Group / ungroup
  - Domain: Create and edit layers
  - UI Location: menu, right-click, shortcut
  - Trigger: `⌘G`/`Ctrl+G` to group, `⇧⌘G`/`⌘Delete` (or `Ctrl+Shift+G`/`Ctrl+Backspace`) to ungroup
  - Inputs: selection of 2+ layers
  - Outputs: group node in layer tree whose bounds equal child bounds
  - Related: Frame, Section
  - Article: The difference between frames and groups

- **Feature:** Section
  - Domain: Create and edit layers
  - UI Location: toolbar, shortcut, right-click ("Wrap in new section")
  - Trigger: `⇧S`, click+drag, right-click selection
  - Inputs: drag rectangle on canvas / selected objects
  - Outputs: top-level section container, optional Fill/Stroke, "Ready for dev" status label
  - Related: Frame, Mark as ready for dev (Dev Mode)
  - Article: Organize your canvas with sections

- **Feature:** Pencil tool (sketch)
  - Domain: Create and edit layers
  - UI Location: toolbar (Creation tools menu), shortcut
  - Trigger: `⇧P`, click-and-drag on canvas; `Shift` to constrain to straight line
  - Inputs: drag path, stroke color/weight/cap from right sidebar Stroke section
  - Outputs: vector layer with stroke (default round 3px black)
  - Related: Pen tool, Brush, Vector edit mode
  - Article: Sketch on the canvas with the pencil tool

- **Feature:** Rectangle tool
  - Domain: Create and edit layers
  - UI Location: toolbar (Shape tools menu), shortcut
  - Trigger: `R`, click-and-drag; `Shift` for square; `Option/Alt` to draw from center
  - Inputs: drag dimensions
  - Outputs: rectangle layer with 4 corner-radius handles
  - Related: Frame (visually similar), Corner radius
  - Article: Shape tools

- **Feature:** Line tool
  - Domain: Create and edit layers
  - UI Location: toolbar Shape menu, shortcut `L`
  - Trigger: `L`, click-and-drag
  - Inputs: start/end points
  - Outputs: line layer with stroke; can be dashed via Advanced stroke settings
  - Related: Arrow, Stroke properties
  - Article: Shape tools

- **Feature:** Arrow tool
  - Domain: Create and edit layers
  - UI Location: toolbar Shape menu, shortcut `⇧L`
  - Trigger: `⇧L`, click-and-drag
  - Inputs: start/end points; cap settings
  - Outputs: arrow line with end-point caps
  - Related: Line, Stroke caps
  - Article: Shape tools

- **Feature:** Ellipse tool
  - Domain: Create and edit layers
  - UI Location: toolbar Shape menu, shortcut `O`
  - Trigger: `O`, click-and-drag; `Shift` for circle
  - Inputs: drag dimensions
  - Outputs: ellipse layer; right-side handle exposes Arc tool controls
  - Related: Arc tool
  - Article: Shape tools

- **Feature:** Polygon tool
  - Domain: Create and edit layers
  - UI Location: toolbar Shape menu
  - Trigger: select Polygon, click-and-drag
  - Inputs: drag dimensions; Count field for sides
  - Outputs: polygon layer (default triangle); Edit object to add points
  - Related: Star, Edit object mode
  - Article: Shape tools

- **Feature:** Star tool
  - Domain: Create and edit layers
  - UI Location: toolbar Shape menu
  - Trigger: select Star, click-and-drag
  - Inputs: drag; on-canvas handles for Count, Ratio, Radius
  - Outputs: star layer (default 5-point)
  - Related: Polygon
  - Article: Shape tools

- **Feature:** Arc tool
  - Domain: Create and edit layers
  - UI Location: canvas (handles on selected ellipse)
  - Trigger: hover/drag the right-side handle of an ellipse
  - Inputs: drag Sweep / Start / Ratio handles
  - Outputs: arc, pie, ring, donut, semi-circle from an ellipse
  - Related: Ellipse
  - Article: Arc tool — create arcs, semi-circles, and rings

- **Feature:** Mask (Use as mask)
  - Domain: Create and edit layers
  - UI Location: right sidebar (More options), right-click, shortcut
  - Trigger: `⌃⌘M` (Mac) / `Ctrl+Alt+M` (Win); right sidebar "Use as mask"
  - Inputs: bottom layer in z-order acts as mask of siblings above
  - Outputs: mask group in layer tree (mask icon + upward arrow on masked layers); Alpha/Vector/Luminance type
  - Related: Clip content, Frame, Group
  - Article: Masks

- **Feature:** Multi-edit (bulk edit objects)
  - Domain: Work with layers
  - UI Location: top of right sidebar (Multi-edit text / Multi-edit variants), shortcut `Q` for variants, `Enter` for text
  - Trigger: select multiple layers across frames, then enable
  - Inputs: multi-selection
  - Outputs: edits propagate across selected layers / matching variants
  - Related: Matching objects, Variants
  - Article: Edit objects on the canvas in bulk

- **Feature:** Matching objects (identify/select)
  - Domain: Work with layers
  - UI Location: canvas, Prototype tab
  - Trigger: select object + hold `Shift` to highlight matches; or `⌥⌘A`/`Alt+Ctrl+A` to select matching layers
  - Inputs: layer name + parent name + hierarchy must match
  - Outputs: matching objects highlighted/selected in light blue
  - Related: Multi-edit, Smart animate (Prototype), State management (Prototype), Sections
  - Article: Identify matching objects

- **Feature:** Selection (single/multi/marquee)
  - Domain: Work with layers
  - UI Location: canvas, Layers panel, right-click (Select layer menu)
  - Trigger: click; double-click for nested; `Enter`=child, `⇧Enter`=parent, `Tab`=next sibling, `⇧Tab`=prev; marquee drag; `⌘`/`Ctrl`+click for deep select; `⌘A`/`Ctrl+A` select all; `⌘⇧A` invert
  - Inputs: cursor position, modifier keys
  - Outputs: selection bounding box; "Selection colors" appears in right sidebar for mixed selection
  - Related: Smart selection, Locked/hidden layers, Matching objects
  - Article: Select layers and objects

- **Feature:** Alignment (left/right/top/bottom/center horizontal/center vertical)
  - Domain: Work with layers
  - UI Location: top of right sidebar Design panel, shortcuts `Alt+W/A/S/D/V/H`
  - Trigger: click alignment icon; hold `Shift` to align each to its own parent frame
  - Inputs: 1+ selected layer
  - Outputs: layers re-positioned relative to parent or to each other
  - Related: Distribute, Tidy up, Auto layout alignment
  - Article: Adjust alignment, rotation, position, and dimensions

- **Feature:** Distribute (horizontal/vertical spacing)
  - Domain: Work with layers
  - UI Location: right sidebar
  - Trigger: click distribute icon
  - Inputs: 2+ selected layers
  - Outputs: equal spacing; outermost objects keep position
  - Related: Tidy up, Smart selection
  - Article: Adjust alignment, rotation, position, and dimensions

- **Feature:** Tidy up
  - Domain: Work with layers
  - UI Location: right sidebar (icon depends on 1D/2D selection)
  - Trigger: click Tidy up
  - Inputs: 2+ selected layers (1D or 2D)
  - Outputs: aligns + distributes into row/column/grid; mode-based "Space between"
  - Related: Smart selection, Distribute
  - Article: Adjust alignment, rotation, position, and dimensions

- **Feature:** Snap to (objects / pixel grid / geometry)
  - Domain: Work with layers
  - UI Location: Preferences menu, quick actions
  - Trigger: drag with snap on; hold `Control` to temporarily disable
  - Inputs: dragging layer/vector point
  - Outputs: red guide line on canvas; aligned position
  - Related: Layout guides, Pixel grid
  - Article: Adjust alignment, rotation, position, and dimensions

- **Feature:** Position (X/Y) and nudge
  - Domain: Work with layers
  - UI Location: Design panel right sidebar; arrow keys
  - Trigger: edit X/Y fields; arrow keys = small nudge (default 1); `Shift+arrow` = big nudge (default 10)
  - Inputs: numeric value or equation (+ - * / ^ () %)
  - Outputs: layer position changes; cursor "scrub" supported on icon labels
  - Related: Equations, Scrub fields, Lock aspect ratio
  - Article: Adjust alignment, rotation, position, and dimensions

- **Feature:** Dimensions (W/H) + Lock aspect ratio
  - Domain: Work with layers
  - UI Location: right sidebar Layout
  - Trigger: edit W/H; drag bounding-box edges/corners; toggle aspect ratio lock; `Shift`-drag temporarily locks
  - Inputs: numeric value or equation
  - Outputs: resized layer; locked W/H ratio when toggled
  - Related: Constraints, Scale tool
  - Article: Adjust alignment, rotation, position, and dimensions

- **Feature:** Rotation
  - Domain: Work with layers
  - UI Location: Design panel field; canvas (hover just outside corner)
  - Trigger: enter degrees in field; click+drag rotation cursor; `Shift` to snap to 15°; `Option/Alt + R` to reveal rotation origin target
  - Inputs: angle (-180° to 180°)
  - Outputs: layer rotates; CSS uses inverted angle
  - Related: Flip horizontal/vertical (`⇧H`/`⇧V`)
  - Article: Adjust alignment, rotation, position, and dimensions

- **Feature:** Layer order (z-index)
  - Domain: Work with layers
  - UI Location: Layers panel drag, right-click menu, shortcuts
  - Trigger: `⌘]` bring forward, `⌘⌥]` to front, `⌘[` send back, `⌘⌥[` to back
  - Inputs: selection
  - Outputs: layer reorders in panel + on canvas; reversed inside auto layout frames
  - Related: Layers panel, Auto layout
  - Article: Adjust alignment, rotation, position, and dimensions

- **Feature:** Copy / Paste / Duplicate
  - Domain: Work with layers
  - UI Location: shortcuts, right-click menu
  - Trigger: `⌘C`/`⌘V`; `⌘D` duplicate; `Option/Alt`-drag to duplicate; `⇧⌘R` paste-to-replace; `⇧⌘V` paste over selection; right-click "Paste here"
  - Inputs: clipboard, selection, cursor position
  - Outputs: pasted object placed by paste-placement rules (preserve x/y in destination frame, else center); clipboard supports objects, properties, PNG, code
  - Related: Multi-paste, Paste to clipped frames, Copy as PNG / Copy as code
  - Article: Copy and paste objects

- **Feature:** Copy/Paste properties
  - Domain: Work with layers
  - UI Location: right sidebar (click-to-highlight property), right-click Copy/Paste as
  - Trigger: select layer, click property to highlight, `⌘C`; for full properties `⌥⌘C`/`⌥⌘V`
  - Inputs: source property (fill/stroke/effect/text), target layer
  - Outputs: target adopts compatible properties
  - Related: Styles, Variables
  - Article: Copy and paste properties between layers

- **Feature:** Scale tool
  - Domain: Work with layers
  - UI Location: toolbar, shortcut `K`, right sidebar Scale panel
  - Trigger: press `K`, click-and-drag bounding box; or use multiplier / W-H fields; anchor box sets scale direction
  - Inputs: drag, multiplier (e.g. 2x), or new W/H
  - Outputs: proportionally resizes including blurs/strokes/font size; ignores constraints
  - Related: Resize (W/H), Lock aspect ratio
  - Article: Scale layers while maintaining proportions

- **Feature:** Measure distances
  - Domain: Work with layers
  - UI Location: canvas (modifier-key hover)
  - Trigger: select obj 1, hold `Option/Alt`, hover obj 2 (add `⌘`/`Ctrl` to measure to nested)
  - Inputs: 2 objects (or vector points in vector edit mode)
  - Outputs: red guide line + numeric H/V distances
  - Related: Vector edit mode, Snap to settings
  - Article: Measure distances between layers

- **Feature:** Lock / Unlock layer
  - Domain: Work with layers
  - UI Location: Layers panel padlock, right-click, shortcut
  - Trigger: `⇧⌘L` / `Ctrl+Shift+L`; click padlock; click-drag across multiple padlocks
  - Inputs: selection
  - Outputs: layer cannot be selected/moved on canvas; padlock shown next to layer; selectable only via Select layer menu / Layers panel
  - Related: Hide layer, Select layer menu
  - Article: Lock and unlock layers

- **Feature:** Toggle visibility (hide/show)
  - Domain: Work with layers
  - UI Location: Layers panel eye icon; right sidebar Appearance; shortcut
  - Trigger: `⌘⇧H` / `Ctrl+Shift+H`
  - Inputs: selection
  - Outputs: hidden layers grayed out in Layers panel; not visible/selectable on canvas
  - Related: Show outlines (`⌘⇧O`)
  - Article: Toggle visibility to hide layers

- **Feature:** Rename layers (single + bulk modal)
  - Domain: Work with layers
  - UI Location: right-click "Rename", shortcut `⌘R`/`Ctrl+R`
  - Trigger: open Rename modal
  - Inputs: Match field, Rename to field, current-name token, ascending/descending number tokens, regex
  - Outputs: layers renamed in bulk with preview
  - Related: Match (regex), AI rename layers
  - Article: Rename layers

- **Feature:** Smart selection
  - Domain: Work with layers
  - UI Location: canvas (pink handles)
  - Trigger: select 2+ equally-spaced overlapping objects (1D or 2D); pink handles appear automatically
  - Inputs: drag handles to adjust spacing; click rings to mark; mark+drag to reorder; `⌘D` duplicate; `Delete` to remove
  - Outputs: spacing/order updates; other layers reflow
  - Related: Tidy up, Distribute
  - Article: Arrange layers with smart selection

- **Feature:** Constraints (horizontal/vertical)
  - Domain: Work with layers
  - UI Location: right sidebar Position section, interactive diagram
  - Trigger: select child of frame, choose Left/Right/Center/Left+Right/Scale (H) and Top/Bottom/Center/Top+Bottom/Scale (V); `Shift`-click for two
  - Inputs: per-axis constraint
  - Outputs: defines child resize behavior when parent frame resizes; hold `⌘`/`Ctrl` to ignore on resize
  - Related: Layout guides (combined behavior), Auto layout (different model)
  - Article: Apply constraints to define how layers resize

- **Feature:** Layout guides (Uniform grid / Column / Row)
  - Domain: Work with layers
  - UI Location: right sidebar Layout guide section (only on selected frame)
  - Trigger: select frame, click "Add layout guide" (default uniform grid)
  - Inputs: type, color, opacity, count, size, type (Stretch / Left / Right / Center / Top / Bottom), width/height, offset, margin, gutter
  - Outputs: visual aid overlay on frame; togglable globally `⇧G`; can be saved as style; can be combined per-frame
  - Related: Constraints, Snap, Layout guide styles
  - Article: Create layout guides

- **Feature:** Pen tool (vector network)
  - Domain: Design with vector tools
  - UI Location: toolbar, shortcut `P`
  - Trigger: `P`, click to add point, click-drag for curve, click first point to close, `Esc` to leave open
  - Inputs: anchor positions, optional bezier handle drag
  - Outputs: vector network layer (multi-direction paths, branching allowed)
  - Related: Bend tool, Vector edit mode
  - Article: Vector networks

- **Feature:** Vector edit mode
  - Domain: Design with vector tools
  - UI Location: secondary toolbar (appears on enter), shortcut `Enter`
  - Trigger: select vector layer + `Enter`
  - Inputs: Move (`V`), Pen (`P`), Bend, Lasso (`Q`), Cut (`X`), Paint (`⇧B`), Variable width tools
  - Outputs: edits points/handles; multiple-point bounding box (Shift=proportional, Option=from center, Shift=15° rotation snap, Space=nudge)
  - Related: Pen, Shape builder, Caps/end points
  - Article: Edit vector layers

- **Feature:** Variable width tool (variable stroke width)
  - Domain: Design with vector tools
  - UI Location: vector edit mode secondary toolbar
  - Trigger: select tool, hover stroke for pink handle, click to add width point
  - Inputs: width point positions and widths
  - Outputs: stroke with varying widths along path
  - Related: Stroke weight, Width profiles
  - Article: Edit vector layers

- **Feature:** Cut tool (split / divide vector)
  - Domain: Design with vector tools
  - UI Location: vector edit mode secondary toolbar, shortcut `X`
  - Trigger: click point/path to split; click+drag across paths to divide into separate layer
  - Inputs: cut path
  - Outputs: split vector path or detached layer
  - Article: Edit vector layers

- **Feature:** Bend tool
  - Domain: Design with vector tools
  - UI Location: vector edit mode secondary toolbar
  - Trigger: click on point/path
  - Inputs: bezier handle drag; mirror mode (None/Angle/Angle+Length)
  - Outputs: curved path with bezier handles
  - Article: Edit vector layers

- **Feature:** Lasso tool
  - Domain: Design with vector tools
  - UI Location: vector edit mode secondary toolbar, shortcut `Q`
  - Trigger: drag around points/paths
  - Inputs: lasso shape
  - Outputs: multi-selected vector points
  - Article: Edit vector layers

- **Feature:** Paint tool (fill closed regions)
  - Domain: Design with vector tools
  - UI Location: vector edit mode secondary toolbar, shortcut `⇧B`
  - Trigger: hover region (diagonal-stripe preview), click to add/remove fill
  - Inputs: region under cursor
  - Outputs: per-region fill on vector network
  - Article: Edit vector layers

- **Feature:** Shape builder
  - Domain: Design with vector tools
  - UI Location: vector edit mode secondary toolbar
  - Trigger: select 2+ vector layers, enter vector mode, select Shape builder
  - Inputs: drag to merge regions; click to extract region; `Option/Alt`+click to subtract
  - Outputs: destructively merged/extracted/subtracted shape
  - Related: Boolean operations (non-destructive alternative)
  - Article: Create custom shapes with the shape builder tool

- **Feature:** Outline stroke
  - Domain: Design with vector tools
  - UI Location: right-click, shortcut `⌥⌘O` / `Ctrl+Alt+O`
  - Trigger: right-click "Outline stroke"
  - Inputs: layer with stroke
  - Outputs: stroke converted to vector path (destructive); stroke style color becomes fill
  - Related: Convert text to vector paths
  - Article: Convert strokes to vector paths

- **Feature:** Convert text to vector paths (Flatten / Outline stroke)
  - Domain: Design with vector tools
  - UI Location: right-click, shortcuts `⌥⇧F`/`Alt+Shift+F` (flatten) or `⌥⌘O`/`Ctrl+Alt+O` (outline stroke)
  - Trigger: right-click flatten or outline
  - Inputs: text layer
  - Outputs: destructive vector layer (flatten = merged single layer; outline stroke = per-glyph layers)
  - Article: Convert text to vector paths

- **Feature:** Offset vector
  - Domain: Design with vector tools
  - UI Location: vector tools menu
  - Trigger: select vector layer, choose Offset vector
  - Inputs: amount (positive=expand, negative=contract); join (square/round)
  - Outputs: destructively offset path
  - Article: Offset a vector path

- **Feature:** Simplify vector
  - Domain: Design with vector tools
  - UI Location: vector tools menu
  - Trigger: select layer, Simplify vector
  - Inputs: simplification slider; or Lasso + `Shift+Delete` (delete and heal) for manual
  - Outputs: fewer points; destructive
  - Article: Simplify a vector path

- **Feature:** Boolean operations (Union/Subtract/Intersect/Exclude)
  - Domain: Design with vector tools
  - UI Location: toolbar Boolean menu, shortcuts `⌥⇧U`/`S`/`I`/`E`
  - Trigger: select 2+ shapes, choose operation
  - Inputs: 2+ shape/vector/text layers (no sections/frames)
  - Outputs: non-destructive boolean group; can ungroup to revert; layer order determines fill source (top for Union/Intersect/Exclude, bottom for Subtract)
  - Related: Shape builder (destructive)
  - Article: Boolean operations

- **Feature:** Flatten layers
  - Domain: Design with vector tools
  - UI Location: right-click, shortcut `⌥⇧F`/`Alt+Shift+F`
  - Trigger: right-click "Flatten"
  - Inputs: selection
  - Outputs: single merged vector layer (destructive); container layers removed
  - Related: Boolean operations, Convert text to vector paths
  - Article: Flatten layers

- **Feature:** Text tool / create text layer
  - Domain: Text and typography
  - UI Location: toolbar, shortcut `T`
  - Trigger: `T` then click (Auto width) or click-drag (Fixed size)
  - Inputs: typing
  - Outputs: text layer; default Inter font; can wrap text on a vector path by hovering path
  - Related: Edit text content (`Enter`/double-click), Multi-edit text
  - Article: Guide to text in Figma Design

- **Feature:** Text properties (font, weight, size, line height, letter spacing, alignment)
  - Domain: Text and typography
  - UI Location: right sidebar Typography section + Type settings panel (Basics/Details/Variable tabs)
  - Trigger: select text/range, edit fields; many keyboard shortcuts (`⌥⌘<`/`>` weight, `⇧⌘<`/`>` size, `⌥<`/`>` letter spacing, `⌥⇧<`/`>` line height)
  - Inputs: numeric or selected values; px or %
  - Outputs: text restyled
  - Related: OpenType, Variable fonts, Text styles
  - Article: Explore text properties

- **Feature:** Add/install fonts (Google + Apple defaults; user-installed via desktop app or Figma font helper; org-shared upload)
  - Domain: Text and typography
  - UI Location: external setup; font picker in Typography section
  - Trigger: install OS font / install font helper; select in font picker
  - Inputs: .TTF / .OTF files
  - Outputs: font available in font picker
  - Related: Browse and apply fonts, Manage conflicting fonts
  - Article: Add a font to Figma

- **Feature:** Browse and apply fonts (font picker)
  - Domain: Text and typography
  - UI Location: Typography section font name dropdown
  - Trigger: click font name
  - Inputs: search field, filter (All/In this file/Popular/Used at org/Installed by you/Google/Variable)
  - Outputs: font applied to text/range
  - Article: Browse and apply fonts

- **Feature:** Text styles (create/apply/edit/detach)
  - Domain: Text and typography
  - UI Location: right sidebar Typography section style icon; Local styles section
  - Trigger: create from layer or new in Local styles; apply via style picker
  - Inputs: name, description, type properties (font/size/spacing/etc.; not color/alignment/resizing)
  - Outputs: reusable text style; can be published to library
  - Related: Color styles, Effect styles, Variables
  - Article: Create and apply text styles

- **Feature:** Text resizing (Auto width / Auto height / Fixed size)
  - Domain: Text and typography
  - UI Location: right sidebar Layout
  - Trigger: select text layer, choose mode
  - Inputs: mode + drag bounding box (manual drag forces Fixed size)
  - Outputs: how text wraps and bounding box behaves
  - Related: Truncate text + max lines
  - Article: Adjust text dimensions and resizing

- **Feature:** Text links (hyperlinks)
  - Domain: Text and typography
  - UI Location: Properties panel "Create link", shortcut `⇧⌘U`
  - Trigger: select text/range, click Create link or shortcut
  - Inputs: URL (paste twice to keep visible URL + link); paste-in-place via `⌘V`
  - Outputs: hyperlinked text; works in prototypes
  - Article: Add links to text

- **Feature:** Emoji and smart symbols
  - Domain: Text and typography
  - UI Location: in-text typing
  - Trigger: type `:` + name (e.g. `:heart`); OS emoji picker; smart symbol toggle in Preferences
  - Inputs: characters like `->`, `(c)`, `(tm)`
  - Outputs: emoji inserted; smart symbol auto-converts to `→`, `©`, `™`, curly quotes, etc.
  - Article: Add emojis and smart symbols to text

- **Feature:** Bulleted / Numbered lists
  - Domain: Text and typography
  - UI Location: Type details panel List style; in-text shortcuts
  - Trigger: type `-` or `*` + Space (bullet); `1.` or `1)` + Space (number); `⌘⇧8` (bullet) / `⌘⇧7` (number) on selection
  - Inputs: list items; up to 5 indent levels
  - Outputs: rendered list with indentation/list spacing settings
  - Article: Create bulleted and numbered lists

- **Feature:** Icon fonts
  - Domain: Text and typography
  - UI Location: font picker
  - Trigger: install icon font (e.g. Font Awesome) on OS
  - Inputs: glyph code in text layer
  - Outputs: icon glyph rendered as text
  - Article: Use icon fonts

- **Feature:** OpenType features (per-font letterforms, ligatures, alt characters, stylistic sets, fractions, slashed zero, etc.)
  - Domain: Text and typography
  - UI Location: Typography → Type settings (Details tab)
  - Trigger: select range, toggle features
  - Inputs: per-font feature availability
  - Outputs: glyph variations applied to text
  - Article: Use OpenType features

- **Feature:** Variable fonts (axes: weight/width/optical-size/slant/+custom)
  - Domain: Text and typography
  - UI Location: Type settings → Variable tab
  - Trigger: select variable font, adjust axis sliders
  - Inputs: per-axis numeric values
  - Outputs: dynamic font variation along axis
  - Article: Use variable fonts

- **Feature:** CJK text input + RTL/bidi text
  - Domain: Text and typography
  - UI Location: text layer input, Type settings text direction control
  - Trigger: type CJK characters with appropriate keyboard / OS IME; for RTL Figma auto-detects but allows override
  - Inputs: language scripts, font fallback (Noto)
  - Outputs: properly rendered CJK / RTL / bidi text
  - Article: Add text in Chinese, Japanese, and Korean; Add right-to-left text

- **Feature:** Fills (Solid / Gradient / Pattern / Image / Video)
  - Domain: Color, gradients, and images
  - UI Location: right sidebar Fill section + color picker
  - Trigger: click `+` to add fill; click swatch to open color picker
  - Inputs: fill type, color, opacity, blend mode
  - Outputs: layer fill (multiple supported); ordered list with drag handle; visibility toggle
  - Related: Stroke, Color picker, Blend modes
  - Article: Guide to fills

- **Feature:** Color picker
  - Domain: Color, gradients, and images
  - UI Location: opened from any swatch (Fill, Stroke, Effect, Selection colors)
  - Trigger: click swatch
  - Inputs: HSV palette, hue slider, opacity slider, color model dropdown (Hex/RGB/CSS/HSL/HSB), eyedropper, library tab
  - Outputs: applied color; can save as style/variable; supports WCAG contrast checker (AA/AAA, with auto-correct suggestion)
  - Related: Eyedropper, Color models, Color styles, Variables
  - Article: Update fills using the color picker

- **Feature:** Gradients (Linear / Radial / Angular / Diamond)
  - Domain: Color, gradients, and images
  - UI Location: color picker → Gradient
  - Trigger: select gradient type, drag color stops
  - Inputs: stops (add by clicking slider; min 2), per-stop variable, flip, rotate
  - Outputs: gradient fill or stroke
  - Article: Use gradients as a fill or stroke

- **Feature:** Pattern fill (canvas-source)
  - Domain: Color, gradients, and images
  - UI Location: color picker → Pattern
  - Trigger: select Pattern, "Select source" → click another canvas object
  - Inputs: source object, tile type, scale, spacing, alignment, opacity
  - Outputs: dynamic pattern fill (updates when source updates)
  - Article: Use patterns as a fill or stroke

- **Feature:** Blend modes (per layer / per fill / per effect)
  - Domain: Color, gradients, and images
  - UI Location: right sidebar Appearance "Apply blend mode"; color picker; effect settings
  - Trigger: click blend mode menu, hover to preview
  - Inputs: mode (Pass through default; Normal, Multiply, etc.)
  - Outputs: visual blend; "Pass through" lets child blend modes affect content beneath parent
  - Article: Apply blend modes to layers, fills, and effects

- **Feature:** Add image / video (Place image)
  - Domain: Color, gradients, and images
  - UI Location: shape tools menu, shortcut `⇧⌘K`/`Ctrl+Shift+K`; color picker; drag-drop from OS; copy-paste from clipboard
  - Trigger: select files; click on canvas to place each (or "Place all"); or drop onto layer fill swatch to replace
  - Inputs: JPG/PNG/HEIC/WebP/GIF/TIFF (Safari); MP4/MOV/WebM (paid); SVG converts to vector
  - Outputs: image/video as fill on rectangle layer or replace existing fill; auto-scaled to ≤4096px longest dim
  - Related: Image properties, Crop image, Replace fill
  - Article: Add images and videos to designs

- **Feature:** Image properties (Fill mode, rotation, adjustments)
  - Domain: Color, gradients, and images
  - UI Location: color picker (image fill)
  - Trigger: open color picker on image fill
  - Inputs: Fill mode (Fill/Fit/Crop/Tile); Rotate 90°; sliders for Exposure/Contrast/Saturation/Temperature/Tint/Highlights/Shadows
  - Outputs: image rendering changes (non-destructive)
  - Article: Adjust the properties of an image

- **Feature:** Crop image
  - Domain: Color, gradients, and images
  - UI Location: right sidebar Image "Crop image"; double-click image; Fill mode → Crop
  - Trigger: enter crop mode, drag handles, set aspect ratio, "Resize to fit"
  - Inputs: drag bounds, slider, aspect ratio picker; `Option/Alt` for opposite-side; `Control/Fn` for free aspect
  - Outputs: non-destructive crop; supports reposition/rotate/resize within crop
  - Article: Crop an image

- **Feature:** Eyedropper (color sampling)
  - Domain: Color, gradients, and images
  - UI Location: color picker icon, shortcuts `I` (Win/Mac) / `⌃C` (Mac)
  - Trigger: toggle eyedropper, hover to preview color value, click to apply
  - Inputs: any pixel on canvas; on macOS desktop app, anywhere on screen
  - Outputs: applied color (raw, style, or variable)
  - Article: Sample colors with the eyedropper tool

- **Feature:** Selection colors (mixed-selection editor)
  - Domain: Color, gradients, and images
  - UI Location: right sidebar Selection colors section (only visible for mixed selection)
  - Trigger: select multi-fill objects
  - Inputs: per-fill swatch, opacity, style/variable detach, target icon to select all using a color
  - Outputs: bulk color edits across selection
  - Article: View and adjust colors in a mixed selection

- **Feature:** Color models (Hex / RGB / CSS / HSL / HSB)
  - Domain: Color, gradients, and images
  - UI Location: color picker dropdown
  - Trigger: click color model dropdown
  - Inputs: notation switch (Hex default; supports `#RRGGBBAA`)
  - Outputs: color displayed in chosen notation; doesn't change rendering
  - Related: Color profiles (sRGB/Display P3)
  - Article: About color models

- **Feature:** Stroke (apply + properties)
  - Domain: Additional properties
  - UI Location: right sidebar Stroke section
  - Trigger: click `+` Add stroke
  - Inputs: stroke fill (any fill type), position (Inside/Outside/Center), weight, width profile, individual sides (All/Top/Bottom/Left/Right/Custom), end-point caps, dash/gap, miter limit
  - Outputs: stroke rendered around layer/path
  - Related: Outline stroke, Variable width
  - Article: Apply and adjust stroke properties

- **Feature:** Effects (Glass / Drop shadow / Inner shadow / Layer blur / Background blur / Noise / Texture)
  - Domain: Additional properties
  - UI Location: right sidebar Effects section
  - Trigger: click `+` to add effect, choose type, configure
  - Inputs: per-effect parameters (e.g. drop shadow: x/y/blur/spread/color; glass: light angle/intensity/refraction/depth/dispersion/frost/splay)
  - Outputs: effect applied to layer (max 8 drop, 8 inner, 1 layer blur, 2 noise, 1 texture, 1 background blur, 1 glass per layer)
  - Article: Apply effects to layers

- **Feature:** Corner radius + Corner smoothing
  - Domain: Additional properties
  - UI Location: right sidebar Corner radius field; canvas corner handles; Independent corners modal (rectangles/frames)
  - Trigger: edit field; drag corner handles; arrow keys (small/big nudge)
  - Inputs: pixel value (or per-corner); smoothing % (squircle)
  - Outputs: rounded corners; per-vector-point radius in vector edit mode
  - Article: Adjust corner radius and smoothing

- **Feature:** Auto layout (toggle on/off + Suggest)
  - Domain: Use auto layout
  - UI Location: right sidebar Auto layout section, shortcut `⇧A`; right-click "Add auto layout"; Suggest = `⌃⇧A` (Mac) / `⌃Alt⇧A` (Win)
  - Trigger: select frame/object
  - Inputs: 1+ layers (wrapped into auto-layout frame if needed)
  - Outputs: auto layout frame with chosen flow; Suggest auto layout adds nested frames automatically (blue dot in Layers panel)
  - Related: Vertical/Horizontal/Grid flows, Resizing
  - Article: Toggle on auto layout in designs

- **Feature:** Auto layout — vertical/horizontal flow
  - Domain: Use auto layout
  - UI Location: right sidebar Auto layout
  - Trigger: select flow icon
  - Inputs: padding (uniform / vertical+horizontal / per-side), gap between items (number or Auto), alignment box (9 positions or 3 if gap=Auto), wrap (horizontal only), per-axis resizing (Hug / Fill / Fixed), min/max constraints
  - Outputs: dynamic layout that flows on x or y; alignment hotkeys `W/A/S/D` or arrow keys; `X` toggles gap Auto
  - Article: Use the horizontal and vertical flows in auto layout

- **Feature:** Auto layout — grid flow (beta)
  - Domain: Use auto layout
  - UI Location: right sidebar grid picker
  - Trigger: choose Grid flow
  - Inputs: number of columns/rows; per-track sizing (Fixed/Hug/Fill); cell span; reorder cells; resize tracks via blue-dot handles
  - Outputs: 2-D grid layout (galleries, dashboards, tables)
  - Related: Layout guides (different feature)
  - Article: Use the grid auto layout flow

- **Feature:** Multi-dimensional auto layout (nested flows)
  - Domain: Use auto layout
  - UI Location: implicit (nest auto layout frames inside each other)
  - Trigger: nest frames with different flow directions
  - Inputs: per-frame flow + padding + gap
  - Outputs: complex responsive layouts (e.g. social feed: vertical author > horizontal profile > vertical posts > vertical feed)
  - Article: Combine vertical, horizontal, and grid auto layout flows

### Build design systems

- **Feature:** Create local style (paint / text / effect / layout guide)
  - Domain: Styles
  - UI Location: right sidebar > Local styles section, or via per-property style picker
  - Trigger: click "+" next to Local styles, or "+" in style picker for selected property
  - Inputs: style type (Text/Color/Effect/Layout guide), name, description, property values
  - Outputs: new style entry in Local styles list; style picker now offers it; objects can bind to it
  - Related: Apply style, Edit style, Publish library
  - Article: Create color, text, effect, and layout guide styles

- **Feature:** Create style from existing object
  - Domain: Styles
  - UI Location: right sidebar > property section (Fill/Stroke/Effects/Text/Layout guides)
  - Trigger: click "+" next to property's style picker on a selected object
  - Inputs: object selection, name, description; "Show more options" exposes editable properties
  - Outputs: new style created and immediately bound to the source object's property
  - Related: Eyedropper (UI3) creates style from sampled color
  - Article: Create color, text, effect, and layout guide styles

- **Feature:** Apply style to selection
  - Domain: Styles
  - UI Location: right sidebar > property section > Apply styles icon (style picker)
  - Trigger: click style swatch in picker; or eyedropper sample
  - Inputs: selected layer(s), chosen style (local or library), list/grid view toggle
  - Outputs: property bound to style; round swatch indicator next to property
  - Related: Apply variable, Color picker, Switch styles, Detach style
  - Article: Apply styles to layers and objects

- **Feature:** Detach style from object
  - Domain: Styles
  - UI Location: right sidebar > property section, hover over applied style
  - Trigger: click "detach style" icon
  - Inputs: object with bound style
  - Outputs: object retains property values but is no longer linked to style
  - Related: Detach variable, Detach instance
  - Article: Apply styles to layers and objects

- **Feature:** Edit / rename / reorder / group styles
  - Domain: Styles
  - UI Location: right sidebar > Styles section (deselected state); also style picker right-click
  - Trigger: hover + adjust icon, right-click "Edit style" / "Add new folder" / "Delete", or drag to reorder
  - Inputs: style selection, new name/description/values, folder hierarchy via "/" or folders
  - Outputs: updates propagate to bound objects; folders rename styles to reflect path
  - Related: Add style description, Move styles between files
  - Article: Manage and share styles

- **Feature:** Copy / paste / duplicate / cut styles across files
  - Domain: Styles
  - UI Location: right sidebar Styles section, right-click menu
  - Trigger: right-click > Copy/Cut/Duplicate style; Ctrl/Cmd+C/V/X; Paste here on canvas
  - Inputs: selected style(s); destination file
  - Outputs: pasted style appears at bottom of destination Styles list; cut requires publish to relink subscribers; not undoable via Ctrl+Z
  - Related: Move published components (similar non-undoable cut/paste flow)
  - Article: Manage and share styles

- **Feature:** Go to style definition
  - Domain: Styles
  - UI Location: right sidebar Styles section, right-click on style
  - Trigger: right-click > "Go to style definition"
  - Inputs: style currently displayed in sidebar
  - Outputs: opens source library file at the style
  - Related: Go to main component
  - Article: Manage and share styles

- **Feature:** Create component (single or in bulk)
  - Domain: Components
  - UI Location: right sidebar (next to selection name), right-click menu, shortcut
  - Trigger: "Create component" button, right-click > Create component, Ctrl/Cmd+Alt+K; "+" menu > Create multiple components
  - Inputs: selected layers (frames/groups/paths/booleans for bulk)
  - Outputs: layers nested in a special component frame (purple Component icon in Layers); main component definition; bulk creates one per item
  - Related: Component properties, Variants, Slots, Detach instance (inverse)
  - Article: Create components to reuse in designs

- **Feature:** Delete and restore main component
  - Domain: Components
  - UI Location: canvas / Layers panel; right sidebar; right-click instance
  - Trigger: select component + Delete; on existing instance: right-click > Main component > Restore main component, or "Restore Component" in right sidebar, or "Go to main component in library" > Restore
  - Inputs: deleted component, surviving instance (for restore)
  - Outputs: instances persist after deletion; restore re-creates main from instance link
  - Related: Move published components, Edit main components
  - Article: Create components to reuse in designs

- **Feature:** Combine as variants (component set)
  - Domain: Components
  - UI Location: right sidebar (with multiple components selected)
  - Trigger: click "Combine as variants"; or use slash naming `name/v1/v2` then combine
  - Inputs: 2+ selected main components
  - Outputs: dashed-purple component set frame containing variants; auto-generated property names (Variant, Property 2...)
  - Related: Add variant, Variant property, Interactive components
  - Article: Create and use variants

- **Feature:** Add new variant to component set
  - Domain: Components
  - UI Location: right sidebar; canvas (below set frame); shortcut
  - Trigger: "+" in right sidebar; "+" below component set; Ctrl/Cmd+D to duplicate; drag component into set frame
  - Inputs: existing component / component set
  - Outputs: new identical variant added; conflict error if value combo duplicates another variant
  - Related: Combine as variants, Variant property values
  - Article: Create and use variants

- **Feature:** Manage variant properties (rename / reorder / values)
  - Domain: Components
  - UI Location: right sidebar > Properties section (component set selected)
  - Trigger: double-click property name; drag handle; right-click > Delete; click edit icon for value reorder
  - Inputs: component set, property name/value text input
  - Outputs: variant layer names re-syntaxed; conflict errors if naming invalid
  - Related: Multi-edit
  - Article: Create and use variants

- **Feature:** Create boolean component property
  - Domain: Components
  - UI Location: right sidebar > Properties section "+" (main component / set selected)
  - Trigger: "+" > Boolean; or from nested layer's Appearance > Apply variable/property
  - Inputs: name, default true/false, optional boolean variable
  - Outputs: purple property pill on layer's visibility control; controllable via instance Properties panel
  - Related: Layer visibility, Boolean variable
  - Article: Explore component properties

- **Feature:** Create instance swap component property
  - Domain: Components
  - UI Location: right sidebar > Properties "+", or top of right sidebar on nested instance
  - Trigger: "+" > Instance swap; modal selects default value and preferred values
  - Inputs: name, default instance, optional preferred instances list
  - Outputs: instance swap dropdown on parent instance; preferred filter shown by default in swap menu
  - Related: Swap instance via Instance menu
  - Article: Explore component properties

- **Feature:** Create text component property
  - Domain: Components
  - UI Location: right sidebar > Properties "+", or Text section on nested text layer
  - Trigger: "+" > Text; or hover text field > Apply variable/property
  - Inputs: name, default string, optional string variable
  - Outputs: editable text field exposed in instance Properties panel
  - Related: String variable, Text layer editing
  - Article: Explore component properties

- **Feature:** Create slot property (open beta)
  - Domain: Components
  - UI Location: right sidebar > Properties; right-click; canvas
  - Trigger: right-click > "Convert to slot"; right-click > "Wrap in new slot"; "+" > Slot; shortcut Ctrl/Cmd+Shift+S
  - Inputs: nested frame OR non-frame layers in a main component
  - Outputs: slot region (pink border on instance hover); slot property in right sidebar; can hold any layer type in instances
  - Related: Instance swap (rigid alternative), Variants, Reset slot, Clear slot
  - Article: Use slots to build flexible components in Figma

- **Feature:** Add content to a slot (instance)
  - Domain: Components
  - UI Location: canvas (slot region on instance)
  - Trigger: drag from canvas/Assets; click "Add instances" popup on slot hover; duplicate within slot; tool-create directly inside slot
  - Inputs: instance with slot, content layers
  - Outputs: layers added to slot without detaching instance; preferred instances filter in popup
  - Related: Override preservation, Reset slot
  - Article: Use slots to build flexible components in Figma

- **Feature:** Reset / clear slot
  - Domain: Components
  - UI Location: right sidebar > More actions on slot layer
  - Trigger: More actions > Reset slot, or > Delete contents
  - Inputs: slot layer in instance
  - Outputs: revert to main component default content; or empty the slot
  - Related: Reset instance changes
  - Article: Use slots to build flexible components in Figma

- **Feature:** Migrate library to slots
  - Domain: Components
  - UI Location: documentation-driven workflow; uses slot creation tools
  - Trigger: identify variant/instance-swap workarounds; convert frames or wrap layers
  - Inputs: existing main component using nested-instance / variant workarounds
  - Outputs: slot-based component with reduced variants
  - Related: Convert to slot, Wrap in new slot
  - Article: Migrate a library to using slots

- **Feature:** Slot vs Instance swap vs Variant decision
  - Domain: Components
  - UI Location: documentation reference (no UI surface)
  - Trigger: design system author choosing property type
  - Inputs: required rigidity vs flexibility, repeating vs stateful needs
  - Outputs: chosen property type for the component
  - Related: All component property types
  - Article: The difference between slots, instance swaps, and variants

- **Feature:** Create interactive component (Change to action)
  - Domain: Components
  - UI Location: right sidebar > Prototype tab; canvas bounding-box noodle handle
  - Trigger: drag noodle handle to destination variant; or "+" in Interactions > "Change to"
  - Inputs: two variants in one component set; trigger (click/hover/etc.)
  - Outputs: variant interaction stored on main; instances auto-play interactions in Presentation
  - Related: Prototype interactions (cross-feature), Variant property, State management
  - Article: Create interactive components with variants

- **Feature:** Expose nested instances on top-level component
  - Domain: Components
  - UI Location: right sidebar > Properties section "+"
  - Trigger: "+" in Properties > Nested instances > pick instances via modal checkboxes
  - Inputs: main/component set with nested instances having component properties
  - Outputs: nested properties surfaced on top-level instance Properties panel; hover highlights nested object on canvas
  - Related: Component properties, Instance editing
  - Article: Explore component properties

- **Feature:** Configure / override instance via Properties panel
  - Domain: Components
  - UI Location: right sidebar > Properties section (instance selected)
  - Trigger: dropdowns / toggles / text fields in panel
  - Inputs: instance, property values (variant, boolean, text, instance swap)
  - Outputs: instance reflects values on canvas; overrides preserved on swap when layer names match
  - Related: Push changes to main, Reset changes
  - Article: Edit instances with component properties; Apply changes to instances

- **Feature:** Reset instance changes
  - Domain: Components
  - UI Location: right sidebar > More actions next to component name
  - Trigger: More actions > Reset > Reset [property] / Reset all changes
  - Inputs: instance (or specific layer) with overrides
  - Outputs: properties revert to main; only changed properties listed
  - Related: Reset slot, Detach instance
  - Article: Apply changes to instances

- **Feature:** Push overrides / changes to main component
  - Domain: Components
  - UI Location: right sidebar > More actions on instance (same-file only)
  - Trigger: More actions > Push overrides / Push changes to main component
  - Inputs: instance with overrides; main must be in same file (not library)
  - Outputs: main updated; all sibling instances in file updated
  - Related: Edit main components
  - Article: Edit main components; Apply changes to instances

- **Feature:** Detach instance
  - Domain: Components / Use libraries
  - UI Location: right sidebar instance menu, right-click on canvas/Layers, shortcut
  - Trigger: instance menu > Detach instance; right-click > Detach instance; Ctrl/Cmd+Alt+B
  - Inputs: instance
  - Outputs: instance becomes a regular frame keeping current properties; link to main severed
  - Related: Detach style, Detach variable; tracked by Library Analytics
  - Article: Detach an instance from the component

- **Feature:** Insert instance from Assets panel
  - Domain: Use libraries
  - UI Location: left sidebar Assets tab
  - Trigger: drag component to canvas, or open component details modal > Insert instance
  - Inputs: library + component selection; optional pre-config in component playground
  - Outputs: new instance on canvas
  - Related: Quick insert, Component playground (Dev Mode)
  - Article: Create and insert component instances

- **Feature:** Quick insert components (Shift+I)
  - Domain: Use libraries
  - UI Location: Resources / Actions modal
  - Trigger: Shift+I
  - Inputs: search query, optional currently selected layer (for swap)
  - Outputs: instance inserted, or selected instance swapped
  - Related: Actions menu
  - Article: Create and insert component instances; Swap components and instances

- **Feature:** Swap instance via Instance menu
  - Domain: Use libraries / Manage your libraries
  - UI Location: right sidebar > component name (instance selected)
  - Trigger: click component name > navigate related components / search / switch library
  - Inputs: selected instance, replacement component
  - Outputs: instance swapped; text overrides preserved when layer names match
  - Related: Override preservation
  - Article: Swap components and instances

- **Feature:** Drag-to-swap from Assets panel (modifier)
  - Domain: Use libraries / Manage your libraries
  - UI Location: left sidebar Assets > canvas
  - Trigger: hold Alt (Win) / Option (Mac) — add Ctrl/Cmd if nested — and drag component over instance
  - Inputs: target instance on canvas, replacement in Assets panel
  - Outputs: instance replaced; modifier release order matters
  - Related: Swap libraries (bulk)
  - Article: Swap components and instances

- **Feature:** Component playground (Dev Mode)
  - Domain: Components
  - UI Location: Dev Mode Inspect panel
  - Trigger: select instance > "Open in playground"
  - Inputs: component instance
  - Outputs: live preview, property toggles, mode switcher; does not change actual design
  - Related: (Dev Mode) Inspect, Variables in Dev Mode
  - Article: Explore component properties

- **Feature:** Add description / external doc link to components
  - Domain: Create and share libraries
  - UI Location: right sidebar > Component configuration (icon next to name)
  - Trigger: click configuration icon
  - Inputs: description string, link URL
  - Outputs: shown in Assets details modal, swap menu, Dev Mode; description used in component search
  - Related: Style description, Variable description
  - Article: Add descriptions to styles, components, and variables

- **Feature:** Open Variables modal
  - Domain: Variables
  - UI Location: right sidebar > Local variables section (deselected); rolling out: left navigation bar
  - Trigger: "Open variables" button; new "variables view" expands edge-to-edge
  - Inputs: none
  - Outputs: modal with collections sidebar, variables grid, mode columns
  - Related: All variables features
  - Article: Create and manage variables and collections

- **Feature:** Create / duplicate / delete variable
  - Domain: Variables
  - UI Location: Variables modal
  - Trigger: "+ Create variable" (pick type Color/Number/String/Boolean); Shift+Enter to duplicate; right-click > Delete
  - Inputs: type, name, value (per mode)
  - Outputs: row in current collection; up to 5,000 per collection
  - Related: Create alias, Eyedropper for color variable
  - Article: Create and manage variables and collections

- **Feature:** Create alias (variable references variable)
  - Domain: Variables
  - UI Location: Variables modal value cell
  - Trigger: right-click value > Create alias > pick variable from Libraries tab
  - Inputs: source variable, target variable of same type
  - Outputs: variable points at another; design-token chains; "Detach alias" reverses
  - Related: Apply variable
  - Article: Create and manage variables and collections

- **Feature:** Edit variable details (name / description / scope / code syntax / hide-from-publishing)
  - Domain: Variables
  - UI Location: Variables modal > Edit variable modal
  - Trigger: hover row > Edit variable icon, or right-click > Edit
  - Inputs: name, description, value, Scope checkboxes (per type), code syntax per platform (Web/Android/iOS), hide flag
  - Outputs: variable limited to chosen properties; code snippet shown in Dev Mode; bulk edit also supported
  - Related: Variables in Dev Mode (cross-product), Hide when publishing
  - Article: Create and manage variables and collections

- **Feature:** Manage variable collections (create / rename / delete / reorder)
  - Domain: Variables
  - UI Location: Variables modal sidebar
  - Trigger: More options > Create collection / Rename / Delete / Reorder collections (drag or Sort A–Z)
  - Inputs: collection name; existing variables (deletion cascades)
  - Outputs: collections drive grouping order in pickers
  - Related: Variable groups, Modes
  - Article: Create and manage variables and collections

- **Feature:** Group variables (within a collection)
  - Domain: Variables
  - UI Location: Variables modal sidebar
  - Trigger: select multiple > right-click > New group with selection; drag to nest groups
  - Inputs: variable selection, group name
  - Outputs: nested folder in sidebar; helpful for token taxonomy
  - Related: Style folders
  - Article: Create and manage variables and collections

- **Feature:** Create variable mode
  - Domain: Variables
  - UI Location: Variables modal column header
  - Trigger: "New variable mode" next to columns; right-click column > Duplicate mode
  - Inputs: collection with at least one variable; mode count gated by plan
  - Outputs: new value column duplicating defaults; per-mode storage
  - Related: Switch mode on object/page
  - Article: Modes for variables

- **Feature:** Set default mode / reorder modes
  - Domain: Variables
  - UI Location: Variables modal column headers
  - Trigger: right-click > Set as default / Move column left/right; drag column
  - Inputs: collection with multiple modes
  - Outputs: leftmost column is default; "Auto" objects inherit
  - Related: Apply variable mode to object/page
  - Article: Modes for variables

- **Feature:** Apply variable mode to object / page
  - Domain: Variables
  - UI Location: right sidebar > Appearance (object) or Page section (deselected)
  - Trigger: "Apply variable mode" icon > pick collection > pick mode (or Auto)
  - Inputs: layer/frame/component/section/page using mode-bearing variables
  - Outputs: mode tag in Layers panel; design contexts switch (theme/lang/device)
  - Related: Mode conflict resolution
  - Article: Modes for variables

- **Feature:** Import / export variable modes (DTCG JSON)
  - Domain: Variables
  - UI Location: Variables modal column / collection right-click
  - Trigger: right-click mode > Import mode / Export mode; right-click collection > Export modes
  - Inputs: JSON file in Design Tokens Community Group format
  - Outputs: variables created/updated by token name match; values exported to file
  - Related: REST API variables
  - Article: Modes for variables

- **Feature:** Extend a variable collection (multi-brand)
  - Domain: Variables
  - UI Location: Variables modal sidebar (Enterprise)
  - Trigger: right-click parent collection > Extend collection; rename child
  - Inputs: parent collection; per-brand JSON exports for migration
  - Outputs: child collection inherits names/scope/order; per-variable overrides shown highlighted; "Reset change" reverts
  - Related: Import mode (used during migration)
  - Article: Extend a variable collection

- **Feature:** Apply color variable
  - Domain: Variables
  - UI Location: right sidebar Fill/Stroke; gradient stops; effect color; style edit
  - Trigger: "Apply styles and variables" icon > Libraries tab > pick variable; or eyedropper
  - Inputs: solid fills, gradient stops, shadow color, color styles
  - Outputs: square swatch displayed (vs round for styles)
  - Related: Apply style, Eyedropper, Mixed selection
  - Article: Apply variables to designs

- **Feature:** Apply number variable
  - Domain: Variables
  - UI Location: right sidebar property fields (radius, dims, padding, gap, opacity, font props, stroke weight, effects)
  - Trigger: "=" in field; or Apply variable in dropdown; Shift+click; right-click > Apply variable
  - Inputs: numeric property; supported variables in scope
  - Outputs: variable bound to property; manipulating via on-canvas controls (e.g., padding handle) detaches it
  - Related: Variable scoping, Detach variable
  - Article: Apply variables to designs

- **Feature:** Apply string variable
  - Domain: Variables
  - UI Location: right sidebar Text section; font family/weight dropdowns; text style edit
  - Trigger: "Apply variable" on text field or font dropdown
  - Inputs: text content, font family, font weight/style, layer visibility ("true"/"false")
  - Outputs: dynamic text/font swap; supports localization workflows
  - Related: Multi-mode for translations
  - Article: Apply variables to designs

- **Feature:** Apply boolean variable to layer visibility
  - Domain: Variables
  - UI Location: right sidebar > Appearance > visibility icon
  - Trigger: right-click visible/hidden icon > pick boolean variable
  - Inputs: layer; boolean variable
  - Outputs: layer shown/hidden by variable value
  - Related: Boolean component property
  - Article: Apply variables to designs

- **Feature:** Apply variable to variant property of instance
  - Domain: Variables / Components
  - UI Location: right sidebar > variant property row on instance
  - Trigger: hover variant property > Assign variable > pick string/number/boolean variable
  - Inputs: instance with variant property; variable values matching variant values
  - Outputs: instance variant switches when mode changes; works on nested instances
  - Related: Variable modes
  - Article: Modes for variables

- **Feature:** Detach variable
  - Domain: Variables
  - UI Location: right sidebar (relevant property)
  - Trigger: hover variable > Detach variable icon; for numbers: clear field with Delete
  - Inputs: object with bound variable
  - Outputs: property keeps last value, no longer linked
  - Related: Detach style
  - Article: Apply variables to designs

- **Feature:** Paste unpublished variables across files
  - Domain: Variables
  - UI Location: canvas (auto toast on paste between files)
  - Trigger: copy + paste object carrying unpublished variables/styles
  - Inputs: object with bound unpublished variables, destination file
  - Outputs: toast offers to copy variables; new collection created or remap to existing collection with same names
  - Related: Move styles between files
  - Article: Apply variables to designs

- **Feature:** Variables vs styles decision
  - Domain: Variables
  - UI Location: documentation
  - Trigger: design-system author decision
  - Inputs: composite vs single value, modes need, aliasing need
  - Outputs: chosen primitive
  - Related: Styles, Variables
  - Article: The difference between variables and styles

- **Feature:** Publish library
  - Domain: Create and share libraries
  - UI Location: left sidebar Assets > Libraries icon (or Alt/Opt+3 shortcut)
  - Trigger: open Libraries modal > "This file" > Publish > add description > select assets > Publish
  - Inputs: file with components/styles/variables; (Org/Ent) target team/workspace/org dropdown
  - Outputs: assets become available to subscribed files; blue badge appears in subscribed files
  - Related: Hide when publishing, Library updates, Move components
  - Article: Publish a library

- **Feature:** Hide / unhide asset when publishing
  - Domain: Create and share libraries
  - UI Location: Libraries modal asset list (right-click)
  - Trigger: right-click asset > Hide when publishing / Show when publishing
  - Inputs: asset in publish-changes list
  - Outputs: asset omitted from library; existing instances persist as orphaned
  - Related: Publish library, Delete style/component
  - Article: Hide styles, components, and variables when publishing

- **Feature:** Unpublish library
  - Domain: Create and share libraries
  - UI Location: Libraries modal > This file > library
  - Trigger: Unpublish > confirm Remove File from Library
  - Inputs: published library file
  - Outputs: subscribers can keep current instances but receive no further updates
  - Related: Remove access to library
  - Article: Unpublish a library

- **Feature:** Move published components between files
  - Domain: Create and share libraries
  - UI Location: Layers/canvas (cut/paste) + Libraries modal (publish)
  - Trigger: cut from origin > paste to destination > publish destination as library; subscribers accept
  - Inputs: published main components, both files in editable state
  - Outputs: components get new IDs but maintain instance links via library accept; not undoable via Ctrl+Z
  - Related: Move styles between files
  - Article: Move published components

- **Feature:** Edit main component (Go to main component)
  - Domain: Create and share libraries
  - UI Location: right sidebar instance section, right-click instance, shortcut
  - Trigger: "Go to main component (in library)"; Ctrl+Alt+Shift+K (Win) / Ctrl+Opt+Cmd+K (Mac); offers "Return to instance"
  - Inputs: instance
  - Outputs: opens main component (possibly in another file)
  - Related: Push changes to main, Restore component
  - Article: Edit main components

- **Feature:** Add / remove library from a file
  - Domain: Manage your libraries
  - UI Location: left sidebar Assets > Libraries icon (modal)
  - Trigger: in modal browse Recommended/Teams/Org/UI kits > Add to file; right-click in Assets > Remove library from file
  - Inputs: published library; file edit access
  - Outputs: library's components/styles/variables become accessible; existing instances persist if removed
  - Related: Enable library for team/org
  - Article: Add or remove a library from a design file

- **Feature:** Enable libraries in drafts
  - Domain: Manage your libraries
  - UI Location: account Settings > Library
  - Trigger: toggle "Enable Libraries for all files in your Drafts"; per-library on/off and file-type scope
  - Inputs: account setting
  - Outputs: libraries available in personal draft Design/FigJam/all files
  - Related: Add library to file
  - Article: Enable access to libraries in your drafts

- **Feature:** Enable library defaults for a team / workspace / org
  - Domain: Manage your libraries
  - UI Location: file browser > team/workspace settings > Libraries
  - Trigger: admin toggles per library On/Off and chooses Design/FigJam/Slides/Buzz/All files
  - Inputs: admin role; published libraries
  - Outputs: libraries auto-enabled in matching files for members
  - Related: Add library to file
  - Article: Enable a library for a team

- **Feature:** Swap libraries (bulk)
  - Domain: Manage your libraries
  - UI Location: Libraries modal > This file > select library > Swap library
  - Trigger: choose replacement library; toggle "Swap default styles in instances"; review matched assets
  - Inputs: file with assets from library A; library B published with matching names
  - Outputs: instances/styles/variables swapped where names match; unmatched stay linked
  - Related: Swap instance (single), Move components
  - Article: Swap libraries

- **Feature:** Remove your access to (leave) a library file
  - Domain: Manage your libraries
  - UI Location: file Share modal in library file
  - Trigger: open library file > Share > find self > Leave
  - Inputs: collaborator status on library file
  - Outputs: assets stop appearing in search; instances on canvas unaffected
  - Related: Disable library in file (different action)
  - Article: Remove your access to a library

- **Feature:** Review and accept library updates
  - Domain: Use libraries
  - UI Location: Assets tab Libraries icon (blue badge); right sidebar instance update icon
  - Trigger: Review library updates > Updates tab > Update / Update all; or Update available on selected instance
  - Inputs: outstanding library changes
  - Outputs: instances/styles/variables updated; Side-by-side or Overlay (with opacity slider) preview
  - Related: Publish library, Mode conflicts
  - Article: Review and accept library updates

- **Feature:** Check designs (private beta)
  - Domain: Use libraries
  - UI Location: right-click on selection; section "Ready for Dev" dropdown; Actions menu
  - Trigger: run Check designs; opens panel with Colors / Dimensions / Typography / Components tabs
  - Inputs: selection (≤25k layers, single page); enabled libraries; ML model trained on team's design system
  - Outputs: ranked suggestions to bind hard-coded values to variables/styles; Apply / Apply all; undoable
  - Related: Variables, Styles
  - Article: Check designs in Figma

- **Feature:** Use UI kits
  - Domain: Use libraries
  - UI Location: Libraries modal > UI kits tab; or Figma Community
  - Trigger: Add to file (Material 3, Simple Design System, Apple iOS/iPadOS/macOS/watchOS/visionOS, etc.); or Open in Figma
  - Inputs: kit chosen; some require EULA acceptance (Apple)
  - Outputs: components/styles/variables enabled; updates auto-flow; Code Connect supported
  - Related: Code Connect (Dev Mode), Apply styles/variables
  - Article: Start designing with UI kits; Get started with Apple's UI kit

### Create prototypes

- **Feature:** Prototype mode toggle (Design ↔ Prototype tab)
  - Domain: Create prototypes
  - UI Location: right sidebar (top tab switcher)
  - Trigger: click the **Prototype** tab; shortcut `Shift + E`
  - Inputs: none
  - Outputs: right sidebar swaps to prototype panel; canvas exposes hotspot/connection drag handles on hover
  - Related: Design tab, View prototype connections
  - Article: Connect your prototype / View prototype connections

- **Feature:** Hotspot
  - Domain: Create prototypes
  - UI Location: canvas (any selected layer/object/frame)
  - Trigger: select object in Prototype tab; small `+` plug icon appears on object's bounding box
  - Inputs: layer selection
  - Outputs: marks the layer as the start of an interaction
  - Related: Connection, Trigger, Action
  - Article: Connect your prototype

- **Feature:** Connection ("noodle") between hotspot and destination
  - Domain: Create prototypes
  - UI Location: canvas
  - Trigger: drag the `+` plug icon from hotspot to a destination frame; or click `+` in **Interactions** section of Prototype panel
  - Inputs: source hotspot, destination top-level frame (or section)
  - Outputs: blue arrow on canvas; opens **Interaction details** modal; first connection auto-creates flow starting point on source frame
  - Related: Bulk connections, Flow starting point, Interaction details
  - Article: Connect your prototype

- **Feature:** Bulk-create connections from multiple hotspots
  - Domain: Create prototypes
  - UI Location: canvas
  - Trigger: multi-select objects (Shift-click or marquee) → drag the shared `+` icon to one destination
  - Inputs: multiple selected source layers, one destination
  - Outputs: identical interactions created on each source object simultaneously
  - Related: Update destinations in bulk, Select matching interactions
  - Article: Connect your prototype

- **Feature:** Inherited connections from main components
  - Domain: Create prototypes
  - UI Location: canvas (main component on same page)
  - Trigger: drag connection from a main component's nested object; instances inherit the connection
  - Inputs: a main component (must be on same page; not from team library); destination frame
  - Outputs: every instance of that component carries the same prototype interaction; inherited connections are hidden until instance is selected
  - Related: Components, Variants, Interactive components
  - Article: Add prototype connections from main components

- **Feature:** Interaction details modal
  - Domain: Create prototypes
  - UI Location: floating modal next to selected connection on canvas (also accessible from right sidebar **Interactions** section)
  - Trigger: click a connection arrow, or create a new connection
  - Inputs: trigger type, action type, destination, animation settings, state-management toggles
  - Outputs: persists interaction config to the connection
  - Related: Triggers, Actions, Animations, State management, Add action (for multi-action / conditionals)
  - Article: Connect your prototype

- **Feature:** Trigger — On click / On tap
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal (Trigger dropdown)
  - Trigger: user click (desktop) / tap (mobile) on hotspot during playback
  - Inputs: none beyond selection
  - Outputs: fires the configured action(s)
  - Related: All other triggers; cannot be combined with **While hovering** on same object
  - Article: Prototype triggers

- **Feature:** Trigger — On drag
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal
  - Trigger: directional drag (Left/Right/Up/Down) on hotspot during playback
  - Inputs: drag direction, drag distance (continuum, scrubbable forwards/backwards)
  - Outputs: fires action; supports scrubbable mid-transition state
  - Related: Smart animate (drag + smart animate creates interactive draggable transitions)
  - Article: Prototype triggers

- **Feature:** Trigger — While hovering
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal
  - Trigger: cursor enters hotspot, returns to original frame on cursor leaving
  - Inputs: none
  - Outputs: shows destination while hovered, auto-reverts on leave
  - Article: Prototype triggers

- **Feature:** Trigger — While pressing
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal
  - Trigger: mouse-down/touch held; reverts on release
  - Article: Prototype triggers

- **Feature:** Trigger — Mouse enter / Mouse leave
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal
  - Trigger: cursor enters or leaves hotspot bounding box (one-shot, not continuous)
  - Outputs: fires once at boundary crossing (legacy "Mouse move inside / outside" interactions kept for old prototypes)
  - Article: Prototype triggers

- **Feature:** Trigger — Mouse down / Mouse up (touch down/up)
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal
  - Trigger: pointer pressed or released over hotspot
  - Outputs: pairing both supports drop-down menu / drag-to-select patterns
  - Article: Prototype triggers

- **Feature:** Trigger — After delay
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal (only valid on top-level frames)
  - Trigger: time elapsed on frame
  - Inputs: delay duration in milliseconds
  - Outputs: fires action automatically
  - Article: Prototype triggers

- **Feature:** Trigger — Key / Gamepad
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal
  - Trigger: keyboard key, key combo, or gamepad button (Xbox One, PS4, Switch Pro)
  - Inputs: captured key/button combo
  - Outputs: fires action
  - Article: Prototype triggers

- **Feature:** Trigger — When video hits / When video ends
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal (only when source is a video fill)
  - Trigger: playback timestamp reached, or video end
  - Inputs: timestamp (for "hits")
  - Outputs: fires action
  - Related: Video properties, Set to specific time action
  - Article: Prototype triggers / Use videos in prototypes

- **Feature:** Action — Navigate to
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal (Action dropdown)
  - Trigger: any trigger
  - Inputs: destination top-level frame (or section)
  - Outputs: pushes destination on prototype history stack; applies animation
  - Related: Back, Sections-as-destinations, Animations
  - Article: Prototype actions

- **Feature:** Action — Back
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal
  - Trigger: any trigger
  - Outputs: pops the prototype history stack (does not record Swap overlay)
  - Article: Prototype actions

- **Feature:** Action — Scroll to
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal
  - Trigger: any trigger
  - Inputs: target object inside same top-level frame; animate (Instant / eased) and easing
  - Outputs: scrolls the containing scrollable frame to bring target into view
  - Related: Scroll & overflow behavior
  - Article: Prototype actions

- **Feature:** Action — Open link
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal
  - Inputs: URL string
  - Outputs: opens URL in new tab; shows "leaving Figma" intermediate page
  - Article: Prototype actions

- **Feature:** Action — Open / Close / Swap overlay
  - Domain: Create prototypes
  - UI Location: Interaction details modal
  - Inputs: destination overlay frame (Open/Swap)
  - Outputs: shows destination frame floating above current frame; Close dismisses; Swap replaces current overlay (not recorded in history)
  - Related: Overlay position, "Close when clicking outside", "Add background behind overlay"
  - Article: Create overlays in your prototypes

- **Feature:** Action — Set variable
  - Domain: Create prototypes > Advanced prototyping
  - UI Location: Interaction details modal
  - Inputs: target variable (string/number/boolean/color), value or expression
  - Outputs: variable value updated at playback time; bound design properties update live
  - Related: Use variables in prototypes, Expressions, Variable modes
  - Article: Use variables in prototypes / Use expressions in prototypes

- **Feature:** Action — Set variable mode
  - Domain: Create prototypes > Advanced prototyping
  - UI Location: Interaction details modal
  - Inputs: variable collection + mode
  - Outputs: changes the page-level mode; objects with mode set to **Auto** flip; explicit mode overrides on objects retained
  - Related: Variable modes (e.g. light/dark)
  - Article: Variable modes in prototypes

- **Feature:** Action — Conditional (if/else)
  - Domain: Create prototypes > Advanced prototyping
  - UI Location: Interaction details modal
  - Inputs: boolean expression in `If`; one or more nested actions for true and (optional) `Else` branches
  - Outputs: branches whichever sub-action(s) executes; invalid expressions outlined red
  - Related: Multiple actions, Expressions
  - Article: Multiple actions and conditionals

- **Feature:** Action — Change to (variant)
  - Domain: Create prototypes
  - UI Location: Interaction details modal (only on interactive component variants)
  - Inputs: target variant in same component set (works on nested instances too)
  - Outputs: instance switches variant during playback
  - Related: Interactive components, State management
  - Article: Prototype actions / advanced examples

- **Feature:** Video actions — Play/pause, Mute/unmute, Set to specific time, Jump forward/backward
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal (when destination is video)
  - Inputs: timestamp / seconds offset where applicable
  - Outputs: alters playback state of destination video fill
  - Related: Video triggers, Reset video state
  - Article: Prototype actions / Use videos in prototypes

- **Feature:** Multiple actions on one trigger
  - Domain: Create prototypes > Advanced prototyping
  - UI Location: Interaction details modal (`+ Add action`)
  - Trigger: any
  - Inputs: ordered list of actions; reorderable via drag handle; collapsible chevron
  - Outputs: runs actions sequentially top-to-bottom (order is semantically significant — e.g. Set var before Conditional)
  - Article: Multiple actions and conditionals

- **Feature:** Animation — Instant / Dissolve / Move In / Move Out / Push / Slide In / Slide Out / Smart animate
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal (Animation section)
  - Inputs: transition type, direction (where applicable), easing, duration (1–10000 ms)
  - Outputs: how destination transitions over current frame at playback
  - Related: Smart animate matching layers, Easing, Spring
  - Article: Prototype animations / Smart animate

- **Feature:** Smart animate (matching-layer interpolation)
  - Domain: Create prototypes > Advanced prototyping
  - UI Location: Animation section (selected as transition, or `Animate matching layers` checkbox alongside another transition)
  - Inputs: matching layer names + hierarchy across two frames
  - Outputs: per-property tween of position, scale, opacity, rotation, fill (gradient/image/solid), corner radius, etc.; unsupported props (drop shadow, shape morph) fall back to dissolve
  - Related: Matching objects, Layer-name conventions
  - Article: Smart animate layers between frames

- **Feature:** Easing presets + custom Bézier curve
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal → Easing dropdown
  - Inputs: preset (Linear, Ease In/Out/InOut, Ease In/Out/InOut Back) or 4-point custom cubic-bezier
  - Outputs: applied to transition's acceleration curve
  - Article: Prototype easing and spring animations

- **Feature:** Spring animation curves
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal → Spring presets (Gentle, Quick, Bouncy, Slow, Custom)
  - Inputs: stiffness, damping, mass (for Custom); draggable spring graph
  - Outputs: spring-based motion replaces fixed-duration easing
  - Article: Prototype easing and spring animations

- **Feature:** Animation preview (in Interaction details modal)
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal — preview window
  - Trigger: hover preview area
  - Outputs: plays current animation config on a sample
  - Article: Prototype easing and spring animations

- **Feature:** Flow starting point
  - Domain: Create prototypes
  - UI Location: blue badge anchored to top-left of starting frame on canvas; Prototype panel **Flow starting point** section
  - Trigger: created automatically on first connection from a frame; or `+` in Flow starting point section; right-click frame → Add starting point; duplicate frame with starting point
  - Inputs: top-level frame
  - Outputs: marks frame as flow entry; flow listed in **Flows** section
  - Related: Flow name & description, Move/Delete starting point
  - Article: Create and manage prototype flows

- **Feature:** Flow rename / description
  - Domain: Create prototypes
  - UI Location: Prototype panel → Flow starting point section; or double-click flow badge on canvas
  - Inputs: flow name string; rich-text description (bold, lists, links)
  - Outputs: shown in left sidebar in presentation view
  - Article: Create and manage prototype flows

- **Feature:** Move / delete flow starting point
  - Domain: Create prototypes
  - UI Location: blue starting-point badge on canvas; or Prototype panel → "Remove starting point"
  - Trigger: drag badge to new frame to move; drag off frame to empty canvas to delete
  - Article: Create and manage prototype flows

- **Feature:** Copy flow link
  - Domain: Create prototypes
  - UI Location: Prototype panel → Flow starting point hover; or presentation-view Share menu
  - Outputs: clipboard URL deep-linked to that flow's starting frame
  - Article: Create and manage prototype flows

- **Feature:** Flows list (page-level)
  - Domain: Create prototypes
  - UI Location: Prototype panel → **Flows** section (visible when no selection)
  - Inputs: hover row to expose Select frame / Copy link / Preview actions
  - Article: Create and manage prototype flows / View prototype connections

- **Feature:** Section as connection destination
  - Domain: Create prototypes
  - UI Location: canvas (drag connection to a section)
  - Inputs: source hotspot, destination section
  - Outputs: connection retains last-visited frame inside section and returns to it (e.g. Back-to-Browse pattern)
  - Article: Use sections in prototyping

- **Feature:** Overlay configuration (position, click-outside-to-close, background)
  - Domain: Create prototypes
  - UI Location: right sidebar (overlay-specific section that appears when overlay frame is selected in Prototype mode)
  - Inputs: 7 default position presets + manual offset; "Close when clicking outside" checkbox; "Add background behind overlay" with color + opacity
  - Outputs: settings stored on the overlay frame itself (reused across all connections that open it)
  - Related: Open/Close/Swap overlay actions
  - Article: Create overlays in your prototypes

- **Feature:** Scroll overflow on frame
  - Domain: Create prototypes
  - UI Location: Prototype panel → **Scroll behavior** → Overflow dropdown (frame selected)
  - Inputs: No scrolling / Horizontal / Vertical / Both directions
  - Outputs: makes frame scrollable at playback (only if content overflows frame bounds)
  - Article: Prototype scroll and overflow behavior

- **Feature:** Scroll position per object (Scroll with parent / Fixed / Sticky)
  - Domain: Create prototypes
  - UI Location: Prototype panel → Scroll behavior → Position dropdown (object selected)
  - Inputs: one of three modes
  - Outputs: Fixed pins object regardless of scroll (auto-promoted above other layers, labeled **Fixed** in Layers panel); Sticky pins on reaching top of parent; Scroll with parent moves with content
  - Article: Prototype scroll and overflow behavior

- **Feature:** Preserve scroll position (state memorization + sharing)
  - Domain: Create prototypes
  - UI Location: implicit (no toggle) — driven by matching layer / frame names
  - Inputs: identical layer names with same parent hierarchy across frames; top-level frames with identical names or shared `Prefix /` naming
  - Outputs: scroll position memorized per layer and shared across matching frames at playback
  - Related: Reset scroll position, Bulk rename (Cmd/Ctrl+R)
  - Article: Preserve scroll position in prototypes

- **Feature:** State management — memorization, sharing, reset (component variant + scroll + video)
  - Domain: Create prototypes > Guides
  - UI Location: Interaction details modal → **State management** section
  - Inputs: checkboxes — Reset scroll position, Reset component state, Reset video state (only shown when relevant)
  - Outputs: overrides default memorize/share behavior on this specific interaction
  - Related: Matching objects, Update legacy interactions ("Update" / "Update all" banner)
  - Article: State management for prototypes

- **Feature:** Matching-objects highlighter
  - Domain: Create prototypes
  - UI Location: canvas (Prototype tab active)
  - Trigger: hover a layer
  - Outputs: Figma highlights all matching objects on other frames (same name + parent hierarchy)
  - Related: Smart animate, State sharing
  - Article: State management / Smart animate

- **Feature:** Select matching interactions (bulk-edit identical interactions)
  - Domain: Create prototypes
  - UI Location: Interaction details modal → **Select matching interactions** icon
  - Outputs: selects all interactions with same action+destination on matching source objects across frames; edits propagate to all
  - Article: Connect your prototype

- **Feature:** Update connection destinations in bulk
  - Domain: Create prototypes
  - UI Location: canvas (multi-select connections, Shift-click or marquee)
  - Trigger: drag selected noodles to a new destination frame
  - Article: Connect your prototype

- **Feature:** Copy / cut / paste interaction details
  - Domain: Create prototypes
  - UI Location: canvas (connection selected)
  - Trigger: `Cmd/Ctrl+C` / `+X` on connection, `Cmd/Ctrl+V` on another object
  - Outputs: pastes trigger+action+animation onto target object
  - Article: Connect your prototype

- **Feature:** Toggle prototype connection visibility (read-only & viewer)
  - Domain: Create prototypes > View prototypes
  - UI Location: shortcut + toolbar **View settings** menu
  - Trigger: `Shift + E` toggles connection display; or toolbar → View settings → Prototyping
  - Outputs: shows/hides all noodles + flow badges on canvas
  - Article: View prototype connections

- **Feature:** Inline preview (Preview button)
  - Domain: Create prototypes > View prototypes
  - UI Location: top toolbar **Preview** button; or click flow starting-point preview icon; shortcut `Shift + Space`
  - Outputs: small embedded prototype window above canvas, mirrors design changes live
  - Inputs: scaling options (Fit width, Responsive, Resize 100%, Respect aspect ratio, Show device frame); Follow prototype toggle
  - Article: Play your prototypes / Create and manage prototype flows

- **Feature:** Presentation view (Present)
  - Domain: Create prototypes > View prototypes
  - UI Location: opened in new browser tab
  - Trigger: toolbar **Present** button; `Cmd+Opt+Return` (Mac) / `Ctrl+Alt+Enter` (Win)
  - Outputs: full-screen prototype with toolbar, footer, optional left sidebar (flows), Restart (`R`), arrow nav, device switcher
  - Related: Options menu (Hints, Hide UI, Accessibility, Make available offline, scaling), Comments mode, Spotlight/Follow
  - Article: Play your prototypes

- **Feature:** Presentation Options menu
  - Domain: Create prototypes > View prototypes
  - UI Location: presentation-view top-right
  - Inputs: Enable Figma shortcuts, Show hints on click (highlights hotspots in blue), Make available offline, Accessibility settings, Hide UI (`&hide-ui=1` URL flag), scaling presets
  - Outputs: changes some settings update the share URL — must re-copy to share
  - Article: Play your prototypes

- **Feature:** Hotspot hints
  - Domain: Create prototypes > View prototypes
  - UI Location: Options menu in presentation view
  - Trigger: clicking outside a hotspot during playback
  - Outputs: highlights all clickable areas with a blue bounding box (when enabled)
  - Article: Play your prototypes

- **Feature:** Offline prototype playback
  - Domain: Create prototypes > View prototypes
  - UI Location: Options menu → Advanced settings → "Make available offline"
  - Inputs: must be online to preload; tab must remain open
  - Outputs: caches assets; "Available to present while offline" indicator appears in header; mobile not supported
  - Article: Present prototypes offline

- **Feature:** Prototype device + model + orientation + background
  - Domain: Create prototypes > View prototypes
  - UI Location: Prototype panel (no selection) → Device, Background sections
  - Inputs: device preset (auto-matched to frame preset), model (e.g. iPhone color), orientation (Portrait/Landscape), background color
  - Outputs: chrome wraps the prototype in inline preview & presentation view; orientation is per-prototype, cannot switch mid-playback
  - Article: Set prototype device and background settings

- **Feature:** Custom Size (Fit) / Presentation (Full) device options
  - Domain: Create prototypes > View prototypes
  - UI Location: Device dropdown
  - Outputs: Custom Size auto-scales to viewport; Presentation fits entire frame on screen (presentation view only)
  - Article: Set prototype device and background settings

- **Feature:** Device switcher (in presentation view)
  - Domain: Create prototypes > View prototypes
  - UI Location: bottom of presentation view (when device frame selected)
  - Outputs: switch among similar devices; scaling: Fit device on screen / Zoom device to fill / Show device at 100%; show/hide device frame
  - Article: Play your prototypes

- **Feature:** Frame ordering & arrow-key navigation
  - Domain: Create prototypes > View prototypes
  - UI Location: presentation view + inline preview
  - Inputs: `→`/`Space`/`N` next, `←` previous, `R` restart
  - Outputs: with starting point → traverses history stack; without → x-then-y canvas coordinate order
  - Article: Play your prototypes

- **Feature:** Animated GIF fill (playback only in presentation view)
  - Domain: Create prototypes > Guides
  - UI Location: any vector/text layer's Fill (image fill); Layers panel shows GIF label
  - Trigger: drag-drop, file browser, place image, paste
  - Outputs: appears static in editor; animates only in presentation view; cannot export as animated
  - Related: Image fills, Blend modes, Masks
  - Article: Use animated GIFs in prototypes

- **Feature:** Video fill in prototypes
  - Domain: Create prototypes > Guides
  - UI Location: Fill section (image picker → video importer); Layers panel video icon
  - Inputs: .mp4/.mov (H.264) or .webm (VP8), up to 100 MB; paid teams only for upload
  - Outputs: video fill on shape; Fill section gets play preview, scrubber, jump-to-time
  - Related: Video properties (autoplay, loop, sound), Video triggers/actions, Video & smart animate, Video + interactive components
  - Article: Use videos in prototypes

- **Feature:** Video properties panel (per-frame in Prototype tab)
  - Domain: Create prototypes > Guides
  - UI Location: Prototype panel → Video section (when video layer selected)
  - Inputs: Autoplay checkbox, Loop icon, Sound icon
  - Outputs: defines video behavior on frame entry during playback
  - Article: Use videos in prototypes

- **Feature:** Mobile mirror (Figma mobile app)
  - Domain: Create prototypes > View prototypes
  - UI Location: mobile app **Mirror** tab; desktop frame selection drives it
  - Inputs: select top-level frame on desktop while logged in to same account
  - Outputs: live frame view on phone; if frame is in a flow, prototype interactions playable; works over wifi or cellular
  - Article: View prototypes on a mobile device

- **Feature:** Mobile prototype options menu (mobile app)
  - Domain: Create prototypes > View prototypes
  - UI Location: mobile presentation view
  - Trigger: double-tap-and-hold anywhere on screen
  - Inputs: switch flow starting point, restart, view file, Fixed vs Responsive scale, toggle hotspot hints, share, exit
  - Article: View prototypes on a mobile device

- **Feature:** Mobile browser presentation / mirror at figma.com/mirror
  - Domain: Create prototypes > View prototypes
  - UI Location: mobile browser
  - Outputs: hotspot-only interaction; browser back not supported as gesture
  - Article: View prototypes on a mobile device

- **Feature:** Accessibility mode for prototypes (screen reader adaptation)
  - Domain: Create prototypes > View prototypes
  - UI Location: Skip-to-content button (`Tab` first focus); presentation Options → Accessibility settings → "Adapt content for screen readers"
  - Inputs: requires VoiceOver/JAWS/NVDA; desktop browser or desktop app only
  - Outputs: maps prototype elements to HTML — Navigate-to/Open-link → links, other actions → buttons, image fills → img with layer-name alt text, frames/components/instances → labeled sections; tab order = layer order
  - Article: Accessible prototypes in Figma

- **Feature:** Inline preview Follow mode
  - Domain: Create prototypes > View prototypes
  - UI Location: inline preview overflow menu
  - Inputs: toggle "Follow prototype"
  - Outputs: canvas selection auto-follows current frame in preview
  - Article: Play your prototypes

- **Feature:** Spotlight / follow presenter (multi-user)
  - Domain: Create prototypes > View prototypes
  - UI Location: presentation view top-right (avatar dropdown)
  - Outputs: synchronizes other viewers' presentation view to follow presenter
  - Article: Play your prototypes

- **Feature:** Comments in presentation view
  - Domain: Create prototypes > View prototypes
  - UI Location: presentation toolbar → comment icon (or `C` if Figma shortcuts enabled)
  - Outputs: pin comments directly on prototype frames
  - Related: cross-product → file comments
  - Article: Play your prototypes

### Work together in files

- **Feature:** Comment mode (enter / exit)
  - Domain: Comments
  - UI Location: toolbar (comment tool); also right-click menu; right sidebar opens on entry
  - Trigger: click toolbar comment tool / shortcut `C` / `Esc` to exit / select another tool
  - Inputs: tool activation
  - Outputs: cursor switches to comment cursor; canvas object editing is disabled; right sidebar opens with comments list
  - Related: Pin/region comment, Hide comments (`Shift+C`), Cursor chat (mutually exclusive modes)
  - Article: Guide to comments in Figma

- **Feature:** Add pinned comment
  - Domain: Comments
  - UI Location: canvas (in comment mode); modal opens at click point
  - Trigger: single click on canvas while in comment mode
  - Inputs: pin location, message text, optional `@` mention, emoji, image/GIF (≤5, PNG/JPG/GIF), markdown styling
  - Outputs: comment pin attached to nearest top-level frame/component/group (or to coordinates), thread created, notifications fired
  - Related: Region comment, Mention collaborator, Add media to comment, Reply
  - Article: Add comments to files

- **Feature:** Add region comment
  - Domain: Comments
  - UI Location: canvas (in comment mode)
  - Trigger: click-and-drag a rectangular region on canvas
  - Inputs: drag start/end, message text
  - Outputs: comment anchored to a region rather than a point; same threading/notification behavior as pin
  - Related: Pinned comment
  - Article: Add comments to files

- **Feature:** @mention in comment
  - Domain: Comments
  - UI Location: comment input field (modal or sidebar)
  - Trigger: type `@` or click `@` button in field
  - Inputs: typed name/email/user-group; selection from suggestion list
  - Outputs: blue mention token inserted; recipient gets email + in-app notification on submit
  - Related: User groups (Org/Enterprise), Notification settings
  - Article: Add comments to files

- **Feature:** Add emoji to comment
  - Domain: Comments
  - UI Location: emoji picker popover inside comment field
  - Trigger: click smiley icon in comment field
  - Inputs: emoji selection (Frequently used / browse / search)
  - Outputs: emoji glyph inserted into message
  - Related: Comment markdown styling
  - Article: Add comments to files

- **Feature:** Attach media to comment
  - Domain: Comments
  - UI Location: image icon inside comment field; also drag-drop / paste into field
  - Trigger: click image icon, drag-drop file, or paste from clipboard
  - Inputs: up to 5 PNG/JPEG/GIF files
  - Outputs: thumbnails appear in field; X removes attachment
  - Related: Pinned comment
  - Article: Add comments to files

- **Feature:** Comment text styling (markdown / shortcuts)
  - Domain: Comments
  - UI Location: comment input field
  - Trigger: keyboard shortcut (e.g. `Ctrl/Cmd+B`) or markdown syntax (`**bold**`, `*italic*`, `~strike~`, `Ctrl+K` link, `Ctrl+Shift+7/8` lists)
  - Inputs: text + shortcut
  - Outputs: styled text in posted comment
  - Related: Add comments
  - Article: Add comments to files

- **Feature:** Comment rate limit
  - Domain: Comments
  - UI Location: implicit (server-side)
  - Trigger: posting comment/reply
  - Inputs: comment volume
  - Outputs: cap of 100 comments/hour per user across all files
  - Related: Add comments
  - Article: Add comments to files

- **Feature:** View comment pin / cluster on canvas
  - Domain: Comments
  - UI Location: canvas overlay
  - Trigger: hover (preview) / click (open modal); zoom-out auto-clusters nearby pins
  - Inputs: hover, click, zoom level
  - Outputs: tooltip preview, comment modal opens, cluster shows count + author avatars
  - Related: Hide comments, Comments sidebar
  - Article: View and manage comments

- **Feature:** Comment modal (open thread)
  - Domain: Comments
  - UI Location: floating overlay anchored to pin
  - Trigger: click pin or sidebar comment row
  - Inputs: hover for reactions, click ellipsis menu, type Reply, Resolve, Close
  - Outputs: thread expanded; reply/react/resolve/delete actions available; Mark as unread, Copy link
  - Related: Reactions, Resolve, Delete
  - Article: View and manage comments

- **Feature:** Reply to comment
  - Domain: Comments
  - UI Location: Reply field in comment modal or sidebar
  - Trigger: focus Reply field, type, press `Enter` / submit
  - Inputs: text, mentions, emoji
  - Outputs: reply appended to thread; participants notified
  - Related: @mention, Reactions
  - Article: View and manage comments

- **Feature:** React to comment
  - Domain: Comments
  - UI Location: hover affordance on comment body in modal
  - Trigger: hover comment → click reaction icon
  - Inputs: emoji selection
  - Outputs: reaction badge added under comment
  - Related: Emoji picker
  - Article: View and manage comments

- **Feature:** Resolve / Unresolve comment
  - Domain: Comments
  - UI Location: checkmark in top-right of comment modal; sidebar filter to unhide
  - Trigger: click resolve icon; uncheck to unresolve; toggle "Show resolved" in sidebar filter
  - Inputs: click
  - Outputs: comment removed from canvas + sidebar default view; reappears under "Show resolved comments"
  - Related: Sidebar filter
  - Article: View and manage comments

- **Feature:** Delete comment / thread
  - Domain: Comments
  - UI Location: ellipsis menu on comment / thread title
  - Trigger: ellipsis → Delete comment / Delete thread → confirm
  - Inputs: confirm
  - Outputs: permanent removal (cannot be restored even via version history)
  - Related: Resolve
  - Article: View and manage comments

- **Feature:** Hide comments toggle
  - Domain: Comments
  - UI Location: shortcut / sidebar Settings menu in comment mode
  - Trigger: shortcut `Shift+C`
  - Inputs: toggle
  - Outputs: comment pins hidden from canvas (still visible in sidebar when in comment mode)
  - Related: Comment mode
  - Article: View and manage comments

- **Feature:** Sort and filter comments (sidebar)
  - Domain: Comments
  - UI Location: filter button at top of right sidebar in comment mode
  - Trigger: click filter icon
  - Inputs: Sort by Date / Unread; toggles for "Only your threads", "Only current page", "Show resolved"
  - Outputs: sidebar list re-orders/filters
  - Related: Comments sidebar
  - Article: View and manage comments

- **Feature:** Mark comment as unread / Copy link to comment
  - Domain: Comments
  - UI Location: ellipsis menu on comment
  - Trigger: click menu item
  - Inputs: click
  - Outputs: thread re-flagged unread for current user; deep-link URL copied to clipboard
  - Related: Sort by unread
  - Article: View and manage comments

- **Feature:** Edit comment content
  - Domain: Comments
  - UI Location: ellipsis menu on own comment
  - Trigger: ellipsis → Edit…
  - Inputs: edited text, then Save
  - Outputs: comment text replaced (only on own comments)
  - Related: Add comment
  - Article: Move or edit comments

- **Feature:** Move (re-pin) comment
  - Domain: Comments
  - UI Location: canvas
  - Trigger: drag pin to new location
  - Inputs: drag start/end coordinates
  - Outputs: pin re-anchored; if pinned to a layer, may re-attach based on drop target
  - Related: Layer-attached comment behavior
  - Article: Move or edit comments

- **Feature:** Layer-attached comment movement (cut/paste / move-to-page)
  - Domain: Comments
  - UI Location: canvas / right-click → Move to page
  - Trigger: cut+paste, Move to page, duplicate file
  - Inputs: layer move action
  - Outputs: cut+paste detaches comment (still in sidebar); Move to page brings pinned comments along; duplicate file does not copy comments; cross-file paste leaves comment as detached in source
  - Related: Move comment
  - Article: Move or edit comments

- **Feature:** Comment on prototype (presentation view)
  - Domain: Comments
  - UI Location: prototype presentation toolbar
  - Trigger: click comment button or `C`; click or drag region on prototype frame
  - Inputs: text/mention/emoji
  - Outputs: pinned comment scoped to prototype; visible only in presentation view
  - Related: Show resolved / Show only your comments (prototype Options menu)
  - Article: Comment on prototypes

- **Feature:** Prototype Options menu (Show resolved / Show only your comments)
  - Domain: Comments
  - UI Location: presentation view toolbar → Options
  - Trigger: click Options
  - Inputs: toggle settings
  - Outputs: filters which comments overlay the prototype
  - Related: Comment on prototypes
  - Article: Comment on prototypes

- **Feature:** Email notification settings (per-file)
  - Domain: Comments
  - UI Location: Settings (gear) at top of right sidebar in comment mode
  - Trigger: comment mode → sidebar Settings dropdown
  - Inputs: choose Everything / Just mentions and replies / Nothing
  - Outputs: per-file email notification scope changes; in-app notifications always on; @mentions always emailed
  - Related: Slack/MS Teams integrations
  - Article: Manage email notifications for comments on files

- **Feature:** Viewer history (avatar dropdown)
  - Domain: Multiplayer tools
  - UI Location: avatar stack in right side of toolbar
  - Trigger: click avatar group
  - Inputs: click; hover row + ellipsis to view profile
  - Outputs: dropdown lists "Currently viewing" + "Previously viewed" with timestamps; account-level opt-out in Settings → Account → View history
  - Related: Multiplayer cursors
  - Article: See viewer history for your files
  - Note: paid plans only; not retroactive before Feb 2025

- **Feature:** Spotlight me (lead session)
  - Domain: Multiplayer tools
  - UI Location: own avatar in toolbar → Multiplayer tools dropdown
  - Trigger: hover own avatar → click "Spotlight me"
  - Inputs: click; viewers see prompt with "Not now" before auto-following
  - Outputs: all viewers' canvases jump to presenter's view; presenter avatar gets dashed border + follower count; "Stop" button at top of canvas
  - Related: Follow user, Ask to spotlight
  - Article: Present to collaborators using spotlight

- **Feature:** Follow user / Observation mode
  - Domain: Multiplayer tools
  - UI Location: other users' avatars in toolbar
  - Trigger: click avatar (auto-follow) or hover → "Ask to spotlight"
  - Inputs: click
  - Outputs: viewport mirrors followed user's canvas (zoom, pan, page switch); colored border around canvas; banner "Following X" with "Stop following"; works in presentation view too
  - Related: Spotlight me, Multiplayer cursors
  - Article: Present to collaborators using spotlight

- **Feature:** Ask to spotlight (request)
  - Domain: Multiplayer tools
  - UI Location: hover state on another user's avatar
  - Trigger: click "Ask to spotlight"
  - Inputs: click
  - Outputs: target user gets prompt to accept/reject becoming the spotlight presenter
  - Related: Spotlight me
  - Article: Present to collaborators using spotlight

- **Feature:** Cursor chat
  - Domain: Multiplayer tools
  - UI Location: canvas (overlay attached to cursor)
  - Trigger: shortcut `/` or right-click canvas → Cursor chat
  - Inputs: typed text (52 char per chat; `Enter` clears prior line)
  - Outputs: live speech bubble follows cursor; visible to other multiplayer users in real time; disappears 5s after last keystroke; never persisted
  - Related: Comments (persistent alternative), Multiplayer cursors
  - Article: Use cursor chat in Figma Design

- **Feature:** Exit cursor chat
  - Domain: Multiplayer tools
  - UI Location: canvas
  - Trigger: `Esc`, click anywhere, switch tool, open menu
  - Inputs: any of above
  - Outputs: bubble cleared; back to previous tool
  - Related: Cursor chat
  - Article: Use cursor chat in Figma Design

- **Feature:** Custom file thumbnail (handoff helper)
  - Domain: Multiplayer tools (handoff)
  - UI Location: canvas right-click on a frame
  - Trigger: right-click frame → Set as thumbnail
  - Inputs: frame selection
  - Outputs: file tile in browser shows that frame as thumbnail
  - Related: Sections "Ready for development" (cross-product → Dev Mode)
  - Article: Optimize design files for developer handoff

- **Feature:** Create branch
  - Domain: Branching and merging
  - UI Location: file-name dropdown menu in left sidebar / toolbar
  - Trigger: click file-name caret → "Create branch…" → name it
  - Inputs: branch name
  - Outputs: new branch file (replica of main at that snapshot); URL gains `/branch/<id>`; sidebar shows `File name › Branch name`
  - Related: Share branch, Update from main, Merge branch
  - Article: Guide to branching
  - Note: Org/Enterprise + Full seat; viewers need "Allow viewers to copy/share/export" enabled

- **Feature:** Share branch
  - Domain: Branching and merging
  - UI Location: branches modal / Share modal on branch / file-name menu
  - Trigger: branches modal ellipsis → Copy link; or branch's Share button → Copy link / Invite
  - Inputs: emails + can view / can edit
  - Outputs: invitee gets branch access + view access to main file; URL contains `/branch/`
  - Related: Permissions
  - Article: Share a branch

- **Feature:** Update from main
  - Domain: Branching and merging
  - UI Location: file-name dropdown in left sidebar (on a branch)
  - Trigger: caret → "Update from main…"
  - Inputs: review previewed adds/edits/removes; click Apply changes
  - Outputs: branch absorbs all main-file changes (no cherry-pick); may surface conflicts modal
  - Related: Resolve conflicts, Restore branch version
  - Article: Get updates from main files

- **Feature:** Resolve conflicts
  - Domain: Branching and merging
  - UI Location: modal launched from Update from main / Merge flow
  - Trigger: click "Resolve conflicts"
  - Inputs: per-conflict pick "main" or "branch" (side-by-side: main=left, branch=right); or Resolve all → Pick main / Pick branch
  - Outputs: each conflict tagged with chosen source; on Next, branch updated with selections
  - Related: Update from main, Merge branch
  - Article: Get updates from main files

- **Feature:** Restore previous branch / main version (rollback merge or update)
  - Domain: Branching and merging
  - UI Location: file-name menu → Show version history → right sidebar
  - Trigger: select earlier checkpoint → ellipsis → Restore this version
  - Inputs: checkpoint selection
  - Outputs: two autosave checkpoints created (current + restored); branch or main reverted; restoring main affects all collaborators
  - Related: Incomplete merges/updates, Branch merge checkpoint
  - Article: Get updates from main files; Incomplete merges or updates

- **Feature:** View all branches (Branches modal)
  - Domain: Branching and merging
  - UI Location: modal launched from file-name menu → "See all branches", or from file browser tile dropdown
  - Trigger: menu item
  - Inputs: tab selection: Active / Archived / Yours
  - Outputs: list of branches; per-row actions: Open, Copy link, Merge, Archive, Rename, Restore
  - Related: All branching steps
  - Article: View and manage branches

- **Feature:** File-browser branch indicator + dropdown
  - Domain: Branching and merging
  - UI Location: file tile in file browser
  - Trigger: passive (icon shows when file has branches); dropdown to switch
  - Inputs: dropdown selection
  - Outputs: opens main file or selected branch; shows total branch count under file name
  - Related: View and manage branches
  - Article: View and manage branches

- **Feature:** Archive / Restore branch
  - Domain: Branching and merging
  - UI Location: branches modal row ellipsis; file-name menu on branch
  - Trigger: Archive (active → Archived tab); Restore (Archived → Active)
  - Inputs: click
  - Outputs: branch state changes; merged branches cannot be restored
  - Related: Branches modal
  - Article: View and manage branches

- **Feature:** Rename branch
  - Domain: Branching and merging
  - UI Location: branches modal row ellipsis
  - Trigger: ellipsis → Rename
  - Inputs: new name (Enter to commit)
  - Outputs: branch identifier updated everywhere (incl. version history)
  - Related: Branches modal
  - Article: View and manage branches

- **Feature:** Duplicate branch as new file
  - Domain: Branching and merging
  - UI Location: file-name menu in left sidebar
  - Trigger: caret → "Duplicate as new file"
  - Inputs: confirm
  - Outputs: new standalone file in same location, name `Main : branch (Copy)`; severs link to main file (cannot merge back)
  - Related: Publish to Community workaround
  - Article: Guide to branching; View and manage branches

- **Feature:** Request branch review
  - Domain: Branching and merging
  - UI Location: file-name menu on branch → Review and merge changes (modal)
  - Trigger: Add reviewers in modal → Request review → optional description → Send to reviewers
  - Inputs: reviewer selection (suggestions: editors of main; search Other team members), description text
  - Outputs: reviewers get in-app + email notification; branch tagged "In review"
  - Related: Review changes, Resend request
  - Article: Request a branch review

- **Feature:** Review status badge (In review / Changes suggested / Approved)
  - Domain: Branching and merging
  - UI Location: branch name area in toolbar; Branch review modal
  - Trigger: passive (driven by reviewer action)
  - Inputs: reviewer outcome
  - Outputs: gray "In review" / yellow "Changes suggested" / green "Approved" badge; "View comments" banner if reviewer left layer comments
  - Related: Request review
  - Article: Request a branch review

- **Feature:** Resend review request
  - Domain: Branching and merging
  - UI Location: Branch review modal
  - Trigger: "Request another review" → update description → Send to reviewer
  - Inputs: optional updated description
  - Outputs: reviewer re-notified
  - Related: Request review
  - Article: Request a branch review

- **Feature:** Approve branch
  - Domain: Branching and merging
  - UI Location: Branch review modal → "Add your review"
  - Trigger: select Approve → optional comment → Submit
  - Inputs: optional comment
  - Outputs: "Approved" badge next to branch name; if reviewer has edit access to main, can also merge
  - Related: Suggest changes, Merge branch
  - Article: Review branch changes

- **Feature:** Suggest changes (review outcome)
  - Domain: Branching and merging
  - UI Location: Branch review modal → "Add your review"
  - Trigger: select Suggest changes → optional comment → Submit
  - Inputs: optional comment + optional canvas comments on branch
  - Outputs: "Changes suggested" badge; comments scoped to branch (do not merge to main)
  - Related: Approve, Comments
  - Article: Review branch changes

- **Feature:** Branch diff viewer (side-by-side / overlay)
  - Domain: Branching and merging
  - UI Location: Branch review / merge modal main panel
  - Trigger: select layer or page in left sidebar of modal
  - Inputs: toggle Side by side or Overlay; opacity slider in Overlay; zoom in / out / Fit; arrows to step through changes
  - Outputs: visual diff of added / edited / removed objects; main on left vs branch on right; overlay with adjustable opacity
  - Related: Approve / Suggest changes / Merge
  - Article: Review branch changes; Merge branch into main file

- **Feature:** Edit own review
  - Domain: Branching and merging
  - UI Location: Branch review modal left sidebar
  - Trigger: ellipsis next to your name → edit comment text
  - Inputs: edited text
  - Outputs: review comment updated
  - Related: Review again
  - Article: Review branch changes

- **Feature:** Review again
  - Domain: Branching and merging
  - UI Location: Branch review modal bottom
  - Trigger: "Review again" → Approve or Suggest changes → Submit
  - Inputs: outcome + optional comment
  - Outputs: latest review supersedes prior badge
  - Related: Approve / Suggest changes
  - Article: Review branch changes

- **Feature:** Merge branch into main
  - Domain: Branching and merging
  - UI Location: Branch review modal → Merge button
  - Trigger: click Merge (after resolving any pending updates from main)
  - Inputs: optional merge name + description (Edit merge description)
  - Outputs: branch changes applied to main; branch auto-archived + locked; "Branch merged" checkpoint added to main version history; pre-merge checkpoint also added
  - Related: Resolve conflicts, Version history
  - Article: Merge branch into main file
  - Note: blocked if file has memory limit banner

- **Feature:** Edit merge description
  - Domain: Branching and merging
  - UI Location: post-merge confirmation toast / version history entry
  - Trigger: click Edit merge description on toast or in version history
  - Inputs: name + description
  - Outputs: stored on main file's merge checkpoint
  - Related: Merge branch
  - Article: Merge branch into main file

- **Feature:** Branch / merge version-history checkpoints
  - Domain: Branching and merging
  - UI Location: right sidebar version history
  - Trigger: passive (auto-created)
  - Inputs: branch lifecycle events
  - Outputs: checkpoints labeled "Branch created", "Updated from main", "Before update", "Before merge", "Branch merged" (with branch-merge icon)
  - Related: Restore version
  - Article: Guide to branching; Incomplete merges or updates

### Import and export

- **Feature:** Import images / vectors / videos / GIFs to design file
  - Domain: Import and export
  - UI Location: canvas (drag-drop), main menu (File > Place image), shortcut
  - Trigger: drag-drop onto canvas / menu item / clipboard paste
  - Inputs: PNG, JPG, SVG, GIF, video file types
  - Outputs: image/video/vector layers placed on canvas
  - Related: Add images and videos to design files; Bulk add images and videos; Use animated GIFs in prototypes; Copy assets between design tools
  - Article: Guide to imports in Figma Design

- **Feature:** Import design / project file via file browser
  - Domain: Import and export
  - UI Location: file browser (Create new dropdown > Import); also drag-drop into file browser
  - Trigger: click "Create new" > Import > Import from computer; or drag-drop
  - Inputs: .sketch, .fig, .jam, .deck, .buzz, .site, .make, .pptx, PNG, JPG
  - Outputs: new file(s) added to drafts/project; conversion if .sketch
  - Related: Import Sketch files; Save a local copy of files
  - Article: Import files to the file browser

- **Feature:** Import Sketch file (.sketch -> Figma conversion)
  - Domain: Import and export
  - UI Location: file browser (Create > Import) OR editor (Main menu > File > New from Sketch file)
  - Trigger: menu item / file browser dropdown / drag-drop
  - Inputs: .sketch file (artboards, pages, symbols, fonts)
  - Outputs: Figma Design file; artboards->frames, symbols->components, pages preserved; styles NOT retained
  - Related: Import files to the file browser; Copy assets between design tools; Publish a library; Manage missing fonts
  - Article: Import Sketch files

- **Feature:** Paste assets from other tools as SVG (clipboard import)
  - Domain: Import and export
  - UI Location: canvas right-click menu
  - Trigger: right-click canvas > "Paste here" (after copy as SVG in source tool)
  - Inputs: SVG on system clipboard (note: SVG marker/pattern elements stripped)
  - Outputs: vector layers on canvas at click location
  - Related: Copy as SVG; Guide to imports
  - Article: Copy assets between design tools

- **Feature:** Copy as SVG / Copy as PNG (clipboard export)
  - Domain: Import and export
  - UI Location: right-click context menu on selected object > Copy/Paste as
  - Trigger: right-click > Copy/Paste as > Copy as SVG / Copy as PNG
  - Inputs: selected object(s)
  - Outputs: SVG or PNG payload on system clipboard
  - Related: Paste assets into Figma; Export from Figma Design
  - Article: Copy assets between design tools

- **Feature:** Slice tool (region export)
  - Domain: Import and export
  - UI Location: toolbar > Region tools dropdown
  - Trigger: select Slice tool, click+drag on canvas
  - Inputs: rectangular region on canvas; requires `can edit` access
  - Outputs: a Slice object that can carry export configurations; absolute padding boundary
  - Related: Export from Figma Design; Ignore overlapping layers (slice-specific behavior)
  - Article: Export from Figma Design

- **Feature:** Add export configuration on selection
  - Domain: Import and export
  - UI Location: right sidebar > Export section (bottom in Design Mode edit; under Properties tab in view-mode; Dev Mode right sidebar when object selected)
  - Trigger: click "+" in Export section
  - Inputs: scale, suffix, format (PNG/JPG/SVG/PDF), format-specific options
  - Outputs: stored export config(s) on the selection (multiple allowed)
  - Related: Export formats and settings; Bulk export; Slice tool
  - Article: Export from Figma Design

- **Feature:** Export single selection
  - Domain: Import and export
  - UI Location: right sidebar > Export section > Export button; Preview link
  - Trigger: click Export (after configuring)
  - Inputs: configured selection; deselected canvas exports current page
  - Outputs: file(s) downloaded; browser downloads dir or desktop save dialog; slash-separated layer names create nested folders
  - Related: Add export configuration; Export formats and settings
  - Article: Export from Figma Design

- **Feature:** Bulk export (page-wide)
  - Domain: Import and export
  - UI Location: Main menu > File > Export; modal dialog
  - Trigger: shortcut Shift+Cmd+E (Mac) / Shift+Ctrl+E (Win), or menu
  - Inputs: all selections on current page that have export configs; per-row include/exclude checkboxes
  - Outputs: batch file download of selected configs; thumbnail preview, scale/format/dimension visible
  - Related: Add export configuration; Export from Figma Design
  - Article: Export from Figma Design

- **Feature:** Export as PNG
  - Domain: Import and export
  - UI Location: Export section format dropdown
  - Trigger: select PNG in format dropdown
  - Inputs: scale, suffix, ignore overlapping layers, include bounding box (text), image quality
  - Outputs: 32-bit RGBA .png (always with alpha)
  - Related: Export formats and settings; Image resampling
  - Article: Export formats and settings

- **Feature:** Export as JPG
  - Domain: Import and export
  - UI Location: Export section format dropdown
  - Trigger: select JPG in format dropdown
  - Inputs: scale, suffix, ignore overlapping layers, include bounding box (text), image quality (default High), image resampling
  - Outputs: lossy raster .jpg (no transparency)
  - Related: Pixel preview
  - Article: Export formats and settings

- **Feature:** Export as SVG
  - Domain: Import and export
  - UI Location: Export section format dropdown
  - Trigger: select SVG in format dropdown
  - Inputs: ignore overlapping layers, include bounding box, include "id" attribute, outline text, simplify stroke (1x scale only)
  - Outputs: XML SVG; text exported as glyphs by default; strokes exported as fills
  - Related: Copy as SVG; Outline text; Simplify stroke
  - Article: Export formats and settings

- **Feature:** Export as PDF
  - Domain: Import and export
  - UI Location: Export section format dropdown
  - Trigger: select PDF in format dropdown
  - Inputs: image quality (default Medium), image resampling; 1x only
  - Outputs: PDF 1.7 file; text as glyphs (selectable but not editable); Plus darker / Plus lighter blend modes unsupported
  - Related: iOS asset workflow
  - Article: Export formats and settings

- **Feature:** Export scale (multiplier / fixed dimension)
  - Domain: Import and export
  - UI Location: Export section scale field
  - Trigger: type value with `x` (multiplier), `w` (fixed width), or `h` (fixed height)
  - Inputs: numeric value + suffix; default 72 DPI base
  - Outputs: rendered at chosen scale (1x, 2x, 3x, etc.); SVG/PDF locked to 1x
  - Related: Suffix; Image resampling
  - Article: Export formats and settings

- **Feature:** Export suffix
  - Domain: Import and export
  - UI Location: Export section suffix text field
  - Trigger: type into suffix field
  - Inputs: arbitrary string
  - Outputs: appended to filename on export (e.g., HomePagedraft.png)
  - Related: Slash-separated naming for nested folder export
  - Article: Export formats and settings

- **Feature:** Export color profile selection
  - Domain: Import and export
  - UI Location: Advanced export settings (gear icon) > color profile dropdown
  - Trigger: open advanced export settings; pick from dropdown
  - Inputs: "Same as file", sRGB, or Display P3
  - Outputs: file rendered in chosen color profile; defaults to file's profile
  - Related: Color management
  - Article: Export formats and settings

- **Feature:** Image resampling option
  - Domain: Import and export
  - UI Location: Advanced export settings > Image resampling dropdown
  - Trigger: open advanced export settings
  - Inputs: Detailed (bicubic, default) or Basic (nearest-neighbor)
  - Outputs: applied during PNG/JPG/PDF rasterization
  - Related: Scale
  - Article: Export formats and settings

- **Feature:** Ignore overlapping layers
  - Domain: Import and export
  - UI Location: Advanced export settings checkbox
  - Trigger: toggle (default on for PNG/JPG/SVG)
  - Inputs: boolean; special semantics when applied to a Slice inside a frame/group
  - Outputs: only selected layer(s) included vs. intersecting layers also rendered
  - Related: Slice tool
  - Article: Export formats and settings

- **Feature:** Include bounding box (text only)
  - Domain: Import and export
  - UI Location: Advanced export settings checkbox (text layer selected)
  - Trigger: toggle
  - Inputs: text layer selection
  - Outputs: export sized to bounding box (incl. empty space) vs. tight to glyphs
  - Related: Outline text
  - Article: Export formats and settings

- **Feature:** Include "id" attribute (SVG)
  - Domain: Import and export
  - UI Location: Advanced export settings checkbox (SVG)
  - Trigger: toggle
  - Inputs: SVG format selected
  - Outputs: SVG `<svg>` includes `id` attribute derived from layer name
  - Related: Outline text; Simplify stroke
  - Article: Export formats and settings

- **Feature:** Outline text (SVG)
  - Domain: Import and export
  - UI Location: Advanced export settings checkbox (SVG)
  - Trigger: toggle (default on if any text selected)
  - Inputs: SVG format
  - Outputs: text rendered as path glyphs (not editable) vs. as text (editable)
  - Related: Include bounding box
  - Article: Export formats and settings

- **Feature:** Simplify stroke (SVG)
  - Domain: Import and export
  - UI Location: Advanced export settings checkbox (SVG)
  - Trigger: toggle (default on for vector network with inside/outside stroke)
  - Inputs: SVG format, vector network with non-center stroke
  - Outputs: rewrites strokes so other renderers handle inside/outside correctly
  - Related: Include "id" attribute
  - Article: Export formats and settings

- **Feature:** Hide layer fill in exports ("Show in exports" toggle)
  - Domain: Import and export
  - UI Location: right sidebar > Fill section checkbox
  - Trigger: deselect "Show in exports" on a fill row
  - Inputs: a fill on a frame/layer
  - Outputs: that fill omitted from exported asset (visible on canvas, hidden in export)
  - Related: Add export configuration
  - Article: Export from Figma Design

- **Feature:** Save .fig file (entire-file export)
  - Domain: Import and export
  - UI Location: main menu > File > Save local copy
  - Trigger: menu item
  - Inputs: current Figma Design file
  - Outputs: .fig file saved to disk
  - Related: Import files to the file browser
  - Article: Export from Figma Design

- **Feature:** Restrict copying / sharing (gates export)
  - Domain: Import and export (cross-cuts file permissions)
  - UI Location: file share menu (toggled by file owner)
  - Trigger: file owner setting
  - Inputs: file-level permission flag
  - Outputs: hides Export section for viewers; blocks Copy as PNG/SVG
  - Related: Export from Figma Design; Copy as SVG
  - Article: Export from Figma Design

## Dev Mode

- **Feature:** Dev Mode toggle (mode switch)
  - Domain: Tour the interface
  - UI Location: top-right of toolbar (toggle button)
  - Trigger: click toggle / shortcut `Shift D` / opening a Dev Mode link
  - Inputs: current Figma Design file
  - Outputs: switches whole UI to Dev Mode (different sidebar, toolbar, right panel)
  - Related: Ready for dev view, Inspect panel, Focus view
  - Article: Guide to Dev Mode

- **Feature:** Mark as ready for dev (status setter)
  - Domain: Statuses & handoff
  - UI Location: toolbar button next to selection / inline label next to section/frame name
  - Trigger: click "Mark as ready for dev" with section/frame/component selected
  - Inputs: selected section, frame, or component
  - Outputs: dev status badge, entry in Ready for dev view, push notification to subscribers
  - Related: Mark as completed, Ready for dev view, Notifications, Sections (Figma Design)
  - Article: Dev Mode statuses and notifications

- **Feature:** Mark as completed (status)
  - Domain: Statuses & handoff
  - UI Location: dropdown on the Ready-for-dev badge / focus view top bar
  - Trigger: click status badge → "Mark as completed"
  - Inputs: a design currently Ready-for-dev (Org/Enterprise only)
  - Outputs: Completed badge, version-history entry, notification
  - Related: Mark as ready for dev, Focus view
  - Article: Dev Mode statuses and notifications

- **Feature:** Changed-state status update
  - Domain: Statuses & handoff
  - UI Location: badge on the Ready-for-dev / Completed indicator
  - Trigger: any meaningful design edit after marking; designer clicks badge → optional reason → "Done with changes"
  - Inputs: change reason (text)
  - Outputs: status reset, change-reason notification
  - Related: Compare changes
  - Article: Dev Mode statuses and notifications

- **Feature:** Inspect panel (right sidebar)
  - Domain: Inspect
  - UI Location: right sidebar (replaces Design panel)
  - Trigger: select any layer in Dev Mode
  - Inputs: selected layer
  - Outputs: layer name/type, last-edited, properties (Code or List view), styles, variables, dev resources, assets, exports, component metadata
  - Related: Code section, Variables in Dev Mode, Compare changes, Dev resources
  - Article: Guide to Dev Mode / Guide to inspecting

- **Feature:** Code section (autogen snippets)
  - Domain: Inspect
  - UI Location: Code section inside Inspect panel
  - Trigger: select layer; pick language/unit from dropdown
  - Inputs: language (CSS / SwiftUI / UIKit / Compose / XML), unit (px/rem/pt/dp/sp), unit scale, codegen plugin
  - Outputs: copyable code snippet (box model or typographic preview), variable refs as code
  - Related: Code Connect, Codegen plugins, Variables
  - Article: Use code snippets in Dev Mode

- **Feature:** List/Code toggle for layer properties
  - Domain: Inspect
  - UI Location: toggle inside layer-properties section of Inspect panel
  - Trigger: click toggle
  - Inputs: selected layer
  - Outputs: List view (clickable property:value pairs, click-to-copy) OR Code view (snippet)
  - Related: Code section
  - Article: Guide to Dev Mode

- **Feature:** Code Connect (UI + CLI)
  - Domain: Code generation
  - UI Location: Code section shows "connected" snippets in place of autogen; setup via Code Connect UI panel or external CLI
  - Trigger: viewing a component that has a Code Connect mapping
  - Inputs: mapped repo path / component name / property mappings
  - Outputs: real design-system code snippet, component playground previews, AI codegen previews
  - Related: Code section, Component playground, MCP server
  - Article: Code Connect

- **Feature:** Dev resources (external links per layer)
  - Domain: Inspect
  - UI Location: Inspect panel → Layer options → "Add a dev resource link"
  - Trigger: click Layer options → paste URL → Enter
  - Inputs: URL (GitHub/Jira/Storybook/VS Code link), selected layer
  - Outputs: clickable resource link on the layer (inherited by instances if added to main component)
  - Related: Figma for VS Code, Plugins
  - Article: Link Dev resources to layers in Dev Mode

- **Feature:** Variable details modal
  - Domain: Inspect (variables)
  - UI Location: floating modal off the Inspect panel
  - Trigger: click variable name in code snippet, OR click variable-details icon in Selection colors
  - Inputs: variable reference on a layer
  - Outputs: name, host file, collection, mode, alias chain to raw value, scope, code snippet; supports mode-switching
  - Related: Suggested variables, Variables modal
  - Article: Variables in Dev Mode

- **Feature:** Suggested variables
  - Domain: Inspect (variables)
  - UI Location: floating modal next to clicked raw value in Inspect
  - Trigger: click a raw value in Inspect panel
  - Inputs: raw value; matched against existing local/library variables (same value + valid scope)
  - Outputs: list of candidate variable names; click to copy name
  - Related: Variable details
  - Article: Variables in Dev Mode

- **Feature:** Read-only Variables modal/table
  - Domain: Inspect (variables)
  - UI Location: modal opened from Inspect panel "Open variables table" (when nothing selected)
  - Trigger: deselect everything → Variables section → "Open variables table"
  - Inputs: local variable collections in file
  - Outputs: read-only table of variables × modes; click to copy values, click to open Variable details
  - Related: Variable details
  - Article: Variables in Dev Mode

- **Feature:** Component playground ("Explore component behavior")
  - Domain: Inspect (components)
  - UI Location: link in Inspect panel below component info → opens playground modal
  - Trigger: select component/instance → click "Explore component behavior"
  - Inputs: component properties, variable modes
  - Outputs: live preview that doesn't mutate the source design
  - Related: Variables in Dev Mode, Code Connect
  - Article: Guide to Dev Mode

- **Feature:** Compare changes (frame history)
  - Domain: Versioning
  - UI Location: link in Inspect panel ("Compare changes" / "Compare with main component") → modal
  - Trigger: select frame/component → click Compare changes (or Shift-click two components)
  - Inputs: top-level frame or component, optional second selection
  - Outputs: version-history timeline, side-by-side / overlay views, edited-layer list (Edited/Added/Deleted), per-layer code & property diff
  - Related: Focus view version history, Detached components (Figma Design)
  - Article: Compare changes in Dev Mode

- **Feature:** Annotations
  - Domain: Annotate
  - UI Location: toolbar Annotate tool, green dot markers on canvas, panel content on click
  - Trigger: `Shift T` or toolbar button → click target layer
  - Inputs: text body, optional layer Property pickers, category label
  - Outputs: persistent annotation node on canvas; properties stay live as design changes
  - Related: Measurements, Annotation categories filter
  - Article: Add measurements and annotate designs

- **Feature:** Annotation categories & filtering
  - Domain: Annotate
  - UI Location: category dropdown in annotation panel; filter via right-click → Filter by, or zoom menu → Annotations
  - Trigger: editing annotation label / right-click annotation
  - Inputs: category (Development / Interaction / Accessibility / Content / custom)
  - Outputs: colored label on annotation; canvas filter that hides others
  - Related: Hide annotations (View menu)
  - Article: Add measurements and annotate designs

- **Feature:** Persistent measurements (Shift M)
  - Domain: Annotate
  - UI Location: toolbar Measure tool; renders on canvas as line + label
  - Trigger: `Shift M` → hover layer → click-drag to second layer
  - Inputs: start layer edge, end layer
  - Outputs: persistent measurement node; double-click to edit text; Delete/Backspace to remove
  - Related: Alt/Option hover-measure (ephemeral)
  - Article: Add measurements and annotate designs

- **Feature:** Hover-measure (ephemeral)
  - Domain: Annotate
  - UI Location: rendered on canvas only while modifier held
  - Trigger: select layer → hold `Alt` (Win) / `Option` (Mac) → hover another layer
  - Inputs: two layers
  - Outputs: red distance line + h/v measurements (not saved)
  - Related: Persistent measurements
  - Article: Guide to inspecting

- **Feature:** Asset / icon auto-detect & download
  - Domain: Inspect (assets)
  - UI Location: Assets section in Inspect panel
  - Trigger: select layer detected as icon/image/GIF/MP4 → hover → click download icon
  - Inputs: detected asset, file format choice (PNG/JPEG/SVG/PDF), source vs layer-export
  - Outputs: downloaded file (current size or original full-resolution source)
  - Related: Export, "Automatically detect icons" toggle (Main menu → View)
  - Article: Guide to inspecting / Guide to Dev Mode

- **Feature:** Export
  - Domain: Inspect (assets)
  - UI Location: Export section in Inspect panel (per-layer export configs)
  - Trigger: select layer(s) → "+" → set format/scale → Export
  - Inputs: PNG/JPG/SVG/PDF settings
  - Outputs: downloaded asset(s)
  - Related: Asset auto-detect, Specify size of image export
  - Article: Guide to inspecting

- **Feature:** Ready for dev view
  - Domain: Navigation / handoff
  - UI Location: full-canvas overlay opened from "Ready for dev" entry in left sidebar
  - Trigger: click "Ready for dev" in left sidebar (only appears if file has any dev statuses)
  - Inputs: filter (All/Ready/Completed), sort (Recent activity/Pages/Name)
  - Outputs: grid/list of all dev-status designs, status badge per card, click → focus view
  - Related: Focus view, Statuses
  - Article: Dev Mode ready for dev view

- **Feature:** Focus view (single-design isolation)
  - Domain: Navigation / handoff
  - UI Location: full-canvas overlay; Inspect + Plugins panels unchanged on right; version history side panel
  - Trigger: click design in Ready-for-dev view, OR canvas: click dev status → "Show in focus view"
  - Inputs: a single ready-for-dev design
  - Outputs: isolated design, scoped version history, interactive resize / mode-switch (temporary, viewer-local), Mark as completed button
  - Related: Compare changes, Variables, Ready for dev view
  - Article: Dev Mode focus view

- **Feature:** Interactive inspection in focus view
  - Domain: Focus view
  - UI Location: handles on focused frame + dropdown for variable mode
  - Trigger: drag width/height handles or type dimension; pick a variable mode
  - Inputs: width/height values, variable mode
  - Outputs: viewer-local preview of resized frame / themed frame; reset button restores
  - Related: Variables in Dev Mode, Component playground
  - Article: Dev Mode focus view

- **Feature:** Mark as completed (focus view button)
  - Domain: Focus view
  - UI Location: top-right of focus view
  - Trigger: click "Mark as completed"
  - Inputs: focused design (Org/Enterprise)
  - Outputs: Completed badge + version-history entry + notification
  - Related: Dev statuses
  - Article: Dev Mode focus view

- **Feature:** Dev Mode notifications
  - Domain: Statuses & handoff
  - UI Location: in-app, email, mobile, Slack/Teams (integrations); per-file settings via Comment-mode Settings dropdown
  - Trigger: status changes (Ready-for-dev set, Changed reset, Completed); user must have viewed file in Dev Mode w/ Full or Dev seat
  - Inputs: per-file setting (Status changes / Nothing)
  - Outputs: grouped notifications with Inspect-in-Dev-Mode link (→ ready-for-dev view) and per-design link (→ focus view)
  - Related: Statuses
  - Article: Dev Mode statuses and notifications

- **Feature:** Search (Dev Mode left sidebar)
  - Domain: Navigation
  - UI Location: search field in left sidebar
  - Trigger: `Cmd/Ctrl F`
  - Inputs: query text, scope (current page / all pages), filters (text/frame/shape/widget/slice…)
  - Outputs: list of matching layers; click jumps to layer; arrow nav between hits
  - Related: Layers panel
  - Article: Navigate designs in Dev Mode

- **Feature:** Frame paging (top-level frame nav)
  - Domain: Navigation
  - UI Location: arrow buttons over canvas + arrow keys
  - Trigger: select top-level frame → ←/→
  - Inputs: current page's frames in order
  - Outputs: selection moves to next/prev frame
  - Related: Search, Pages list
  - Article: Navigate designs in Dev Mode

- **Feature:** Layers panel (Dev Mode left sidebar)
  - Domain: Navigation
  - UI Location: left sidebar; replaces nav panel when a top-level frame is selected
  - Trigger: select a top-level frame
  - Inputs: selected frame's nested layer tree
  - Outputs: scoped layer hierarchy; ready-for-dev assets pinned; section content prioritized
  - Related: Sections (Figma Design), Ready for dev
  - Article: Guide to Dev Mode

- **Feature:** Plugins tab (Dev Mode)
  - Domain: Plugins
  - UI Location: right sidebar Plugins tab
  - Trigger: click Plugins tab
  - Inputs: recently used + Community recommended dev-mode plugins
  - Outputs: pinned plugins from org admin, codegen plugins (extend Code section), auto-run plugin
  - Related: Code section, Org Dev Mode settings
  - Article: Guide to Dev Mode / Manage Dev Mode settings for an organization

- **Feature:** Org-level Dev Mode admin settings
  - Domain: Admin
  - UI Location: Admin → Settings → Extensions → Dev Mode settings
  - Trigger: org admin opens panel
  - Inputs: pinned plugin URLs, default code language + unit, single auto-run plugin URL
  - Outputs: applied to all org files (excl. drafts)
  - Related: Plugins tab, Code section
  - Article: Manage Dev Mode settings for an organization

- **Feature:** Figma for VS Code extension
  - Domain: IDE integration
  - UI Location: VS Code activity bar → Figma; Inspect panel surfaces "Open in VS Code" option
  - Trigger: install extension + sign in; either start in VS Code or jump from Inspect "Options → Open in VS Code"
  - Inputs: design file, selected layer, codebase
  - Outputs: file/section/page nav, code snippets, dev resources, assets, comments, autocomplete suggestions, codegen-plugin support
  - Related: Dev resources, Code section, Comments
  - Article: Figma for VS Code

- **Feature:** Figma MCP server (read context for AI agents)
  - Domain: AI / IDE integration
  - UI Location: external MCP client (Cursor, Claude Code, VS Code, Codex, Windsurf…); requires either remote `mcp.figma.com/mcp` or desktop server in Figma desktop app
  - Trigger: paste a Figma URL into MCP client and prompt
  - Inputs: Figma node URL, prompt
  - Outputs: design context (variables, components, layout, code snippets), Code Connect-aware code generation
  - Related: Code Connect, Skills, use_figma write tool
  - Article: Guide to the Figma MCP server / Get started with the Figma MCP server

- **Feature:** Write-to-canvas via use_figma (MCP)
  - Domain: AI / write integration
  - UI Location: invoked from MCP client (no Figma UI surface beyond resulting canvas changes)
  - Trigger: prompt with figma-use skill + file URL
  - Inputs: file URL, prompt, design system context
  - Outputs: real Figma frames/components/variables/auto-layout written to file (Full seat outside drafts; Dev seat in drafts only)
  - Related: figma-use skill, Code Connect
  - Article: Figma MCP server FAQs / Figma skills for MCP

- **Feature:** Code-to-canvas (generate_figma_design)
  - Domain: AI integration
  - UI Location: triggered from MCP client; in-browser capture toolbar appears
  - Trigger: prompt MCP client to capture live UI
  - Inputs: live web app URL (prod/staging/localhost)
  - Outputs: new Figma file with flat layers reflecting captured UI
  - Related: use_figma (refine after capture)
  - Article: Guide to the Figma MCP server

- **Feature:** Figma MCP skills bundle
  - Domain: AI integration
  - UI Location: installed in MCP client (slash commands like `/figma-use`)
  - Trigger: install Figma plugin/skills, invoke via slash command
  - Inputs: skill-specific prompt args
  - Outputs: orchestrated multi-tool MCP flows (figma-use, figma-implement-design, figma-create-design-system-rules, figma-create-new-file, figma-code-connect-components, figma-generate-library, figma-generate-design)
  - Related: MCP server tools, Code Connect
  - Article: Figma skills for MCP

- **Feature:** "Automatically detect icons" toggle
  - Domain: Inspect settings
  - UI Location: Main menu → View → Automatically detect icons
  - Trigger: deselect to inspect underlying vector layers individually
  - Inputs: toggle state
  - Outputs: changes whether Inspect shows icon as a single asset or per-vector
  - Related: Asset / icon auto-detect
  - Article: Guide to Dev Mode

## Projects

> Note on scope: the "Projects" section in this corpus is a *tutorial collection* (mini-projects / starter projects). The articles do not introduce new product surfaces; they exercise existing Figma Design, Figma Draw, FigJam, and Figma Buzz tools through guided builds. Features below are the concrete tools/UI affordances those tutorials drive — useful for the mock app because they enumerate which tools must exist and what each operation looks like end-to-end.

- **Feature:** Text tool (create text layer)
  - Domain: Figma Design canvas tools
  - UI Location: Toolbar (top), or `T` shortcut
  - Trigger: click toolbar icon / `T` / click on canvas to place
  - Inputs: typed string, click position, then Typography panel (font family, size, weight)
  - Outputs: new text layer in Layers panel, name auto-matches typed string
  - Related: Typography panel; Rename Layers; Truncate text [cross: Figma Design]
  - Article: Create a simple button component

- **Feature:** Shape tools (Rectangle / Ellipse / Polygon / Star / Line)
  - Domain: Figma Design / Figma Draw canvas tools
  - UI Location: Toolbar shape-tools dropdown
  - Trigger: dropdown click, single-letter shortcut (`R`, `O`), then click or click-drag on canvas
  - Inputs: drag dimensions, `Shift` to constrain proportions, W/H fields in right sidebar
  - Outputs: shape layer with default fill, bounding box, handles
  - Related: Fill, Stroke, Corner radius, Boolean operations
  - Article: Design a search icon; Create a reusable icon grid; Create an illustration in Figma Design

- **Feature:** Frame tool
  - Domain: Figma Design containers
  - UI Location: Toolbar (`F`); right sidebar exposes preset device sizes (iPhone 14 Pro, Plugin/file cover, etc.)
  - Trigger: `F` then click-drag, OR select preset in right sidebar
  - Inputs: drag dimensions, preset size choice, name (rename via double-click in Layers)
  - Outputs: frame container in Layers panel, child layers nested inside
  - Related: Auto layout; Constraints; Set as thumbnail; Layout grid
  - Article: Create a photo gallery prototype; Design a file thumbnail

- **Feature:** Pen tool / vector edit mode
  - Domain: Figma Design / Figma Draw vector authoring
  - UI Location: Toolbar (`P`); secondary toolbar appears in vector edit
  - Trigger: `P`, click points; `Enter` on existing layer to enter vector edit; `Enter`/`Esc` to exit
  - Inputs: click points, drag handles, Bend tool, Variable width tool
  - Outputs: vector layer (path), can be open or closed; Mirror angle/length on points
  - Related: Boolean operations; Flatten; Stroke (weight, end cap); Pencil tool
  - Article: Design a search icon; Create a noodle bowl illustration; Create a strawberry illustration

- **Feature:** Pencil tool
  - Domain: Figma Draw freehand drawing
  - UI Location: Toolbar (`Shift P`)
  - Trigger: keyboard shortcut, click-drag freehand
  - Inputs: cursor path, stroke weight, fill color
  - Outputs: rough vector path; can be smoothed/closed in vector edit mode
  - Related: Vector edit mode; Stroke
  - Article: Create a strawberry illustration

- **Feature:** Arc tool (on ellipses)
  - Domain: Figma Draw / shape modifier
  - UI Location: Arc handle appears on hover over selected ellipse; also in right sidebar Arc settings
  - Trigger: hover ellipse, drag arc handle, OR enter Sweep/Ratio % values
  - Inputs: Sweep %, Ratio %
  - Outputs: arc/semicircle/ring shape (non-destructive — original bounding box preserved)
  - Related: Flatten (to bake the new shape); Ellipse tool
  - Article: Create a noodle bowl illustration; Create an orange illustration

- **Feature:** Boolean operations (Union / Subtract / Intersect / Exclude)
  - Domain: Figma Design / Figma Draw vector composition
  - UI Location: Right sidebar / toolbar "Union selection" button
  - Trigger: select 2+ layers → Union selection (also right-click menu)
  - Inputs: selected vector/shape layers
  - Outputs: combined boolean layer; bounding box hugs combined geometry
  - Related: Flatten; Group; vector edit mode
  - Article: Design a search icon; Design a file thumbnail; Illustrate a flower vase

- **Feature:** Flatten
  - Domain: Vector composition (destructive merge)
  - UI Location: Right-click → Flatten, or shortcut `Option/Alt + Shift + F`
  - Trigger: shortcut / context menu / secondary toolbar
  - Inputs: selected layers (frames, vectors, text)
  - Outputs: single Vector layer; child layers no longer separable
  - Related: Boolean operations; version history (undo)
  - Article: Create an orange illustration; Create a noodle bowl illustration

- **Feature:** Group / Frame selection
  - Domain: Layer organization
  - UI Location: shortcut `Cmd/Ctrl + G` (group); right-click → Frame selection
  - Trigger: select layers → shortcut or context menu
  - Inputs: selected layers
  - Outputs: nested container in Layers panel
  - Related: Auto layout (different from group); Sections
  - Article: Create a tooltip component set; Design a file thumbnail; Create an illustration

- **Feature:** Auto layout
  - Domain: Layout system
  - UI Location: Right sidebar Auto layout section; shortcut `Shift + A`
  - Trigger: select frame/object → `Shift A`, or right-click → Add auto layout
  - Inputs: Flow (horizontal/vertical), Alignment, Gap, Padding, Horizontal/Vertical resizing (Hug / Fill / Fixed), min/max W/H, Clip content
  - Outputs: responsive frame that auto-resizes to children or container
  - Related: Constraints; Frame tool; Components
  - Article: Create a simple button component; Create a responsive card; Create a tooltip component set

- **Feature:** Constraints
  - Domain: Layout (non-auto-layout)
  - UI Location: Right sidebar Constraints menu
  - Trigger: select child of frame → open Constraints
  - Inputs: horizontal (Left/Center/Right/Scale/Stretch) and vertical (Top/Center/Bottom/Scale/Stretch)
  - Outputs: child layer pins/anchors when parent resizes
  - Related: Auto layout; Frame
  - Article: Create a responsive card with auto layout and constraints

- **Feature:** Fill (solid / gradient / image / pattern)
  - Domain: Appearance
  - UI Location: Right sidebar Fill section + color picker modal
  - Trigger: click `+` in Fill section, click swatch to open picker
  - Inputs: hex color, opacity, gradient stops, image upload + crop modes, pattern source layer + tile/scale/spacing/alignment
  - Outputs: fill applied to selected layer
  - Related: Stroke; Eyedropper (`I`); Make an image (AI); Swap image
  - Article: Create a strawberry illustration (pattern); Create a photo gallery prototype (image); Illustrate a flower vase (gradient)

- **Feature:** Stroke
  - Domain: Appearance
  - UI Location: Right sidebar Stroke section
  - Trigger: click `+` in Stroke section
  - Inputs: fill (color), Position (Inside/Center/Outside), Weight, Dash, End points (Round/Square/Arrow), Stroke width profiles (Variable width via vector edit secondary toolbar)
  - Outputs: stroke applied; can be inverted with `Shift X` (swap fill/stroke)
  - Related: Vector edit mode; Pen tool
  - Article: Design a search icon; Create a noodle bowl illustration

- **Feature:** Effects (Drop shadow / Inner shadow / Layer blur / Background blur / Texture / Glass)
  - Domain: Appearance
  - UI Location: Right sidebar Effects section, dropdown selector
  - Trigger: click `+` in Effects, choose effect type, click effect to open settings panel
  - Inputs: X/Y offset, Blur, Spread, Color, Opacity; Texture has Size/Radius/Clip-to-shape; Glass has Light angle/intensity/Refraction/Depth/Dispersion/Frost
  - Outputs: visual effect applied; nests under layer
  - Related: Fill; Stroke
  - Article: Create a simple button component (drop shadow); Create a noodle bowl (inner shadow + texture); Illustrate a flower vase (glass)

- **Feature:** Corner radius (uniform + independent corners)
  - Domain: Appearance
  - UI Location: Right sidebar Appearance section
  - Trigger: enter value, or click "Independent corners" toggle
  - Inputs: single radius, OR per-corner radius
  - Outputs: rounded corners on frames/rectangles/vectors with corners
  - Related: Auto layout
  - Article: Create a tooltip component set; Create a simple button component

- **Feature:** Components (main component + instance)
  - Domain: Reusability
  - UI Location: Right sidebar / toolbar "Create component" button; shortcut `Opt/Alt + Cmd/Ctrl + K`
  - Trigger: select frame → Create component; create instances by `Opt/Alt`-drag from main, or from Assets panel
  - Inputs: a frame/group; layer naming with `/` becomes hierarchy in Assets
  - Outputs: main component (purple icon), instances; Assets panel populated under "Created in this file"
  - Related: Variants; Component sets; Properties (boolean, instance swap)
  - Article: Create a simple button component; Create a reusable icon grid

- **Feature:** Variants & component sets
  - Domain: Reusability
  - UI Location: Right sidebar "Create variant" / "Add variant"; purple-dashed component-set border on canvas; purple `+` to add variants
  - Trigger: select component → Create variant; or select multiple components → "Create component set" from toolbar dropdown
  - Inputs: variant property name, value(s); naming convention `name/value/value` auto-builds set
  - Outputs: component set with property keys & values surfaced on instances in right sidebar
  - Related: Components; Prototype interactive components; Boolean properties
  - Article: Design an interactive button component; Create a tooltip component set

- **Feature:** Component properties (Boolean / Text / Instance swap / Variant)
  - Domain: Reusability / API surface of a component
  - UI Location: Right sidebar Properties section on main component; "Apply variable/property" affordance on child layers
  - Trigger: select layer inside main → Apply variable/property → create property
  - Inputs: property name, default value
  - Outputs: toggleable/editable controls on instances
  - Related: Variants; Variables
  - Article: Design an interactive button component

- **Feature:** Variables (Boolean / Number / String / Color)
  - Domain: Design tokens / prototype state
  - UI Location: Right sidebar "Open variables" → modal; collections + groups
  - Trigger: with nothing selected, Open variables; create via `+`; assign via "Assign variable" or right-click on property
  - Inputs: type, name, default value, value per mode
  - Outputs: variable usable in layer properties, prototype Set variable actions, conditional expressions
  - Related: Conditional logic; Set variable action; component properties
  - Article: Create an onboarding flow with advanced prototyping

- **Feature:** Prototype connections
  - Domain: Prototyping
  - UI Location: Prototype tab in right sidebar (`Shift E`); blue `+` handle on selected object edge
  - Trigger: switch to Prototype tab → drag blue plus from object/frame to target → Interaction details modal
  - Inputs: Trigger (On click / On tap / While hovering / Mouse down/up/enter/leave / After delay / On drag / Key/Gamepad), Action (Navigate to / Change to / Open overlay / Close / Set variable / Open link / Conditional Check if/else), Animation (Instant/Dissolve/Smart animate/Move in/out/Push/Slide), Transition curve, Duration, Destination/target
  - Outputs: connection arrow on canvas; entry in Interactions list
  - Related: Smart animate; Variables; Variants (interactive components); Inline preview
  - Article: Design an interactive button; Create a loading animation; Create a photo gallery prototype

- **Feature:** Smart animate
  - Domain: Prototyping animation
  - UI Location: Animation dropdown in Interaction details modal
  - Trigger: pick "Smart animate" + curve + duration
  - Inputs: relies on matching layer names across source/target frames
  - Outputs: Figma tweens matching layers (position, size, rotation, opacity)
  - Related: Bulk rename layers; Prototype connections
  - Article: Create a loading animation; Create a photo gallery prototype

- **Feature:** Conditional logic & expressions in prototypes
  - Domain: Advanced prototyping
  - UI Location: Interaction details modal → Add action → "Check if / else"; "Set variable" with expression field
  - Trigger: in Interaction details, choose Check if/else; type expression like `topicsSelected > 0`
  - Inputs: condition expression, branch actions, value expressions (e.g. `topicsSelected + 1`, `"enabled"`)
  - Outputs: branched prototype behavior at runtime
  - Related: Variables; Set variable action
  - Article: Create an onboarding flow with advanced prototyping

- **Feature:** Inline preview / Present mode
  - Domain: Prototype playback
  - UI Location: Inline = `Shift Space` or Prototype-view → Preview; Present = toolbar Present button
  - Trigger: shortcut or button click
  - Inputs: starting flow, current variant/variables
  - Outputs: in-canvas (inline) or full-window (Present) interactive prototype
  - Related: Prototype connections; Flow starting points
  - Article: Design an interactive button; Create a loading animation; Create a photo gallery prototype

- **Feature:** Layout grid
  - Domain: Frame guides
  - UI Location: Right sidebar Layout grid section (only on selected frame)
  - Trigger: select frame → click `+` → Layout grid settings
  - Inputs: grid type (uniform/columns/rows), size, color, opacity
  - Outputs: visual guide in frame
  - Related: Snap to pixel grid (Zoom/view options); Pixel grid
  - Article: Create a reusable icon grid

- **Feature:** Smart selection
  - Domain: Layer alignment helper
  - UI Location: Pink handles appear on multi-selection of evenly-spaceable layers
  - Trigger: select 3+ similar layers → drag pink handles
  - Inputs: spacing values via drag
  - Outputs: redistributed layers
  - Related: Tidy up; Alignment controls
  - Article: Create a loading animation

- **Feature:** Tidy up
  - Domain: Layer alignment helper
  - UI Location: Right sidebar (appears on multi-select)
  - Trigger: button click on multi-select
  - Inputs: selection
  - Outputs: layers rearranged into grid/row, enables Smart selection
  - Article: Create a loading animation

- **Feature:** Alignment & distribution controls
  - Domain: Positioning
  - UI Location: Right sidebar alignment row (top of design panel on multi-select)
  - Trigger: select 1+ layer → click Align horizontal/vertical centers, distribute, etc.
  - Inputs: selected layers, optionally relative to parent frame
  - Outputs: aligned/distributed positions
  - Related: Smart selection; Constraints
  - Article: Create a reusable icon grid; Create a loading animation

- **Feature:** Bulk rename layers (`Cmd/Ctrl + R`)
  - Domain: Layer organization
  - UI Location: Modal opened by `Cmd/Ctrl + R`
  - Trigger: select 1+ layers → shortcut → enter "Rename to"
  - Inputs: pattern with optional numbering / current-name token
  - Outputs: layer names updated in bulk
  - Related: Smart animate (depends on matching names)
  - Article: Create a photo gallery prototype

- **Feature:** Lock / unlock layer
  - Domain: Layer organization
  - UI Location: Lock icon in Layers panel row; also in right sidebar
  - Trigger: click lock icon
  - Inputs: target layer
  - Outputs: layer cannot be selected/moved on canvas
  - Article: Design a file thumbnail; Create an illustration

- **Feature:** Selection colors panel
  - Domain: Bulk color editing
  - UI Location: Right sidebar (appears when multi-selecting layers with shared/varied colors)
  - Trigger: select frame containing colored layers → "Selection colors" section
  - Inputs: replace one color with another across selection
  - Outputs: bulk recolor
  - Article: Create a loading animation

- **Feature:** Eyedropper
  - Domain: Color sampling
  - UI Location: shortcut `I`
  - Trigger: `I` then click any pixel
  - Inputs: target pixel color
  - Outputs: applies sampled color to current fill/stroke target
  - Article: Create a noodle bowl illustration

- **Feature:** Copy/Paste properties
  - Domain: Style transfer
  - UI Location: shortcuts `Cmd/Ctrl + Opt/Alt + C` (copy properties), `Cmd/Ctrl + Opt/Alt + V` (paste properties)
  - Trigger: select source → copy properties; select target → paste properties
  - Inputs: source layer style
  - Outputs: target inherits style (fills, strokes, effects)
  - Article: Create a reusable icon grid

- **Feature:** Scale tool
  - Domain: Resizing
  - UI Location: shortcut `K`
  - Trigger: `K` then drag, or set Scale value
  - Inputs: scale factor
  - Outputs: proportional resize including strokes / effects
  - Related: regular resize handles (which don't scale stroke)
  - Article: Design a file thumbnail

- **Feature:** Transforms (Radial repeat / Linear repeat / Mirror)
  - Domain: Figma Draw non-destructive pattern generation
  - UI Location: Right sidebar transform buttons (Repeat group container)
  - Trigger: select layer → click transform → opens Transform settings
  - Inputs: Count, Gap, units; nested original layer remains editable
  - Outputs: Repeat group containing original + generated copies
  - Related: Pattern fill; Boolean operations
  - Article: Create an orange illustration; Illustrate a flower vase

- **Feature:** Pattern fill
  - Domain: Figma Draw fills
  - UI Location: Fill section → Pattern type
  - Trigger: add fill → choose Pattern → Select source layer
  - Inputs: source layer reference, Tile type (Square/Hexagonal), Direction, Scale, X/Y spacing, Alignment, Opacity
  - Outputs: tiled fill that updates if source layer changes; persists if source deleted
  - Related: Transforms; Fills
  - Article: Create a strawberry illustration; Create a social media post using Figma Draw

- **Feature:** Stroke width profiles / Variable width
  - Domain: Figma Draw vector strokes
  - UI Location: Vector edit mode secondary toolbar → Variable width
  - Trigger: enter vector edit → select Variable width tool → click point → enter width value
  - Inputs: per-point width values
  - Outputs: tapered stroke
  - Article: Create a noodle bowl illustration; Create a social media post using Figma Draw

- **Feature:** Offset vector path
  - Domain: Figma Draw vector ops
  - UI Location: secondary toolbar in vector edit (or right-click)
  - Trigger: select vector path → Offset vector
  - Inputs: offset distance
  - Outputs: parallel offset path
  - Article: Create a social media post using Figma Draw

- **Feature:** Text on a path
  - Domain: Figma Draw text
  - UI Location: select text + path → option in toolbar/right sidebar
  - Trigger: pair text layer with path → Text on path
  - Inputs: text content, target path
  - Outputs: text rendered along curve
  - Article: Create an orange illustration; Create a social media post using Figma Draw

- **Feature:** Truncate text
  - Domain: Text properties
  - UI Location: Right sidebar Text → Type settings → Truncate text
  - Trigger: select text → enable truncate
  - Inputs: Max lines
  - Outputs: text clipped with ellipsis when overflowing container
  - Article: Create a responsive card

- **Feature:** Text width modes (Hug / Fixed / Fill / Add max width)
  - Domain: Text + auto layout
  - UI Location: Width dropdown in right sidebar
  - Trigger: select text → Width dropdown → Add min/max width
  - Inputs: max/min width value
  - Outputs: text wraps at constraint
  - Article: Create a tooltip component set

- **Feature:** Make an image (AI)
  - Domain: Figma Design AI
  - UI Location: Actions menu → Make an image; or in Fill swatch
  - Trigger: select frame/layer → Make an image → enter prompt → Make it
  - Inputs: text prompt, optional context
  - Outputs: AI-generated image fill
  - Related: Fill (image); Replace image; Swap image
  - Article: Create a responsive card

- **Feature:** Set as thumbnail
  - Domain: File-level metadata
  - UI Location: Right-click on a frame → Set as thumbnail
  - Trigger: context menu
  - Inputs: selected frame
  - Outputs: that frame is used as the file's preview in the file browser / Community
  - Related: Frame presets (Plugin / file cover)
  - Article: Design a file thumbnail

- **Feature:** Frame size presets
  - Domain: Frame creation
  - UI Location: Right sidebar (visible after activating Frame tool with no selection)
  - Trigger: `F` → choose preset (iPhone 14 Pro, Plugin/file cover, Desktop, etc.)
  - Inputs: preset choice
  - Outputs: frame at preset dimensions added to canvas
  - Article: Create a photo gallery prototype; Design a file thumbnail

- **Feature:** Sections (FigJam)
  - Domain: FigJam organization
  - UI Location: Bottom toolbar / `Shift S`
  - Trigger: shortcut → click-drag on board
  - Inputs: drag area, color, name (double-click)
  - Outputs: titled section that groups objects; can be locked, hidden
  - Related: Groups (Figma Design); Lock background
  - Article: Create your first meeting board in FigJam; Run meetings in FigJam

- **Feature:** Stickies (FigJam)
  - Domain: FigJam content
  - UI Location: Bottom toolbar / `S`
  - Trigger: shortcut → click on board
  - Inputs: typed text; auto-tagged with author name (toggleable)
  - Outputs: sticky note with author label
  - Article: Create your first meeting board in FigJam

- **Feature:** Widgets (FigJam)
  - Domain: FigJam embeds
  - UI Location: Bottom toolbar → "More" → Widgets tab → search
  - Trigger: search → select widget → drag to board
  - Inputs: widget configuration (varies — Photo booth, Timeline, Asana, Jira, etc.)
  - Outputs: interactive embedded widget on board
  - Article: Create your first meeting board in FigJam

- **Feature:** Stamps / emotes / high-fives (FigJam)
  - Domain: FigJam reactions
  - UI Location: Toolbar / `E`; right-click → Stamp
  - Trigger: shortcut → choose stamp from wheel → click on board/object
  - Inputs: stamp choice (uses avatar / initials)
  - Outputs: stamp placed at cursor/object
  - Article: Create your first meeting board in FigJam

- **Feature:** Audio call (FigJam / Figma Design)
  - Domain: Collaboration
  - UI Location: Top toolbar audio button
  - Trigger: click → start/join conversation
  - Inputs: mic permissions
  - Outputs: in-file audio call with green Connected indicator
  - Article: Run meetings in FigJam

- **Feature:** Spotlight (presenter mode)
  - Domain: Collaboration
  - UI Location: Hover own avatar in top toolbar → Spotlight me
  - Trigger: hover avatar → click Spotlight me
  - Inputs: presenter request
  - Outputs: collaborators are pulled to presenter's view; dashed avatar border
  - Article: Run meetings in FigJam

- **Feature:** Open session (24-hr public collab)
  - Domain: Sharing
  - UI Location: Share modal → Open session section → Start
  - Trigger: paid-plan only; click Start, copy link
  - Inputs: link sharing settings (public / password / org-wide)
  - Outputs: 24-hour link allowing non-Figma users to view/edit
  - Related: Share modal; Permissions
  - Article: Run meetings in FigJam

- **Feature:** Share modal (permissions / invite / link)
  - Domain: File access
  - UI Location: Top toolbar Share button
  - Trigger: click Share
  - Inputs: emails, role (Can edit / Can view), link sharing scope
  - Outputs: invitations + shareable link; right-click any object → Copy link to deep-link
  - Article: Run meetings in FigJam

- **Feature:** File browser entry points
  - Domain: File creation
  - UI Location: file browser → Drafts → New design / FigJam / Buzz file; URL shortcuts (`figma.new`, `figjam.new`, `figma.com/buzz/new`)
  - Trigger: click "New …" tile or visit URL
  - Inputs: target file type
  - Outputs: opens new empty file in editor
  - Article: Create a photo gallery prototype; Create your first meeting board in FigJam; Create marketing assets in Figma Buzz

- **Feature:** Buzz template picker
  - Domain: Figma Buzz file creation
  - UI Location: Appears on opening a new Buzz file; tabs From Figma / From your team; categories (Ads, etc.)
  - Trigger: open Buzz file → browse / search template → Add template
  - Inputs: template selection
  - Outputs: file pre-populated with the template's asset
  - Article: Create marketing assets in Figma Buzz

- **Feature:** Edit content (Buzz)
  - Domain: Figma Buzz no-design editing
  - UI Location: Left navigation bar → Edit content tab; Text and Image sections
  - Trigger: select asset → Edit content
  - Inputs: typed text per text field; uploaded image per image field
  - Outputs: asset content updated without touching design
  - Related: Make an image (AI), Bulk create
  - Article: Create marketing assets in Figma Buzz

- **Feature:** Bulk create (Buzz)
  - Domain: Figma Buzz batch generation
  - UI Location: Left navigation bar → Bulk create
  - Trigger: select asset → Bulk create → Upload XLSX/CSV → map columns to layers → Create assets
  - Inputs: XLSX with text + embedded images per row, layer-to-column mapping
  - Outputs: many duplicated assets, each row producing one asset variant
  - Article: Create marketing assets in Figma Buzz

- **Feature:** Snap to settings (pixel grid / objects / nudge)
  - Domain: Editor preferences
  - UI Location: Main menu → Preferences; Zoom/view options (top-right of toolbar) for Pixel grid / Snap to pixel grid
  - Trigger: toggle in menus
  - Inputs: per-setting toggle; nudge amount (small/big in px)
  - Outputs: red snap guides on canvas; arrow-key nudge step changes
  - Article: Create a reusable icon grid; Design a search icon

- **Feature:** Export
  - Domain: Output
  - UI Location: Right sidebar Export section
  - Trigger: select layer → configure preset (PNG/JPG/SVG/PDF + scale) → Export
  - Inputs: format, scale, suffix
  - Outputs: file downloaded
  - Article: Create an illustration in Figma Design

- **Feature:** Version history (undo to past state)
  - Domain: File-level safety net
  - UI Location: file menu / version history; undo `Cmd/Ctrl + Z`
  - Trigger: open version history; or undo
  - Outputs: revert to earlier file state
  - Article: Create an orange illustration

## Figma Draw

- **Feature:** Draw mode toggle
  - Domain: Figma Draw
  - UI Location: toolbar (toggle between Design and Draw)
  - Trigger: Click "Draw" in the toolbar (requires `can edit` access)
  - Inputs: Toggle state (Design ↔ Draw)
  - Outputs: Toolbar and sidebars swap to illustration-focused tools/properties
  - Related: Auto layout and prototyping disabled while in Draw (cross-product: Figma Design)
  - Article: Explore Figma Draw

- **Feature:** Pen tool (vector network creation)
  - Domain: Figma Draw
  - UI Location: toolbar (in Draw mode)
  - Trigger: Select Pen from toolbar; click to place anchor points
  - Inputs: Click positions, anchor handles
  - Outputs: Precise point-by-point vector path / vector network
  - Related: Vector networks, vector edit mode (cross-product: Figma Design)
  - Article: Explore Figma Draw / Draw with illustration tools

- **Feature:** Pencil tool
  - Domain: Figma Draw
  - UI Location: toolbar (in Draw mode); secondary toolbar for stroke settings
  - Trigger: Select Pencil; click-drag on canvas (Shift = straight line)
  - Inputs: Cursor drag path, stroke color/size/style from secondary toolbar
  - Outputs: Vector network with auto-placed points along drawn path
  - Related: Brush tool, vector edit mode, Apple Pencil via Sidecar
  - Article: Draw with illustration tools

- **Feature:** Brush tool
  - Domain: Figma Draw
  - UI Location: toolbar (in Draw mode); brush styles menu in toolbar
  - Trigger: Select Brush; click-drag on canvas
  - Inputs: Cursor drag path, brush style, color/size/style
  - Outputs: Textured / hand-painted vector stroke (vector network)
  - Related: Custom brush styles, Advanced stroke settings (cross-product: Figma Design)
  - Article: Draw with illustration tools

- **Feature:** Custom brush style (Stretch / Scatter)
  - Domain: Figma Draw
  - UI Location: right-click context menu → "Create brush"; appears in Brush styles menu
  - Trigger: Right-click a single closed vector layer → Create brush → Stretch or Scatter
  - Inputs: A single vector layer (must be closed; use Outline stroke if open)
  - Outputs: Reusable brush style added to file's brush styles menu
  - Related: Outline stroke, Convert text to vector paths (cross-product: Figma Design); brush travels via copy-paste across files
  - Article: Draw with illustration tools

- **Feature:** Brush style portability across files
  - Domain: Figma Draw
  - UI Location: implicit (copy/paste)
  - Trigger: Copy a layer using a custom brush into another file
  - Inputs: Layer with custom brush applied
  - Outputs: Brush automatically registered in destination file's brush menu (persists even after deleting the pasted layer)
  - Related: Custom brush styles
  - Article: Draw with illustration tools

- **Feature:** Radial repeat transform
  - Domain: Figma Draw
  - UI Location: right sidebar → Additional transform modifier menu
  - Trigger: Select object → choose Radial repeat from transform menu
  - Inputs: Source object, repetition count, spacing
  - Outputs: Object repeated around a central point inside a non-destructive transform group
  - Related: Linear repeat, Apply transforms to selection, boolean operations (cross-product: Figma Design)
  - Article: Create patterns with transforms

- **Feature:** Linear repeat transform
  - Domain: Figma Draw
  - UI Location: right sidebar → Additional transform modifier menu
  - Trigger: Select object → choose Linear repeat from transform menu
  - Inputs: Source object, repetition count, spacing
  - Outputs: Object repeated horizontally/vertically as evenly spaced sequence inside transform group
  - Related: Radial repeat, Apply transforms to selection
  - Article: Create patterns with transforms

- **Feature:** Apply transforms to selection
  - Domain: Figma Draw
  - UI Location: right sidebar (Transform settings)
  - Trigger: Click "Apply transforms to selection" on a transform group
  - Inputs: Existing transform group
  - Outputs: Converts transform group's repetitions into real, individual canvas layers (destructive bake step)
  - Related: Radial / Linear repeat
  - Article: Create patterns with transforms

- **Feature:** Transform group (non-destructive container)
  - Domain: Figma Draw
  - UI Location: implicit, surfaces in right sidebar Transform panel
  - Trigger: Auto-created when a transform is added to an object
  - Inputs: One or more source objects
  - Outputs: Wrapped group preserving original object; objects can be added later for complexity
  - Related: Radial / Linear repeat, Apply transforms to selection
  - Article: Create patterns with transforms

- **Feature:** Layer thumbnail preview (Draw mode)
  - Domain: Figma Draw
  - UI Location: left sidebar → Layers section
  - Trigger: Always shown while in Draw mode
  - Inputs: Layer contents
  - Outputs: Enlarged visual preview of each layer; double-click zooms canvas to that layer
  - Related: Layers panel (cross-product: Figma Design has standard list view)
  - Article: Explore Figma Draw
