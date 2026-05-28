# 2026-05-28 — Word-faithful ribbon rewrite + deep feature coverage

## Trigger

Owner asked: *"DEEP DIVE — make sure every LibreOffice feature is wired into
the ribbon. Look up the MS Word structure and adapt to it."*

## Method

1. **Web research** — pulled Word 365's ribbon structure from public docs
   (Microsoft Support / addbalance.com): exact tabs (File, Home, Insert, Draw,
   Design, Layout, References, Mailings, Review, View, Help), per-tab groups
   and the control kinds (button / dropdown / colour-picker / gallery / combo).
2. **LO surface audit** — re-read three authoritative sources to know what
   LO Writer can do:
   - `command-catalog.json` (1520 `.uno:` from WriterCommands.xcu +
     GenericCommands.xcu)
   - `writer-menu-tree.json` (11 menus / 497 items)
   - `sw/uiconfig/swriter/ui/notebookbar.ui` (LO's own Writer ribbon — 17 tabs,
     434 commands; parsed `.uno:` from every `<property name="action-name">`)
3. **Map** — every Word group → the LO commands that fit it, organised so the
   ribbon's shape matches Word's even when the underlying engine is LO.
4. **Codex parallel pass** — dispatched a second analysis for cross-check.
   Codex parsed the same four sources and confirmed the gap inventory; its
   sandbox blocked the audit-file write but the in-memory work agreed with
   this restructure.
5. **Rewrote** `build_ribbon.py`'s SPEC accordingly.

## What shipped

- `build_ribbon.py` SPEC v3 — Word's tab/group skeleton, populated from LO.
- **11 tabs (Word's exact set), 53 groups, 213 items, 138 icons.**
- Added the **Draw** tab (Shapes / Lines / Edit / Text) and the **Mailings**
  tab (Create / Start Mail Merge / Write & Insert Fields / Finish).
- Compound controls now: **10 dropdowns** (LineSpacing, Bullets, Numbering,
  ChangeCase, PageMargin, Orientation, PageSize, Columns, Zoom, TextWrap),
  **4 colour pickers** (FontColor, BackColor, BackgroundColor ×2 ¶+page),
  **29 toggles**, **2 combos** (font name / size).
- Word-faithful additions beyond what we had: PasteSpecial, FontDialog,
  ParagraphDialog, OutlineBullet, proper ChangeCase dropdown, more paragraph
  styles (No Spacing / Subtitle / Quote), the full shapes family (Basic /
  Arrow / Symbol / Star / Callout / Flow), Comments group in Insert,
  InsertSection / InsertColumnBreak in Layout, ParaspaceIncrease/Decrease,
  HelplinesMove, ZoomPlus/Minus, DeleteCommentThread / ResolveComment /
  ShowAnnotations toggle, RedactDoc, full Mail Merge group.
- Verified: 0 commands missing from the catalog, 0 icon-fetch failures,
  render_test green, screenshots of every tab clean.

## Notes / honest limits

- **PageMargin / Orientation / PageSize / Columns / Mail Merge** dropdowns
  fall back to the relevant dialog (`PageDialog` / `FormatColumns` /
  `MailMergeWizard`) because LO doesn't expose those as argful `.uno:` slots —
  they live in sidebar Control widgets. Refining to a real arg-dispatch popup
  via the `SfxItemSet` route is a tail item (audit pointed at
  `sw/source/uibase/sidebar/*Control.cxx`).
- The Mailings tab is sparse compared to Word's — LO's mail-merge is wizard-
  driven, with most steps inside the wizard rather than as ribbon commands.
- Word features that simply don't exist in LO (Icons, 3D Models, SmartArt,
  Dictate, Editor AI, Copilot, Ink-to-Math) are correctly omitted.

## Tail (still open)

- Real SfxItemSet popups for Margin / Orientation / Size / Columns presets.
- Colour palette: hand-curated 8×5 theme/standard set (currently a
  Word-ish generic palette).
- Bullet/Numbering **style gallery** (currently a 2-option dropdown).
- Native Qt FileDialog for Open / Save-As / InsertGraphic.
- HyperlinkDialog `enabled.cxx` patch.
- Keyboard shortcuts → `.uno:` map.
