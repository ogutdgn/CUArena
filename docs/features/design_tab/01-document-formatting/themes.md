# Themes — Design ▸ Document Formatting

> Parity reference: **Word for Windows 16.0** (ADR-0006). Real-Word flow captured this
> session by driving Word (Design ▸ Themes gallery + the *Save Current Theme* dialog).

## What real Word does

**Design ▸ Themes** is a split gallery button. It is the *top* of the formatting cascade:
a theme bundles **one color set + one font pair + one effect set**, and changing it restyles
the *entire* document at once (every theme-aware color, font, and shape effect).

Clicking the button opens a fly-out with:

1. **Built-in gallery** (header **"Office"**) — ~30 live-preview thumbnails: Office (current),
   Office 2013-2022, Facet, Gallery, Integral, Ion, Ion Boardroom, Organic, Retrospect, Slice,
   Wisp, Banded, Basis, Berlin, Circuit, Damask, Dividend, Droplet, Frame, … Each thumbnail is an
   "Aa" sample painted in the theme's **heading font** with the theme's **accent color strip**.
   **Hovering live-previews** the whole document; clicking commits. A **Custom** section appears
   above "Office" once you've saved a custom theme.
2. **Reset to Theme from Template** — reverts the document's theme to whatever its attached
   template (`Normal.dotm` or a custom `.dotx`) defines. *Not* the same as "apply Office".
3. **Browse for Themes…** — a *Choose Theme or Themed Document* file picker; loads a theme from a
   `.thmx` package **or** lifts the theme out of another `.docx`/`.dotx`/`.thmx`.
4. **Save Current Theme…** — saves the current color+font+effect combination as an **Office Theme
   (`.thmx`)** file. Confirmed default target: `…\AppData\Roaming\Microsoft\Templates\Document
   Themes\`, which also holds the sibling **Theme Colors / Theme Effects / Theme Fonts** folders
   (where the *Customize Colors/Fonts* dialogs drop their `.xml` overrides).

**OOXML.** A theme is the part **`word/theme/theme1.xml`** (`a:theme` → **`a:themeElements`**):
- **`a:clrScheme`** — 12 named colors: `dk1/lt1/dk2/lt2` (text/background pairs) + `accent1…accent6`
  + `hlink/folHlink`.
- **`a:fontScheme`** — **`a:majorFont`** (headings) + **`a:minorFont`** (body), each with a
  `latin/ea/cs` + script fallbacks.
- **`a:fmtScheme`** — effect styles (`a:fillStyleLst`, `a:lnStyleLst`, `a:effectStyleLst`,
  `a:bgFillStyleLst`) consumed by **shapes/SmartArt/charts**, *not* body text.

The document then *references* theme values by token rather than baking RGB/font names:
`w:rPr/w:color w:themeColor="accent1"`, `w:rFonts w:asciiTheme="minorHAnsi"`, etc. A `.thmx` is
simply that `theme1.xml` wrapped in its own minimal OPC package.

## Current clone state

**Working (functional) but not theme-faithful.** The Themes button is fully wired — gallery,
live preview, and apply all hit real bridge verbs.

- **UI** — `H.themes` (`commands.js:973-977`) builds a `galleryMenu('Office', WC.Design.THEMES, …)`
  with hover→`WC.PM.dePreviewTheme('theme', t)` and click→`WC.PM.deApplyTheme(t)`, an "is-active"
  predicate, **and the 3 trailing menu items** matching Word: *Reset to Theme from Template*,
  *Browse for Themes…*, *Save Current Theme…*.
- **Catalog** — `WC.Design.THEMES` (`design-tools.js:22-53`) is a clone-owned table of ~30 themes,
  each `{ name, heading, body, color, accents[6] }` with Linux-safe font fallback chains.
- **Apply** — `deApplyTheme` (`bridge/design.ts:76-82`) calls `editor.commands.redefineNamedStyles`
  (`extensions/linked-styles/linked-styles.js:121`) to **rewrite named-style definitions**:
  `Title/Subtitle/Heading1/2/3` get the heading font + heading color, `Normal` gets the body font;
  it also writes **docDefaults run `fontFamily`**. `redefineNamedStyles` **exports to
  `word/styles.xml`** and repaints the PM view. Live preview uses the same path with `{export:false}`
  + a snapshot/restore (`dePreviewTheme`/`dePreviewRestore`, `design.ts:153-176`).
- **The 3 menu items** — *Reset to Theme from Template* just **re-applies `THEMES[0]` (Office)**
  (`commands.js:974`), not the document's actual template theme. *Browse for Themes…* and *Save
  Current Theme…* are **`WC.notImplemented` stubs** (`commands.js:975-976`).

**The fidelity gap.** Applying a clone theme **never rewrites `theme1.xml`**; it bakes concrete font
names + RGB into named styles. So after applying a clone theme and re-opening in real Word:
- Word's Themes dropdown still highlights the **original** theme (theme1.xml is untouched).
- New theme-token content (a table style or shape using `accent1`, a `w:themeFont` run) keeps the
  **old** theme's value — the cascade is broken.
- **Effects** (`a:fmtScheme`) are never applied (see the separate `effects.md`).

Notably, the fork **already has the read-side theme machinery**: `SuperConverter.js:1082` parses
`word/theme/theme1.xml` (`a:fontScheme` major/minor → `themeColors`), the part is **carried and
re-emitted** on export (relationship `Target: 'theme/theme1.xml'`, `exporter-docx-defs.js:1795`),
and the default-styles exporter emits real `w:themeColor`/`w:asciiTheme` references
(`exporter-docx-defs.js`). The clone simply doesn't *write back* to it.

## Can we build it in our engine?

**Verdict:** ✅ **Already works (functional, shallow)** · 🟡 **for true `theme1.xml` fidelity** ·
🟡 **for `.thmx` Browse/Save** (bounded file-IO).

**Why.** The everyday job of the button — "restyle this document's fonts + heading colors from a
gallery, with live preview" — already works end-to-end and **round-trips** (as concrete named-style
values in `styles.xml`). The shortfall is purely *theme-faithfulness*:
- Making it write `theme1.xml` is **NO-FORK additive**: the fork already imports the part and carries
  it through export, so we add an **owned upsert** into `editor.converter.convertedXml['word/theme/
  theme1.xml']` (rewrite `a:clrScheme` from `accents[]`, `a:fontScheme` from heading/body) — exactly
  the owned-XML pattern already used for `settings.xml` (hyphenation) and `bodySectPr` (columns). No
  edit to `superdoc-fork/` source.
- `.thmx` Browse/Save is a small, self-contained file-IO subsystem (read/write a minimal OPC zip
  containing `theme1.xml`) — it can reuse the main-process zip machinery the `.docx` path already
  uses. Bounded, but genuinely new (hence 🟡, not ✅).

Nothing here needs a new rendering engine or a fork rewrite.

## Required structures

- **PM node/extension:** none new. Functional path reuses `redefineNamedStyles` + docDefaults; theme
  tokens (`w:themeColor`/`w:themeFont`) already round-trip via existing run/mark handlers.
- **Converter handler:** `theme1.xml` already imported (`SuperConverter.js:1082`) and re-emitted
  (`exporter-docx-defs.js:1795`). For fidelity: an **owned writer** that rebuilds
  `a:clrScheme`/`a:fontScheme`(/`a:fmtScheme`) in `convertedXml['word/theme/theme1.xml']`.
- **OOXML target:** `word/theme/theme1.xml` (`a:clrScheme` 12 colors, `a:fontScheme` major/minor,
  `a:fmtScheme` effects); document refs via `w:themeColor`/`w:asciiTheme`/`w:hAnsiTheme`; `.thmx` =
  the theme as a standalone OPC package.
- **Bridge verb(s):** `WC.PM.deApplyTheme` exists; extend to also upsert `theme1.xml`. New verbs for
  `deThemeBrowse` (load `.thmx`/extract from `.docx`) and `deThemeSave` (write `.thmx`).
- **Fork edit?** None — owned XML upsert + reuse of existing import/export infra.
- **Rough size:** Functional path **DONE** (S to align the gallery catalog to this Word build).
  `theme1.xml` fidelity **M**. `.thmx` Browse/Save **M** (needs an OPC zip read/write helper).
  • **Dependencies:** Effects (`a:fmtScheme`) is shared with the *Effects* button + the shapes
  engine; Colors/Fonts buttons would feed the same `theme1.xml` writer.

## Open questions for our discussion

1. **Is "functional restyle" enough for v1?** The current named-style baking gives the right *look*
   and round-trips as concrete styling. Do we want the heavier **`theme1.xml` fidelity** (so Word
   shows the applied theme as current, and theme tokens cascade to shapes/tables/new content)?
2. **Catalog parity.** The clone's `THEMES` list diverges from this Word build's built-in set — it
   has Atlas/Badge/Celestial/Crop/Depth/etc. that this Word doesn't show, and is **missing
   Basis/Circuit/Damask** (visible in the captured gallery). Align it to the real built-in catalog?
3. **Effects.** Apply the theme's `a:fmtScheme` at all? That's coupled to the *Effects* button and
   whatever shape-effect rendering we commit to — decide there and reference back here.
4. **"Reset to Theme from Template"** currently just re-applies Office. Make it a real
   template-theme reset (needs a template/theme store), or leave the simplification + relabel?
5. **Browse / Save `.thmx`** — in scope for this pass, or defer? They need an OPC `.thmx`
   reader/writer (bounded, but a new file-IO subsystem; Browse must also extract a theme from a
   `.docx`/`.dotx`).

## Decision

**TBD — to be decided together.**
