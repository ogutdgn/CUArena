# Chrome

**Region role:** Top-level application chrome elements that are *not* part of the toolbar, sidebars, or canvas proper. In UI3, the traditional "top bar" is largely gone — file metadata moved into the left navigation panel, and the collaborator chrome (avatars + Share) migrated to the top-of-right-panel area.

**Anatomy summary:**
- File-name bar — lives in the left navigation panel (see `regions/left-navigation.md` → file-name-dropdown)
- Branch indicator — adjacent to the file name when on a branch (`visual-only`; branching out of scope)
- Avatar stack — top-of-right-panel area, collaborator presence
- Share button — top-of-right-panel area, top chrome
- Present (play-triangle) — top-of-right-panel area, near avatars
- No persistent global top bar in UI3 outside the above.

**Canonical reference images:**
- `helper/figma_docs/articles/Figma Design/navigating-ui3/images/img_06.png` — right-panel header with collaborator chrome (referenced, not directly inspected)
- `helper/figma_docs/articles/Figma Design/design-prototype-and-explore-layer-properties-in-the-right-sidebar/images/img_01.png` — header row of right panel shows avatar + play + Share

---

### avatar-stack
- **Scope flag:** visual-only
- **Location:** Top of the right properties panel (to the left of the Share button). *Not* a standalone top bar — it's in the right-panel header row.
- **Default appearance:** Circular avatars (user initials on a colored background, or profile image) stacked / overlapping. Own avatar always leftmost. Shows up to ~3 visible avatars, a "+N" pill for overflow.
- **States:**
  - default — avatars render, no special emphasis
  - hover over own avatar — dropdown opens ("Multiplayer tools" → Spotlight me) — `visual-only`
  - hover over collaborator avatar — tooltip with name / status — `visual-only`
  - spotlight active — own avatar shows dashed border + numeric follower count badge — `visual-only`
  - viewer history dropdown (click the stack) — list of "Currently viewing" and "Previously viewed" collaborators — `visual-only`
- **Notes:** Render the visual placeholder (a single avatar for the current user is enough) to preserve UI3 appearance. No real multiplayer runs.

### share-button
- **Scope flag:** visual-only
- **Location:** Top-right of the right properties panel, next to the avatar stack.
- **Default appearance:** Prominently styled button, solid fill background, text label "Share". Typically the most visually prominent button in the top chrome.
- **States:**
  - default — filled solid color (signature Figma blue-ish primary color), text label "Share"
  - hover — not covered in corpus
  - click — opens Share modal (see `regions/floating-overlays.md` → share-modal) — `visual-only`
- **Source articles:** `design-prototype-and-explore-layer-properties-in-the-right-sidebar`, multiplayer articles

### present-triangle-button
- **Scope flag:** visual-only
- **Location:** Between the avatars and the Share button in the right-panel header.
- **Default appearance:** Play-triangle glyph icon-button.
- **Behavior in real Figma:** Opens Presentation view in a new tab (Prototype presentation).
- **Notes:** Render the icon; click is a no-op.

### branch-indicator
- **Scope flag:** visual-only
- **Location:** Inline with the file-name dropdown in the left navigation panel. Appears only when the current file is on a branch.
- **Default appearance:** File name rendered as `<File name> › <Branch name>` with a branch icon. Status badge (gray "In review" / yellow "Changes suggested" / green "Approved") may appear adjacent.
- **Notes:** Branching out of scope; we never render a branch state. Listed here for completeness.

### file-name-bar
- **Scope flag:** functional-in-scope
- **Location:** Lives in the left navigation panel — see `regions/left-navigation.md` → file-name-dropdown. *Not* a separate top chrome element in UI3.
- **Notes:** In the mock, we can use a static file name ("Untitled" or a placeholder). Renaming via the dropdown is `visual-only`.

---

## View-only / view-seat chrome variants (not rendered)

Per plan/00 §3a, the mock always renders the edit-access view. Chrome variants that exist only in view-only mode are documented here for completeness but are NOT rendered:

- **Ask-to-edit button** — appears in the toolbar for view-only access. Not rendered.
- **Comment / Properties tabs** — right-panel variant for view-only. Not rendered.
- **Prototype view-options toggle** — exposed only in the Zoom/view-options dropdown for view-only users. Not rendered.
- **Restricted-copying absence** — some items (Export section, Copy-as-SVG/PNG) are hidden when a file owner enables "restrict copying". Not a state we enter.

---

## Window-level considerations

- **No persistent global top bar** in UI3 outside file-name bar (in left nav) and avatar/Share (in right-panel header).
- **Browser chrome** (tab, URL bar) is outside the mock's responsibility.
- **Desktop-app chrome** (native window title bar) is outside scope — the mock is a web app.
