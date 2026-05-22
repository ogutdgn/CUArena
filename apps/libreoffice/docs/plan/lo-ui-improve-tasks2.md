# Microsoft Word — Home Tab Ribbon: Complete Layout Specification

This document describes the **Home tab ribbon** of Microsoft Word (Office 365 / Word 2021+, dark theme) in exhaustive detail. Every button, every group, every separator, every alignment relationship is specified so that the layout can be reconstructed precisely without referring to the source image.

The Home ribbon sits **immediately below the tab strip** (where File, Home, Insert, Design, ... live). It is a horizontal band that spans the full width of the application window. The active tab here is **Home**.

---

## 1. Ribbon Container — Global Dimensions

- **Total ribbon height:** ~96px, composed of:
  - **Content area:** ~76px (where buttons, icons, dropdowns live)
  - **Group label strip:** ~20px (the thin row at the bottom showing group names like "Clipboard", "Font", "Paragraph", etc.)
- **Background color:** `#2B2B2B` (same dark gray as the tab strip — no visual seam between tab strip and ribbon)
- **Top border:** none (continuous with tab strip)
- **Bottom border:** a 1px horizontal line in `rgba(255,255,255,0.06)` separating the ribbon from the document canvas below
- **Left/right padding:** ~4px inner padding from window edges
- **Group label strip background:** same `#2B2B2B`, group labels are centered horizontally within each group, in `#A6A6A6` (muted light gray), font Segoe UI, 11px, normal weight

---

## 2. Group Structure — Left to Right Order

The Home ribbon contains **7 functional groups**, separated by thin vertical lines. From left to right:

1. **Clipboard**
2. **Font**
3. **Paragraph**
4. **Styles**
5. **Editing**
6. **Adobe Acrobat** (third-party add-in group — present only if Acrobat add-in is installed)
7. **Voice**
8. **Editor**
9. **Add-ins**

> Note: Groups 6–9 are right-aligned and appear as a cluster at the right side of the ribbon. Groups 1–5 occupy the left and center portions. There is approximately **8–12px horizontal padding** inside each group and a **1px vertical separator** at `rgba(255,255,255,0.08)` between adjacent groups, spanning the full content area height (but **not** crossing into the group label strip).

Each group has:
- A **content area** (top ~76px) holding the actual buttons
- A **label** at the bottom (~20px strip) with the group name in muted gray
- Some groups have a **dialog box launcher** — a tiny arrow icon (↘) at the **bottom-right corner of the group label strip**, just to the right of the group name. This icon opens an advanced dialog. Color: `#A6A6A6`, size ~10px.

---

## 3. Group 1: Clipboard

**Position:** Leftmost group, starting ~8px from the left edge of the window.
**Approximate width:** ~80–90px.
**Dialog launcher:** YES (small ↘ arrow to the right of the "Clipboard" label).

### Layout — two columns

**Column 1 (left): Paste button — large vertical button**
- Occupies the **full content area height** (~76px)
- Width: ~44px
- Visual structure (top to bottom):
  1. **Paste icon** (clipboard with a sheet of paper graphic), ~24×24px, centered horizontally, positioned in the upper portion (~8px from top)
  2. **"Paste" label** below the icon, Segoe UI 11px, white `#FFFFFF`, centered horizontally
  3. **Small downward chevron (▾)** below the label, ~8px, centered — indicates a dropdown menu
- The entire Paste button is a single click target; the chevron area is a separate sub-target for the dropdown
- Hover state: very subtle background highlight `rgba(255,255,255,0.05)`

**Column 2 (right): Three small horizontal items stacked vertically**
- Width: ~50px
- Each row height: ~22px
- Three rows, top to bottom:
  1. **Cut** — small scissors icon (✂) + text "Cut" to the right. Icon ~14px, text Segoe UI 12px, color `#E6E6E6`. **Note: this row appears dimmed/disabled** (`#7A7A7A`) because no text is currently selected in the document.
  2. **Copy** — small icon (two overlapping pages) + text "Copy". Same styling, also **dimmed/disabled**.
  3. **Format Painter** — small paintbrush icon (often shown in gold/yellow) + text "Format Painter". This row is **enabled** (full white text), since Format Painter can be activated independently.
- Icons are left-aligned within the column, with ~6px gap between icon and text
- Vertical spacing between rows: tight, ~2px

### Group label
- Text: **"Clipboard"**
- Position: centered horizontally in the label strip beneath the group
- Dialog launcher arrow (↘) to the right of the label text

---

## 4. Vertical Separator

A 1px vertical line at `rgba(255,255,255,0.08)`, extending from ~6px below the top of the ribbon down to the top of the group label strip (~76px tall). Same separator pattern appears between every group below — won't be repeated.

---

## 5. Group 2: Font

**Approximate width:** ~250px.
**Dialog launcher:** YES.

### Layout — two horizontal rows, each spanning the full group width

**Row 1 (top, ~36px tall): Font family + size + case controls**

From left to right:
1. **Font family dropdown:**
   - Width: ~110px
   - Height: ~22px
   - Background: `#3A3A3A` (slightly lighter than ribbon)
   - Border: 1px solid `rgba(255,255,255,0.1)`
   - Inside: text "Aptos (Body)" in Segoe UI 12px, white `#FFFFFF`, left-aligned with ~6px left padding
   - Dropdown chevron (▾) on the right side of the field, ~8px, color `#E6E6E6`
2. **Font size dropdown:**
   - ~4px to the right of the font family dropdown
   - Width: ~44px
   - Height: ~22px
   - Same styling as font family field
   - Inside: text "12"
   - Dropdown chevron on the right
3. **Grow Font (A↑):**
   - ~6px gap from font size dropdown
   - A capital "A" with a small upward arrow to its upper-right
   - Size: ~22×22px clickable area
   - Icon color: `#E6E6E6`
4. **Shrink Font (A↓):**
   - Immediately to the right of Grow Font, ~2px gap
   - Capital "A" with a small downward arrow
   - Same dimensions and styling
5. **Change Case (Aa▾):**
   - ~4px gap from Shrink Font
   - Shows "Aa" with a dropdown chevron
   - ~30×22px including chevron
6. **Clear All Formatting:**
   - ~4px gap
   - Icon: a capital "A" with a small eraser/diagonal pink stroke
   - ~22×22px

**Row 2 (bottom, ~32px tall): Text formatting buttons**

From left to right, each button is approximately ~22×22px with ~2px spacing:
1. **Bold (B)** — bold uppercase "B"
2. **Italic (I)** — italic uppercase "I"
3. **Underline (U▾)** — uppercase "U" with underline beneath it, plus a small dropdown chevron to its right (for underline style options). Includes the chevron in its hit area.
4. **Strikethrough (ab with horizontal line through it)** — lowercase "ab" with strike line
5. **Subscript (X₂)** — capital X with subscript 2
6. **Superscript (X²)** — capital X with superscript 2
7. **Text Effects and Typography (A▾)** — a stylized "A" (sometimes with a slight glow effect) plus dropdown chevron. ~4px gap before this.
8. **Text Highlight Color (▾)** — a marker/highlighter icon with a **yellow underline strip** beneath it (showing currently selected color), plus dropdown chevron
9. **Font Color (▾)** — capital "A" with a **red underline strip** beneath it (currently selected color), plus dropdown chevron

All icons in Row 2 are rendered in `#E6E6E6` outline/stroke style, except the color indicators (yellow strip under Highlight, red strip under Font Color) which use full saturated color.

### Group label
- Text: **"Font"**, centered, with dialog launcher (↘) to its right.

---

## 6. Group 3: Paragraph

**Approximate width:** ~220px.
**Dialog launcher:** YES.

### Layout — two horizontal rows

**Row 1 (top, ~36px tall): List and indent controls**

From left to right:
1. **Bullets (▾):** Three small horizontal lines with bullet dots on the left + dropdown chevron. ~30×22px.
2. **Numbering (▾):** Three small horizontal lines with "1. 2. 3." style numbers + dropdown chevron. ~30×22px. ~2px gap from Bullets.
3. **Multilevel List (▾):** Icon showing nested/indented lines + dropdown chevron. ~30×22px.
4. **Decrease Indent:** Icon showing lines with a left-pointing arrow. ~22×22px. ~6px gap.
5. **Increase Indent:** Icon showing lines with a right-pointing arrow. ~22×22px.
6. **Sort (A↓Z):** Icon showing "A" over "Z" with a downward arrow on the side. ~22×22px. ~4px gap.
7. **Show/Hide ¶ (paragraph mark):** The pilcrow symbol ¶. ~22×22px. ~4px gap.

**Row 2 (bottom, ~32px tall): Alignment and spacing controls**

From left to right:
1. **Align Left:** Icon showing horizontal lines all left-aligned. ~22×22px.
2. **Align Center:** Lines centered. ~22×22px.
3. **Align Right:** Lines right-aligned. ~22×22px.
4. **Justify:** Lines all stretched to full width. ~22×22px.
5. **Line and Paragraph Spacing (▾):** Icon showing lines with up/down arrows on the side + dropdown chevron. ~30×22px. ~4px gap.
6. **Shading (▾):** Paint bucket icon + dropdown chevron. ~30×22px. ~4px gap.
7. **Borders (▾):** A 2×2 grid icon (with one border highlighted) + dropdown chevron. ~30×22px.

### Group label
- Text: **"Paragraph"**, centered, with dialog launcher (↘) to its right.

---

## 7. Group 4: Styles

**Approximate width:** ~440px (this is the **widest group** in the ribbon).
**Dialog launcher:** YES.

### Layout — a horizontal gallery of style preview cards

This group is unique: instead of small icon buttons, it shows a **horizontal row of large rectangular style preview cards** that occupy nearly the full content area height.

- The gallery spans the full group width
- Each card height: ~58px (most of the content area)
- Each card width: varies by content, approximately 70–95px
- Cards are spaced ~4px apart
- Each card has:
  - A **1px border** in `rgba(255,255,255,0.15)` (subtle, like a frame)
  - A **light/cream background** (`#F5F1E8` or similar warm off-white) — these cards stand out dramatically against the dark ribbon
  - The style name rendered inside the card **in the actual style** it represents (so "Title" looks large and serif, "Heading" looks bold, etc.)

### Card order (left to right):

1. **Normal**
   - Text "Normal" in a standard sans-serif, ~13px, dark color
   - The **currently active style** — has a slightly thicker/brighter border to indicate selection (~1.5px border in lighter gray)
   - Centered text

2. **No Spacing**
   - Text "No Spacing" in same standard sans-serif, ~13px
   - Centered

3. **Heading**
   - Text "Heading" in a **larger, blue-tinted** style (`#2B7CD3` blue color), serif or semibold font, ~16–18px
   - Slightly bolder appearance
   - Centered

4. **Heading 2**
   - Text "Heading 2" in blue (`#2B7CD3`), slightly smaller than Heading (~14–15px)
   - Centered

5. **Title**
   - Text "Title" in a **large serif font** (~22–24px), black/dark gray color, with a thin underline beneath the text inside the card
   - Centered
   - Visually the most prominent card

6. **Subtitle**
   - Text "Subtitle" in a **lighter gray** (`#888888`), italic-like or letter-spaced style, ~13–14px
   - Centered

### Gallery controls (right edge of the Styles group)

At the very right edge of the Styles group, attached to the right side of the last visible card (Subtitle), there is a small **vertical stack of three controls**:
- **Scroll up arrow (▲)** — small triangle, ~12px, in `#E6E6E6`
- **Scroll down arrow (▼)** — small triangle, ~12px, in `#E6E6E6`
- **More / Expand gallery (▾ with horizontal line above it)** — opens the full styles panel
- These three are vertically stacked, each ~18px tall, total stack height ~58px (matches card height)
- Background: same as ribbon (`#2B2B2B`), with a subtle border on the left edge separating them from the last card

### Group label
- Text: **"Styles"**, centered beneath the gallery, with dialog launcher (↘) to its right.

---

## 8. Group 5: Editing

**Approximate width:** ~100px.
**Dialog launcher:** NO.

### Layout — three horizontal rows, each with an icon + text label

This group is laid out vertically with three menu-style entries. Each row is ~22px tall, with icon on the left and text on the right.

From top to bottom:
1. **Find (▾)**
   - Magnifying glass icon (🔍) ~14px, in `#E6E6E6`
   - Text "Find" in Segoe UI 12px, `#E6E6E6`, to the right of icon with ~6px gap
   - Small dropdown chevron (▾) to the right of the text
2. **Replace**
   - Icon: two horizontal arrows or "abc → xyz" style replacement icon, ~14px
   - Text "Replace", same styling
   - No dropdown chevron
3. **Select (▾)**
   - Icon: a cursor/arrow with a selection rectangle, ~14px
   - Text "Select", same styling
   - Dropdown chevron to the right

All rows are left-aligned within the group; icons align vertically in a column.

### Group label
- Text: **"Editing"**, centered, **no dialog launcher**.

---

## 9. Group 6: Adobe Acrobat (Add-in Group)

**Approximate width:** ~60px.
**Dialog launcher:** NO.

This group is added by the Adobe Acrobat Office plugin and only appears if installed. It contains a single large button.

### Layout — one large vertical button

- **Create a PDF**
  - Large button occupying the full content area height
  - Width: ~50–55px
  - Top: Adobe Acrobat logo icon (red/white stylized "A" within a document shape), ~28×28px, centered horizontally
  - Below the icon: text "Create" on one line, "a PDF" on the next line, centered, Segoe UI 11px, `#FFFFFF`
  - The text wraps onto two/three lines to fit the narrow button width

### Group label
- Text: **"Adobe Acrobat"**, centered, **no dialog launcher**.

---

## 10. Group 7: Voice

**Approximate width:** ~55px.
**Dialog launcher:** NO.

### Layout — one large vertical button

- **Dictate (▾)**
  - Large vertical button, similar structure to Paste
  - Width: ~44px
  - Top: Microphone icon (🎤) in **brand colors** — typically a stylized microphone with a colored dot/glow, ~26×26px, centered horizontally
  - Middle: text "Dictate" in Segoe UI 11px, `#FFFFFF`, centered
  - Bottom: small downward chevron (▾) indicating dropdown for language/settings

### Group label
- Text: **"Voice"**, centered, **no dialog launcher**.

---

## 11. Group 8: Editor

**Approximate width:** ~55px.
**Dialog launcher:** NO.

### Layout — one large vertical button

- **Editor**
  - Width: ~44px
  - Top: Editor icon — a stylized pen/pencil with a small flourish, often in **blue** (`#2B7CD3`) brand color, ~26×26px, centered
  - Below: text "Editor" in Segoe UI 11px, `#FFFFFF`, centered
  - No dropdown chevron

### Group label
- Text: **"Editor"**, centered, **no dialog launcher**.

---

## 12. Group 9: Add-ins

**Approximate width:** ~55px.
**Dialog launcher:** NO.

### Layout — one large vertical button

- **Add-ins**
  - Width: ~44px
  - Top: A 2×2 grid icon in **orange/red** (`#E07B30` or similar warm tone), ~26×26px, centered — represents the add-ins/extensions marketplace
  - Below: text "Add-ins" in Segoe UI 11px, `#FFFFFF`, centered
  - No dropdown chevron

### Group label
- Text: **"Add-ins"**, centered, **no dialog launcher**.

---

## 13. Far-Right Edge — Collapse Ribbon Arrow

At the very far-right edge of the ribbon, **below the Share button** (which lives in the top tab strip area, not the ribbon itself), there is a small **collapse/expand ribbon arrow**:
- Icon: small downward chevron (▾) or upward chevron (︿) depending on state
- Size: ~12px
- Color: `#A6A6A6`
- Position: aligned to the right edge, vertically positioned at the bottom of the ribbon content area
- Hover state: subtle background highlight

---

## 14. Typography Summary (Ribbon-Wide)

- **All button text and labels:** `Segoe UI`, fallbacks `-apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif`
- **Standard button text size:** 12px
- **Vertical button labels (Paste, Dictate, Editor, Add-ins, Create a PDF):** 11px
- **Group labels (bottom strip):** 11px, color `#A6A6A6`
- **Font family dropdown / Font size dropdown internal text:** 12px
- **Style gallery card text:** varies by card to reflect the style itself (13–24px)
- **No bold anywhere** except where the icon itself is bold (e.g., the Bold "B" button glyph)

---

## 15. Color Summary (Ribbon-Wide)

- **Ribbon background:** `#2B2B2B`
- **Input field backgrounds (font dropdowns):** `#3A3A3A`
- **Input field borders:** `1px solid rgba(255,255,255,0.1)`
- **Icon strokes (default):** `#E6E6E6`
- **Disabled/dimmed text (Cut, Copy when no selection):** `#7A7A7A`
- **Enabled text (everything else):** `#FFFFFF` or `#E6E6E6`
- **Group labels:** `#A6A6A6`
- **Group separators:** `1px` vertical line in `rgba(255,255,255,0.08)`
- **Highlight color indicator (under highlight button):** `#FFFF00` (yellow)
- **Font color indicator (under A button):** `#E81123` (red)
- **Style gallery card background:** `#F5F1E8` (warm off-white)
- **Style gallery card border:** `rgba(255,255,255,0.15)`
- **Heading text color in style cards:** `#2B7CD3` (Word blue)
- **Acrobat icon:** red/white (`#E60000` accent)
- **Editor icon:** Word blue (`#2B7CD3`)
- **Add-ins icon:** orange (`#E07B30`)
- **Dictate microphone icon:** multicolor brand gradient (blue/purple accent)

---

## 16. Spacing and Alignment Rules

- **Vertical alignment within rows:** Every button, icon, and dropdown is **vertically centered** within its row
- **Horizontal alignment within groups:** Buttons are left-aligned within the group, with consistent ~2–4px gaps between adjacent buttons in the same row
- **Two-row groups (Font, Paragraph):** Row 1 and Row 2 are vertically stacked with ~4px gap between them
- **Vertical groups (Paste, Acrobat, Voice, Editor, Add-ins):** The icon-text-(chevron) stack is vertically centered within the content area
- **Group label strip:** All group labels sit on the same horizontal baseline at the bottom of the ribbon
- **Dialog launcher arrows (↘):** Appear at the right end of group labels, ~4–6px to the right of the label text, same vertical baseline

---

## 17. Interaction States

- **Hover:** Subtle background `rgba(255,255,255,0.06)` on the hovered button, with a 1–2px corner radius
- **Pressed/Active:** Background `rgba(255,255,255,0.1)` with a slight inset feel
- **Selected (e.g., the active style "Normal"):** A more prominent border (1.5px) and a slightly brighter background
- **Disabled (Cut/Copy when no selection):** Icon and text rendered at `#7A7A7A`, no hover response
- **Dropdown chevron click area:** Separate from the main button — clicking the icon executes default action, clicking the chevron opens the dropdown menu

---

## 18. Aesthetic Goal

The ribbon should feel like a **dense but breathable** functional surface. Despite cramming dozens of controls into ~96px of vertical space, the layout uses:
- Clear vertical grouping via the bottom label strip
- Subtle separators that imply structure without adding visual noise
- Iconography in muted light gray that recedes until needed
- Bright, saturated accent colors only on **meaningful indicators** (style gallery cards, color swatches, brand icons)

The result is the recognizable Microsoft Word dark-theme ribbon — professional, information-dense, and instantly familiar to any Office user.