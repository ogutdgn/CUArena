# Step 2 — APP SKEL coverage note (Home tab)

**Scope:** the Home tab treated as the whole app. Every control on the Home ribbon face was
pressed and classified by *measured* outcome (window-delta + COM state fingerprint), never by
name. Run: `run-20260709-042323-step2`.

## What was documented
- **`ui:main-window`** — the frame: the tab strip (Home → `opens ui:ribbon-home`; the other 9
  tabs listed as `unexplored` names, per scope), the File tab (boundary: Backstage), and the
  Quick Access Toolbar buttons (`unexplored` chrome — Save is never pressed).
- **`ui:ribbon-home`** — the Home tab face: **54 element records**, each with control_type,
  label, icon crop, bounds, shortcut/keytip, and **exactly one measured marker**:
  - **26 `triggers`** (fire a feature — Bold, Italic, alignment, indents, Grow/Shrink Font,
    Clear Formatting, Cut, the split-button default-apply zones, Show All …). 24 proven by a
    doc/format/app **state delta**; 2 (Copy, Format Painter) + Shading-apply marked by **idMso**
    because their effect (clipboard / armed mode / paragraph fill) is not state-fingerprintable.
  - **25 `opens`** (reveal a surface — dialogs, dropdowns, menus, panes), each resolving to a
    stub container.
  - **4 `unexplored` boundaries** (see below).
- **24 stub containers** (`explored: false`) — one per opened dialog/dropdown/menu/pane, each
  with a window-true screenshot and empty `children[]`, to be entered in Step 5 by priority.

## Measured surface types (all verified against their screenshots)
dialogs: Font, Paragraph, Sort, Find-and-Replace · panes: Styles (floating), Office Clipboard,
Navigation (Find) · menus: Change Case, Line Spacing, Multilevel List, Borders, Underline,
Select, Paste-options, Find-menu · dropdowns/galleries: Font, Font Size, Font Color, Text
Highlight, Shading, Text Effects, Bullets, Numbering, Quick Styles.

## What stayed `unexplored`, and why (honest boundaries)
- **Boundary groups (4 controls), journaled as deliberate skips — never pressed:**
  - **Adobe Acrobat / Create a PDF** — third-party COM add-in (config `exclude_labels`); not native Word.
  - **Voice / Dictate** — turns on the microphone + cloud service (reference boundary D8).
  - **Editor** — cloud proofing pane, network/AI (config `exclude_labels`).
  - **Add-ins** — Office add-in store flyout, external content (reference boundary D8).
- **Out of scope this run (named, not entered):** the other ribbon tabs (Insert…Acrobat),
  File/Backstage, the status bar, and window-chrome buttons. Per the run's scope (Home tab = the
  whole app), these are recorded as names only.

## Honesty notes
- **Copy / Format Painter / Shading-apply** returned no measurable state delta (clipboard / armed
  mode / paragraph-fill outside the format fingerprint). They are real features, so they carry a
  `triggers` marker with `source: idmso` (the app's own command id) rather than a false
  `unexplored`. Flagged for confirmation at depth.
- **Reset discipline:** 49/49 pressed controls reset-verified back to baseline (windows, panes,
  doc hash, format signature, app view-state). Run end state == start state; original fixture
  untouched; work done only on a throwaway scratch copy.
