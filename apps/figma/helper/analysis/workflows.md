# Workflows

_Source: synthesized from 216 articles across 4 Figma products. See `analysis/_partial/` for raw per-domain extracts._

## Figma Design

### Tour the interface

(Domain is mostly chrome; only a handful of multi-step UI workflows.)

- **Open file > orient via four regions** — toolbar (bottom), left sidebar (file/assets), right sidebar (properties or comments), canvas. Permission level (`can edit` vs `can view`) determines which sidebar tabs render. (Article: *Explore design files*.)
- **Insert object via keyboard-only flow** — pick tool with shortcut or `F6`/`Ctrl F6` to focus toolbar + arrow keys; crosshair appears on canvas; `Return` places. Lines, vectors, connectors, tables not supported. (Article: *Use Figma products with a keyboard*.)
- **Create a custom thumbnail** — make a 1920x1080 frame, right-click > Set as thumbnail; revert with Restore default thumbnail. (Article: *Set custom thumbnails*.)
- **Add a guide and measure distance** — Main menu > View > Rulers; drag from ruler; `Opt`/`Alt` while dragging with frame selected to see redline. (Article: *Add guides*.)
- **Find > Select > Replace text in bulk** — `Cmd/Ctrl F` > query > select one/many results > Replace tab > "Replace with" > Replace or Replace all. (Article: *Find and replace*.)

### Create designs

- **Workflow:** Create a frame from existing objects and convert to a section ready for dev
  - Touches: Dev Mode (cross-product handoff)
  - Steps:
    1. Select objects → bounding box appears
    2. `⌥⌘G` / `Ctrl+Alt+G` → frame wraps the selection
    3. Right-click → "Wrap in new section" → section container created
    4. Click "Mark as ready for dev" on section → "Ready for dev" label appears; status will auto-flip to "Changed" if edits happen later
  - Preconditions: can edit access; objects on canvas
  - Result: section labeled Ready for dev visible to dev seats
  - Article: Frames in Figma Design + Organize your canvas with sections

- **Workflow:** Create a mask from a shape over an image
  - Touches: none
  - Steps:
    1. Place mask shape below image in z-order (Layers panel)
    2. Select both layers
    3. `⌃⌘M` / `Ctrl+Alt+M` → mask group created (mask icon + upward arrow on masked layers)
    4. Optionally select mask + change mask type (Alpha/Vector/Luminance) in right sidebar Mask section
  - Preconditions: edit access
  - Result: image displayed only inside mask shape; non-destructive
  - Article: Masks

- **Workflow:** Bulk rename layers with numerical suffix
  - Touches: none
  - Steps:
    1. Select layers in canvas or Layers panel
    2. `⌘R` / `Ctrl+R` → Rename layers modal
    3. Type new base name in "Rename to"
    4. Click Number ↑ or ↓ button → token inserted
    5. Adjust start value, view live Preview
    6. Click Rename → all layers updated with unique numeric suffix
  - Preconditions: edit access
  - Result: bulk-renamed layers
  - Article: Rename layers

- **Workflow:** Build a vector network with the Pen tool, then refine in vector edit mode
  - Touches: none
  - Steps:
    1. `P` → Pen tool active
    2. Click on canvas to add anchor; click-drag to add curved point with handles
    3. Hover existing point to close path (small circle indicator) or `Esc` to leave open
    4. `Enter` to enter vector edit mode
    5. Use Move/Bend/Lasso/Cut/Paint/Variable width tools in secondary toolbar
    6. `Enter` again to exit
  - Preconditions: edit access
  - Result: editable vector network layer
  - Article: Vector networks + Edit vector layers

- **Workflow:** Make a 2-D smart selection grid and reflow by deletion
  - Touches: none
  - Steps:
    1. Select a 2-D grid of equally-spaced overlapping objects → pink center handles appear
    2. Hover edge → pink spacing handles appear; drag to set spacing
    3. Click center handle of one object to mark it (solid pink)
    4. Press `Delete` → other layers reflow to fill the gap
  - Preconditions: layers must be equal-distance and overlap on the relevant axis (use Tidy up otherwise)
  - Result: rearranged grid
  - Article: Arrange layers with smart selection

- **Workflow:** Apply auto layout + make responsive nesting (Suggest auto layout)
  - Touches: none
  - Steps:
    1. Select frame/component
    2. `⌃⇧A` (Mac) / `⌃⌥⇧A` (Win) → Suggest auto layout runs
    3. Figma adds nested auto layout frames where appropriate (blue dot in Layers panel)
    4. Adjust per-frame flow (vertical/horizontal/grid), padding, gap, alignment
  - Preconditions: moderately complex design (cards, nav bars, mobile screens)
  - Result: fully or partially responsive layout
  - Article: Toggle on auto layout in designs

- **Workflow:** Multi-paste an object into many frames at once
  - Touches: none
  - Steps:
    1. Select object, `⌘C`/`Ctrl+C`
    2. Select multiple destination frames
    3. `⌘V`/`Ctrl+V` → object pasted into each, preserving relative x/y where possible (centered if not)
  - Preconditions: edit access on destination frames
  - Result: object instances pasted across frames
  - Article: Copy and paste objects

- **Workflow:** Sample a color and apply it to a stroke via eyedropper
  - Touches: none
  - Steps:
    1. Select target layer
    2. Open color picker on Stroke fill swatch
    3. Click Eyedropper or press `I`
    4. Hover canvas to preview color/value, click to apply
  - Preconditions: edit access
  - Result: stroke color updated; can be a raw value, style, or variable
  - Article: Sample colors with the eyedropper tool

### Build design systems

- **Workflow:** Build a button design-system component with variants and properties
  - Touches: none
  - Steps:
    1. Design 4+ button states/variants on canvas → arrange in grid
    2. Select all → "Combine as variants" in right sidebar → component set with dashed-purple stroke
    3. Rename auto-generated property names (Variant/Property 2 → State/Size) → conflict errors flagged
    4. Add boolean property for "show icon" on icon layer (Properties +> Boolean) → icon visibility toggleable per instance
    5. Add text property to label layer → string editable per instance
    6. Optionally add Change-to interactions in Prototype tab → interactive component
    7. Publish via Assets > Libraries
  - Preconditions: edit access; Variants need same property keys
  - Result: reusable button set; instance Properties panel exposes State/Size dropdowns + icon toggle + label text
  - Article: Create and use variants; Explore component properties

- **Workflow:** Create a token-based color system with light/dark modes
  - Touches: none
  - Steps:
    1. Open Variables modal (right sidebar Local variables > Open variables)
    2. Create primitives collection with raw colors (Color variables)
    3. Create semantic collection with aliased variables referencing primitives (right-click value > Create alias)
    4. Add a second mode to semantic collection ("New variable mode") and override values for Dark
    5. Apply semantic variables to fills/strokes via "Apply styles and variables" picker
    6. On a top frame: Appearance > Apply variable mode > pick Light or Dark
    7. Publish library
  - Preconditions: paid plan to publish; modes capped by plan
  - Result: theme switch propagates instantly; alias chain keeps single source of truth
  - Article: Overview of variables, collections, and modes; Create and manage variables and collections; Modes for variables

- **Workflow:** Localize designs with string variables
  - Touches: none
  - Steps:
    1. Create string variable per copy element with mode columns per language
    2. Apply string variable to text content via "Apply variable" in Text section
    3. Switch page or frame mode to test each language
  - Preconditions: paid plan for modes; matching string variable per text
  - Result: single canvas swaps language without duplicating frames
  - Article: Apply variables to designs; Modes for variables

- **Workflow:** Publish a design system update and propagate
  - Touches: none
  - Steps:
    1. Edit main components / styles / variables in source library file
    2. Open Assets > Libraries > Publish # changes
    3. Add description; uncheck assets to skip; choose target (Org/Ent)
    4. Subscribers see blue badge on Libraries icon in their files
    5. Subscriber clicks Review library updates > Updates tab > Update / Update all (Side-by-side or Overlay preview)
  - Preconditions: paid plan; edit access on both ends
  - Result: aligned components across files; mode conflicts surfaced separately if version chains diverge
  - Article: Publish a library; Review and accept library updates

- **Workflow:** Move a published component to a new library file
  - Touches: none
  - Steps:
    1. Publish hidden dependencies first
    2. Cut component from origin (Ctrl/Cmd+X) > Paste in destination (Paste here)
    3. Publish destination as library
    4. Origin library: publish removal
    5. Subscribers accept updates from both libraries
  - Preconditions: edit access on both files; not undoable via Ctrl+Z
  - Result: component lives in new library; instance links rewired via library accept
  - Article: Move published components

- **Workflow:** Swap a file's library to a new version
  - Touches: none
  - Steps:
    1. Open Libraries modal in subscriber file
    2. Select current library > Swap library
    3. Choose replacement library (must have matching asset names)
    4. Toggle "Swap default styles in instances" override behavior
    5. Confirm matches via checkboxes > Swap library
    6. Manually swap unmatched via Instance menu
  - Preconditions: both libraries published; can edit file; can view both libraries
  - Result: bulk re-bind components/styles/variables to new library
  - Article: Swap libraries

- **Workflow:** Use Check designs to enforce design system
  - Touches: (Dev Mode) section "Ready for Dev" entry point
  - Steps:
    1. Select layers (≤25k) on a single page
    2. Right-click > Check designs (or via Ready-for-Dev section dropdown / Actions menu)
    3. Review tabs: Colors / Dimensions / Typography / Components
    4. Hover row to highlight on canvas; pick suggested binding
    5. Apply / Apply all; Ctrl+Z to revert
  - Preconditions: Org/Ent plan + private beta access; published variables-based design system
  - Result: hard-coded values bound to variables/styles; component mismatches flagged for manual fix
  - Article: Check designs in Figma

- **Workflow:** Convert a flexible card component to a slot
  - Touches: none
  - Steps:
    1. In main component, select content frame
    2. Right-click > Convert to slot (or Cmd/Ctrl+Shift+S)
    3. Edit slot property: name, description, optional preferred instances
    4. Publish library
    5. Designers add content via instance: drag in, "Add instances" popup, or duplicate-in-slot — instance stays attached to main
  - Preconditions: open beta access; main component edit
  - Result: simpler library, fewer detached instances, healthier design system
  - Article: Use slots to build flexible components in Figma; Migrate a library to using slots

### Create prototypes

- **Workflow:** Create your first prototype connection
  - Touches: none
  - Steps:
    1. Open Prototype tab (`Shift + E`) → right sidebar swaps mode
    2. Select source layer → small `+` plug icon appears on bounding box
    3. Drag `+` to destination frame → blue noodle drawn; first connection auto-creates flow starting point on source frame; **Interaction details** modal opens
    4. In modal: pick Trigger → pick Action (defaults to Navigate to) → pick Animation + duration/easing
    5. Click Preview in toolbar (`Shift + Space`) → inline preview plays the prototype
  - Preconditions: design lives inside a top-level frame
  - Result: a playable single-step prototype with a starting point
  - Article: Connect your prototype

- **Workflow:** Build a multi-flow prototype using sections
  - Touches: none
  - Steps:
    1. Group related frames into a Section (`Shift + S`, drag over frames) per user-flow (e.g. Browse / Cart / Checkout)
    2. From a back button, drag a connection to the Section (not a specific frame) → Figma will return user to last-visited frame in section
    3. Set flow starting points on each section's entry frame
    4. Rename flows in Prototype panel for presentation-view sidebar
  - Result: prototype with N flows that respects last-visited-frame semantics
  - Article: Use sections in prototyping / Create and manage prototype flows

- **Workflow:** Prototype with main components for shared navigation
  - Touches: Components (cross-domain within Figma Design)
  - Steps:
    1. Move main component to same page as design instances
    2. Switch to Prototype tab, select an interactive object inside the main component (e.g. tab in nav bar)
    3. Drag connection from main component to destination frame
    4. All instances inherit the connection (visible only when instance selected)
  - Preconditions: component is local to page (team-library components cannot be prototyped this way)
  - Result: one connection covers every instance of the navbar/footer/etc.
  - Article: Add prototype connections from main components

- **Workflow:** Build a stateful interactive component (checkbox / button)
  - Touches: Components / Variants
  - Steps:
    1. Create component set with two variants + property `isChecked` true/false
    2. Add **Change to** Prototype action between variants
    3. (Optional) Bind variant property to a boolean variable so other layers respond to state
    4. Place instances → state shared across frames via state-management (memorization + sharing)
  - Result: reusable interactive component whose state persists across navigation
  - Article: Advanced prototyping examples

- **Workflow:** Build a counter / volume bar with variables + expressions
  - Touches: Variables (cross-domain)
  - Steps:
    1. Create number variable (e.g. `volumeLevel`) with default value
    2. Bind variable to a layer property (e.g. width of rectangle)
    3. On `+` button add Prototype interaction → On click → Set variable → expression `volumeLevel + 5`
    4. Mirror for `-` button with `volumeLevel - 5`
    5. Play prototype to test
  - Result: live numerical control during playback
  - Article: Advanced prototyping examples / Use expressions in prototypes

- **Workflow:** Light/dark theme toggle via Set variable mode
  - Touches: Variables / Modes
  - Steps:
    1. Create variable collection with Light + Dark modes for color tokens
    2. Bind tokens to design (fills, etc.)
    3. On a toggle button add interaction → action **Set variable mode** → pick collection + mode
    4. Play prototype → page-level mode flips
  - Result: theme switch in prototype with no extra frames
  - Article: Variable modes in prototypes

- **Workflow:** Form with conditional submit + error overlay
  - Touches: Variables / Conditionals / Overlays
  - Steps:
    1. Create string vars per question (default `"none"`); bind to radio-button variant properties
    2. Build error overlay frame + success frame
    3. On Submit button: trigger On tap → action Conditional → if `q1=="none" or q2=="none"` Open overlay (error), else Navigate to (success)
  - Result: validation with no extra frames per state combination
  - Article: Advanced prototyping examples / Multiple actions and conditionals

- **Workflow:** Set up a scrollable frame with sticky header
  - Touches: none
  - Steps:
    1. Resize content beyond frame bounds (hold Cmd/Ctrl while dragging to ignore constraints)
    2. Enable Clip content on the frame (Design panel → Layout)
    3. Prototype panel → Scroll behavior → Overflow = Vertical
    4. Select header object → Position = Sticky (or Fixed)
    5. Verify in inline preview
  - Result: scrolling frame with pinned UI; layer order in Layers panel determines stacking
  - Article: Prototype scroll and overflow behavior

- **Workflow:** Preserve scroll position across frames
  - Touches: none
  - Steps:
    1. Ensure top-level frames share identical names or `Prefix / Suffix` pattern (use Cmd/Ctrl+R bulk rename)
    2. Ensure scrolling layers within frames have matching name + parent hierarchy
    3. (No toggle needed — preserved by default)
    4. To opt out on a single transition: select the connection → Interaction details → State → check Reset scroll position
  - Result: consistent scroll position across navigation; legacy interactions need "Update" / "Update all" click
  - Article: Preserve scroll position in prototypes / State management

- **Workflow:** Smart-animate two screens
  - Touches: none
  - Steps:
    1. Duplicate the source frame to keep layer names identical
    2. Modify properties (position/size/opacity/rotation/fill) on duplicate
    3. Connect frame A → frame B with Animation = Smart animate (or other transition + "Animate matching layers")
    4. Tune duration & easing; preview in modal or inline preview
  - Tips: regroup or rename layers to opt particular layers in/out of matching
  - Result: per-property tween instead of whole-frame transition
  - Article: Smart animate layers between frames

- **Workflow:** Play and present
  - Touches: none
  - Steps:
    1. Inline: toolbar **Preview** or `Shift + Space` → embedded preview
    2. Full: toolbar **Present** or `Cmd+Opt+Return` / `Ctrl+Alt+Enter` → new tab
    3. Adjust scaling/device/Hide UI in Options menu (URL gets updated `&hide-ui=1` etc., re-copy share link)
    4. Optionally Make available offline (preload while online)
    5. Press `R` to restart, arrow keys to navigate
  - Article: Play your prototypes / Present prototypes offline

- **Workflow:** Mirror / view on mobile
  - Touches: none
  - Steps:
    1. Open file on desktop, sign into Figma mobile app with same account
    2. Select a top-level frame on desktop
    3. On mobile open Mirror tab → live frame appears; tap to interact via prototype connections
    4. Or open prototype share link in mobile browser
  - Article: View prototypes on a mobile device

### Work together in files

- **Workflow:** Leave actionable feedback as a viewer
  - Touches: none
  - Steps:
    1. Press `C` → enter comment mode → comment cursor; sidebar opens.
    2. Click on canvas (or drag for region) → comment composer opens.
    3. Type message, press `@` to mention reviewer → suggestion list.
    4. Submit → pin appears on canvas, recipient notified.
    5. Press `Esc` to exit comment mode and resume editing.
  - Preconditions: at least can-view access to file.
  - Result: persistent threaded comment anchored to design region.
  - Article: Add comments to files

- **Workflow:** Resolve and clean up a comment thread
  - Touches: none
  - Steps:
    1. Click pin / sidebar row → comment modal.
    2. Reply or react; on consensus click resolve checkmark → thread hidden.
    3. (Optional) sidebar filter → toggle "Show resolved comments" to revisit.
    4. Owner ellipsis → Delete thread → confirm if permanent removal needed.
  - Preconditions: own comment for delete; any user for resolve.
  - Result: clean canvas; resolved threads archived.
  - Article: View and manage comments

- **Workflow:** Present a design walkthrough remotely
  - Touches: none (works in editor and prototype presentation view)
  - Steps:
    1. Hover own avatar → Multiplayer tools → "Spotlight me".
    2. Viewers see prompt; click "Not now" or auto-follow.
    3. Pan/zoom/switch pages → followers' canvases mirror.
    4. (Optional) Use cursor chat (`/`) to overlay live captions.
    5. Click "Stop" at top of canvas to end.
  - Preconditions: at least one other user in file; multiplayer cursors visible to others.
  - Result: synchronous presentation without screen-share.
  - Article: Present to collaborators using spotlight

- **Workflow:** Branch → review → merge full lifecycle
  - Touches: none (Org/Enterprise plan; cross-references Dev Mode for handoff)
  - Steps:
    1. From main file, file-name menu → Create branch → name it. Sidebar shows `File › Branch`.
    2. Edit branch freely; periodically file-name menu → Update from main → resolve conflicts if any.
    3. Share branch via Share modal or branches modal Copy link.
    4. File-name menu → Review and merge changes → add reviewers → Request review with description.
    5. Reviewer opens branch, uses side-by-side / overlay diff, picks Approve or Suggest changes.
    6. Branch creator addresses suggestions, Resend request if needed.
    7. Editor of main clicks Merge → resolves any remaining conflicts → optional Edit merge description → confirm.
    8. Branch auto-archived; main version history records "Branch merged" checkpoint.
  - Preconditions: Full seat on Organization/Enterprise plan; main-file edit access for create+merge of viewer-owned branches requires the "Allow viewers to copy/share/export" setting.
  - Result: branch changes integrated into main with auditable checkpoints.
  - Article: Guide to branching (+ Share / Update / Request / Review / Merge / Manage articles)

- **Workflow:** Recover from a bad merge or update
  - Touches: none
  - Steps:
    1. Open affected file (branch or main) → file-name menu → Show version history.
    2. Identify pre-event checkpoint ("Before update" or "Before merge"; merge has branch-merge icon).
    3. Ellipsis → Restore this version → Done.
    4. If restoring main, all collaborators see rollback; if branch was archived, restore from Branches modal Archived tab.
    5. Re-attempt update or merge cleanly.
  - Preconditions: edit access to affected file.
  - Result: file rolled back; two new autosave checkpoints inserted.
  - Article: Incomplete merges or updates

### Import and export

- **Workflow:** Import a Sketch file via the file browser
  - Touches: none
  - Steps:
    1. Open file browser, click Create > Import (top-right) -> dropdown opens
    2. Click "From your computer" -> OS file picker
    3. Select .sketch file, click Open -> upload spinner / progress
    4. Click Done -> new converted Figma Design file appears in project
  - Preconditions: `can edit` to project (or own drafts); .sketch file ideally from latest Sketch version
  - Result: Figma Design file with artboards->frames, pages preserved, symbols->components; styles NOT migrated; missing-fonts prompt may appear
  - Article: Import Sketch files

- **Workflow:** Import a Sketch file from inside an open file
  - Touches: none
  - Steps:
    1. Click Main menu (top-left)
    2. File > New from Sketch file -> file picker
    3. Pick .sketch and Open -> creates new design file from import
  - Preconditions: have a design file open; `can edit`
  - Result: new file (not merged into current); same conversion semantics as file-browser path
  - Article: Import Sketch files

- **Workflow:** Drag-drop file(s) into the file browser
  - Touches: none
  - Steps:
    1. Drag file(s) from OS into file browser window -> drop overlay
    2. Release -> upload begins, items appear in current project/drafts
  - Preconditions: supported file types (.fig/.sketch/.jam/.deck/.buzz/.site/.make/.pptx/PNG/JPG)
  - Result: imported files in file browser
  - Article: Import files to the file browser

- **Workflow:** Move asset between design tools using clipboard SVG
  - Touches: none (external app handles its side)
  - Steps:
    1. In source tool, copy asset as SVG to clipboard
    2. In Figma Design file, right-click canvas -> Paste here -> vector layer appears at cursor
  - Preconditions: source app supports SVG clipboard; SVG markers/patterns will be lost
  - Result: vector content placed on Figma canvas
  - Article: Copy assets between design tools

- **Workflow:** Copy a Figma asset out as SVG
  - Touches: none
  - Steps:
    1. Select object on canvas
    2. Right-click -> Copy/Paste as -> Copy as SVG -> SVG on clipboard
    3. Paste into target external app
  - Preconditions: not blocked by file-level "restrict copying"
  - Result: asset transferred to other tool with vector fidelity
  - Article: Copy assets between design tools

- **Workflow:** Export selection with single configuration
  - Touches: none
  - Steps:
    1. Select layer/frame/component/group/section
    2. Click "+" in Export section (right sidebar) -> default config row appears
    3. Set scale, suffix, format -> live preview updates
    4. Optional: click Preview to inspect
    5. Click Export -> browser download or desktop save dialog
  - Preconditions: not blocked by "restrict copying"; desktop app prompts for filename and location
  - Result: file written to disk; slash-separated layer names produce nested folders
  - Article: Export from Figma Design

- **Workflow:** Slice-based region export
  - Touches: none
  - Steps:
    1. Open Region tools dropdown in toolbar -> pick Slice tool
    2. Click+drag on canvas to define slice bounds
    3. Optionally move/resize slice
    4. Add export configuration on the slice (right sidebar Export section)
    5. Click Export
  - Preconditions: `can edit` access (Slice tool gated)
  - Result: PNG/JPG/SVG/PDF of the exact rectangular region with absolute padding
  - Article: Export from Figma Design

- **Workflow:** Bulk export all configured selections on a page
  - Touches: none
  - Steps:
    1. Press Shift+Cmd+E (Mac) / Shift+Ctrl+E (Win), or Main menu > File > Export
    2. Export modal lists every configured selection on current page with thumbnail / scale / format / dimensions
    3. Hover thumbnails for filename; click thumbnail to jump to canvas
    4. Uncheck rows to exclude
    5. Click Export -> all selected files downloaded together
  - Preconditions: at least one selection on the page has an export configuration
  - Result: zip / multi-file download of all checked items
  - Article: Export from Figma Design

- **Workflow:** Export entire current page (no selection)
  - Touches: none
  - Steps:
    1. Deselect everything on canvas
    2. Use Export section to add a config (acts on the page)
    3. Click Export
  - Preconditions: no selection
  - Result: full canvas exported as one file
  - Article: Export from Figma Design

- **Workflow:** Export with custom scale / fixed dimension
  - Touches: none
  - Steps:
    1. In Export config row, edit scale field
    2. Type number + `x` (multiplier), `w` (width px), or `h` (height px) -> field accepts and applies
    3. Click Export
  - Preconditions: SVG and PDF only support 1x; raster formats accept any scale
  - Result: rasterized output at that scale (DPI = 72 * multiplier)
  - Article: Export formats and settings

- **Workflow:** Hide a fill in the exported file only
  - Touches: none
  - Steps:
    1. Select frame/layer with a fill
    2. In Fill section, deselect "Show in exports" on that fill row -> canvas unchanged, fill marked excluded
    3. Export normally
  - Preconditions: layer has at least one fill
  - Result: fill visible on canvas but absent in exported asset
  - Article: Export from Figma Design

- **Workflow:** Export to Dev Mode handoff
  - Touches: Dev Mode (cross-product)
  - Steps:
    1. Switch to Dev Mode
    2. Select an object -> Export section appears in right sidebar
    3. Configure and export, or download the asset directly from the Dev Mode export panel
  - Preconditions: in Dev Mode; object selected
  - Result: same export pipeline available to developers in handoff
  - Article: Export from Figma Design (links to Dev Mode "export or download assets" article)

## Dev Mode

- **Workflow:** Inspect a design and copy code to IDE
  - Touches: Figma Design (file), Dev Mode, IDE
  - Steps:
    1. Open file in Figma Design → toggle Dev Mode (`Shift D`) → mode switches, sidebars repaint
    2. Click target layer on canvas → Inspect panel populates
    3. (Optional) Choose language + unit from Code-section dropdown → snippet regenerates
    4. Hover snippet → click Copy → snippet on clipboard
    5. Paste in IDE
  - Preconditions: Full or Dev seat
  - Result: code lifted from Dev Mode into editor
  - Article: Guide to inspecting / Use code snippets in Dev Mode

- **Workflow:** Designer hands a frame off to dev
  - Touches: Figma Design (designer), Dev Mode (developer), Notifications channel
  - Steps:
    1. Designer selects section/frame/component
    2. Click "Mark as ready for dev" → badge appears, version-history entry written
    3. Notification fanout to anyone who previously opened file in Dev Mode
    4. Developer opens file → "Ready for dev" sidebar entry visible → opens Ready-for-dev view
    5. Click design → Focus view
  - Preconditions: paid plan, Full/Dev seat for setting status
  - Result: design surfaced in handoff queue, dev notified
  - Article: Dev Mode statuses and notifications / Dev Mode ready for dev view

- **Workflow:** Resolve a "Changed" design after handoff
  - Touches: Figma Design (designer), Dev Mode (developer)
  - Steps:
    1. Edit lands → design auto-flagged Changed
    2. Developer sees Changed badge → clicks "Compare changes" in Inspect → modal opens
    3. Reviews edited-layers list and side-by-side / overlay
    4. Designer clicks Changed badge → enters reason → "Done with changes" → status reset, notification with reason fires
  - Preconditions: design previously marked ready/completed (Org/Enterprise for full status flow)
  - Result: developer aligned with latest spec; status cleared
  - Article: Dev Mode statuses and notifications / Compare changes in Dev Mode

- **Workflow:** Annotate a design for handoff
  - Touches: Figma Design (designer adds), Dev Mode (developer reads)
  - Steps:
    1. Designer presses `Shift T` → click target layer
    2. Type note + click "+ Property" to bind live properties
    3. Pick category (Development/Interaction/Accessibility/Content/custom)
    4. Repeat with `Shift M` for measurements (click-drag between layers)
    5. Developer in Dev Mode sees green dots → click to read; can filter by category from zoom menu
  - Preconditions: Full seat + can-edit to add; Full/Dev + view to read
  - Result: persistent contextual notes that update with design changes
  - Article: Add measurements and annotate designs

- **Workflow:** Link a Jira/GitHub/Storybook resource to a layer
  - Touches: External tool (URL source), Dev Mode
  - Steps:
    1. Copy URL externally
    2. Select layer in Dev Mode → Inspect → Layer options → "Add a dev resource link"
    3. Paste URL → Enter
    4. (If layer is main component) link inherits to all instances
  - Preconditions: Full/Dev seat
  - Result: clickable contextual link on layer; if a matching plugin exists it auto-launches in Plugins tab
  - Article: Link Dev resources to layers in Dev Mode

- **Workflow:** Set up Code Connect (CLI) for a design system
  - Touches: Codebase (CLI), GitHub, Dev Mode
  - Steps:
    1. Plan mappings; install code-connect package for stack (React/HTML/SwiftUI/Compose)
    2. Author `.figma.ts` (or equivalent) mapping props code↔Figma
    3. Run `figma connect publish` from CLI → snippets pushed
    4. In Dev Mode, inspect component → Code section says "connected" and shows real snippet
  - Preconditions: Org/Enterprise plan, Full/Dev seat
  - Result: design-system code snippets surface in Dev Mode and via MCP server
  - Article: Code Connect

- **Workflow:** Inspect & implement via VS Code extension
  - Touches: Dev Mode, VS Code extension, codebase
  - Steps:
    1. Install Figma for VS Code → sign in
    2. Either: in Dev Mode select frame → Inspect → Options → "Open in VS Code"; OR in VS Code Figma sidebar pick file
    3. View Inspect / Code / Component / Dev resources / Assets tabs in editor sidebar
    4. Use autocomplete suggestions while typing
    5. (Optional) Click dev-resource link → opens local file if matching path exists
  - Preconditions: VS Code extension installed; Full/Dev seat
  - Result: design context next to code without browser context-switch
  - Article: Figma for VS Code

- **Workflow:** Implement a design via MCP server + AI agent
  - Touches: MCP client (Cursor/Claude/VS Code/Codex), Figma MCP server, codebase, optionally Code Connect
  - Steps:
    1. Install remote Figma MCP server in client; install Figma plugin/skills (incl. `/figma-implement-design`)
    2. In Figma, copy URL of frame/selection
    3. In MCP client, paste URL and prompt (e.g. "implement this")
    4. Skill orchestrates MCP tool calls → reads design context, variables, Code Connect snippets → writes code
  - Preconditions: supported MCP client; remote server connected; (recommended) Code Connect
  - Result: code matching design + design system in repo
  - Article: Get started with the Figma MCP server / Figma skills for MCP

- **Workflow:** Compare a frame's versions
  - Touches: Dev Mode, Version history
  - Steps:
    1. Select top-level frame (or Shift+click two components)
    2. Inspect → "Compare changes" → modal
    3. Pick prior version from timeline → side-by-side or overlay
    4. Click an edited layer → see code-diff and property-diff
  - Preconditions: file has version history (auto/manual)
  - Result: clear delta between current and chosen version
  - Article: Compare changes in Dev Mode

- **Workflow:** Try component variants without editing the file
  - Touches: Dev Mode, Component playground (modal)
  - Steps:
    1. Select component or instance in Dev Mode
    2. Inspect panel → "Explore component behavior" → playground modal
    3. Toggle variants/props/variable modes
    4. Read updated specs; close modal — original file unchanged
  - Preconditions: component with properties / variants
  - Result: viewer-local exploration of component states
  - Article: Guide to Dev Mode

- **Workflow:** Trace a variable to a raw value
  - Touches: Dev Mode (Variables modal + Inspect)
  - Steps:
    1. Inspect a layer → click variable name in code or "Variable details" icon
    2. Modal shows alias chain → optionally swap mode
    3. Copy code snippet for the variable
  - Preconditions: file uses variables
  - Result: developer knows mode-aware raw value and tokenized name
  - Article: Variables in Dev Mode

## Projects

- **Workflow:** Build a reusable button main component
  - Touches: Figma Design only
  - Steps:
    1. `T` → click canvas → type "Button" → text layer "Button" appears, auto-named
    2. Select text → set Typography (font Outfit, size 16) → preview updates live
    3. `Shift A` → wraps text in auto-layout frame "Frame N"
    4. Set Horizontal/Vertical resizing to "Hug contents" → frame snaps to text bounds
    5. Rename frame to "Button" → Layers panel updates
    6. Add Fill (#DEB0FB), Stroke (#000, Inside, 1px), Corner radius (1000), Drop shadow effect
    7. Tweak auto-layout padding (H 32, V 24)
    8. Click Create component (or `Opt/Alt + Cmd/Ctrl + K`) → component icon turns purple → instance appears in Assets panel
  - Preconditions: Editor open in a design file with edit access
  - Result: Reusable text-driven Button component
  - Article: Create a simple button component

- **Workflow:** Build an interactive button via variants + prototype
  - Touches: Figma Design (Prototype tab)
  - Steps:
    1. Build save-icon component, then create variant → component set with `Has fill = false/true`
    2. Build button main component (auto-layout, fill, stroke, drop shadow, radius), drop icon instance inside (`Opt/Alt`-drag), set Auto-layout Gap 12
    3. Apply Boolean properties `Show label`, `Show icon` to inner layers via Apply variable/property → toggles appear on instance
    4. Add variants: rename Property 1→state (default/hover/pressed), Property 2→status (unsaved/saved); change fills per variant
    5. Switch to Prototype tab → drag blue `+` between variants to add: While hovering → Mouse down → Mouse leave → Mouse up connections, all Smart animate Ease in/out 150ms
    6. `Shift Space` → inline preview → cursor over button cycles states
  - Preconditions: Component & component-set features available
  - Result: Stateful button component set with hover/press/save semantics
  - Article: Design an interactive button component

- **Workflow:** Build a 12-variant tooltip component set
  - Touches: Figma Design
  - Steps:
    1. Text "Tooltip" → `Shift A` → set Fill container H, Hug V, max width 250 → frame "Content" (vertical layout, padding 12/8, gap 4)
    2. Polygon (triangle) → vector edit, round top point radius 1 → resize 12x8 → rotate -90 → align as "Arrow"
    3. Right-click both → Frame selection → name "Tooltip/left" → `Shift A` → drop shadow → Create component
    4. Add variant (right) → flip arrow horizontally → set property `arrowDirection=right`
    5. Add `top`, `bottom` variants (change auto-layout flow to vertical, rotate arrow with `Shift`)
    6. For 8 minor variants (leftTop/leftBottom/etc.): change alignment + Independent corners radius on Content
  - Preconditions: Auto layout, Variants
  - Result: 12-variant component set with positional arrow
  - Article: Create a tooltip component set

- **Workflow:** Build a responsive card component (auto layout + constraints + min/max)
  - Touches: Figma Design
  - Steps:
    1. Build play-button component (40x40 frame, fill, radius, drop shadow, polygon triangle, optical-center)
    2. Build album-art frame 360x240, image fill (Choose image OR Make an image AI), nest play-button instance, apply Constraints Right/Bottom → button pins to bottom-right when frame resizes
    3. Add gradient fill on top of image for contrast
    4. Two text layers (title, creator), `Shift A` to wrap → Truncate text Max lines 1 → Fill container width
    5. Select album-art + metadata → `Shift A` → name "card" → set children resizing to Fill container, except metadata height = Fixed
    6. Add min/max W/H on card → Create component
  - Preconditions: Image or AI image generation
  - Result: Responsive podcast card component with anchored play button
  - Article: Create a responsive card with auto layout and constraints

- **Workflow:** Build a 3-frame loading animation as a component set
  - Touches: Figma Design (Prototype + Components)
  - Steps:
    1. Frame "loading/1" 100x100 black → 4 ellipses 24x24, snap to corners, use Smart selection pink handles to set 24px gap, recolor white via Selection colors panel
    2. Duplicate → "loading/2" → select all ellipses → rotate -90° (`Shift` drag)
    3. Duplicate → "loading/3" → resize ellipses to 60x60 → align centers
    4. Prototype tab → connect 1→2→3→1, each After delay 100ms, Smart animate Custom bezier `0.5,-0.1,0.5,1.1` 300ms
    5. Multi-select 3 frames → Create component dropdown → Create component set → variants "1","2","3" auto-named
    6. Drop instance into iPhone-preset frame → Present
  - Preconditions: prior workflow steps; consistent slash-naming
  - Result: Looping loader component set
  - Article: Create a loading animation in Figma

- **Workflow:** Build photo-gallery prototype with bulk-rename + smart animate
  - Touches: Figma Design
  - Steps:
    1. Drafts → New design file
    2. `F` → iPhone 14/15 Pro preset → frame "gallery-view"; duplicate → "expanded-view"
    3. `R` + `Shift` → 200x200 square in gallery-view, image fill (Swap image → Upload new)
    4. Duplicate square twice, replace image fills with two more uploads
    5. In expanded-view: text "Back" 24px Semi Bold; rectangle 393x700; duplicate frame ×2 → expanded-view-1/2/3
    6. Copy fill from gallery image → paste into matching expanded-view rectangle
    7. Multi-select matching pairs → `Cmd/Ctrl + R` → bulk rename to image-1/2/3 (smart animate needs matching names)
    8. `Shift E` → drag prototype connections gallery → expanded views (On click + Smart animate); reverse via Back button → Present
  - Preconditions: prepared images
  - Result: Interactive gallery prototype with smart-animated transitions
  - Article: Create a photo gallery prototype

- **Workflow:** Advanced prototype using variables + conditional logic
  - Touches: Figma Design (Variables modal, Prototype tab)
  - Steps:
    1. Duplicate Community starter file (preset Get-started/Loading/Home pages)
    2. Create 4 Boolean variables (hasMusic/hasFood/hasDesign/hasNews) defaulting False
    3. Assign each Boolean to topic-button instance and to corresponding podcast cards (eye → Assign variable) — cards hidden when False
    4. In Prototype tab, edit topic component "false" interaction → Set variable `topicsSelected = topicsSelected + 1` (creates Number variable)
    5. Create String `buttonState=disabled`, assign to Continue button's `state` variant property
    6. Add Check if/else `topicsSelected > 0` → Set `buttonState="enabled"`
    7. Mirror logic on "true" variant for decrement + revert
    8. Add Skip button → on click, Set all 4 hasXxx variables to true → Navigate to Loading
    9. `Shift Space` to verify
  - Preconditions: Variables, Interactive components, prior prototype skills
  - Result: State-aware onboarding flow that gates Continue and supports Skip
  - Article: Create an onboarding flow with advanced prototyping

- **Workflow:** Design a custom file thumbnail
  - Touches: Figma Design + file metadata
  - Steps:
    1. `F` → right sidebar choose "Plugin / file cover" preset → 1920x1080 frame
    2. Right-click frame → Set as thumbnail
    3. Build pattern: rectangle + polygon → Union → stroke outside → duplicate icon to row of 20 with set spacing 100 → group → repeat for 15 rows → group, rotate -30°, lock
    4. Copy tooltip component set from Community playground file → paste into working file → Assets panel populates
    5. Drag tooltip instance, set arrowDirection=bottom, edit text "Web Tooltips", `K` Scale to 9, lock
    6. Add subheading text, lock; add scattered tooltip instances grouped + scaled + rotated
  - Preconditions: existing component library or Community file copy
  - Result: Custom thumbnail surfaced in file browser & Community
  - Article: Design a file thumbnail

- **Workflow:** Build a search-icon component (vector + boolean)
  - Touches: Figma Design
  - Steps:
    1. Enable Pixel grid + Snap to pixel grid in Zoom/view options
    2. Inside 24x24 icon-grid frame, `O` + `Shift` → 16x16 ellipse in top-right corner; remove fill, add 2px stroke
    3. `P` → click two points to draw 4-px line in bottom-left → 2px stroke, round end caps
    4. Multi-select → Union selection → centered with alignment controls
    5. Rename frame "search-icon"
  - Preconditions: 24x24 icon grid template
  - Result: Reusable single-vector search icon with proper bounding box
  - Article: Design a search icon

- **Workflow:** Build a reusable icon grid component
  - Touches: Figma Design
  - Steps:
    1. `F` + `Shift` → 24x24 frame "Icon grid"
    2. Layout grid: enable, set size 1; enable Snap to grid; set small nudge 0.5
    3. Use `P` to draw a red 0.2-weight reference line above frame (style source)
    4. Draw orthogonal X with Pen, duplicate + flip, then 3 vertical + 3 horizontal center lines (Copy properties / Paste properties)
    5. Add 20x20 ellipse, 16x20 + 18x18 rectangles (corner radius 1) — paste reference style each time
    6. Select frame → `Enter` to drill in → Union selection → opacity 10% on red fill
    7. Create component
  - Preconditions: clean canvas
  - Result: Reusable 24x24 icon grid component with safe area + trim area
  - Article: Create a reusable icon grid

- **Workflow:** Illustrate using Figma Draw tools (noodle bowl)
  - Touches: Figma Design ↔ Figma Draw toggle in toolbar
  - Steps:
    1. Toolbar → Draw → enters Figma Draw mode
    2. Build bowl: 180 ellipse → arc handle Sweep 50%; 40x12 rectangle base, send to back; group, corner radius 2, Inner shadow + Texture effect
    3. Build noodles: 6 overlapping 25-px ellipses → invert fill/stroke → Flatten → vector edit, alternately delete left/right points → Bend tool to smooth → set width / stroke
    4. Build chopsticks: paths with Variable width per point in vector edit (stroke width profiles)
    5. Compose final illustration
  - Preconditions: edit access; Figma Draw available
  - Result: Stylized vector illustration
  - Article: Create a noodle bowl illustration

- **Workflow:** Apply a pattern fill from a source layer (strawberry seeds)
  - Touches: Figma Draw
  - Steps:
    1. Create base ellipse, modify in vector edit (Mirror angle/length), apply texture effect
    2. Create a small "Seed" reference layer
    3. Select base → add Fill → Pattern → Select source → click Seed
    4. Configure tile (Hexagonal), Direction, Scale, X/Y spacing, Alignment, Opacity
    5. Delete Seed layer (pattern persists)
  - Result: Dynamic pattern fill that updates if source changes
  - Article: Create a strawberry illustration

- **Workflow:** Build with non-destructive transforms (orange slices)
  - Touches: Figma Draw
  - Steps:
    1. Two ellipses; use arc handle Sweep 15% on top one for slice shape
    2. Click Radial repeat → Repeat group 1 created with original nested
    3. Edit Repeat: Count 7, Gap 0.1 Units; rotate / change corner radius on inner original — propagates
    4. Add center ellipse; align centers; right-click → Flatten → single Vector layer "Slices"
  - Result: Realistic sliced-orange composition with editable source
  - Article: Create an orange illustration

- **Workflow:** Build a glass-vase scene
  - Touches: Figma Draw
  - Steps:
    1. 600x750 frame, dark fill; locked rectangle background with linear gradient
    2. Vase = Union of circle + 2 rectangles (one with Individual corners radius), positioned via X/Y
    3. Linear gradient fill on vase
    4. Effects → Glass with Light angle/intensity/Refraction/Depth/Dispersion/Frost
    5. Add flower shapes via shape primitives + Transforms
  - Result: Translucent vase illustration
  - Article: Illustrate a flower vase using shapes, transforms, and the glass effect

- **Workflow:** Compose a Figma Draw social-media post
  - Touches: Figma Draw
  - Steps:
    1. Pen + Variable width to build knife/fork/spoon utensils
    2. Use arc handles for ellipse-based fork bowl, then Flatten so bounding box hugs new shape
    3. Compose three utensil illustrations as pattern source
    4. Apply Pattern fill on background frame using utensils source
    5. Add Text on a path for headline; Offset vector for decorative outline
  - Result: Branded social-media graphic
  - Article: Create a social media post using Figma Draw

- **Workflow:** Create marketing assets in Figma Buzz with Bulk create
  - Touches: Figma Buzz
  - Steps:
    1. Visit `figma.com/buzz/new` → Buzz file with template picker opens
    2. Pick template (Ads tab → Instagram ad) → Add template
    3. Left nav → Edit content → update text fields and image (or Make an image AI)
    4. Prepare XLSX with columns Title / Date / Image (image embedded in cell)
    5. Left nav → Bulk create → Upload XLSX → click each canvas layer then map to data column → Create assets
  - Preconditions: spreadsheet of asset variants
  - Result: Many on-brand asset variants generated in one pass
  - Article: Create marketing assets in Figma Buzz

- **Workflow:** Build a FigJam meeting board
  - Touches: FigJam
  - Steps:
    1. New FigJam file (`figjam.new` or file browser tile)
    2. `Shift S` → drag 5 sections → recolor each → name (Roll call / Show & tell / General reminders / Project updates / Question of the week) → optionally lock background
    3. Add Photo booth widget (toolbar More → Widgets → search) into Roll call; add Timeline / Asana / Jira widgets to Project updates
    4. `S` → place stickies in General reminders (auto-tagged with author, can disable)
    5. Drag/drop or paste images into Show & tell (`Cmd/Ctrl Shift K`)
    6. `E` → choose stamp from wheel → place
    7. (Optional) Hide section contents until reveal time
  - Result: Reusable meeting board ready to facilitate
  - Article: Create your first meeting board in FigJam

- **Workflow:** Run a meeting in FigJam (collaboration layer)
  - Touches: FigJam (+ share/permissions)
  - Steps:
    1. Plan agenda; pick template or board
    2. Click Share → set Can edit / Can view per invitee or via link → optionally Open session for outside participants → Send invite or Copy link
    3. Attach FigJam link to Google Calendar / Microsoft Teams meeting
    4. Start audio call from toolbar → green Connected indicator
    5. Hover own avatar → Spotlight me to lead participants through sections
    6. Use sections + voting / stamps / cursor chat / emotes for engagement
  - Preconditions: file with content, paid plan for Open session
  - Result: Facilitated meeting with collaborators in-file
  - Article: Run meetings in FigJam

- **Workflow:** Beginner illustration in Figma Design (magic potion)
  - Touches: Figma Design
  - Steps:
    1. Add ellipse + 2 rectangles with shape tools, resize via W/H fields, round corners on lip
    2. Align via red guides + Align horizontal centers
    3. `Cmd/Ctrl G` → group "Bottle" → set fill → lock
    4. Modify potion ellipse via Edit object (vector edit) — drag top point
    5. Add small bubble ellipses, group with potion → "Potion"
    6. Add cork rectangle, reorder layer beneath Bottle in Layers panel
    7. (Optional) Frame selection + Export panel
  - Result: Layered illustration with locked organized layers
  - Article: Create an illustration in Figma Design

## Figma Draw

- **Workflow:** Enter Figma Draw and access illustration tools
  - Touches: Figma Design (host editor)
  - Steps:
    1. Open a Figma Design file with `can edit` access → Design toolbar visible
    2. Click "Draw" in the toolbar toggle → toolbar swaps to Pen/Brush/Pencil; right sidebar swaps to illustration properties; left sidebar Layers shows enlarged previews
    3. Use illustration tools; switch toggle back to "Design" to regain auto layout / prototyping
  - Preconditions: Full seat on paid plans; can edit access
  - Result: User is in Draw mode with illustration UI surface
  - Article: Explore Figma Draw

- **Workflow:** Sketch a stroke with the Pencil or Brush tool
  - Touches: Figma Design (vector edit mode for later refinement)
  - Steps:
    1. Switch to Draw mode → Draw toolbar appears
    2. Select Pencil or Brush from toolbar → secondary toolbar appears
    3. Set color, size, style in secondary toolbar → preview updates
    4. Click and drag on canvas (Shift to constrain straight) → stroke renders as vector network with auto-placed points
    5. (Optional) Enter vector edit mode to adjust points
  - Preconditions: In Draw mode
  - Result: New vector-network stroke layer on canvas
  - Article: Draw with illustration tools

- **Workflow:** Create and reuse a custom brush
  - Touches: Figma Design (Outline stroke, text→vector conversion)
  - Steps:
    1. Prepare a single closed vector layer (shape, custom path, or flattened text); use Outline stroke if path is open
    2. Right-click the layer → hover "Create brush" → choose Stretch or Scatter → brush appears in Brush styles menu
    3. Select Brush tool → pick the new style → draw on canvas
    4. (Cross-file) Copy-paste a layer using the brush into another file → brush auto-registers there permanently
  - Preconditions: Closed vector path; Draw mode for drawing step
  - Result: Reusable brush style available in current file (and any file it's pasted into)
  - Article: Draw with illustration tools

- **Workflow:** Build a repeating pattern with transforms
  - Touches: Figma Design (canvas + boolean ops conceptually similar)
  - Steps:
    1. Switch toolbar toggle to Draw
    2. Select source object on canvas
    3. In right sidebar, open "Additional transform modifier" menu → pick Radial repeat or Linear repeat → object wrapped in transform group, repetitions render
    4. Click the transform in right sidebar → adjust repetition count and spacing in Transform settings
    5. (Optional) Add more objects to the transform group for complexity
    6. When satisfied, click "Apply transforms to selection" → repetitions baked into individual canvas layers
  - Preconditions: In Draw mode; an object selected
  - Result: Pattern as either live transform group (editable) or flattened layers (after Apply)
  - Article: Create patterns with transforms
