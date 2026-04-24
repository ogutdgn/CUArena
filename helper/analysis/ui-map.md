# UI Map — Figma Spatial Layout

_Synthesized from 216 articles. Authoritative source: *Navigating UI3*, *Access design tools from the toolbar*, *View layers and pages in the left sidebar*, *Design, prototype, and explore layer properties in the right sidebar* (all Figma Design > Tour the interface). Per-domain overlays from sibling partials._

The "UI3" interface is the current Figma Design / Dev Mode / Draw chrome (rolled out 2024). All four products covered here share **the same shell** — file browser, top window chrome, canvas, plus left + right sidebar slots — and swap their **content** based on product / mode / selection. Figma Draw is a *toolbar toggle* inside Figma Design, not a separate app. Dev Mode is a *mode toggle* inside Figma Design. Only FigJam and Figma Buzz use a different toolbar geometry, but they're outside this corpus's primary focus.

---

## 1. Top-level layout (UI3 default — Figma Design, edit access)

```
+---------------------------------------------------------------+
| [left navigation panel]    [   canvas   ]    [right sidebar]  |
| (full height, dockable)    (fills space)     (full height)    |
|                                                               |
|                            [bottom-center toolbar]            |
+---------------------------------------------------------------+
                            [optional bottom-bar overlays:      ]
                            [keyboard shortcuts panel,          ]
                            [help & resources, toast notifs     ]
```

Four interactive regions: **toolbar (bottom-center, floating)**, **left navigation panel (left edge, full height)**, **right properties panel (right edge, full height)**, **canvas (center, scrollable)**. There is **no persistent global top bar** in UI3 — file name moved into the left navigation panel.

---

## 2. Toolbar (bottom-center, floating)

**Product:** Figma Design (incl. Draw mode and Dev Mode variants). FigJam puts tools in a different bottom toolbar; Buzz uses a left navigation bar instead.

**Layout (left → right) in Figma Design edit mode:**

| Group | Items | Default shortcut |
|---|---|---|
| Move tools dropdown | Move / Hand / Scale | `V` / `H` / `K`; `Space` = temporary Hand |
| Region tools dropdown | Frame / Section / Slice | `F` / `Shift S` / *Slice action* |
| Shape tools dropdown | Rectangle (default) / Line / Arrow / Ellipse / Polygon / Star / Image–video | `R` / `L` / `O` / `Shift Cmd K` |
| Creation tools dropdown | Pen / Pencil | `P` |
| Text | — | `T` |
| Comment tools dropdown | Comment / Annotation / Measurement | `C` / `Shift T` / `Shift M` |
| Actions menu | Floating panel anchored to icon | — |
| Mode switcher | Design ↔ Prototype ↔ Dev Mode | `Shift D` for Dev Mode; `Shift E` for Prototype |
| Figma Draw entry | Toggles Draw mode | — |

**Variants:**

- **Vector-edit mode**: secondary toolbar **replaces** the main toolbar, exposing Move / Pen / Bend / Lasso / Cut / Paint / Variable width / Shape builder. Entered with `Enter` on a vector; exited with `Enter` / `Esc` / Done.
- **Dev Mode**: edit-time tools (shapes, pen) are absent. Toolbar exposes Annotate (`Shift T`), Measure (`Shift M`), and the dev-status / Mark-as-ready button when a section/frame/component is selected.
- **Draw mode**: shape/frame/component creation tools are replaced with **Pen, Brush, Pencil**. A tool-sensitive secondary toolbar (color/size/style for Pencil/Brush; brush styles menu for Brush) appears.
- **View-only / View seat**: reduced toolbar with an `Ask to edit` button.

**Keyboard focus:** `F6` (Mac) / `Ctrl F6` (Win), then arrow keys to pick a tool.

---

## 3. Left navigation panel (left edge, full height)

**Product:** Figma Design (with Dev Mode and Draw variants).

**Anatomy (top → bottom):**

1. **File-name dropdown** (Move file, Publish library, Branch, Version history, etc.) + main `…` menu.
2. **Minimize UI button** (top corner, also `Shift \`).
3. **Tabs:** **File** (default, `Opt 1` / `Ctrl 1`) — **Assets** (`Opt 2` / `Ctrl 2`).
4. **File tab body:**
   - **Pages selector** (click current page name to expand pages list with `+` to add).
   - **Layers tree** (new layers added to top of list / top of group).
   - **Collapse-layers** icon in top-right corner.
5. **Assets tab body:**
   - Libraries modal opener.
   - Search field.
   - Libraries-and-settings menu (filter libs, Grid/List view toggle).
   - Grouped library list (file > page > frame).
6. **Find / Replace** — icon also lives in left sidebar; opening it **takes over the panel contents**; `Esc` returns to Layers.

**Width:** resizable by dragging right edge.

**Dev Mode variant:** Replaced with a Dev-Mode-specific Navigation panel: search, Pages-with-status, "Ready for dev" entry, ready-flagged sections. When a top-level frame is selected, the panel collapses into a **scoped Layers panel** for that frame only.

**Draw mode variant:** Layers panel renders **enlarged visual previews** instead of compact text rows; double-click a preview = zoom canvas to that layer.

**Rolling-out separate left navigation bar (Full-seat users):** a narrow vertical strip docked to the far left, *additional* to the left navigation panel. Houses Variables modal entry, Assets, Find-and-Replace; bottom of the bar shows file notifications (library updates, missing-font alerts). Collapses on Minimize UI / `Shift \`.

---

## 4. Right properties panel (right edge, full height)

**Product:** Figma Design (Dev Mode and Draw variants).

**Anatomy:**

1. **Header row** — zoom % + Zoom/view options dropdown.
2. **Sub-header row** — selection actions: Mask, Component, Boolean ops, More `…`. Multi-edit text and Multi-edit variants buttons appear when applicable.
3. **Tabs (edit access):** **Design** | **Prototype**.
4. **Tabs (view-only):** **Comment** | **Properties**.
5. **Body — context-driven sections** (typical order with selection):
   - Layout (or **Auto layout** when applied)
   - Position (rotate / flip / align / constraints / Ignore auto layout)
   - Appearance (visibility eye, blend modes, variable modes, opacity)
   - Typography (was Text)
   - Fill, Stroke, Effects
   - Component / Component properties / Variants
   - Export
6. **Body — nothing selected:** Page section (background color picker + Hide eye), local styles + variables, Export page.

**Section visibility rules (most state-dependent panel in Figma):**

- Layout guide → frames only.
- Mask → mask groups only.
- Selection colors → mixed selections only.
- Properties → components / instances only.
- Constraints → auto-layout-free children of a frame only.
- Auto layout settings → auto-layout frames only.
- Export in Dev Mode → only when an object is selected.

**Behavior with Minimize UI:** panel collapses; selecting an object temporarily re-expands it; deselecting re-collapses.

**Dev Mode variant:** Replaces Design tab with **Inspect** tab — read-only properties for handoff: Code section (language + unit picker, Code/List toggle, copyable snippets, codegen-plugin slot), Styles, Variables (read-only table; click → variable details modal), dev resources, asset auto-detect + source/layer image export, export configs. A **Plugins** tab sits alongside.

**Prototype mode variant:** Entire sidebar swaps to prototyping properties — `Shift E` (or clicking the Prototype tab) is the toggle. Sections include Flows, Interactions, Scroll behavior (Overflow + Position), Variables/conditions.

**Draw mode variant:** Slider-driven illustration property set + a unique **Additional transform modifier** menu with no Design equivalent.

**Comment mode variant:** Sidebar contents are replaced with the comments list.

---

## 5. Canvas

**Product:** All. Centered, fills space between sidebars and above the toolbar.

**Interactions:**

- **Pan:** `Space` + drag, two-finger trackpad slide, arrow keys (Shift = bigger step, scaled to zoom).
- **Zoom:** `Cmd/Ctrl` + scroll, pinch, Magic Mouse double-tap, or `Shift +/-/1/2`. Default opens at "Zoom to fit". Zoom % visible in top-right of right sidebar.
- **Hover** a layer → bounding box; click selects.
- **Default background:** light `#F5F5F5`, dark `#1E1E1E`; per-page; new pages inherit; **not editable in Dev Mode**.

**Canvas overlays / on-canvas chrome:**

| Overlay | When shown | Notes |
|---|---|---|
| Selection bounding box | Object selected | `W×H` label below; rotation cursor outside corners; corner-radius circle handles inside rounded shapes; pink handles for smart selection; arc handles on ellipses; on-canvas blue track handles for grid auto layout |
| Dashed selection bounds | Parent of selection | Distinguishes parent from child |
| Layout guides | When enabled / inside frames | Dotted (canvas guides) or solid (inside frames); rulers along top/left edges of canvas (when enabled); rulers highlight blue when a frame is selected |
| Snap / Measure guides | While transforming | Red guide line + measurement labels |
| Mask outlines | Toggle in View menu | Green outlines |
| Pixel grid | Zoom ≥ 400% (when enabled) | Per-pixel grid |
| Action bar | Object selected (bottom-center on canvas) | Quick actions: Mark as ready for dev, create-component, suggest auto-layout |
| Multiplayer cursors | Always (toggleable) | Colored per-user, name label; can be hidden |
| Cursor chat bubble | While typing in cursor chat | Cursor-anchored; pulses 5s after last keystroke; ≤ 52 chars; ephemeral |
| Comment pins | Comment mode visible OR `Shift C` toggle | Live in canvas overlay space, not selectable layers; auto-cluster on zoom-out (count + author avatars on hover); move with parent frame/component/group |
| Annotation dots (Dev Mode) | Always in Dev Mode | Small green dots; expand to text + bound layer properties on click |
| Persistent measurement nodes (Dev Mode) | Always in Dev Mode | Labeled line nodes on canvas; visible to all viewers |
| Ephemeral measure lines | Hold `Alt`/`Option` over a 2nd layer in Dev Mode | Red distance lines; local-only; disappear on release |
| Dev status badges | Dev Mode | "Ready for dev" / "Completed" / "Changed" next to section/frame/component labels |
| Prototype noodles | Prototype mode | Blue lines between connected frames; `+` plug icon on selection hover |
| Prototype flow start badges | Prototype mode | Blue play badge at top-left of starting frame; flow name; double-click rename; drag to move |
| Component-set frame | Always | Dashed-purple stroke, no fill |
| Slot region (instance) | Hover/select inside instance slot | Pink border |
| Spotlight follower border | Following a presenter | Colored border around viewport (matches presenter avatar) + "Following X" banner |
| Pixel cursor box-select overlay | Keyboard box selection mode | Pink cursor overlay |
| Insertion crosshair | Keyboard-driven object insertion | Crosshair at placement point |

---

## 6. Mode-driven UI variations (summary table)

A "mode" is a global UI state that swaps multiple regions at once.

| Mode | Trigger | Toolbar | Left sidebar | Right sidebar | Canvas chrome |
|---|---|---|---|---|---|
| **Design** (default) | — | Full edit toolbar | Layers/Assets/Pages | Design tab + selection-driven sections | Standard |
| **Prototype** | `Shift E` or tab click | Same toolbar | Same | Prototype tab (Flows, Interactions, etc.) | Noodles, plug icons, flow badges |
| **Dev Mode** | `Shift D` or open dev link | Annotate, Measure, Mark-as-ready (no edit tools) | Dev nav (search, ready-for-dev, scoped layers) | Inspect tab + Plugins tab | Annotation dots, measurement nodes, status badges; aggressive hover measurements |
| **Draw** | Toolbar toggle | Pen / Brush / Pencil + secondary toolbar | Layer thumbnails (enlarged previews) | Slider illustration props + transforms | Same as Design (no auto-layout / prototyping) |
| **Vector edit** | `Enter` on vector | Vector secondary toolbar | Same | Reduced | Vector points + handles visible |
| **Crop** | Crop action on image | — | — | Sliders + aspect ratio picker | Crop handles |
| **Multi-edit variants** | `Q` while in component set | — | — | Multi-edit variants section | Dotted rectangles around variants |
| **Comment** | `C` | Comment tool active | — | Comments list replaces sidebar | Pins; canvas object editing disabled |

---

## 7. UI hide / minimize states

| State | Trigger | Effect |
|---|---|---|
| **Minimize UI** | `Shift \` | Collapses left + right panels (and new nav bar). Toolbar stays. Selecting an object temporarily re-expands the right panel. |
| **Hide / Show UI** | `Cmd/Ctrl \` | Toggles entire chrome (toolbar + both sidebars). |
| **Spotlight** | Click on collaborator avatar (Spotlight) | Minimizes left + right + toolbar; presenter avatar in toolbar gets dashed border + numeric follower count; followers see colored canvas border + top-of-canvas "Following X" banner. |

---

## 8. Floating overlays / non-docked surfaces

**Product:** Figma Design (most also in Dev Mode and Draw).

| Surface | Anchor | Notes |
|---|---|---|
| Actions menu | Toolbar Actions icon | Floating panel; overlays canvas |
| Find / Replace | Replaces left sidebar contents | Esc to return to Layers |
| Keyboard shortcuts panel | Bottom of viewport | Floating, dockable strip |
| Help and resources | Bottom-right corner | — |
| Color picker | Anchored to swatch | Floating modal |
| Libraries modal | Assets tab → Libraries button | Floating modal |
| Variable details modal (Dev Mode) | Variables list entry | Modal |
| Interaction details modal (Prototype) | Selected connection on canvas | Floating modal anchored to selection — **not** a sidebar panel |
| Compare changes modal (Dev Mode) | Inspect → Compare button | Timeline + side-by-side / overlay diff |
| Branches modal / Branch review modal | File-name dropdown / branch indicator | Side-by-side or overlay diff (rasterized) |
| Bulk export modal | `Shift Cmd/Ctrl E` | Aggregates configured selections |
| Rename modal | `Cmd/Ctrl R` | Bulk rename with regex/match preview |
| Right-click context menu | Cursor | Selection-sensitive (e.g., Draw "Create brush" only on closed vector; Export entries hidden when restrict-copying is on) |
| Toast notifications | Bottom of screen | E.g., "Pixel preview: 2x" |
| Inline preview window (Prototype) | `Shift Space` | Floating in-editor window; mirrors live edits |
| Presentation view | Opens new tab | Top + bottom toolbar, left flows sidebar, Options menu; URL mutates with options like `&hide-ui=1` |
| Cursor chat bubble | Cursor | Ephemeral; overlay |

---

## 9. Permission-driven variations

| Access level | Toolbar | Right sidebar tabs | Notes |
|---|---|---|---|
| Edit | Full toolbar | Design / Prototype | All left-sidebar interactions |
| View-only / View seat | Reduced toolbar with `Ask to edit` button | Comment / Properties | Can still copy code/SVG/PNG; Prototyping toggle exposed only in Zoom/view options |
| Dev Mode reader | Dev-mode toolbar (read-only) | Inspect | No edit tools |
| Restrict copying enabled | — | Export section disappears for viewers; "Copy as SVG/PNG" context menu entries suppressed | UI absence, not just disabled |

---

## 10. Per-product UI shape

| Product | Toolbar geometry | Sidebar shape | Notes |
|---|---|---|---|
| **Figma Design** | Bottom-center | Left + right sidebars | Canonical UI3; everything above |
| **Dev Mode** | Bottom-center (dev variant) | Left dev nav, right Inspect | Mode of Figma Design; same shell |
| **Figma Draw** | Bottom-center (Draw variant) | Left layer thumbnails, right illustration props | Mode toggle inside Figma Design |
| **Projects** | n/a — file-management surface | n/a | Corpus content here is *tutorials* (build-along projects), not a separate UI surface; references file browser only peripherally |
| **FigJam** (referenced) | **Bottom toolbar** with different tool set | — | Separate file type |
| **Figma Buzz** (referenced) | **Left navigation bar** (Edit content / Bulk create) | — | Separate file type |

---

## 11. Cross-product and shared chrome

These elements appear regardless of mode:

- **File name + branch indicator** (top of left nav panel): renders `File name › Branch name` when on a branch; URL contains `/branch/<id>`.
- **Avatar stack** (right side of toolbar / top of right panel area): collaborator avatars; entry to viewer history, Follow / Spotlight, Multiplayer tools dropdown.
- **Share button** (top): opens Share modal (Can edit / Can view roles, link sharing scopes).
- **Mode switcher** at right end of toolbar (Design / Prototype / Dev Mode / Draw).
- **Branch review status badges** (next to branch name): gray "In review" / yellow "Changes suggested" / green "Approved".

---

## 12. UI elements relevant to the classifier (semantic-event boundaries)

Flagging UI states whose presence/absence is observable and meaningful for distinguishing semantic events:

- **Mode toggle state** (Design / Prototype / Dev Mode / Draw / Vector edit / Crop / Multi-edit variants / Comment) — distinguishes the same raw input as different semantic actions.
- **Selection presence and type** — drives most of right-sidebar visibility; absence of an action bar implies no selection.
- **Modal / overlay open** (Interaction details, Color picker, Libraries, Compare changes, Bulk export, Rename) — gates whether a click is canvas-edit or modal interaction.
- **Vector edit mode entry/exit** (`enter_vector_edit` / `exit_vector_edit`) — a sub-mode boundary.
- **Comment mode entry/exit** — disables canvas object editing.
- **Restrict copying** — UI absence (Export section gone, copy-as menu suppressed); useful negative signal.
- **Branch indicator** — distinguishes branch-context edits from main-file edits.
- **Read-only viewer mode** — connections hidden by default; only main-component variant interactions visible.
- **Multiple equivalent triggers** for the same semantic action: `Shift A` ≡ right-click → Add auto layout; `Opt+Cmd+K` ≡ create-component button; `Opt`-drag from main ≡ drag from Assets ≡ copy/paste an instance — the classifier must collapse these to one event.
- **Drag-drop import vs paste import** — both create a layer but the classifier should record them as distinct (different event sources, different position semantics).
- **Single export vs bulk export** — distinct commands, similar shortcut family.
- **Inline preview vs Presentation view** — two distinct playback contexts with different chromes and URL state.
