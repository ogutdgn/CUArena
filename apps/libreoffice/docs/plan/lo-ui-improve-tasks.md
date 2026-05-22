# Rich-Text Editor Top UI Transformation to Microsoft Word Style

Transform the **top section** of my rich-text editor application (title bar, ribbon tab bar, and tab headers) into a modern Microsoft Word (Office 365 / Word 2021+) appearance. Follow every detail below precisely. The lower toolbar (the Home tab contents — Font, Paragraph, Styles, Editing groups) already looks correct, so **only redesign the topmost title bar and tab strip**.

## 1. Overall Structure and Architectural Change

The current design has **two separate rows**:
- Row 1: Window title ("Untitled 1 — LibreOfficeDev Writer") centered, close button on the right
- Row 2: A small icon toolbar on the left (save, undo, print, etc.) followed by File/Home/Insert/... tabs

Convert this into a **single unified top strip (unified title bar + tab strip)** architecture. Like in Word:
- A single thin bar at the very top
- This bar will follow the order from left to right: **Quick Access Toolbar → Document name → Search bar → Account/Window controls**
- Tabs (File, Home, Insert, ...) will sit **immediately below** this bar, on a separate, shorter second row

## 2. Color Palette (Dark Theme – Word Dark Mode)

The current background is a grayish-black tone; bring it in line with Word's dark theme:

- **Top strip (title bar) background:** `#1F1F1F` or `#202020` (very dark anthracite, almost black)
- **Tab strip background:** `#2B2B2B` (one shade lighter than the title bar)
- **Active tab's ribbon content area below:** same as `#2B2B2B`, the seam between tab and ribbon should appear continuous
- **Inactive tab text color:** `#FFFFFF` or `#E6E6E6` (white / light gray)
- **Active tab text color:** `#FFFFFF` with a **Word blue** (`#2B7CD3` or in the `#4A9EFF` range) thin underline (2px) beneath it
- **Hover state:** When hovering on a tab, the background should subtly brighten to `#3A3A3A`
- **Separator lines:** Almost invisible; in Word, vertical separators between groups have very low opacity (`rgba(255,255,255,0.08)`)

## 3. Top Strip (Title Bar) – Left to Right Layout

### 3a. Top-left corner – Word application icon
- A small **Word icon** at the far left (with the blue "W" letter) or the application's own brand icon. Size: approximately 16×16 px, vertically centered, ~8px padding from the left edge.

### 3b. Quick Access Toolbar
Immediately to the right of the Word icon, as small icons:
1. **AutoSave toggle:** The text "AutoSave" + a small on/off switch next to it (gray "Off" when disabled, green/blue "On" when enabled)
2. **Save** (floppy disk icon)
3. **Undo** (curved left arrow) – with a small dropdown chevron next to it
4. **Redo / Repeat** (curved right arrow)
5. **Customize Quick Access Toolbar** (small downward chevron — customization menu)

Icons: 14–16px, **outline / stroke style**, white or light gray (`#E6E6E6`). ~6–8px spacing between them. Click targets (hit areas) ~24×24px.

### 3c. Document name (mid-left region)
- Right after the Quick Access Toolbar, but **not perfectly centered** — slightly left-of-center document name: e.g. `Document1 - Word`
- Font: Segoe UI (or system sans-serif), size ~12px, color `#E6E6E6`, normal weight (font-weight: 400)
- This text is positioned in the middle of the available title bar space extending to the right

### 3d. Search bar (center)
- A wide search bar at the **exact center** of the title bar
- Width: approximately **30–35%** of title bar width (e.g. ~500–600px on a 1920px screen)
- Height: ~24px
- Background: `#3A3A3A` (slightly lighter than title bar), corners are **slightly rounded** (border-radius: 3–4px)
- Inside, a small magnifying glass icon (🔍) on the left, with placeholder text: `Search` — color `#A6A6A6`
- Border: none, or `1px solid rgba(255,255,255,0.1)`
- On focus, a blue accent line appears at the bottom (Word style)

### 3e. Right side – Account and window controls
From left to right:
1. **User account avatar:** Round, ~24px diameter, gray placeholder or user's initial
2. **Ribbon Display Options:** A small icon (optional — exists in Word)
3. **Minimize:** ➖ icon, ~46×30px click area, hover `#3A3A3A`
4. **Maximize/Restore:** ⬜ icon, same size
5. **Close (X):** ✕ icon, hover with **red background** (`#E81123`), white icon

These three window controls follow Windows 11 styling — flat, no fill, background only changes on hover. Height matches the title bar height, vertically centered.

### 3f. Total title bar height
Approximately **30–32px**. Compact but clickable.

## 4. Tab Strip – Below the Title Bar

### 4a. Position and dimensions
- Immediately below the title bar, height ~32–36px
- Background color `#2B2B2B`
- Slight inner padding on the left edge (~12px)

### 4b. Tab order and names (left to right)
The standard sequence in Word:
1. **File** (special – different from the others, must be a **blue-backgrounded tab** — Word's signature blue "File" button, `#2B5797` or a similar tone, with white text)
2. **Home** (default active tab)
3. **Insert**
4. **Design**
5. **Layout**
6. **References**
7. **Mailings**
8. **Review**
9. **View**
10. **Help**
11. **Acrobat** (optional – if Adobe integration exists)

### 4c. Tab styling
- Font: Segoe UI, 13–14px, font-weight: 400, color `#FFFFFF`
- Horizontal padding between tabs: ~16–20px (around the tab text)
- **No border**, **no background** (in inactive state)
- **Active tab:** Text color `#FFFFFF`, with a **2px thick blue underline** (`#4A9EFF`) below. Background does not change — only the underline marks it
- **Hover:** Subtle `rgba(255,255,255,0.05)` background
- "File" tab is the **exception**: it appears as a permanently blue-backgrounded button

### 4d. Items to remove from the current design
The small icon cluster on the left of the tab strip in the second image (save, undo, print, etc.) **must no longer be here** — these have been moved up to the Quick Access Toolbar (section 3b).

## 5. Typography

- **All text:** `Segoe UI`, with fallbacks `-apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif`
- Title bar text: 12px
- Tab text: 13–14px
- Search placeholder: 12px
- Do not use bold anywhere (including the active tab — emphasis comes only from the underline)
- Letter-spacing: normal (0)

## 6. Alignment and Spacing

- Title bar height: 30px
- Tab strip height: 34px
- Total top area height: ~64px
- All icons and text must be **vertically centered**
- **No visual divider** between title bar and tab strip — only the background color difference (`#1F1F1F` → `#2B2B2B`) separates them

## 7. Fine Details

- Window controls (min/max/close) must be **strictly in the top-right corner**, nowhere else
- Search bar must be **truly centered** (exact midpoint of the title bar), balanced via flexbox on both sides
- The blue background of the "File" tab must span the **full tab height** (top to bottom), and its horizontal padding can be slightly larger than other tabs (~20px)
- The active tab's underline must not span only the **text width** — it should extend across the tab's entire clickable area width
- The AutoSave switch is a horizontal toggle like in Word — a rounded capsule shape, ~32×16px

## 8. Overall Aesthetic Goal

The result should feel like: **"As if I just enabled Microsoft Word's dark theme."** Modern, flat, minimal, professional. No gradients, shadows, or 3D effects of any kind. Fully flat design. Minimal borders, maximum differentiation through color contrast.

The lower ribbon content (Font, Paragraph, Styles, Editing groups) **remains as-is** — only the two top strips (title bar + tab strip) are to be redesigned.