# Writer Ribbon (Notebookbar) Anatomy

> Source-of-truth map for the Tabbed Writer notebookbar. When you want
> to change "where does button X live, what icon, what label, what
> command" — answer is here, not in a grep session.
>
> **Source file:** [`sw/uiconfig/swriter/ui/notebookbar.ui`](../../libreoffice-codebase/sw/uiconfig/swriter/ui/notebookbar.ui)
> (17,349 lines, GtkBuilder XML).
> **Doc generated:** 2026-05-22. Regenerate after structural ribbon edits.
> **What this enables:** [ui-plan.md](ui-plan.md) Phase 1.1.

---

## 1. How to use this doc

- "I want to rename Bold" → §4, find `Home-Bold`, jump to line 3522 in
  `notebookbar.ui`, add inline `<property name="label">Kalın</property>`.
- "I want to swap the Bold icon" → same row, `icon-name` column says
  "(from command)" → the runtime resolves `.uno:Bold` to
  `icon-themes/<theme>/cmd/lc_bold.svg`. Either add explicit
  `icon-name="custom"` in the .ui to override, or swap the file in the
  active icon theme.
- "I want to move a button to a different group" → find current line
  range from §4, cut/paste into the target group's `<sfxlo-NotebookbarToolBox>`.
- "I want to add a new tab" → §3 lists all tabs with line ranges;
  copy any existing tab block as template, edit label and contents.

After editing the source `.ui`, sync it to `instdir/share/config/
soffice.cfg/modules/swriter/ui/notebookbar.ui` and restart `soffice` —
no rebuild needed for layout/label/icon-name changes (see
[USAGE.md](../USAGE.md) "Ribbon iteration" once that section exists).

**Caveat — user-profile UI shadowing:** the runtime checks
`${UserInstallation}/user/config/soffice.cfg/modules/swriter/ui/`
**before** the shared `instdir/` path (`vcl/source/control/notebookbar.cxx:32-44,86-89`).
If a `notebookbar*.ui` file ever ended up in the user profile (manual
drop, prior LO customization), edits to the shared `instdir/` copy
are silently ignored. Phase 1.2's `sync-ui.sh` will handle this; for
manual testing, check the user profile path first.

---

## 2. XML macro structure

Top-down hierarchy of the Tabbed notebookbar:

```
<GtkGrid id="NotebookBar">
  └─ <GtkBox>
       └─ <sfxlo-NotebookbarTabControl id="ContextContainer">    (line 2392)
            ├─ tab page 1
            │   ├─ <sfxlo-PriorityHBox id="File Tab">             (tab content)
            │   │     └─ <sfxlo-PriorityMergedHBox id="File">
            │   │           ├─ <VclOptionalBox id="File-Section-New">
            │   │           │     └─ <GtkBox id="GroupB1">
            │   │           │           ├─ <sfxlo-NotebookbarToolBox>
            │   │           │           │     ├─ <GtkToolButton id="File-AddDirect"
            │   │           │           │     │      action-name=".uno:AddDirect"/>
            │   │           │           │     └─ <GtkToolButton id="File-Open" .../>
            │   │           │           └─ <GtkLabel id="File-Label-New">
            │   │           ├─ <VclOptionalBox id="File-Section-Recent">
            │   │           └─ ...more sections
            │   └─ <GtkLabel id="FileLabel"> (tab title at line 3211)
            ├─ tab page 2 (Home)
            └─ ...15 more tab pages
```

**Key widget vocabulary** (custom LO classes, not standard GTK):

| Class | Role |
|---|---|
| `sfxlo-NotebookbarTabControl` | Root tab strip, holds all tab pages |
| `sfxlo-PriorityHBox` | Tab content container; responsive shrinking |
| `sfxlo-PriorityMergedHBox` | Inner layout with merge rules at narrow widths |
| `VclOptionalBox` | Wraps a group; collapses/hides when space is tight |
| `sfxlo-NotebookbarToolBox` | Toolbar that holds button rows inside a group |
| `sfxlo-DropdownBox` | Right-aligned overflow container ("Home ▾" menu) |
| `svtlo-ManagedMenuButton` | Menu button with managed popup |

**Group priority pattern**: every section has a `<style><class name="priority-N"/></style>`
tag (e.g., `priority-8` = highest, kept visible; `priority-1` = lowest,
first to collapse). This drives the responsive shrink order when the
window is narrowed.

**Button declaration shape:**
```xml
<object class="GtkToolButton" id="Home-Bold">
  <property name="visible">True</property>
  <property name="action-name">.uno:Bold</property>
</object>
```
- No icon path specified → resolved at runtime via `vcl::CommandInfoProvider`
  from the icon theme by command name.
- No label specified → resolved from UNO command metadata registry.
- Override either by adding `<property name="icon-name">x</property>`
  or `<property name="label">X</property>` inline.

---

## 3. All Tabs (inventory)

In notebookbar.ui declaration order:

| # | Tab name | Tab ID | Content line range | Label line |
|---|---|---|---|---|
| 1 | File | FileLabel | 2397-3207 | 3211 |
| 2 | Home | HomeLabel | 3219-4510 | 4496 |
| 3 | Insert | InsertLabel | 4511-5713 | 5717 |
| 4 | Design | DesignLabel | 5726-5843 | 5847 |
| 5 | Layout | LayoutLabel | 5856-7033 | 7037 |
| 6 | References | ReferencesLabel | 7046-7820 | 7824 |
| 7 | Mailings | MailingsLabel | 7833-8010 | 8014 |
| 8 | Review | ReviewLabel | 8023-9010 | 9014 |
| 9 | View | ViewLabel | 9023-9999 | 10004 |
| 10 | Help | HelpLabel | 10013-10101 | 10094 |
| 11 | Table | TableLabel | 10103-11317 | 11321 |
| 12 | Image | ImageLabel | 11333-12640 | 12644 |
| 13 | Draw | DrawLabel | 12656-14066 | 14070 |
| 14 | Object | ObjectLabel | 14085-15018 | 15022 |
| 15 | Media | MediaLabel | 15035-15901 | 15905 |
| 16 | Print | PrintLabel | 15917-16414 | 16418 |
| 17 | Form | FormLabel | 16430-17306 | 17310 |

**Context-aware visibility:** tabs 11-17 (Table, Image, Draw, Object,
Media, Print, Form) are conditionally shown based on document context
(see "Patterns" §7). The Home tab itself has CSS classes
`context-default`, `context-any`, `context-Text`, `context-DrawText`
on its label, indicating it's reshown across multiple contexts.

---

## 4. Home tab — full per-button inventory

Every button on the Home tab, in declaration order. Groups in
declaration order from left to right.

| Group | Button ID | UNO command | Inline label? | Icon name | Line |
|---|---|---|---|---|---|
| Clipboard | Home-Paste | `.uno:Paste` | (from registry) | (from command) | 3251 |
| Clipboard | Home-Cut | `.uno:Cut` | (from registry) | (from command) | 3280 |
| Clipboard | Home-Copy | `.uno:Copy` | (from registry) | (from command) | 3290 |
| Clipboard | Home-FormatPaintbrush | `.uno:FormatPaintbrush` | (from registry) | (from command) | 3313 |
| Font | Home-CharFontName | `.uno:CharFontName` | (from registry) | (from command) | 3407 |
| Font | Home-FontHeight | `.uno:FontHeight` | (from registry) | (from command) | 3431 |
| Font | Home-Grow | `.uno:Grow` | (from registry) | (from command) | 3455 |
| Font | Home-Shrink | `.uno:Shrink` | (from registry) | (from command) | 3465 |
| Font | Home-ChangeCase | `.uno:ChangeCaseRotateCase` | (from registry) | (from command) | 3475 |
| Font | Home-ResetAttributes | `.uno:ResetAttributes` | (from registry) | (from command) | 3485 |
| Font | Home-Bold | `.uno:Bold` | (from registry) | (from command) | 3522 |
| Font | Home-Italic | `.uno:Italic` | (from registry) | (from command) | 3532 |
| Font | Home-UnderlineSimple | `.uno:Underline` | (from registry) | (from command) | 3542 |
| Font | Home-Strikeout | `.uno:Strikeout` | (from registry) | (from command) | 3552 |
| Font | Home-SubScript | `.uno:SubScript` | (from registry) | (from command) | 3562 |
| Font | Home-SuperScript | `.uno:SuperScript` | (from registry) | (from command) | 3572 |
| Font | Home-FontworkGallery | `.uno:FontworkGalleryFloater` | (from registry) | (from command) | 3582 |
| Font | Home-BackColor | `.uno:BackColor` | (from registry) | (from command) | 3606 |
| Font | Home-Color | `.uno:FontColor` | (from registry) | (from command) | 3616 |
| Paragraph | Home-DefaultBullet | `.uno:DefaultBullet` | (from registry) | (from command) | 3705 |
| Paragraph | Home-DefaultNumbering | `.uno:DefaultNumbering` | (from registry) | (from command) | 3715 |
| Paragraph | Home-MultilevelList | `.uno:ChapterNumberingDialog` | (from registry) | (from command) | 3725 |
| Paragraph | Home-DecrementIndent1 | `.uno:DecrementIndent` | (from registry) | (from command) | 3735 |
| Paragraph | Home-IncrementIndent1 | `.uno:IncrementIndent` | (from registry) | (from command) | 3745 |
| Paragraph | Home-SortDialog | `.uno:SortDialog` | (from registry) | (from command) | 3755 |
| Paragraph | Home-ControlCodes1 | `.uno:ControlCodes` | (from registry) | (from command) | 3765 |
| Paragraph | Home-LeftPara | `.uno:LeftPara` | (from registry) | (from command) | 3789 |
| Paragraph | Home-CenterPara | `.uno:CenterPara` | (from registry) | (from command) | 3799 |
| Paragraph | Home-RightPara | `.uno:RightPara` | (from registry) | (from command) | 3809 |
| Paragraph | Home-JustifyPara | `.uno:JustifyPara` | (from registry) | (from command) | 3819 |
| Paragraph | Home-LineSpacing1 | `.uno:LineSpacing` | (from registry) | (from command) | 3829 |
| Paragraph | Home-BackgroundColor1 | `.uno:BackgroundColor` | (from registry) | (from command) | 3839 |
| Paragraph | Home-BorderDialog | `.uno:BorderDialog` | (from registry) | (from command) | 3849 |
| Styles | Home-StylesPreview | `.uno:StylesPreview` | (from registry) | (from command) | 3938 |
| Styles | Home-DesignerDialog | `.uno:DesignerDialog` | (from registry) | (from command) | 3963 |
| Editing | Home-SearchDialog | `.uno:SearchDialog` | (from registry) | (from command) | 4051 |
| Editing | Home-Replace | `.uno:SearchDialog` | (from registry) | (from command) | 4074 |
| Editing | Home-SelectAll | `.uno:SelectAll` | (from registry) | (from command) | 4084 |
| Voice | Home-Dictate | `.uno:SpellingDialog` | yes ("Dictate") | (from command) | 4167 |
| Editor | Home-Editor | `.uno:SpellingDialog` | yes ("Editor") | (from command) | 4252 |
| Add-ins | Home-AddIns | `.uno:ExtensionManager` | yes ("Add-ins") | (from command) | 4337 |
| (overflow) | Home-FocusToFindbar | `.uno:SearchDialog` | (from registry) | (from command) | 4438 |

**Notes on Home buttons:**
- Three buttons (Dictate, Editor, Add-ins) have inline labels. The rest
  inherit from UNO command metadata.
- `Home-Replace` shares `.uno:SearchDialog` with `Home-SearchDialog` —
  both buttons declare the identical `action-name` with no
  differentiating argument in the XML (`notebookbar.ui:4051-4076`).
  Likely a placeholder for a future Replace-focused dispatch; right
  now both open the same dialog identically.
- Voice / Editor groups currently wired to `.uno:SpellingDialog` —
  these appear to be placeholder slots from upstream LO targeting
  future ML features.
- `Home-FocusToFindbar` lives in the right-side `sfxlo-DropdownBox`
  (the "Home ▾" overflow menu).

**Group priority order** (from XML `priority-N` class):
Clipboard 8 · Font 8 · Paragraph 7 · Styles 4 · Editing 3 · Voice 2 ·
Editor 1 · Add-ins 1. Higher number = stays visible longer when the
window narrows.

---

## 5. Other tabs — group-level summary

Tier-2 detail. Per-button tables for these can be added later as needed.
Line ranges are approximate; primary commands are a sampling.

### 5.1 File tab (2397-3207)
| Group | Button count | Primary commands | Line range |
|---|---|---|---|
| New | 2 | AddDirect, Open | 2413-2484 |
| Recent | 1 | RecentFileList | 2500-2553 |
| Close | 1 | CloseDoc | 2569-2623 |
| Save | 4 | Save, SaveAs, SaveAll, SaveACopy | 2639-2778 |
| Versions | 2 | CheckOut, CheckIn | 2794-2906 |
| Reload | 1 | Reload | 2922-2975 |
| Export | 3 | ExportTo, ExportToPDF, ExportToEPUB | 2991-3131 |
| Print | 4 | Print, PrintPreview, PrintDefault, PrinterSetup | 3147-3189 |

### 5.2 Insert tab (4511-5713)
| Group | Button count | Primary commands | Line range |
|---|---|---|---|
| Page Break | 2 | PageBreak, ColumnBreak | 4521-4624 |
| Table | 4 | InsertTable, InsertRowsAbove, DeleteRows, TableProperties | 4635-4745 |
| Image | 4 | InsertGraphic, Crop, ResetCropArea, InsertCaptionDialog | 4764-4874 |
| Bookmark | 2 | InsertBookmark, DeleteBookmark | 4893-4974 |
| Field | 4 | InsertFieldCtrl, FieldMenu, UpdateFields, HideFieldCodes | 5022-5145 |
| Draw Text | 4 | DrawText, TextVariations, ConnectorStart, ArrowStart | 5076-5208 |
| Draw | 5 | BasicShapes, CalloutShapes, StarShapes, SymbolShapes, FlowChartShapes | 5215-5410 |
| Symbol | 3 | SpecialCharacter, Footnote, Endnote | 5481-5633 |

### 5.3 Design tab (5726-5843)
Single group containing the styles preview gallery (StylesPreview at
line 5736-5825). This tab is mostly empty in vanilla — a candidate for
expansion in Phase 2 / future ribbon work.

### 5.4 Layout tab (5856-7033)
| Group | Button count | Primary commands | Line range |
|---|---|---|---|
| Page Setup | 5 | PageSetupDialog, ColumnsDialog, WrapText, ParallelColumns, TextRTL | 5868-6073 |
| Paragraph Margin | 4 | IncrementIndent, DecrementIndent, LeftPara, RightPara | 6103-6253 |
| Backgrounds | 3 | BackgroundColor, BackColor, BorderDialog | 6263-6475 |
| Select & Group | 2 | ObjectSelectAll, Exit | 6472-6552 |
| Wrap | 5 | WrapOff, WrapOn, WrapThrough, WrapIdeal, ArrangeWrap | 6562-6757 |
| Arrange | 4 | ArrangeNone, ArrangeRotation, FlipHorizontal, FlipVertical | 6767-6950 |

### 5.5 References tab (7046-7820)
| Group | Button count | Primary commands | Line range |
|---|---|---|---|
| TOC | 2 | InsertTableOfContents, UpdateTableOfContents | 7065-7185 |
| Footnotes | 2 | InsertFootnote, InsertEndnote | 7201-7321 |
| Citations & Bibliography | 2 | InsertCitation, ManageSources | 7337-7482 |
| Captions | 2 | InsertCaptionDialog, UpdateAllIndexes | 7498-7618 |

### 5.6 Mailings tab (7833-8010)
| Group | Button count | Primary commands | Line range |
|---|---|---|---|
| Mail Merge | 3 | MailMerge, MailMergeDataSourceConnection, MailMergeEditDataSource | 7852-7978 |

### 5.7 Review tab (8023-9010)
| Group | Button count | Primary commands | Line range |
|---|---|---|---|
| Track Changes | 3 | TrackChanges, ShowTrackedChanges, RejectAllChanges | 8042-8162 |
| Comments | 2 | InsertAnnotation, DeleteAllAnnotations | 8178-8298 |
| Protect | 2 | SetDocumentProperties, ProtectDocument | 8314-8434 |
| Language | 1 | HyphenationDot | 8450-8503 |

### 5.8 View tab (9023-9999)
| Group | Button count | Primary commands | Line range |
|---|---|---|---|
| Views | 2 | WebLayoutMode, NormalMode | 9042-9162 |
| Zoom | 3 | ZoomPage, ZoomPageWidth, ZoomOptimal | 9178-9298 |
| Show | 3 | ShowTrackedChanges, Marks, ShowGraphics | 9314-9451 |

### 5.9 Help tab (10013-10101)
Three buttons in a single group: HelpIndex, SendFeedback, About
(10029-10067).

### 5.10 Context tabs (Table / Image / Draw / Object / Media / Print / Form)

Shown conditionally based on selection / document context. Group-level
summaries:

**Table (10103-11317):** Design (8 buttons), Layout (8), Data (3).
**Image (11333-12640):** Crop & Rotate (4), Colors (3), Effects (2), Arrange (5), Size & Position (2).
**Draw (12656-14066):** Insert Shapes (7), Colors (3), Arrange (5), Size & Position (2).
**Object (14085-15018):** Format (4), Arrange (5).
**Media (15035-15901):** Play (3), Properties (2).
**Print (15917-16414):** Print Preview (3), Page Setup (2).
**Form (16430-17306):** Form Design (4), Controls (3).

---

## 6. Where labels and icons actually come from

For buttons without inline `label` / `icon-name`. Verified against
`vcl/source/helper/commandinfoprovider.cxx`.

**Label resolution path** (runtime, for a toolbar button):
1. `vcl::CommandInfoProvider::GetLabelForCommand(".uno:Bold", xFrame)`
   (`commandinfoprovider.cxx:246-255`)
2. → reads the `Name` property of the command's metadata (not the
   `Label` property — `Label` is used for menu entries, `Name` for
   toolbars / generic display).
3. Command metadata fetched via `frame::theUICommandDescription::get()`,
   resolved per module (`commandinfoprovider.cxx:44-55, 212-230`).
4. Backing data: per-module command XCU like
   `officecfg/registry/data/org/openoffice/Office/UI/WriterCommands.xcu`
   (and `GenericCommands.xcu` for cross-app commands). Entry shape
   includes a `<Name>` and `<Label>` per locale.

**Icon resolution path** (runtime):
1. `vcl::CommandInfoProvider::GetImageForCommand(".uno:Bold", xFrame)`
   (`commandinfoprovider.cxx:341-399`)
2. → checks the **document's** `XImageManager` first (commands can
   have document-scoped icon overrides).
3. → falls back to the **module's** `XImageManager` (the global icon
   theme).
4. The module image manager resolves the icon name (derived from the
   command name) against the active icon theme's packed
   `images_<theme>.zip` (not a direct filesystem read — themes are
   discovered and consumed as zip archives at runtime).
5. Active theme set by `Office.Common/Misc/SymbolStyle` registry key.

**To override per-button without touching registry**:
- Inline label: `<property name="label">My Label</property>`
- Inline icon: `<property name="icon-name">my-icon</property>` (must
  exist as `my-icon.svg` / `my-icon.png` in the active theme's
  packed zip).

**To override globally for a command** (label):
- Add an override XCU under
  `officecfg/registry/data/org/openoffice/Office/UI/WriterCommands.xcu`
  for that command. Affects every place the command appears (menu,
  toolbar, every ribbon, command palette). Note: override the
  `Name` property for toolbar display; `Label` for menu display.

---

## 7. Patterns worth knowing

**Context filtering.** Tab labels carry style classes like
`context-Text`, `context-DrawText`, `context-default`. The `sfxlo-NotebookbarTabControl`
shows / hides tabs based on the current selection context. To make a
tab always visible regardless of context, ensure it carries
`context-default` and `context-any`.

**Responsive priority.** Each group's `priority-N` class drives collapse
order at narrow widths. To pin a group always-visible, raise its
priority to 9. To make a group collapse first, drop to 1.

**Optional sections.** `VclOptionalBox` wraps each group. Setting
`<property name="visible">False</property>` on the box hides the entire
group at startup. Useful for stripping unwanted groups without removing
their XML (easier to restore later).

**Overflow menu.** The right-aligned `sfxlo-DropdownBox` at the end of
each tab holds secondary buttons that appear in a dropdown when the
tab overflows. Buttons there have id pattern `{Tab}-FocusToFindbar`
etc.

**NotebookBarAddons merge points.** Extension toolbars get merged in at
`<menu name="NotebookBarAddonsMenuMergePoint">` markers. Search for
that string to find injection points if you want to drop in a custom
toolbar group from an addon.

---

## 8. Updating this doc

This doc was generated by parsing `notebookbar.ui` at commit
`9340fa487` (2026-05-22). After a structural ribbon edit (adding /
removing / reordering buttons, groups, or tabs), regenerate the §3, §4,
§5 tables — line numbers will have shifted.

Cheap regeneration: run the same notebookbar-extraction agent that
produced the first version (prompt is captured in this session's
history; will be moved into `scripts/` as `extract-ribbon.py` later).

Heavy regeneration (after large fork divergence): also re-verify §2
custom widget classes haven't changed, and §6 resolution paths still
match `vcl::CommandInfoProvider` source.
