# Left Navigation Panel

**Region role:** Primary surface for navigating file structure (pages + layer tree) and file metadata. Left edge of editor, full window height, always visible with edit access.

**Anatomy, top → bottom:**
1. File-name dropdown + main `…` menu + minimize-UI button
2. Tabs: **File** (default) / **Assets**
3. File tab body: Pages selector → Layers tree
4. Assets tab body: Libraries opener + search + grouped library list
5. (Optional, rolling out) Narrow left navigation bar docked even further left — separate strip

**Global behavior:**
- Width is resizable by dragging the right edge of the panel.
- Pressing `Shift \` minimizes both sidebars; selecting an object temporarily re-expands the right sidebar only (not this one).
- Pressing `Cmd/Ctrl \` hides / shows the entire UI chrome including this panel.

**Canonical reference images:**
- `helper/figma_docs/articles/Figma Design/view-layers-and-pages-in-the-left-sidebar/images/img_01.png` (not directly inspected; article's canonical hero image shows the navigation panel on a purple background)
- `helper/figma_docs/articles/Figma Design/navigating-ui3/images/img_01.png` — side-by-side Previous UI / New navigation bar comparison

---

### file-name-dropdown
- **Scope flag:** mixed (entries vary)
- **Location:** Top of panel, row 1.
- **Default appearance:** File name rendered as text, with a small chevron (`⌄`) immediately to its right indicating a dropdown. To the right of that a minimize-UI icon (a diagonal double-arrow or collapse glyph).
- **States:**
  - default — file name visible, no background
  - hover — not covered in corpus
  - dropdown open — overlay menu anchored below the file name
- **Dropdown entries (from docs / ui-map):**
  - Move file — `visual-only` (file management out of scope)
  - Publish library — `visual-only`
  - Create branch — `visual-only`
  - Version history — `visual-only`
  - Show version history — `visual-only`
  - Show all branches — `visual-only`
  - File actions: duplicate, rename, delete — `visual-only`
- **Notes / gaps:** Every menu entry is visual-only for this mock; the dropdown itself is rendered but does not trigger actions. Clicking the chevron opens the menu as a pure UI gesture — behavior decided in `plan/03`.

### main-menu-button
- **Scope flag:** mixed
- **Location:** Top row of panel, to the right of the file-name dropdown (sometimes shown as part of the same visual row).
- **Default appearance:** Three-dot `…` icon (or hamburger on some rollouts).
- **Dropdown entries:** File actions + View submenu (Rulers, Property labels, theme toggle, Outlines, Pixel grid) + Preferences submenu (Highlight layers on hover, Nudge amount, Use old shortcuts for outlines, Accessibility).
  - View submenu entries: mostly `visual-only` (Rulers, Pixel grid out of scope; Property labels / Outlines — could be rendered if trivial, but default `visual-only`).
  - Preferences entries: `visual-only`.
  - Theme toggle (light/dark) — `visual-only` in the menu; actual theme is handled by ThemeProvider in code and defaults to dark.
- **Reference images:** not directly inspected
- **Source articles:** `view-layers-and-pages-in-the-left-sidebar`, `navigating-ui3`, `adjust-your-zoom-and-view-options`
- **Notes / gaps:** GAP — the exact visual shape / placement of the main menu entry button varies across rollouts (sometimes inline with file name, sometimes separate). Pick the most common form from `navigating-ui3` imagery.

### minimize-ui-button
- **Scope flag:** functional-in-scope
- **Location:** Top-right of this panel (same row as file-name header).
- **Trigger / shortcut:** `Shift \` or click.
- **Default appearance:** Collapse icon (two arrows pointing inward / diagonal close glyph).
- **States:**
  - default — icon visible
  - panels minimized — button icon may flip to an expand glyph, or stay the same (corpus ambiguous)
- **Behavior:** Collapses left navigation panel and right properties panel. Selecting an object on canvas re-expands only the right panel temporarily; deselecting re-collapses.
- **Reference images:** `navigating-ui3/images/img_01.png` (visible in both halves of side-by-side)
- **Source articles:** `view-layers-and-pages-in-the-left-sidebar`, `navigating-ui3`

### tabs-file-assets
- **Scope flag:** mixed — File tab functional-in-scope, Assets tab visual-only
- **Location:** Below file-name row, spanning the top of the panel body.
- **Default appearance:** Two text tabs labeled "File" and "Assets", side-by-side. Active tab shown with heavier weight or underline (exact indicator varies — not captured precisely in corpus).
- **Tabs:**
  - **File** — `Opt/Alt 1`. Default. `functional-in-scope`. Contains pages + layers.
  - **Assets** — `Opt/Alt 2`. `visual-only`. Switching to this tab is allowed (UI swap), but the Assets body is populated only with empty-state messaging since components/libraries are out of scope.
- **Reference images:**
  - `navigating-ui3/images/img_01.png` — tabs visible at top of the nav panel in the "New navigation bar" half
- **Source articles:** `view-layers-and-pages-in-the-left-sidebar`

### pages-selector
- **Scope flag:** functional-in-scope
- **Location:** Top of File tab body.
- **Default appearance:** Current page name rendered as a clickable text row, with a small expand indicator (disclosure triangle or chevron to the left of the name).
- **States:**
  - collapsed — shows only the current page name
  - expanded — reveals the full pages list below; current page is highlighted; `+` button at the right end of the pages-list header adds a new page
  - hover over page row — right-click reveals context menu (rename / duplicate / delete / copy link to page — copy-link visual-only)
- **Behavior:** Click the current page name (or the chevron) to toggle the pages list. Click any other page row to switch to that page. `+` creates a new page. Right-click enters the rename/delete context. `Cmd/Ctrl R` may bulk-rename when a page row is selected.
- **Reference images:** `navigating-ui3/images/img_01.png` shows the Pages list with "Row text" entries — and the `+` adder
- **Source articles:** `view-layers-and-pages-in-the-left-sidebar`

### layers-tree
- **Scope flag:** functional-in-scope
- **Location:** Below the pages selector in the File tab body. Takes the remaining vertical space of the panel.
- **Default appearance:** Indented list of layer rows. Each row shows (left → right):
  - Indent lines / disclosure triangle (for rows that have children)
  - Layer-type icon (specific to the layer type — see below)
  - Layer name (editable on double-click or `Cmd/Ctrl R`)
  - Hover-only icons on the right: eye (visibility toggle) and padlock (lock toggle)
- **Layer-type icons (from docs):**
  - Frame — rounded-square outline
  - Group — dashed square
  - Component — purple four-square / rhombus icon (`visual-only` — components out of functional scope, but layer may still display as a frame internally)
  - Instance — similar purple icon, darker (`visual-only`)
  - Text — `T` glyph
  - Shape — icon varies by shape (rectangle, ellipse, line, etc.)
  - Image — mountain / landscape glyph
  - Auto-layout frame — icon reflects configuration (vertical / horizontal / grid) — the layer still shows as a frame for us since auto layout is visual-only
  - Section — distinct section icon (rounded rectangle with a section mark)
  - Animated GIF / video — play-triangle overlay on image icon
- **States per layer row:**
  - default — name + icon, subdued color
  - selected — highlighted background (matches canvas selection)
  - hovered — eye + padlock icons appear on the right
  - hidden — grayed out
  - locked — padlock icon remains visible (not just on hover)
  - mask indicator — mask icon + upward arrow on the masked layers (mask ops visual-only per plan/00 §3)
  - top-level frame name — bolded
- **Behavior highlights:**
  - Click a row to select that layer on canvas.
  - Double-click name or `Cmd/Ctrl R` to rename.
  - Drag a row to reorder / reparent.
  - Arrow keys navigate; Enter enters a group / component; `Esc` or `Shift Enter` exits.
  - Collapse-all icon in top-right corner of the Layers section collapses every expanded row except the current selection.
- **Reference images:**
  - `navigating-ui3/images/img_01.png` — Layers section visible with rows "Frame 1", "Header / Desktop", "Checkout Flow", "Cart", "Button / Active", "Footer", "Warning"
- **Source articles:** `view-layers-and-pages-in-the-left-sidebar`, `explore-design-files`, `basic-shape-tools-in-figma-design`
- **Notes / gaps:** Exact hover-transition behavior for eye / padlock icons not captured in corpus; will use a clean "appear on row hover" default.

### collapse-layers-icon
- **Scope flag:** functional-in-scope
- **Location:** Top-right corner of the Layers section (not the panel header — the Layers subsection).
- **Default appearance:** Collapse glyph (chevrons pointing together).
- **Behavior:** Collapses all expanded layers; if a layer is selected, its ancestors stay expanded so the selection remains visible.
- **Source articles:** `view-layers-and-pages-in-the-left-sidebar`

### assets-tab-body
- **Scope flag:** visual-only (entire body — components and libraries out of scope)
- **Location:** Content area of the panel when Assets tab is active.
- **Contents (from docs, for visual rendering):**
  - Libraries button (icon) — opens Libraries modal — `visual-only`
  - Search field — `visual-only`
  - Libraries-and-settings gear icon (filter libraries, toggle Grid / List view) — `visual-only`
  - Empty-state message when no libraries are linked — can serve as the permanent state in our mock
  - Grouped library list (file > page > frame) — empty for us
- **Reference images:** `navigating-ui3` — Assets tab appears in later images; specific image index not confirmed.
- **Source articles:** `view-layers-and-pages-in-the-left-sidebar`
- **Notes / gaps:** Because the entire Assets body is visual-only, populating it with realistic sample libraries is unnecessary. An empty-state visual is sufficient.

### find-replace-takeover
- **Scope flag:** visual-only
- **Location:** Replaces the entire navigation panel body when open (keeps the panel's outer chrome but swaps the File/Assets contents).
- **Trigger / shortcut:** `Cmd/Ctrl F`, or clicking a Find icon in the panel (position varies with rollout).
- **Default appearance (when open):** Query input field at top, filter chips (text / frame / shape, etc.), scope toggle (current page / all pages), result list below, Replace tab switch.
- **Behavior (per docs):** Typing filters results; clicking a result selects the corresponding layer on canvas; `Esc` closes and returns to Layers.
- **Source articles:** `view-layers-and-pages-in-the-left-sidebar`, `find-and-replace-in-figma`
- **Notes / gaps:** Since functional-scope §2 does not list Find/Replace, we mark the whole takeover surface as visual-only — the panel can render the Find icon and allow the takeover to open, but queries do not execute.

---

## Rolling-out narrow left navigation bar
- **Scope flag:** visual-only
- **Location:** Narrow vertical strip *further* left than the main navigation panel (separate, additional region).
- **Contents (from docs):**
  - Variables modal entry icon — `visual-only` (variables out of scope)
  - Assets tab icon — `visual-only`
  - Find-and-replace icon — `visual-only`
  - Bottom: file notifications (library updates, missing-font alerts) — `visual-only`
- **Collapse behavior:** Collapses along with the main panel on Minimize UI / `Shift \`.
- **Reference images:** `navigating-ui3/images/img_01.png` right-half shows the new nav bar with Pages / Assets / Find / Variables / notifications icons stacked vertically to the far left.
- **Notes / gaps:** Presence of the new navigation bar is a rollout-variant; user may or may not want it rendered in the mock. Default assumption: **render it**, all icons visual-only. Flagged in `gaps.md` for user confirmation.

---

## Panel container
- **Shape:** Full-height vertical panel docked to the left edge.
- **Background:** Distinct panel background color (near-white in the light-theme reference; dark-panel color in dark theme via ThemeProvider).
- **Edges:** Right edge is draggable to resize the panel width. Drag cursor appears on hover at that edge.
- **Separator:** Subtle 1-pixel divider between the panel and the canvas (qualitative — exact color handled by ThemeProvider).
- **Reference images:** `view-layers-and-pages-in-the-left-sidebar/` hero image, `navigating-ui3/images/img_01.png`.
- **Notes / gaps:** Width default not captured numerically; we pick a sensible default at build time.
