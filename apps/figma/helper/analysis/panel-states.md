# Panel States

_Source: synthesized from 216 articles across 4 Figma products. See `analysis/_partial/` for raw per-domain extracts._

## Figma Design

### Tour the interface

- **Panel:** Toolbar
  - Location: bottom-center of editor (UI3 moved it from top to bottom)
  - Shows when: always (unless Hide/Show UI toggled, or in spotlight)
  - Contains, left to right: Move tools (Move/Hand/Scale) -> Region tools (Frame/Section/Slice) -> Shape tools (Rect/Line/Arrow/Ellipse/Polygon/Star/Image-video) -> Creation tools (Pen/Pencil) -> Text -> Comment tools (Comment/Annotation/Measurement) -> Actions menu -> Dev Mode toggle (also `Draw` entry)
  - Changes when: tool selected (active state); permission downgrade renders a reduced toolbar with `Ask to edit` button visible

- **Panel:** Navigation panel (left sidebar) — UI3 current layout
  - Location: left side of editor
  - Shows when: always; collapsible via Minimize UI button at top
  - Contains:
    - File-name + dropdown (file actions: move, publish library, create branch, version history)
    - Tabs: **File** (default, `Opt/Alt 1`) and **Assets** (`Opt/Alt 2`)
    - File tab: Pages list (with current page selector), Layers list (nested tree)
    - Assets tab: search field, Libraries modal opener, Libraries-and-settings menu (filter libs, Grid/List view), all libraries grouped (file > page > frame)
    - Main `…` menu: more actions, settings, Preferences (dark mode, scroll behavior, accessibility, nudge, highlight-layers-on-hover)
    - Search/Find icon (`Cmd/Ctrl F`)
  - Width: drag right edge to resize
  - Changes when: tab switched, layer selected (highlights in Layers list), pages added/renamed, library added; in upcoming new-nav-bar build, Assets + Find/Replace + variables modal entry move out into the dedicated nav bar, and file notifications appear at its bottom

- **Panel:** New left navigation bar (UI3 rollout, in progress)
  - Location: narrow vertical strip at far left, separate from existing navigation panel
  - Shows when: rolled out for Full-seat users
  - Contains: variables modal entry, Assets tab, Find and replace, file notifications (bottom: library updates, missing fonts)
  - Changes when: notifications change; collapses with rest of UI on Minimize UI

- **Panel:** Properties panel (right sidebar) — edit access
  - Location: right side of editor; resizable
  - Shows when: always with edit access
  - Contains:
    - Header with zoom percentage + Zoom/view options dropdown
    - Tabs: **Design** and **Prototype**
    - Selection-actions header row (Mask, Component, Boolean, More menu)
    - With nothing selected: Page section (background color), local styles & variables, Export-page action
    - With selection: grouped sections — Layout (or Auto layout when applied), Position (incl. constraints, rotate/flip, alignment, ignore-auto-layout), Appearance (visibility eye, blend modes, variable mode swatch, opacity), Typography (text settings), Fill, Stroke, Effects, Component / Component properties / Variants, Export
    - More-menu (`…`) hides overflow actions per selection
  - Changes when: selection changes, auto-layout applied, component vs instance selected, multi-edit toggled, spotlight requested

- **Panel:** Properties panel (right sidebar) — view-only access
  - Location: right side
  - Shows when: viewer permission, or View seat
  - Contains: Tabs **Comment** and **Properties**
    - Comment tab: list of all comments, search field, filter (date/unread/specific set), reply UI
    - Properties tab: selected layer name, properties (layout, colors), Export configuration at bottom
  - Changes when: layer selected, new comments arrive

- **Panel:** Page-section (sub-panel of right sidebar with no selection)
  - Location: top of properties panel when nothing selected
  - Shows when: nothing selected, edit access
  - Contains: page background color picker (hex + opacity + Hide eye), Export page

- **Panel:** Zoom / view options menu
  - Location: dropdown opened from the zoom % shown in top-right of right sidebar (per docs also called "from the toolbar"; in UI3 it's adjacent to the properties panel header)
  - Shows when: opened by click on zoom value or shortcut
  - Contains: Zoom in / out / to fit / to selection / custom %; Pixel preview (Disabled / 1x / 2x); Pixel grid; Snap to pixel grid; Layout guides; Multiplayer cursors; Outlines (Show outlines, Include hidden layers, Include object bounds); Property labels; Prototyping (view-only users only)
  - Changes when: each toggle persists across the file viewing session for this user only

- **Panel:** Actions menu (floating overlay)
  - Location: floating, anchored to Actions toolbar icon; overlays canvas
  - Shows when: opened with toolbar icon or `Cmd/Ctrl K`
  - Contains: search field; AI tools section (Make designs, Make prototypes, Rename layers, Replace content, Riff/write, Make image, Remove background, Boost resolution, Expand image, Vectorize, Erase object); productivity actions (layer ops, selection/styling, editing tools, view/nav, file management, preferences); Plugins & widgets tab; Find more like
  - Changes when: text typed (filters list); selection changes (Find more like enabled)

- **Panel:** Find / Replace panel
  - Location: replaces left sidebar contents (current UI3) — pinned to left; in upcoming nav-bar variant moves into the new nav bar
  - Shows when: opened with `Cmd/Ctrl F`
  - Contains: query input, filter chips (text, frame, shape, etc.), scope toggle (current page / all pages), result list, Replace tab with `Replace with` field + Replace + Replace all
  - Changes when: typing updates results; selecting result selects layer in canvas; Esc returns left sidebar to Layers

- **Panel:** Keyboard shortcuts panel
  - Location: floating panel docked along bottom of screen
  - Shows when: opened from Help and resources or `Ctrl Shift ?`
  - Contains: category tabs, shortcut list, Layout tab for keyboard-layout selection; previously-used shortcuts highlighted live
  - Changes when: user presses a shortcut (it highlights), tab changed

- **Panel:** Help and resources menu
  - Location: bottom-right corner of screen
  - Shows when: clicked
  - Contains: Keyboard shortcuts entry (and other help items)

- **Panel:** Main menu (the `…` / hamburger entry)
  - Location: top of left navigation panel
  - Shows when: clicked
  - Contains: View submenu (Rulers, Property labels, dark mode, etc.), Preferences submenu (Highlight layers on hover, Nudge amount, Use old shortcuts for outlines, Accessibility settings > Adapt content for screen readers, etc.), file actions

- **Panel:** Pages browser
  - Location: opens from current page name in left sidebar
  - Shows when: clicked
  - Contains: list of pages, "+" to add page, right-click for `Copy link to page`, rename, etc.

- **Panel:** Color picker (canvas background)
  - Location: floating modal anchored to color swatch in Page section of right sidebar
  - Shows when: clicked from Page section
  - Contains: color picker, hex input, opacity field, Hide eye

- **Panel:** Right-click context menu (canvas, layer, frame)
  - Location: floating at cursor
  - Shows when: right-click on canvas/layer
  - Contains (varies): Copy, Copy/paste as code (CSS/iOS/Android/SVG/PNG/properties/link), Set as thumbnail (frames), Restore default thumbnail, Remove guide (on guides), select-deeper-layer

- **Panel:** Libraries modal
  - Location: floating modal opened from Assets tab Libraries icon
  - Shows when: opened
  - Contains: enabled/disabled libraries, library settings

- **Panel:** Spotlight overlay
  - Location: minimizes left + right panels and toolbar to give canvas full focus
  - Shows when: a user spotlights themselves from properties panel
  - Contains: just the canvas + active spotlight badge

### Create designs

- **Panel:** Layers panel
  - Location: left sidebar (default tab)
  - Shows when: always (file open)
  - Contains: hierarchical tree of every layer on current page; per-layer icons (frame/shape/text/image/video/component/instance/mask/section); hover-only padlock + eye icons; collapse-all toggle in top-right; bolded names = top-level frames
  - Changes when: layers are created/deleted/renamed/reordered; selection mirrors canvas; locked layers show padlock; hidden layers grayed out

- **Panel:** Design panel (right sidebar — default state)
  - Location: right sidebar
  - Shows when: 1+ layer selected
  - Contains: Multi-edit toggle (when applicable); alignment row + tidy up; Position (X/Y/rotation/flip); Layout (W/H/lock aspect/resizing/constraints); Appearance (opacity/visibility/blend mode/corner radius/corner smoothing); Layout guide (frames only); Auto layout (frames only); Fill; Stroke; Effects; Mask; Selection colors (when mixed)
  - Changes when: selection changes (different sections appear per layer type); fills/strokes/effects added/removed; mixed selection adds Selection colors; auto layout toggled adds AL section

- **Panel:** Typography section / Type settings
  - Location: right sidebar (visible for text layer)
  - Shows when: text layer selected (or text being edited)
  - Contains: text style picker; font picker (with filter dropdown); weight/style; size; line height; letter spacing; horizontal+vertical alignment; "..." opens Type settings panel with Basics/Details/Variable tabs (decoration, case, vertical trim, lists, paragraph spacing, truncation, indentation, OpenType features, variable axes)
  - Changes when: text layer / text range selected; font choice updates available OpenType features and variable axes

- **Panel:** Layout guide section
  - Location: right sidebar (frame selected only)
  - Shows when: frame selected (including components which are frames)
  - Contains: per-guide entry (uniform grid / column / row), color/opacity, count, type (Stretch / Left/Right/Center / Top/Bottom), width-height, offset, margin, gutter; visibility toggle; styles "Apply styles"
  - Changes when: guides added/removed; toggled globally with `⇧G` or per-guide eye icon

- **Panel:** Auto layout section
  - Location: right sidebar (auto layout frame only)
  - Shows when: frame with auto layout selected (or candidate before toggle)
  - Contains: flow toggle (vertical/horizontal/grid); padding (uniform/vh/per-side); gap between items (number or Auto); 9-position alignment box; wrap (horizontal); resizing per axis; min/max sizes; for Grid: track count, per-track size, span
  - Changes when: AL toggled on/off; flow changed; values edited

- **Panel:** Color picker (modal)
  - Location: floats next to right sidebar swatch
  - Shows when: any color swatch clicked (Fill, Stroke, Effect, Selection colors)
  - Contains: fill type tabs (Solid/Gradient/Pattern/Image/Video); HSV palette + hue/opacity sliders; eyedropper; blend mode; color contrast checker; color model dropdown (Hex/RGB/CSS/HSL/HSB); Libraries tab (styles + variables); for image: Fill mode + rotation + adjustment sliders + crop; for gradient: stops list + flip/rotate; for pattern: Select source + tile/scale/spacing/alignment
  - Changes when: type tab switched; eyedropper toggled; library tab opened

- **Panel:** Vector edit mode secondary toolbar
  - Location: above canvas (replaces top toolbar) when in vector edit mode
  - Shows when: `Enter` on a vector layer
  - Contains: Move (`V`), Pen (`P`), Bend, Lasso (`Q`), Cut (`X`), Paint (`⇧B`), Variable width, Shape builder; mirroring options
  - Changes when: tool selection changes; `Enter` again exits

- **Panel:** Rename layers modal
  - Location: floats above canvas
  - Shows when: triggered by `⌘R` / `Ctrl+R` or right-click → Rename
  - Contains: Match field (regex supported); Rename to field; Current name token; Number ↑ / ↓ tokens; Start ascending from / Stop descending at; live Preview list; Rename button
  - Changes when: token clicked, fields edited

- **Panel:** Properties panel (view-only)
  - Location: right sidebar for can-view users
  - Shows when: layer selected with view-only access
  - Contains: layer name; Parent component link if instance; properties + layout + colors (read-only); for text: Content + per-property Copy button

### Build design systems

- **Panel:** Local Styles (right sidebar)
  - Location: right sidebar > Design tab when nothing selected
  - Shows when: file has at least one local style and selection is empty
  - Contains: grouped lists for Text / Color / Effect / Layout guide; per-style adjust icon; "+" to add; folders
  - Changes when: styles created/deleted/renamed/reordered/grouped; Edit style modal opens

- **Panel:** Style picker (per-property)
  - Location: pop-out from each property's "Apply styles" / "Apply styles and variables" icon in right sidebar
  - Shows when: clicking style icon next to Fill/Stroke/Effects/Text property
  - Contains: Libraries tab with circular swatches (styles) and square swatches (color variables), search bar, library dropdown filter, list/grid toggle
  - Changes when: applying/right-click Edit style/Copy style; library subscriptions change

- **Panel:** Local Variables / Variables modal
  - Location: right sidebar Local variables section opens modal (rolling out: left navigation bar entry)
  - Shows when: deselected (current entry) or always (new nav bar)
  - Contains: collections sidebar, variables grid (rows), mode columns, header search/filter, Edit variable modal, Scope tab, Code syntax section
  - Changes when: create/edit/delete variable; add mode column; right-click row/column for context actions; expand to "variables view"

- **Panel:** Properties (component / instance)
  - Location: right sidebar > Properties section
  - Shows when: main component, component set, or instance selected
  - Contains: variant property dropdowns (top), boolean toggles, text fields, instance swap dropdowns, slot indicators, exposed nested instance properties, "+" to add property
  - Changes when: select different component/instance; switch variant; toggle boolean; edit text; swap instance; multi-edit

- **Panel:** Component configuration modal
  - Location: opened from icon next to component name in right sidebar
  - Shows when: editing main component / variant
  - Contains: description text area, documentation link field
  - Changes when: typing in fields; affects search results, instance details modal, Dev Mode

- **Panel:** Assets panel
  - Location: left sidebar Assets tab (Alt/Opt+2)
  - Shows when: tab active
  - Contains: library list, search, components grouped by file > page > frame, list/grid toggle, sub-folder show/hide, Libraries modal entry
  - Changes when: libraries added/removed; new published components; right-click Go to main component / Remove library from file

- **Panel:** Libraries modal
  - Location: opens from Assets tab Libraries icon, or Alt/Opt+3
  - Shows when: invoked
  - Contains: This file (Publish/Unpublish/Swap), Updates tab (Update / Update all), Browse libraries (Recommended / Teams / Your organization / UI kits), per-asset publish checkboxes, Hide-when-publishing toggles, target dropdown (Org/Ent)
  - Changes when: publishing changes; new updates available (badge); add/remove libraries; swap library flow

- **Panel:** Component details modal / playground
  - Location: opened from Assets panel by clicking a component
  - Shows when: viewing component before insertion
  - Contains: description, link, default preview, (paid) playground with variant preview, property toggles, mode switcher, Insert instance button
  - Changes when: editing properties in playground; switching modes

- **Panel:** Instance menu (swap)
  - Location: opens from clicking component name in right sidebar of a selected instance
  - Shows when: instance selected
  - Contains: related components (same file/page/frame, slash-grouped siblings), search, library switcher, group nav, list/grid toggle
  - Changes when: navigating libraries; selecting replacement

- **Panel:** Edit style modal
  - Location: opens via adjust icon in Local styles, or right-click Edit style in style picker
  - Shows when: editing existing style
  - Contains: name, description, properties list, hide/remove property icons, Go to style definition (cross-file)
  - Changes when: edits propagate to all bound objects

- **Panel:** Edit variable modal
  - Location: hover row in Variables modal > Edit variable icon
  - Shows when: editing single or bulk-selected variables
  - Contains: name, description, per-mode values, Code syntax (Web/Android/iOS), Hide from publishing, Scope tab with type-specific checkboxes
  - Changes when: edits/saves; bulk edit limited to scope + hide

- **Panel:** Updates tab in Libraries modal
  - Location: Libraries modal > Updates tab
  - Shows when: subscribers have outstanding updates (blue badge on icon)
  - Contains: per-page filter toggle, list of updates, per-asset Update buttons, Update all
  - Changes when: publishers push changes; preview opens Side-by-side / Overlay (with opacity slider) view

- **Panel:** Check designs panel
  - Location: opens from right-click / Ready-for-Dev / Actions menu
  - Shows when: invoked on selection (Org/Ent beta)
  - Contains: Colors / Dimensions / Typography / Components tabs; rows with current value vs suggestion dropdown; Apply / Apply all; settings (library scope, row counts)
  - Changes when: bound on apply; canvas highlights mirror hover; Ctrl+Z to revert

### Create prototypes

- **Panel:** Prototype tab (right sidebar)
  - Location: right sidebar, top-tab toggle next to Design
  - Shows when: user clicks Prototype tab or presses `Shift + E`; replaces Design panel contents
  - Contains (selection-dependent):
    - No selection → **Device**, **Background**, **Flows** list
    - Frame selected → **Flow starting point** (add/remove/name/description/copy link), **Scroll behavior** (Overflow), **Interactions**
    - Object selected → **Interactions** (Add `+`), **Scroll behavior** (Position), Video properties (if video fill)
    - Overlay frame selected (in Prototype mode) → Overlay settings (position, click-outside, background)
  - Changes when: selection changes; mode toggled to Design

- **Panel:** Interaction details modal
  - Location: floating modal anchored to selected connection or hotspot on canvas
  - Shows when: connection or interaction is selected; auto-opens when connection created (suppress with hold Shift)
  - Contains: Trigger dropdown, Action dropdown, Destination dropdown/picker, Animation (transition/direction/easing/duration), `Animate matching layers` checkbox, State management section (Reset scroll/component/video), `+ Add action`, Select matching interactions icon, Update button (for legacy interactions), preview window
  - Changes when: trigger/action selection changes which sub-fields appear; relevant Reset toggles only show when destination has scroll/video/components

- **Panel:** Inline preview window
  - Location: floating window above canvas
  - Shows when: Preview button clicked, `Shift + Space`, or flow starting-point preview icon clicked
  - Contains: prototype playback area, prev/next arrows, restart, scaling overflow menu (Fit width, Responsive, Resize 100%, Respect aspect ratio, Show device frame, Follow prototype), open-in-presentation button, close X
  - Changes when: design changes (live), frame selection on canvas (jumps to that frame), device setting

- **Panel:** Presentation view (full window)
  - Location: separate browser tab
  - Shows when: user clicks Present in toolbar or `Cmd+Opt+Return` / `Ctrl+Alt+Enter`
  - Contains: top toolbar (Figma logo, sidebar toggle, comments, avatar/spotlight, Share, Options, Fullscreen), left sidebar (Flows + descriptions, toggleable), bottom toolbar (prev/next, device switcher, Restart), main playback area
  - Changes when: Hide UI toggled (toolbar/footer/sidebar disappear, URL gains `&hide-ui=1`); Make available offline toggled; flow selection changes which prototype plays

- **Panel:** Properties / Interactions section (right sidebar, view access)
  - Location: right sidebar **Properties** tab (read-only in view access)
  - Shows when: viewer toggles connection visibility on (`Shift + E`) and selects a connection or starting frame
  - Contains: trigger type, action + destination, animation type + direction, easing curve, duration; Flows list with Select frame / Copy link / Preview hover actions
  - Changes when: connection selection changes; viewer cannot edit, only inspect

- **Panel:** Variables modal (used from prototypes)
  - Location: opened from Local variables in right sidebar (no-selection state)
  - Shows when: user opens variables (often during Set variable / expression authoring)
  - Contains: collections, variables grid (name/value/mode columns), mode tabs
  - Changes when: variables added/edited/modes changed (relevant for Set variable mode action)

### Work together in files

- **Panel:** Comments sidebar (right sidebar in comment mode)
  - Location: right sidebar; replaces design panels while comment mode active
  - Shows when: user enters comment mode (toolbar comment button or `C`)
  - Contains: filter button (sort by Date / Unread; toggles Only your threads / Only current page / Show resolved); per-comment row with author, text, page label, ellipsis menu; Settings (gear) for per-file email notifications (Everything / Just mentions / Nothing)
  - Changes when: comments added/resolved/deleted; filter toggled; user exits comment mode

- **Panel:** Comment modal (canvas overlay)
  - Location: floating overlay anchored to comment pin on canvas
  - Shows when: user clicks a pin or a sidebar comment row
  - Contains: thread composer; per-comment hover reactions; ellipsis menu (Mark as unread / Copy link / Edit / Delete); Resolve checkmark; Close (X); Reply field with `@`/emoji/image/Submit
  - Changes when: replies added; reactions toggled; resolve state changes

- **Panel:** Multiplayer tools dropdown (own avatar)
  - Location: anchored to own avatar in toolbar
  - Shows when: user hovers/clicks own avatar
  - Contains: "Spotlight me" action and related multiplayer settings
  - Changes when: user is in spotlight (avatar shows dashed border + follower count badge)

- **Panel:** Avatar stack / viewer history dropdown
  - Location: right side of toolbar
  - Shows when: user clicks avatar group
  - Contains: "Currently viewing" list, "Previously viewed" list with timestamps, hover ellipsis to view profile
  - Changes when: collaborators join/leave; viewer history opt-out toggled in account settings

- **Panel:** Branches modal
  - Location: centered modal launched from file-name menu ("See all branches") or file-browser tile
  - Shows when: user invokes "See all branches"
  - Contains: tabs Active / Archived / Yours; per-row branch name + author + status; row actions Open / Copy link / Merge / Archive / Rename / Restore
  - Changes when: branches created, archived, merged, renamed, restored

- **Panel:** Branch review / merge modal
  - Location: full-screen modal launched from file-name menu → "Review and merge changes"
  - Shows when: user opens review/merge flow on a branch
  - Contains: left sidebar with branch summary, change list grouped by page, review request meta, reviewer list; main viewport with side-by-side / overlay diff, opacity slider, zoom controls, navigation arrows; bottom-right Add your review / Merge buttons; Edit merge description on completion
  - Changes when: reviewer adds/edits review; conflicts resolved; merge completed

- **Panel:** Update from main modal
  - Location: centered modal launched from file-name menu → "Update from main…"
  - Shows when: pending changes exist on main while viewing branch
  - Contains: list of added / edited / removed items, preview pane, "Resolve conflicts" entry point, "Apply changes" button
  - Changes when: main file evolves further; conflicts created/resolved

- **Panel:** Conflict resolution view
  - Location: modal section reached via "Resolve conflicts" within Update / Merge flow
  - Shows when: branch has conflicting edits with main
  - Contains: left-side conflict list, side-by-side preview (main left, branch right), per-conflict pick badges, "Resolve all → Pick main / Pick branch" menu, Next button
  - Changes when: user makes per-conflict picks

- **Panel:** Version history sidebar (branch / main, with branch checkpoints)
  - Location: right sidebar
  - Shows when: file-name menu → Show version history
  - Contains: chronologically ordered checkpoints incl. "Branch created", "Updated from main", "Before update", "Before merge", "Branch merged" (with branch-merge icon); per-row ellipsis with "Restore this version"; Done button to exit
  - Changes when: any branch lifecycle event or autosave; restore action adds two new checkpoints

- **Panel:** Prototype presentation Options menu
  - Location: presentation-view toolbar (top of screen)
  - Shows when: viewing prototype in presentation view
  - Contains: Show resolved comments, Show only your comments toggles
  - Changes when: comments exist on prototype (otherwise grayed out)

### Import and export

- **Panel:** Export section (right sidebar)
  - Location: bottom of right sidebar in Design Mode edit access; under Properties tab in view access; right sidebar in Dev Mode (only when object selected)
  - Shows when: a selection is active (or, with deselected canvas, applies to current page)
  - Contains: list of export configuration rows (scale, suffix, format dropdown), "+" to add, gear/Advanced export settings (color profile, image resampling, format-specific toggles), Preview link, Export button
  - Changes when: selection changes; access level changes; mode switches (Design vs Dev); file owner toggles "restrict copying" (panel hides for viewers)

- **Panel:** Bulk Export modal
  - Location: centered modal opened via Main menu > File > Export or Shift+Cmd/Ctrl+E
  - Shows when: user triggers bulk export and the current page has at least one selection with an export config
  - Contains: scrollable list of all configured selections on the page, each with thumbnail, scale, format, dimensions, hoverable filename, include/exclude checkbox, "Export" confirmation button
  - Changes when: page selection set changes; user toggles row checkboxes; clicking a thumbnail navigates the canvas behind the modal

- **Panel:** Advanced export settings popover
  - Location: opens from gear icon inside an Export config row
  - Shows when: user clicks the advanced/gear control on a config row
  - Contains: color profile dropdown (Same as file / sRGB / Display P3), image resampling (Detailed / Basic) for raster formats, format-specific toggles (Ignore overlapping layers, Include bounding box, Include "id", Outline text, Simplify stroke), image quality slider for JPG/PDF
  - Changes when: format dropdown of the parent row changes (toggles enable/disable per format matrix)

- **Panel:** File browser "Create new" > Import dropdown
  - Location: top-right of file browser, inside Create new menu
  - Shows when: user opens Create new dropdown
  - Contains: "Import" entry that opens secondary "Import from computer / From your computer" dialog leading to OS file picker; supports drag-drop into browser as alternative
  - Changes when: plan / role determines whether import-to-team is allowed (drafts always allowed)

- **Panel:** Fill row "Show in exports" checkbox
  - Location: inside each fill row of the Fill section in the right sidebar
  - Shows when: a layer with at least one fill is selected
  - Contains: per-fill checkbox that controls inclusion in exported assets only
  - Changes when: selection changes; fills are added/removed

## Dev Mode

- **Panel:** Inspect (right sidebar)
  - Location: right sidebar
  - Shows when: Dev Mode active AND a layer is selected
  - Contains: layer name + type + last edited; Compare changes link; Dev resources; Component info + Explore component behavior; Code section (Code/List toggle, language+unit dropdown, codegen plugin picker); Styles & Variables; Assets (icon detection, source/layer image export, GIF/MP4); Export configs
  - Changes when: selection changes, language/unit changes, Code Connect mapping toggles between connected/auto, codegen plugin chosen

- **Panel:** Plugins (right sidebar tab)
  - Location: right sidebar (alongside Inspect tab)
  - Shows when: Dev Mode active
  - Contains: recently used plugins, Community-recommended Dev Mode plugins, org-pinned plugins
  - Changes when: plugin run, codegen plugin selected as active for Code section, admin changes pinned/auto-run plugin

- **Panel:** Dev Mode left sidebar (Navigation panel)
  - Location: left sidebar
  - Shows when: Dev Mode active AND no top-level frame selected
  - Contains: search field, Pages list (Dev Mode icon flag pages with statuses), Ready for dev entry, Sections marked Ready for development
  - Changes when: dev statuses added/removed, page changed, search opened (`Cmd/Ctrl F`)

- **Panel:** Dev Mode left sidebar (Layers panel)
  - Location: left sidebar (replaces nav panel)
  - Shows when: Dev Mode active AND a top-level frame is selected
  - Contains: scoped layer tree of selected frame; non-section content collapsed by default
  - Changes when: selection changes top-level frame, layer hover on canvas (highlight)

- **Panel:** Ready for dev view
  - Location: full-canvas overlay (replaces canvas while open)
  - Shows when: Dev Mode active AND ≥1 design has a dev status AND user clicks "Ready for dev" in left sidebar
  - Contains: counter, filter (All/Ready/Completed), sort (Recent activity/Pages/Name), card grid with status badges and last-activity timestamps
  - Changes when: filter/sort changes, statuses change in file, design clicked → opens Focus view

- **Panel:** Focus view
  - Location: full-canvas overlay; right side hosts Inspect/Plugins panels and version history
  - Shows when: a design is opened from Ready-for-dev view OR from canvas dev-status menu → "Show in focus view"
  - Contains: isolated design in center; interactive resize handles + variable-mode dropdown; scoped version history with Inspect/Compare/Copy-link options; Mark as completed; "See all ready for dev" / "Inspect on page" nav controls
  - Changes when: leave/reset (temporary changes discarded), new version added, status changes

- **Panel:** Compare changes (frame history) modal
  - Location: floating modal over canvas
  - Shows when: user clicks "Compare changes" / "Compare with main component" or selects 2 components with Shift+click
  - Contains: version timeline (top-level frames only), edited-layers list (Edited/Added/Deleted), Side-by-side and Overlay viewers, code-diff and property-diff per selected layer, language/unit pickers
  - Changes when: version chosen, layer selected in list, language switched, opacity slider in overlay mode

- **Panel:** Variable details modal
  - Location: floating modal anchored off Inspect panel
  - Shows when: user clicks variable name in code snippet OR "Variable details" icon in Selection colors
  - Contains: variable name, host file link, collection, mode, alias chain, value, scope, code snippet, mode-switch dropdown
  - Changes when: mode switched, different variable clicked

- **Panel:** Variables modal (read-only table)
  - Location: floating modal
  - Shows when: nothing selected in Dev Mode AND user clicks "Open variables table"
  - Contains: collections × modes table of variables; click-to-copy values; click variable → Variable details
  - Changes when: collection switched

- **Panel:** Suggested variables modal
  - Location: small floating popover next to clicked value in Inspect
  - Shows when: user clicks a raw value that matches existing variable(s) in scope
  - Contains: ranked list of candidate variable names
  - Changes when: different raw value clicked

- **Panel:** Component playground modal ("Explore component behavior")
  - Location: floating modal
  - Shows when: component or instance selected AND user clicks Explore component behavior
  - Contains: live component preview, property toggles, variable mode toggles
  - Changes when: prop / variant / mode changed (viewer-local only)

- **Panel:** Annotation editor (canvas-attached)
  - Location: floating attached to a green annotation dot on canvas
  - Shows when: Annotate tool active OR existing annotation clicked
  - Contains: text field, "+ Property" picker, category label dropdown
  - Changes when: properties on annotated layer change (auto-update), category edited

- **Panel:** Notification settings (Dev Mode)
  - Location: right sidebar (visible only when Comment mode is active in Dev Mode)
  - Shows when: Dev Mode active AND `C` pressed / Comment toolbar entered AND user opens Settings
  - Contains: toggle between "Status changes" and "Nothing"
  - Changes when: user changes preference per file

- **Panel:** Org Dev Mode settings (admin)
  - Location: Admin → Settings → Extensions → Dev Mode settings
  - Shows when: org admin on Enterprise plan
  - Contains: Pinned plugins list, Default code language + unit, Auto-run plugin (single)
  - Changes when: admin saves changes; propagates to all non-draft files

## Projects

- **Panel:** Layers panel (left sidebar)
  - Location: Left sidebar
  - Shows when: Always (in design / draw / FigJam / Buzz files when something is on canvas)
  - Contains: Tree of frames, components (purple icon), groups, shapes, text, vectors; lock icon, visibility eye; supports drag-reorder, double-click rename
  - Changes when: Selection change updates highlight; layer naming with `/` becomes hierarchy in Assets

- **Panel:** Assets panel (left sidebar tab)
  - Location: Left sidebar, Assets tab
  - Shows when: Toggled
  - Contains: Components "Created in this file", linked libraries; thumbnails, drag-out to instantiate
  - Changes when: New component created or library imported

- **Panel:** Design panel (right sidebar)
  - Location: Right sidebar (default tab in Figma Design / Draw)
  - Shows when: A layer is selected
  - Contains: Position (X/Y), Dimensions (W/H + lock-aspect), Rotation, Constraints (or Auto layout), Layout grid (frames only), Appearance (Opacity, Corner radius, Independent corners), Fill, Stroke, Effects, Export, Selection colors, Text/Typography (text layers only), Properties (components/instances), Local variables
  - Changes when: Different layer type selected → relevant sections appear/disappear

- **Panel:** Prototype panel (right sidebar tab)
  - Location: Right sidebar, Prototype tab (`Shift E`)
  - Shows when: Tab active
  - Contains: Interactions list with blue `+` connectors on canvas; per-frame Flow starting point; Prototype-view dropdown (Preview / Present); Device selector; Background; Scrolling
  - Changes when: Selection change; switching tab toggles canvas overlay arrows

- **Panel:** Variables modal
  - Location: Modal launched from "Open variables" in Local variables section
  - Shows when: Invoked
  - Contains: Collections, groups, variables (Boolean / Number / String / Color / Alias), modes, default values
  - Changes when: + Create variable; right-click for duplicate (`Shift Enter`)

- **Panel:** Interaction details modal
  - Location: Floating modal anchored to selected prototype connection
  - Shows when: Click a connection or its blue plus
  - Contains: Trigger dropdown, Add actions list (Navigate to / Change to / Set variable / Check if/else / Open overlay / Open link / Close), Animation + Curve + Duration, Destination
  - Changes when: Action type chosen → fields update (e.g. Set variable shows target + value expression)

- **Panel:** Color picker
  - Location: Modal opened by clicking a color swatch in Fill / Stroke / Effect color
  - Shows when: Swatch clicked
  - Contains: Color wheel, hex/RGB/HSL inputs, opacity, fill type (Solid / Linear / Radial / Angular / Diamond gradient / Image / Pattern / Video on some surfaces); Image options (Choose image / Swap image / Make an image AI), Pattern options (Select source, Tile/Direction/Scale/Spacing/Alignment)
  - Changes when: Fill type changed

- **Panel:** Toolbar (top)
  - Location: Top of editor
  - Shows when: Always
  - Contains: Move tool / Frame / Shape tools dropdown / Pen / Pencil / Text / Hand tool; Figma Design ↔ Figma Draw toggle; Create component dropdown; Boolean operations; Present; Share; collaborator avatars (Spotlight me on hover); Zoom/view options (Pixel grid / Snap settings)
  - Changes when: Tool selected; vector edit mode replaces with secondary toolbar

- **Panel:** Secondary toolbar (vector edit mode)
  - Location: Top, replaces normal toolbar contents while in vector edit
  - Shows when: A vector layer is being edited (`Enter` to enter)
  - Contains: Bend tool, Variable width, Paint bucket, Offset vector, Flatten, Done/Close
  - Changes when: Exited via `Enter` / `Esc` / Done

- **Panel:** Toolbar (FigJam, bottom)
  - Location: Bottom of FigJam canvas
  - Shows when: FigJam file open
  - Contains: Move/Hand, Sticky (`S`), Section (`Shift S`), Shape, Text, Connector, Marker, Stamp (`E`), recent widgets/stickers stack, More, Audio call
  - Changes when: Recent items reflect usage

- **Panel:** Buzz left navigation
  - Location: Left nav bar in Figma Buzz
  - Shows when: Buzz file open
  - Contains: Templates picker, Edit content (Text / Image sections), Bulk create (data upload + layer-to-column mapping)
  - Changes when: Editing mode selected

- **Panel:** Share modal
  - Location: Modal from Share button (top toolbar)
  - Shows when: Invoked
  - Contains: Email invite, role dropdown (Can edit / Can view), link sharing scope (private / org / public / password), Open session controls, Copy link
  - Changes when: Plan tier; org settings

- **Panel:** Properties section (component instances)
  - Location: Right sidebar Properties when an instance is selected
  - Shows when: Selected layer is a component instance
  - Contains: Per-property controls — Boolean toggles (Show icon / Show label), Variant dropdowns (state, status, arrowDirection), Text overrides, Instance-swap dropdowns
  - Changes when: Different instance / variant property surface

- **Panel:** Inline preview (in-canvas)
  - Location: Floating window inside editor (`Shift Space`)
  - Shows when: Triggered while a frame/flow is selected
  - Contains: Live runnable prototype with current variable state
  - Changes when: Edits to prototype reflect immediately

## Figma Draw

- **Panel:** Draw toolbar (top)
  - Location: top toolbar (replaces standard Design toolbar when toggle = Draw)
  - Shows when: Toolbar toggle is set to Draw
  - Contains: Draw/Design toggle, Pen tool, Brush tool, Pencil tool, brush styles menu (when Brush selected), secondary stroke toolbar (color, size, style)
  - Changes when: Toggling between Design/Draw; selecting different tool surfaces a tool-specific secondary toolbar

- **Panel:** Right sidebar (Draw mode)
  - Location: right side
  - Shows when: In Draw mode
  - Contains: Streamlined illustration-related properties with slider controls, Additional transform modifier menu, Transform settings (repetition count + spacing), Apply transforms to selection action; access to Advanced stroke settings
  - Changes when: Selection changes; adding a transform reveals Transform settings; selecting a transform group surfaces its repetition controls

- **Panel:** Left sidebar — Layers (Draw mode)
  - Location: left side
  - Shows when: In Draw mode
  - Contains: Enlarged visual preview of each layer's contents (vs. standard list rows in Design)
  - Changes when: Layer selection / canvas content changes; double-click on a preview zooms canvas to that layer

- **Panel:** Brush styles menu
  - Location: secondary toolbar when Brush tool selected; also Advanced stroke settings in right sidebar
  - Shows when: Brush tool active or editing a stroke's brush style
  - Contains: Built-in brush styles + any custom Stretch/Scatter brushes registered in the file
  - Changes when: A custom brush is created (Right-click → Create brush) or imported by pasting a layer that uses one

- **Panel:** Transform settings (within right sidebar)
  - Location: right sidebar, after a transform is added
  - Shows when: A transform group is selected or its transform entry is clicked
  - Contains: Repetition count, spacing controls; option to add objects to the transform group; "Apply transforms to selection" action
  - Changes when: Adding/removing transforms; modifying parameters re-renders repetitions live without adding layers
