# Research — 030 Table Styles Catalog + Gallery + Theme Palette

> Phase 0 output. Three parallel read-only research passes (styles seam / theme / gallery+preview),
> 2026-07-02. All file:line refs verified against the working tree @ `750f845`.

## R1 — The NO-FORK registration/materialization seam (catalog)

**Decision:** generated catalog module + lazy materialization in the bridge, wrapped around the
fork's existing `setTableStyle` command.

- The fork requires a style def in **TWO** places: `converter.translatedLinkedStyles.styles[id]`
  (in-app paint — `resolveTableStyleVisuals` returns null without it) **and** the in-memory
  `word/styles.xml` xml-js tree (gallery enumeration via `getTableStyles` [table.ts:371] +
  Word-safe export — Word DROPS an orphaned `w:tblStyle` ref, exporter-docx-defs.js:905-908).
- `editor.commands.setTableStyle(id)` [fork table.js:1617] dual-writes `tableStyleId` +
  `tableProperties.tableStyleId` (→ `<w:tblStyle>`) and bakes STABLE visuals (whole-table borders
  + firstRow fill) via `resolveTableStyleVisuals`; banding is deliberately not baked in-app
  (goes stale on row edits) — the exported def carries it for Word.
- Import precedence is already solved: `addDefaultStylesIfMissing` [docxImporter.js:764] pushes a
  default ONLY if `existsOnDoc` is false — the document's own def wins. Our materializer must use
  the same guard.
- **Mechanism (mirrors 021 createNamedStyle, bridge-side, no fork edit):**
  1. `scripts/gen-table-style-defs.js` reads `parity/oracle/table_style_defs.json` → emits
     `src/renderer/core/generated/table-style-defs.ts` (AUTO-GENERATED banner convention, like
     `blank.docx.b64.ts`): `TABLE_STYLE_DEFS: { [styleId]: { name, basedOn, xml } }` (verbatim XML
     strings; parse per-use with the fork's public `parseXmlToJson` path — cheaper than shipping
     pre-parsed JSON x113).
  2. New bridge helper `ensureTableStyleMaterialized(editor, id)` in `bridge/table.ts` (or a
     sibling `bridge/table-styles.ts`): `existsOnDoc` guard → else splice the parsed `<w:style>`
     element into `convertedXml['word/styles.xml'].elements[0].elements` + register the translated
     entry into `translatedLinkedStyles.styles[id]` + `STYLE_NAME_TO_ID`/`STYLE_ID_TO_NAME`.
  3. `tableSetStyle(id)` calls the materializer first, then `setTableStyle(id)` unchanged.
  4. `getTableStyles()` returns the UNION of catalog ids + styles.xml entries (no write
     amplification; blank-doc styles.xml stays lean, Word-like lazy behavior).

**Alternatives considered:** eager registration of all 113 into DEFAULT_LINKED_STYLES (rejected:
fork edit + bloats every export); runtime fetch of the oracle JSON (rejected: parity/ is not a
runtime dependency; generated-module convention exists).

## R2 — Theme palette (the teal/royal-blue finding's real root)

**Decision:** the palette itself needs NO change — fix the stale literal hex CACHES in the fork's
fallback style data, sourced from the new-build captures.

- Already correct (no change): the blank template's `word/theme/theme1.xml`
  [core/blank-docx.ts — decoded: accent1 156082, Aptos fonts]; the themeColor resolver
  [layout-adapter/marks/theme-color.ts:85 — palette-agnostic, reads the DOC's theme];
  import (`getThemeColorPalette` [docxImporter.js:1291] — doc-theme-wins, verified);
  export (theme part passes through); chrome pickers [util.js:97 THEME_COLORS] and Design
  schemes [design-tools.js:23/56] — all already Aptos.
- **The actual bug:** `resolveColorFromAttributes` [application.ts:228-244] prefers the LITERAL
  `attrs.color` over theme resolution. The fork's `DEFAULT_LINKED_STYLES.GridTable4-Accent1`
  fallback def carries stale LEGACY literals paired with themeColor refs (`4472C4` fills/borders,
  `8EAADB` tinted borders; injected into every blank doc at parse). Literal wins → legacy blue
  renders even though the doc theme is teal.
- **Fix path:** replace the stale GT4A1 entry's data with the locked-build capture (the same
  verbatim def already in `table_style_defs.json` — its literals ARE the new palette because it
  was captured on the locked build). This is a **data-only fork edit** (exporter-docx-defs.js,
  DEFAULT_LINKED_STYLES values; no logic) — constitution Principle I allows a minimal, documented
  fork change by explicit plan decision; recorded as such in plan.md. Heading1-3's stale `0F4761`
  literals are the same class but OUT of this feature's scope → follow-up seed.
- **Risk:** result JSONs asserting `4472C4` go stale (they get re-measured anyway);
  round-trip snapshots that hash fallback-injected styles.xml need re-baselining (gates will show).

## R3 — Gallery UI + hover live preview

**Decision:** in-ribbon `makeGalleryCarousel` strip + archive tile shapes + More-flyout sections
+ footer; live preview via an `addToHistory:false` transaction snapshot/restore — the codebase's
own proven pattern.

- The generic in-ribbon gallery mechanism EXISTS: `makeGalleryCarousel` [ribbon.js:296-333],
  used by Home Styles [renderStylesGallery :335] and Design Style Sets [:405] — the exact
  structural template (tiles + More + footer + active highlight).
- Archive `c498c6b` tile code (pure-DOM 4×5 mini-tables, name-parsed accent hue) transplants
  nearly verbatim; its `WC.PM.getThemeColors()` dependency doesn't exist → rewire to
  `WC._themeAccents` (design-tools.js:108) / THEME_COLORS. Archive `0ecc..0ecbfd3` footer
  (Modify…/Clear/New; Clear = `tableSetStyle('')` — confirmed: fork deletes tableStyleId) is a
  clean drop-in. All `.tblstyle-*` CSS must be re-added to ribbon.css.
- **Live preview = option (b):** mirror `bridge/style-preview.ts` (paragraph linked-style hover
  preview): snapshot `editor.state`, build tr with `tr.setMeta('addToHistory', false)` (the fork's
  history plugin honors it — history.js:48), run the real setTableStyle logic, dispatch; restore
  via `editor.setState(snap)` (NOT view.updateState — "mismatched transaction" trap documented in
  style-preview.ts:4-9), cancel on keydown/beforeinput, hop-contract between tiles. Runs the real
  apply path → perfect fidelity (banding incl.), zero undo entries, zero fork edits.
  Rejected: chrome-side inline CSS (TableView.update() fights it; re-derives the cascade);
  PM decorations (can't restyle attr-driven cell fills).
- **Sections:** inline strip = the gallery; the More flyout holds the full grid with
  Plain/Grid/List section headers + the footer.
- **Extra risk found:** contextual-tab teardown mid-preview (caret leaves table → tabs hide) must
  restore any active preview — add a restore call to the tab-hide path.

## Cross-cutting

- In-app banding limitation (R1): the live preview DOES show banding? No — preview runs
  setTableStyle whose bake is borders+firstRow only; banding appears on Word open. The VISUAL L4
  screenshot showed a band because the PE also resolves conditional fills at render for
  DEFAULT-registered styles (observed behavior). Acceptance judges the re-captured pair — if
  banding renders weaker than Word's, that's an honest VISUAL finding for a follow-up, not a
  blocker for this feature's SCs.
- Order of work: theme-data fix FIRST (so tiles + previews render true colors), then catalog,
  then gallery/preview UI.
