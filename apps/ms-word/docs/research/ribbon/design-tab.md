# Design tab — Word ↔ LibreOffice

> **Status.** Word build: Microsoft 365 (target). **Word-side: web-sourced + LO-verified —
> screenshot-pending** (not yet confirmed against a live build). LO-side: high. Produced by the
> per-tab pipeline: 3 independent extractors → reconciled canonical → mapped to LO `.uno:` →
> verified against the LibreOffice source tree. The Word/idMso side was set-diffed against the
> official `wordcontrols.xlsx` (Microsoft Mac idMso list + ribboncreator reference) and nearly
> every idMso was confirmed verbatim; the LO command facts were checked against the vendored LO
> tree. **No owner screenshot exists for this tab yet**, so conditional/version-sensitive controls
> below are *expected-conditional, unverified against a live build*. The LO-side prose carried
> several **material corrections** (the project ribbon is `notebookbar_cua.ui`, not a non-existent
> `ribbon.json`; LO *does* ship a preset theme-color gallery; the theme color editor is a separate
> dialog; `.uno:AddTheme` starts empty and is colors-only) — all applied below (see
> [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
Design-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 26 catalogued Word Design-tab controls, **none wire straight through** to an existing LO
`.uno:` command (Free = 0): the Design tab is all galleries, pickers, and dialogs, never a bare
verb. The largest band — 12 — is **our-layer UI**: the Themes / Colors gallery (which LO *does*
have, via `.uno:ThemeDialog`), the Watermark dialog, the Page Color / Fill Effects / Page Border
surfaces, and the two group hosts. A solid **behavior-shim** band exists (6): theme-font pairs,
document-wide paragraph-spacing presets, default-spacing, Save-as-default, and Save-Current-Theme
— all capabilities LO carries in its model or via a multi-step flow, but with different semantics
that our dispatch layer must massage. The decisive number for the engine decision is
**Engine gap = 7** — almost entirely **Word's coordinated Style-Set system** (the live-preview
gallery of paragraph+font formatting bundles) plus **theme-effect swapping**, `.thmx` import, and
the watermark building-block gallery. Only one control (More Themes on Office.com) is **Cut**.

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 0 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 12 | build the Word-faithful gallery/dialog/host; dispatch the LO command |
| **Behavior shim** | 6 | intercept/massage in our dispatch layer; LO's result/semantics differ |
| **Engine gap** | 7 | LO engine genuinely can't; cut or accept reduced fidelity |
| **Cut** | 1 | out of scope by product choice (cloud/AI/M365, online catalogs) |
| **Optional our-layer feature** | 0 | LO lacks it but it's app-state we could build |
| **Total** | **26** | |

**Decisive learning:** on Design the engine gap is small and tightly clustered —
**Engine gap = 7 / 26 (~27% of controls, but concentrated)** — and it is dominated by **Word's
Style-Set subsystem** (Style Set gallery + Reset-to-Default + Save-as-New-Style-Set = 3 of the 7):
a curated, swappable, live-previewing set of coordinated paragraph+font formatting bundles applied
document-wide, which LO has **no equivalent for** (LO exposes only individual styles via the Styles
sidebar). The remaining gaps are **theme-effect swapping** (the OOXML effect scheme exists in
`model::Theme` for round-trip but there is *no command or gallery to pick/swap it*), **`.thmx`
import** (LO's theme model cannot consume the file format), and the **watermark building-block
gallery** (no Building Blocks system). Critically, the LO-source pass **overturned** the original
inventory's biggest claim: LO **does** ship a preset theme gallery (`.uno:ThemeDialog`, a GtkIconView
of 7 named color-sets — Beach/Breeze/Forest/Libreoffice/Ocean/Rainbow/Sunset), so Themes/Colors
moved from "missing" to **our-layer UI**. → still supports **LO-via-LOK + scoped parity**, with
the Style-Set system explicitly out of scope.

> **Recurring our-layer theme.** Word's Design tab is **coordinated document-wide formatting**:
> Style Sets, Themes, theme Colors/Fonts/Effects, Paragraph-Spacing presets, and the page-background
> trio (Watermark, Page Color, Page Borders). LO covers the *theme color* picker, the watermark
> dialog, and the page background/border via the Page Style dialog — the repeated shape of work is
> wrapping LO's **per-style / per-page-style** dialogs in Word's **document-wide gallery** idiom.
> The genuine gaps are the **Style-Set bundle system** and **theme-effect swapping**; the
> theme-font pair exists in LO's model but has **no editing UI**, making Fonts a shim rather than
> a free wire.

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none).
`work` is the bucket from the table above. Rows touched by the LO-source corrections are marked
**✓ verified vs LO source** in the note.

### Document Formatting (GroupStyleSet)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Document Formatting group | GroupStyleSet | group | — | differs | Our-layer UI | Ribbon group container (left, larger of the two Design groups) holding Style Set, Themes, Colors, Fonts, Paragraph Spacing, Effects, and Set as Default. — **LO:** No matching rich group. LO's Design tab is a SINGLE flat toolbox (`Design-Section-Main` / `DesignToolBox`) with **no** "Document Formatting" sub-group — its buttons are DesignerDialog, LoadStyles, ParaspaceIncrease, ParaspaceDecrease, Watermark, PageDialog, BorderDialog. The visible Word group also merges what the idMso schema splits across GroupStyleSet and a separate GroupThemesWord (see QA flags). ✓ verified vs LO source. |
| Style Set | QuickStylesSets | gallery | `.uno:DesignerDialog` | LO-missing | Engine gap | Large in-ribbon gallery; each thumbnail is a coordinated set of paragraph+font formatting for the document's built-in styles (Heading 1, Title, body). Hovering live-previews; clicking reformats every styled element document-wide. Flyout exposes Reset to Default Style Set and Save as a New Style Set. — **LO:** LO has NO Style-Set concept — no curated, swappable, live-previewing bundle of style-formatting. It exposes only individual styles via the Styles sidebar (`.uno:DesignerDialog`); the nearest workflow is swapping the template, which is manual and not a gallery. Mapped to DesignerDialog only as the nearest styles entry point. ✓ verified vs LO source. |
| Reset to the Default Style Set | QuickStylesResetFromTemplate | button | `.uno:LoadStyles` | LO-missing | Engine gap | Menu item at the bottom of the Style Set flyout; resets document formatting to the style set defined by the attached template. — **LO:** No Style Set, so no "reset to template's style set." The conceptually-adjacent op is reloading styles from the template via `.uno:LoadStyles` ("~Load Styles from Template"), but that reloads ALL style definitions, not a named default set, and lives in a dialog, not a one-click reset. ✓ verified vs LO source. (Word's idMso label is "Reset to Quick Styles from Template"; a sibling QuickStylesResetDocumentStyles was omitted — see QA flags.) |
| Save as a New Style Set… | QuickStylesSaveQuickStyleSet | button | `.uno:SaveAsTemplate` | LO-missing | Engine gap | Menu item at the bottom of the Style Set flyout; saves the current document formatting as a reusable style set for future documents. — **LO:** LO cannot save a reusable style set independent of a document. The only reuse mechanism is saving the whole document as a template (`.uno:SaveAsTemplate`, "Save as Template…") — a full template, not a lightweight style-set overlay. ✓ verified vs LO source. |
| Themes | ThemesGallery | gallery (dropdown) | `.uno:ThemeDialog` | differs | Our-layer UI | Dropdown gallery of built-in document themes; hovering live-previews and clicking applies a coordinated set of theme colors, fonts, and effects document-wide. Flyout bottom: Reset to Theme from Template, More Themes on Office Online, Browse for Themes, Save Current Theme. — **LO:** **Corrected:** LO DOES ship a built-in gallery of named preset theme color-sets — `.uno:ThemeDialog` opens a GtkIconView picker (`iconview_theme_colors`) with an Add button, and 7 presets ship (Beach, Breeze, Forest, Libreoffice, Ocean, Rainbow, Sunset). So "apply a coordinated theme via a thumbnail gallery of named presets" exists for theme COLORS. Differs: the presets carry colors only (no font/effect variants exposed), no live hover-preview, no template-bound themes. (`.uno:ThemeSelectorPanel` is the docked deck; do NOT confuse with `.uno:ChangeTheme`, the app Dark-Mode toggle.) ✓ verified vs LO source. |
| Reset to Theme from Template | ThemeResetFromTemplate | button | — | LO-missing | Engine gap (revisit) | Menu item under Themes; restores the theme defined by the document's attached template. — **LO:** No command to reset the document's theme to the template's. LO themes are not template-bound in this way and there is no reset-theme-from-template action in the catalog. (revisit — niche; could be our-layer if template-theme binding is ever modelled.) ✓ verified vs LO source. |
| More Themes on Office Online / More on Office.com | ThemeSearchOfficeOnline | button | — | LO-missing | Cut | Menu item under Themes linking to additional themes from Office Online. (Same idMso also appears as the Watermark gallery's "More on Office.com" entry — de-duplicated to this single row.) — **LO:** No Office.com/online theme catalog integration; themes are local only. (Word itself has largely deprecated this link.) |
| Browse for Themes… | ThemeBrowseForThemes | button | — | LO-missing | Engine gap | Menu item under Themes; opens a file picker to load a theme (`.thmx` or themed document) from disk. — **LO:** LO cannot load a theme from a standalone file. `.uno:AddTheme` defines a NEW theme but offers no file-picker import of an external theme, and the `.thmx` format is not consumed by LO's theme model. ✓ verified vs LO source. |
| Save Current Theme… | ThemeSaveCurrent | button | `.uno:AddTheme` | differs | Behavior shim | Menu item under Themes; saves the current color/font/effect combination as a reusable `.thmx` file in the Document Themes folder. — **LO:** **Corrected:** `.uno:AddTheme` ("Add Theme…") does NOT capture the current state — it creates an EMPTY color set, opens ThemeColorEditDialog to define 12 colors + a name from scratch, then inserts the named color-set into the global collection (also written as a `<name>.theme` file). It captures COLORS only — no fonts, no effects, no current-document capture, no portable `.thmx` export. Closest persist mechanism but semantically different. ✓ verified vs LO source. |
| Colors | ThemeColorsGallery | gallery (dropdown) | `.uno:ThemeDialog` | differs | Our-layer UI | Dropdown gallery of theme color palettes (text/background + accent swatches); selecting one swaps the document's theme colors, recoloring any theme-color-bound element. Ends with Customize Colors… — **LO:** **Corrected:** `.uno:ThemeDialog` IS a gallery/picker of curated, NAMED theme-color sets (the 7 shipped presets + any user-added), not an inline editor. The 12-color model (dk1/lt1/dk2/lt2 + 6 accents + 2 hyperlink) is confirmed. Differs only in UX (icon-view picker vs Word's swatch dropdown, no live hover-preview). The earlier "no standalone gallery of named palettes" claim was wrong. ✓ verified vs LO source. |
| Customize Colors… | ThemeColorsCreateNew | button | `.uno:ThemeDialog` | differs | Our-layer UI | Menu item under Colors; opens the dialog to define and name a custom theme color set. — **LO:** **Corrected:** the 12 theme colors are edited in a DEDICATED sub-dialog, ThemeColorEditDialog (themecoloreditdialog.ui: 12 color pickers + name field), reached via ThemeDialog's Add button or directly by `.uno:AddTheme` (SID_ADD_THEME). So LO DOES have a named-color-set creation dialog — contradicting the earlier "edits colors inline / no separate dialog" claim. Differs: `.uno:AddTheme` starts from an EMPTY set, not the current one. ✓ verified vs LO source. |
| Fonts | ThemeFontsGallery | gallery (dropdown) | `.uno:ThemeDialog` | differs | Behavior shim | Dropdown gallery of theme font pairs (heading over body); selecting one changes the document's theme fonts so all heading/body theme-font text updates. Ends with Customize Fonts… — **LO:** **Corrected:** a LO theme's font pair (FontScheme: major/minor Latin/Asian/Complex) exists ONLY in the data model and round-trips via OOXML — the ThemeDialog path (themedialog.ui + themecoloreditdialog.ui) exposes **NO font fields at all**. So there is no theme-fonts gallery AND no editing UI; the capability is model-only. Realizing Word's font-pair gallery means our layer driving the model directly. ✓ verified vs LO source. |
| Customize Fonts… | ThemeFontsCreateNew | button | `.uno:ThemeDialog` | differs | Behavior shim | Menu item under Fonts; opens the dialog to define and name a custom heading/body theme font pairing. — **LO:** **Corrected:** no dedicated Create-New-Theme-Fonts dialog and no theme-fonts editing UI anywhere on the ThemeDialog path — the FontScheme is data-model-only. The earlier "set the two fonts manually inside the Theme dialog" claim is false. Shim: our layer writes the model's FontScheme; LO has no command. ✓ verified vs LO source. |
| Paragraph Spacing | ParagraphSpacing | gallery (dropdown menu) | `.uno:ParaspaceIncrease` | differs | Behavior shim | Dropdown of document-wide paragraph/line spacing presets (Default, No Paragraph Space, Compact, Tight, Open, Relaxed, Double) with live preview; clicking applies that before/after-paragraph and line-spacing scheme to the whole document. Ends with Custom Paragraph Spacing… — **LO:** **Corrected:** LO has NO document-wide spacing PRESET menu. The Design buttons are `.uno:ParaspaceIncrease` / `.uno:ParaspaceDecrease` ("Increase/Decrease Paragraph Spacing") — incremental nudges of the selected paragraph's above/below spacing, no line-spacing component, no live preview. Fixed line-spacing commands `.uno:SpacePara1/115/15/2` ("Line Spacing: 1/1.15/1.5/2") exist but are line-spacing-only, per selection. The coordinated presets must be composed in our layer over these commands. ✓ verified vs LO source. |
| Custom Paragraph Spacing… | ParagraphSpacingCustom | button | `.uno:DesignerDialog` | LO-missing | Behavior shim | Menu item under Paragraph Spacing; opens Manage Styles (Set Defaults tab) to set exact document-wide before/after + line-spacing defaults. — **LO:** LO has no "set defaults" tab and no single document-default-spacing dialog. The nearest is editing the Default Paragraph Style's Indents & Spacing via the Styles dialog (`.uno:DesignerDialog`), which changes the default style rather than a document-default override. The inventory's original `.uno:PageDialog` map is acknowledged-wrong; re-targeted to DesignerDialog. (idMso ParagraphSpacingCustom is plausible-but-unverified — see QA flags.) ✓ verified vs LO source. |
| Effects | ThemeEffectsGallery | gallery (dropdown) | — | LO-missing | Engine gap | Dropdown gallery of theme effect sets (subtle/moderate/intense shadow/reflection/line/fill schemes); selecting one restyles shapes, SmartArt, and charts that use theme effects. No sub-menu items. — **LO:** **Corrected (nuanced):** at the DATA-MODEL level `model::Theme` DOES carry a FormatScheme with an EffectStyle list (OuterShadow/InnerShadow/Glow/SoftEdge/Reflection/Blur) for OOXML round-trip — so "no effects component at all" was wrong about the model. But at the UI/command level there is **no `.uno:` command or gallery to pick or swap an effect scheme**, and the 7 shipped presets carry colors only. Shape formatting in LO is per-object (Area/Line/Shadow tabs), never driven by a document-wide theme-effect set. The swap capability is genuinely absent. ✓ verified vs LO source. |
| Set as Default | QuickStylesSetAsDefault | button | `.uno:SaveAsTemplate` | differs | Behavior shim | Applies the current theme/style-set/spacing as the default for all new documents based on the active template (typically Normal.dotm). One click, no dialog. — **LO:** No one-click "set as default" on the ribbon. The equivalent is a two-step manual flow: save the document as a template (`.uno:SaveAsTemplate`) and mark it default in the Template Manager (`.uno:TemplateManager`, "Set As Default" — a dialog action, not a standalone command). Result is similar (new docs inherit formatting) but the mechanism, granularity (whole template vs. just formatting), and step count differ. ✓ verified vs LO source. |

### Page Background (GroupPageBackground)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Page Background group | GroupPageBackground | group | — | differs | Our-layer UI | Ribbon group container (right side of the Design tab) holding Watermark, Page Color, and Page Borders. — **LO:** **Corrected:** no "Page Background" sub-group exists. LO's Design tab is one flat toolbox; the page-background-adjacent buttons actually present are `.uno:Watermark`, `.uno:PageDialog` ("~Page Style…"), and `.uno:BorderDialog`. `.uno:BackgroundColor` is NOT on the Design tab at all (it lives on the Home tab). The earlier mapping cited a non-existent ribbon.json. ✓ verified vs LO source. |
| Watermark | WatermarkGallery | gallery (dropdown / split-button) | `.uno:Watermark` | differs | Our-layer UI | Dropdown gallery of preset ghost-text watermarks (CONFIDENTIAL, DO NOT COPY, DRAFT, SAMPLE, ASAP, URGENT). Clicking a preset inserts it behind body text on every page. Bottom: Custom Watermark, Remove Watermark, Save Selection to Watermark Gallery, More on Office.com. — **LO:** **Corrected (confirmed):** `.uno:Watermark` ("Watermark…") is a single button opening ONE text-only Watermark dialog (text, font, color, angle, transparency — verified in watermarkdialog.ui and the OK handler). There is NO preset gallery, NO split-button, NO picture-watermark branch, and NO Save-to-Gallery. Core capability (ghost-text watermark on all pages) exists; presets + picture + gallery are our-layer/absent. ✓ verified vs LO source. |
| Custom Watermark… | WatermarkCustomDialog | button | `.uno:Watermark` | differs | Our-layer UI | Menu item under Watermark; opens the Printed Watermark dialog to configure a Text watermark (text/font/size/color/transparency/layout) or a Picture watermark (select picture, scale, washout). — **LO:** `.uno:Watermark` IS LO's watermark dialog — the closest direct map. Differs: Text-only (no Picture watermark branch, no scale/washout), and no layout/orientation chooser beyond a numeric angle. ✓ verified vs LO source. |
| Remove Watermark | WatermarkRemove | button | `.uno:Watermark` | differs | Our-layer UI | Menu item under Watermark; removes the current watermark. — **LO:** No dedicated remove command — removal is done inside the `.uno:Watermark` dialog by clearing the text field. Same end result, in-dialog rather than one-click. ✓ verified vs LO source. |
| Save Selection to Watermark Gallery… | SaveSelectionToWaterMarkGallery | button | — | LO-missing | Engine gap | Menu item under Watermark (when content is selected); saves the selection as a reusable watermark building block. — **LO:** No watermark gallery and no Building Blocks system, so nothing to save a selection into. Fully missing. |
| Page Color | PageColorPicker | gallery (color picker) | `.uno:BackgroundColor` | differs | Our-layer UI | Color-picker dropdown (Theme Colors, Standard Colors, No Color, More Colors…, Fill Effects…); selecting a color sets the on-screen page background fill document-wide. Intended for screen/web display, not printed by default. — **LO:** **Corrected:** there is NO `.uno:PageColor` command in LO (none exists across the config tree). `.uno:BackgroundColor` ("Background Color") is a color-popup control, but in real LO the robust document-wide page background is set in the Page Style dialog's Area tab (`.uno:PageDialog`), and `.uno:BackgroundColor` is a Home-tab control, not Design. LO's page background also prints by default (Word's does not). Differs in command, location, and print behavior. ✓ verified vs LO source. |
| More Colors… | PageColorMoreColorsDialog | button | `.uno:BackgroundColor` | differs | Our-layer UI | Menu item under Page Color; opens the Colors dialog for a custom page-background color. — **LO:** LO's color picker includes a "Custom Color…" entry opening LO's "Pick a Color" dialog (RGB/HSB/Hex, palettes) — functionally equivalent to Word's More Colors → Colors dialog, but LO's own dialog with a different layout. ✓ verified vs LO source. |
| Fill Effects… | PageColorFillEffects | button | `.uno:PageDialog` | differs | Our-layer UI | Menu item under Page Color; opens the Fill Effects dialog (gradient, texture, pattern, picture) for the page background. — **LO:** LO supports gradient/bitmap/pattern/hatch page backgrounds, but NOT from a color-dropdown Fill Effects button — they live in the Page Style dialog's Area tab (`.uno:PageDialog` → Area, with Color/Gradient/Image/Pattern/Hatch sub-tabs). Capability exists (arguably richer), reached via the page-style dialog rather than a Fill-Effects menu item; organization differs entirely. ✓ verified vs LO source. |
| Page Borders | PageBorderAndShadingDialog | button (dialog launcher) | `.uno:PageDialog` | differs | Our-layer UI | Opens Borders and Shading on the Page Border tab — choose a Setting (None/Box/Shadow/3-D/Custom), line Style/Color/Width or an Art decorative border, toggle edges in Preview, scope with Apply to; OK applies a border around the page margins. — **LO:** **Corrected:** page-scoped borders are set in the Page Style dialog's Borders tab (`.uno:PageDialog` → Borders): arrangement, style, width, color, spacing, shadow. The Design-tab `.uno:BorderDialog` button ("Borders") is the PARAGRAPH/object border dialog (selection-scoped), NOT the page border — but `.uno:PageDialog` is ALSO present on the same flat Design toolbox, so the page-border path does not require leaving the tab. Differences: LO has NO decorative Art (clip-art) page borders, and no combined "Borders and Shading" dialog (page border + page background fill are separate tabs of the page-style dialog). ✓ verified vs LO source. |

---

## LO-source verification

These mappings were checked against the vendored LibreOffice tree at
`apps/ms-word/libreoffice-codebase/` and **override** the mapped rows where they conflicted.
The LO-side prose carried several **material corrections** that reverse the inventory's original
conclusions; the rest **confirm** the mapped command, label, slot, and (where cited) shortcut.

**Material corrections (CORRECTED):**

- **Design-tab structure (group membership)** — the inventory described a "Document Formatting"
  group and a "Page Background" group sourced from a `ribbon.json`. **No `ribbon.json` exists.** The
  real project ribbon is `sw/uiconfig/swriter/ui/notebookbar_cua.ui`, whose Design tab is a SINGLE
  flat toolbox (`Design-Section-Main` / `DesignToolBox`) with **no** sub-groups. Its buttons are
  exactly: DesignerDialog, LoadStyles, ParaspaceIncrease, ParaspaceDecrease, Watermark, PageDialog,
  BorderDialog. `.uno:ChangeTheme` ("Dark Mode") is **not** on the Design tab (hidden View-tab
  button). `.uno:BackgroundColor` is **not** on the Design tab (it is a Home-tab control). The
  mapping omitted `.uno:PageDialog`, which IS present. Evidence: `notebookbar_cua.ui:5726-5841`
  (Design flat toolbox), `:5791` (Watermark), `:5801` (PageDialog), `:5811` (BorderDialog),
  `:9259` (ChangeTheme on View tab, hidden), `:3839` (BackgroundColor on Home tab).
- **Themes — preset gallery EXISTS** — the inventory asserted LO has "NO built-in preset theme
  gallery" and "ships essentially no presets." Wrong. `.uno:ThemeDialog` (SID_THEME_DIALOG) opens
  `themedialog.ui`, a GtkIconView gallery (`iconview_theme_colors`) of named theme color-set
  thumbnails + an Add button (a picker, not an inline editor). LO ships **7** `.theme` presets:
  Beach, Breeze, Forest, Libreoffice, Ocean, Rainbow, Sunset (`svx/uiconfig/themes/`). So applying a
  coordinated theme via a thumbnail gallery of named presets DOES exist for theme colors (colors
  only; no font/effect variants in the picker). Evidence: `themedialog.ui:108,132`;
  `svx/source/dialog/ThemeDialog.cxx:23-44`; `svx/source/styles/ColorSets.cxx:184-200`;
  `Glob svx/uiconfig/themes/*.theme`.
- **Colors / Customize Colors — separate edit dialog** — the inventory said LO "edits colors inline
  in `.uno:ThemeDialog`" with "no separate dialog." Wrong. The 12 theme colors are edited in a
  DEDICATED dialog, ThemeColorEditDialog (`themecoloreditdialog.ui`: 12 color pickers + name),
  opened via ThemeDialog's Add button or directly by `.uno:AddTheme`. So LO has a named-color-set
  creation dialog. Evidence: `themecoloreditdialog.ui:100,143-495`; `ThemeDialog.cxx:46-73`;
  `basesh.cxx:3086-3105`.
- **`.uno:AddTheme` starts empty, colors-only** — `.uno:AddTheme` (SID_ADD_THEME) does NOT capture
  the current color/font set; it creates an EMPTY color set, opens ThemeColorEditDialog for the user
  to define 12 colors + a name from scratch, then inserts the named set (also written as a
  `<name>.theme` file). Colors only — no fonts, no current-document capture, no portable `.thmx`.
  Label "Add Theme…" confirmed. Evidence: `basesh.cxx:3086-3105`; `drviews2.cxx:4418-4442`;
  `ColorSets.cxx:232-280`; `GenericCommands.xcu:8083-8086`.
- **Theme model HAS an effects component, but no swap UI** — the inventory said a LO theme is "colors
  + fonts only" with "NO effects dimension at all." At the model level this is wrong: `model::Theme`
  has a ColorSet, a FontScheme, AND a FormatScheme whose EffectStyle list includes OuterShadow,
  InnerShadow, Glow, SoftEdge, Reflection, Blur (the OOXML effect scheme, read/written). The
  UI-level point still holds — there is **no `.uno:` command or gallery to pick/swap an effect
  scheme**, and the shipped presets carry colors only. Softened to "no effects-swapping UI/command
  (the OOXML effect scheme exists only in the data model)." Evidence:
  `include/docmodel/theme/Theme.hxx:155-175`; `include/docmodel/theme/FormatScheme.hxx:398-445`;
  `svx/uiconfig/themes/Breeze.theme:1-18`.
- **Fonts / Customize Fonts — NO editing UI** (opposite-direction correction) — the inventory claimed
  the theme font pair is "editable in `.uno:ThemeDialog`." Wrong: the ThemeDialog path
  (`themedialog.ui` + `themecoloreditdialog.ui`) exposes **no font widgets at all**. The FontScheme
  exists only in the data model (round-trips via OOXML) and is not editable through any command. The
  broader "no theme-fonts gallery" conclusion holds; the mechanism claim does not. Evidence:
  `themedialog.ui` (no font widgets); `themecoloreditdialog.ui:143-495` (12 color fields only);
  `Theme.hxx:43-152,161` (FontScheme in model).

**Confirmed (CONFIRMED) — command/label/slot (and cited shortcut) match the mapping:**

- **Watermark** — `watermarkdialog.ui` has exactly TextInput/Font/Color/Angle/Transparency (no
  picture branch); the OK handler dispatches only those via `.uno:Watermark`; label "Watermark…".
  No preset gallery, no separate remove command. Evidence: `watermarkdialog.ui:98-215`;
  `watermarkdialog.cxx:112-124`; `WriterCommands.xcu:4353-4356`.
- **No `.uno:PageColor`** — grep across all officecfg `.../UI` config finds none. `.uno:BackgroundColor`
  exists ("Background Color", supports a color-popup). The page-color runtime/print-default behavior
  is not verifiable from config/slot sources and is not asserted from them. Evidence:
  `GenericCommands.xcu:3797-3804`; `WriterCommands.xcu:1571-1574` (`.uno:PageDialog` "~Page Style…").
- **Page Borders — BorderDialog vs PageDialog** — the Design-tab Borders button is `.uno:BorderDialog`
  ("Borders", selection-scoped paragraph/object border). `.uno:PageDialog` ("~Page Style…") is ALSO
  on the same flat Design toolbox, so the page-border path is present on the tab. Evidence:
  `notebookbar_cua.ui:5811-5813,5801-5803`; `WriterCommands.xcu:1542-1545,1571-1574`.
- **Paragraph Spacing** — `.uno:ParaspaceIncrease` ("Increase" / "Increase Paragraph Spacing") and
  `.uno:ParaspaceDecrease` are the Design buttons; line-spacing commands `.uno:SpacePara1/115/15/2`
  ("Line Spacing: 1/1.15/1.5/2") exist. No paragraph-spacing PRESET-menu command exists. Evidence:
  `GenericCommands.xcu:160-187,1995-2022`; `notebookbar_cua.ui:5771-5783`.
- **Reset to Default Style Set → `.uno:LoadStyles`** — label "~Load Styles from Template" confirmed.
  The dialog-level "Overwrite" option is left UNCERTAIN (no load-styles `.ui` locatable in this
  stripped tree). Evidence: `WriterCommands.xcu:1524-1530`.
- **Save as New Style Set / Set as Default** — `.uno:SaveAsTemplate` ("Save as Template…") and
  `.uno:TemplateManager` ("Templates") confirmed; the "Set As Default" action is a Template-Manager
  dialog element, not a standalone command. Evidence: `GenericCommands.xcu:3335-3338,7702-7705`.
- **ChangeTheme disambiguation** — `.uno:ChangeTheme` is "Dark Mode" (tooltip "Toggle between dark and
  light modes"), the application dark/light toggle — distinct from document themes
  (`.uno:ThemeDialog`/`ThemeSelectorPanel`/`AddTheme`). Evidence: `GenericCommands.xcu:1491-1501`.
- **Effects — no command** — no `.uno:` command for a theme-effects gallery or effect-scheme swap
  exists in any Office/UI command definition (the EffectStyle/FormatScheme is model-only). Evidence:
  grep `ThemeEffects|EffectsGallery` across officecfg `.../UI` → none; `FormatScheme.hxx:432-445`.

**Uncertain (UNCERTAIN) — not treated as authoritative:**

- **Keyboard shortcuts** — the mapping made no shortcut claims, so none required correction. For
  context, `Accelerators.xcu:871-880` binds `.uno:DesignerDialog` (the F11 Styles-sidebar family)
  and `.uno:SaveAsTemplate`, but since neither is claimed, there is nothing to confirm.

---

## Conditional / version-sensitive controls

There is **no owner screenshot for the Design tab yet**, so the following are flagged
**expected-conditional, unverified against a live build** — a screenshot sweep would confirm them.

- **"Document Formatting" group idMso backing** — the visible single Design-tab group spans Style
  Set + Themes + Colors + Fonts + Paragraph Spacing + Effects + Set as Default, but the idMso schema
  splits this across **GroupStyleSet** and a separate **GroupThemesWord** (the latter unrepresented
  in the inventory). Which idMso(s) actually back the visible group is build-sensitive — a
  right-click → Customize Ribbon / hover capture is needed.
- **`ThemeSearchOfficeOnline` ("More Themes on Office.com")** — present here as a single de-duplicated
  Themes-flyout row; its presence/label in the target build is screenshot-pending.
- **`ParagraphSpacingCustom` idMso** — the *command* (Custom Paragraph Spacing → Manage Styles → Set
  Defaults) is real, but the exact idMso string is unconfirmed in any authoritative list — treat as
  plausible-but-unverified.
- **`CustomWatermarkGallery`** — a distinct gallery idMso exists in the official list separately from
  WatermarkGallery and WatermarkCustomDialog; whether it surfaces on the Design-tab Watermark
  dropdown vs. being legacy/alternate is uncertain — verify by screenshot before adding.

---

## Out of scope

- **Engine gap — Style-Set system + theme-effect swapping + `.thmx` import (the true engine
  blockers, 7 controls).** Three clusters: (1) **Word's Style-Set subsystem** — the Style Set
  gallery + Reset to Default Style Set + Save as a New Style Set: a curated, swappable,
  live-previewing set of coordinated paragraph+font formatting bundles applied document-wide. LO has
  no Style-Set concept (only individual styles via the Styles sidebar). (2) **Theme-effect swapping**
  — the Effects gallery; the OOXML effect scheme exists in `model::Theme` for round-trip but there is
  no command or gallery to pick/swap it, and shape formatting is per-object. (3) **External theme +
  watermark building-blocks** — Browse for Themes (`.thmx` import, which LO's theme model cannot
  consume) and Save Selection to Watermark Gallery (no Building Blocks system). Cut now, or accept
  reduced fidelity. This is the band that would matter if the engine were ever reconsidered.
  *(Reset to Theme from Template is also Engine gap but tagged revisit — niche, no template-theme
  binding in LO.)*
- **Cloud / AI / M365 (cut by product choice).** More Themes on Office Online / Office.com — an
  online theme catalog with no engine equivalent and not part of a local clone's scope.
- **Sub-feature gaps inside otherwise-our-layer controls.** Several controls map to a working LO
  command but lose a sub-feature: picture watermarks (LO watermark is text-only), decorative Art
  page borders (LO has none), Word's screen-only/non-printing page color (LO's prints by default),
  and theme-font *editing UI* (the FontScheme is model-only). These are noted in-row, not separate
  Cut entries.

---

## QA flags & resolutions

From `result.qa`. The Word/idMso side was set-diffed against the official Microsoft Mac idMso list
and the ribboncreator reference and is medium-high complete; the LO-source pass overturned the
inventory's LO-side conclusions. Because there is **no owner screenshot for this tab**, several
structural items remain **screenshot-pending**.

| QA flag | Status | Resolution |
|---|---|---|
| Themes/Colors claim "no preset theme gallery / no named schemes / edits inline"? | **Resolved (LO source) — REVERSED** | Wrong — `.uno:ThemeDialog` IS a GtkIconView gallery/picker of named theme color-sets; LO ships 7 presets (Beach/Breeze/Forest/Libreoffice/Ocean/Rainbow/Sunset); the 12 colors are edited in a SEPARATE dialog (ThemeColorEditDialog). Themes and Colors moved LO-missing/inline → **differs / Our-layer UI**. Most consequential correction on this tab. |
| Fonts "editable in `.uno:ThemeDialog`"? | **Resolved (LO source) — REVERSED** | Wrong (opposite direction) — the ThemeDialog path has NO font fields; the FontScheme is data-model-only. No theme-fonts editing UI exists; Fonts/Customize Fonts are **Behavior shim** (our layer drives the model). |
| Effects "no effects component at all"? | **Resolved (LO source) — softened** | Partially wrong — `model::Theme` carries a FormatScheme/EffectStyle list (OuterShadow/Glow/Reflection/…) for OOXML round-trip. But the UI conclusion holds: no command/gallery to swap effects, presets carry colors only. Stays **Engine gap** (no swap UI), worded as model-exists-but-no-command. |
| `.uno:AddTheme` "captures the current color/font set"? | **Resolved (LO source) — corrected** | Wrong — it starts from an EMPTY color set, captures colors only (no fonts, no current-doc), writes a `.theme` (not portable `.thmx`). Save Current Theme stays **Behavior shim**. |
| Design-tab group membership sourced from "ribbon.json"? | **Resolved (LO source) — REVERSED** | No ribbon.json exists. The real ribbon is `notebookbar_cua.ui`; the Design tab is a single flat toolbox (DesignerDialog/LoadStyles/ParaspaceIncrease/ParaspaceDecrease/Watermark/PageDialog/BorderDialog) with no sub-groups, no ChangeTheme, no BackgroundColor; it OMITS `.uno:PageDialog` which IS present. All LO-side group prose re-grounded. |
| `Custom Paragraph Spacing → .uno:PageDialog` map? | **Resolved (LO source) — re-targeted** | The inventory's own notes admit "PageDialog is not actually it." Re-targeted to `.uno:DesignerDialog` (Default Paragraph Style → Indents & Spacing). Stays **Behavior shim** (no document-default-spacing dialog in LO). |
| "Document Formatting" group's true idMso (GroupStyleSet vs GroupThemesWord)? | **Open (screenshot-pending)** | The visible group merges what the schema splits across GroupStyleSet and GroupThemesWord; the latter is unrepresented. Does not change buckets; needs a Customize-Ribbon/hover capture. |
| `QuickStylesResetDocumentStyles` omitted? | **Open (source set-diff)** | A clear omission — a Style-Set-dropdown sibling of the Reset/Save/Set-as-Default commands. Would be **Engine gap** (same as the other Style-Set rows, closest is `.uno:LoadStyles`). Add after screenshot confirmation. |
| `QuickStylesSaveSelectionAsNew`, `CustomWatermarkGallery` omitted? | **Open (screenshot-pending)** | Borderline — SaveSelectionAsNew may be a Home-tab Styles-gallery command (LO has a real near-equivalent, `.uno:StyleNewByExample`); CustomWatermarkGallery may be legacy/alternate. Screenshot-confirm before adding; do not assume. |
| `ParagraphSpacingCustom` idMso real? | **Open (idMso unverified)** | The command is real (Manage Styles → Set Defaults); the exact idMso string is absent from every authoritative list checked. Plausible-but-unconfirmed. |
| idMso label drift ("More Themes on Office Online" vs "…Microsoft Office Online…"; "Reset to the Default Style Set" vs "Reset to Quick Styles from Template")? | **Open (minor, screenshot-pending)** | idMsos confirmed; user-facing labels drift across builds. Low impact; pick canonical labels by screenshot. |
| Built-in Themes/Style-Set/Spacing gallery preset ITEMS not enumerated as rows? | **Resolved (source)** | Correct as-is — gallery contents are not controls and legitimately have no idMso; leaving them out matches Microsoft's schema. NOT missing. |

> **`completenessConfidence`: Medium-high on the Word/idMso side** (Microsoft's idMSOWordMac list
> was obtained; nearly every inventory idMso was confirmed verbatim, with correct spellings and
> control types; the gap is small and bounded — QuickStylesResetDocumentStyles is a clear omission,
> QuickStylesSaveSelectionAsNew and CustomWatermarkGallery are borderline and must be
> screenshot-confirmed). The inventory could not be confirmed scoped to a specific Word build, and
> the Design tab's control set / group structure varies across 2016/2019/365 — a real-Word
> screenshot is the single highest-value next step (group idMso backing, Style-Set and Watermark
> dropdown contents, the unverified ParagraphSpacingCustom idMso). **LO-side confidence is HIGH as
> corrected** — the original inventory prose was materially wrong on the theme preset gallery, the
> color/font edit dialogs, and the flat-toolbox structure, but the LO-source corrections fix those
> and are trusted over the inventory prose.
