# Toolbar

**Region role:** Primary tool selection + mode switching surface. Bottom-center, floating, always visible (except when UI is hidden / user is in Spotlight).

**Anatomy, left → right:**
1. Move tools dropdown
2. Region tools dropdown
3. Shape tools dropdown
4. Creation tools dropdown (Pen / Pencil)
5. Text tool
6. Comment tools dropdown
7. Actions menu
8. Mode switcher (three-button segmented control on the far right: **Draw / Design / Dev Mode**)

**Global behavior:** A tool selected via the toolbar (or its keyboard shortcut) replaces the active tool and shows an **active** state on the corresponding button. Pressing `Esc` reverts to the Move tool in most contexts.

**Canonical reference images:**
- `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/images/img_01.png` — full toolbar, Move tool active, all groups visible, mode switcher on right
- `helper/figma_docs/articles/Figma Design/navigating-ui3/images/img_01.png` — onboarding-style tour with whole UI visible

---

### move-tools-dropdown
- **Scope flag:** functional-in-scope
- **Location:** Toolbar, leftmost group.
- **Default appearance:** Single arrow-cursor icon (Move tool) + small chevron (`⌄`) indicating the dropdown can be expanded.
- **States:**
  - default — icon visible, no background fill
  - active / selected — solid blue filled square behind the icon (the arrow cursor turns white on blue). This is the default state when a file opens (Move tool is selected by default).
  - hover — not covered in corpus
- **Dropdown entries (when chevron is clicked):**
  - **Move** — `V`. Default sub-tool. Select and move objects.
  - **Hand** — `H`. Pan canvas without selecting. Also temporarily activated by holding `Space`.
  - **Scale** — `K`. Resize entire objects including their strokes, text, and nested layers.
- **State-driven content changes:** The icon shown on the button reflects whichever sub-tool is active (arrow for Move, open-hand for Hand, expand-arrows-diagonal for Scale).
- **Reference images:**
  - `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/images/img_01.png` — leftmost icon in blue-active state
- **Source articles:** `access-design-tools-from-the-toolbar`, `navigating-ui3`

### region-tools-dropdown
- **Scope flag:** functional-in-scope (individual sub-tools vary — see below)
- **Location:** Toolbar, second group from left.
- **Default appearance:** Frame icon (stylized `#` / hash shape suggestive of frame bounds) + chevron.
- **States:**
  - default — icon visible, no fill
  - active / selected — solid blue filled square when the Frame, Section, or Slice tool is being used
  - hover — not covered in corpus
- **Dropdown entries:**
  - **Frame** — `F`. Create a frame by dragging on canvas (free-size) or with a preset via the right sidebar (desktop/mobile/etc.). *Functional-in-scope.*
  - **Section** — `Shift S`. Create a section (a container for organizing frames). *Functional-in-scope.*
  - **Slice** — opens slice-creation sub-tool (no explicit shortcut in UI3 toolbar; previously had its own shortcut). *Functional-in-scope for the slice region itself; coupled export operation is visual-only per plan/00 §3.*
- **State-driven content changes:** Button icon reflects active sub-tool.
- **Reference images:**
  - `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/images/img_01.png`
- **Source articles:** `access-design-tools-from-the-toolbar`, `frames-in-figma-design`

### shape-tools-dropdown
- **Scope flag:** functional-in-scope
- **Location:** Toolbar, third group from left.
- **Default appearance:** Rectangle icon (empty square) + chevron. Rectangle is the default sub-tool so the rectangle icon is what shows until a different shape sub-tool is picked.
- **States:**
  - default — rectangle (or currently-selected shape) icon, no fill
  - active / selected — solid blue fill when a shape tool is in use (ready to draw)
  - hover — not covered in corpus
- **Dropdown entries:**
  - **Rectangle** — `R`
  - **Line** — `L`
  - **Arrow** — `Shift L`
  - **Ellipse** — `O`
  - **Polygon** — (no default shortcut)
  - **Star** — (no default shortcut)
  - **Image / video** — `Shift Cmd/Ctrl K` (opens OS file picker to select one or more media files for placement)
- **State-driven content changes:** Button icon reflects active sub-tool.
- **Reference images:**
  - `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/images/img_01.png`
- **Source articles:** `access-design-tools-from-the-toolbar`, `basic-shape-tools-in-figma-design`

### creation-tools-dropdown
- **Scope flag:** functional-in-scope
- **Location:** Toolbar, fourth group from left.
- **Default appearance:** Pen-nib icon (with a small anchor-point dot) + chevron.
- **States:**
  - default — pen/pencil icon, no fill
  - active / selected — solid blue fill while the pen or pencil tool is active (cursor shows insertion crosshair or pencil)
  - hover — not covered in corpus
- **Dropdown entries:**
  - **Pen** — `P`. Builds vector networks with anchor points and bezier curves.
  - **Pencil** — (no default shortcut). Freehand drawing; Figma applies smoothing.
- **Reference images:**
  - `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/images/img_01.png`
- **Source articles:** `access-design-tools-from-the-toolbar`, `vector-networks`

### text-tool
- **Scope flag:** functional-in-scope
- **Location:** Toolbar, fifth position from left (single button, no dropdown).
- **Trigger / shortcut:** `T`.
- **Default appearance:** Capital `T` icon.
- **States:**
  - default — `T` icon, no fill
  - active / selected — solid blue fill; cursor becomes text-placement crosshair; click places a text layer, click-drag places bounded-width text
  - hover — not covered in corpus
- **Reference images:**
  - `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/images/img_01.png`
- **Source articles:** `access-design-tools-from-the-toolbar`, `explore-text-properties`

### comment-tools-dropdown
- **Scope flag:** visual-only (comments, annotations, measurements all out of functional scope)
- **Location:** Toolbar, sixth position from left.
- **Default appearance:** Speech-bubble icon + chevron.
- **States:**
  - default — icon, no fill
  - hover — not covered in corpus
  - click — in real Figma, clicking enters comment mode and opens dropdown with sub-entries. Here: dropdown opens visually but entries are non-functional.
- **Dropdown entries (all visual-only):**
  - **Comment** — `C`. Visual-only.
  - **Annotation** — `Shift A` (Full-seat). Visual-only.
  - **Measurement** — `Shift M` (Full-seat). Visual-only.
- **Reference images:**
  - `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/images/img_01.png`
- **Source articles:** `access-design-tools-from-the-toolbar`, `guide-to-comments-in-figma`
- **Notes / gaps:** Click behavior of a visual-only dropdown — does the menu still expand? — is a `plan/03` engine-behavior decision.

### actions-menu-button
- **Scope flag:** visual-only (Actions menu content — AI features, plugins, productivity commands — all out of scope)
- **Location:** Toolbar, right of comment tools.
- **Default appearance:** Sparkle / star-icon glyph (indicates AI-adjacent features).
- **States:**
  - default — icon, no fill
  - hover — not covered in corpus
  - click — in real Figma: opens floating Actions panel anchored to icon; shortcut `Cmd/Ctrl K`. Here: visual-only.
- **Reference images:**
  - `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/images/img_01.png`
  - `helper/figma_docs/articles/Figma Design/navigating-ui3/images/img_04.png` — not inspected; listed as reference per article content
- **Source articles:** `access-design-tools-from-the-toolbar`, `navigating-ui3`
- **Notes / gaps:** Actions panel content entirely visual-only — inventory of entries (AI tools, plugins, productivity commands) not documented here because panel does not open behaviorally.

### mode-switcher
- **Scope flag:** mixed (see sub-elements below)
- **Location:** Toolbar, far right; three-button segmented control visually separated from the rest of the toolbar by a small gap.
- **Default appearance:** Three icons side-by-side forming a rounded-rectangle segmented control. Left to right:
  - Draw — squiggle/brush stroke icon
  - Design — ruler-plus-cursor icon (active by default, shown with solid background fill)
  - Dev Mode — `</>` code brackets icon
- **States (per segment):**
  - default — icon only, no background fill
  - active — solid background fill behind the icon indicating the current mode
  - hover — not covered in corpus
- **Sub-elements:**
  - **Draw toggle** — `visual-only`. Clicking would enter Figma Draw mode; here non-functional.
  - **Design button** — `functional-in-scope` (this is the mode we are always in; segment stays in active state permanently).
  - **Dev Mode button** — `visual-only`. Keyboard shortcut `Shift D`. Clicking would enter Dev Mode; here non-functional.
- **State-driven content changes:** In real Figma, clicking Draw or Dev Mode replaces the whole toolbar and sidebars with the respective mode's UI. Because those modes are visual-only, we do not render their replacements — the Design segment remains active.
- **Reference images:**
  - `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/images/img_01.png` — right-side three-button block clearly visible
- **Source articles:** `access-design-tools-from-the-toolbar`, `navigating-ui3`, `guide-to-dev-mode`
- **Notes / gaps:** The Prototype mode is *not* part of this segmented control; Prototype lives as a right-panel tab (see `regions/right-properties.md`). `ui-map.md` describes the mode-switcher as "Design/Prototype/Dev Mode" but the toolbar image shows Draw/Design/Dev Mode. Image is the source of truth; analysis was imprecise.

---

## Secondary toolbar — Vector edit mode (visual-only)
- **Scope flag:** functional-in-scope (vector edit mode itself is in scope per plan/00 §2 "vector edit mode")
- **Location:** Replaces the main toolbar when the user enters vector edit mode (`Enter` on a selected vector).
- **Default appearance:** Same bottom-center rounded-pill shape; different icon set.
- **Entries (left → right):**
  - Move (`V`)
  - Pen (`P`)
  - Bend — convert corner points to smooth, or adjust bezier handles
  - Lasso (`Q`) — drag a lasso to select multiple vector points
  - Cut (`X`) — cut the path at a point
  - Paint (`Shift B`) — fill closed regions of the network
  - Variable width — edit stroke width profile per point
  - Shape builder — merge and cut regions (may be out of scope; flag)
  - Done / Exit — exits vector edit; also `Enter` or `Esc`
- **States:** Same as main toolbar buttons (default / active / hover).
- **Reference images:** Not directly covered in the articles I read; `helper/analysis/ui-map.md` §2 documents this layout.
- **Notes / gaps:** GAP — no reference image inspected for vector-edit secondary toolbar. Listed in `gaps.md`.

---

## Mode variants we do not render
- **Draw mode toolbar** — replaces main toolbar with Pen / Brush / Pencil + secondary stroke-style toolbar. `visual-only` for the entry button only; the replacement toolbar is never rendered because we do not enter Draw mode.
- **Dev Mode toolbar** — Annotate, Measure, Mark-as-ready, no edit tools. Not rendered.
- **View-only toolbar** — reduced toolbar with `Ask to edit` button. Not rendered (per plan/00 §3a: we always render the edit-access view).
- **Presentation toolbar** — different window entirely. Out of scope.

## Overall toolbar container
- **Shape:** horizontally elongated rounded rectangle (pill-shaped), floating over the canvas near the bottom center of the screen.
- **Background:** distinct panel color (looks like a neutral near-white in the light theme reference images; in dark theme this will be a dark panel color handled at ThemeProvider).
- **Spacing:** small gaps between tool groups; tool groups themselves are dropdowns so adjacent chevrons produce a tight pairing.
- **Elevation:** appears to float above the canvas — implied soft shadow.
- **Reference images:** `access-design-tools-from-the-toolbar/images/img_01.png`.
- **Notes / gaps:** Hover states for the container (cursor changes? subtle emphasis?) are not covered in the corpus.
