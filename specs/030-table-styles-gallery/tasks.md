# Tasks: Table Styles Catalog + Visual Gallery + Theme Palette

**Input**: plan.md (implementation order), research.md (mechanics), spec.md (SC-001..006)
**Branch**: parity-v2 (direct commits per piece; gates before every commit)

## Phase A — Foundations (parallel-safe: disjoint files)

- [ ] T001 [P] Generator + catalog module. `scripts/gen-table-style-defs.js` reads
      `parity/oracle/table_style_defs.json` → emits `src/renderer/core/generated/table-style-defs.ts`
      (`TABLE_STYLE_DEFS: {id: {name, basedOn, section, xml}}`, AUTO-GENERATED banner, section
      derived from name family). Run it; `npm run test:bundle` must stay green (code-split the
      module out of the entry if needed — it is only imported by the bridge).
- [ ] T002 [P] Theme data fix (the ONE approved data-only fork edit). Replace
      `DEFAULT_LINKED_STYLES['GridTable4-Accent1']`'s stale legacy literals (4472C4/8EAADB and
      derivations) with the locked-build capture values (source: the same style's entry in
      `parity/oracle/table_style_defs.json`; convert verbatim XML → the existing xml-js element
      shape). Fork-edit comment marker per convention. NO logic changes.

## Phase B — Bridge (after T001)

- [ ] T003 `src/renderer/bridge/table-styles.ts`: `installTableStyles(editor)` returning
      `{ ensureTableStyleMaterialized, listCatalogStyles, tableStylePreviewEnter, tableStylePreviewLeave }`.
      Materializer: existsOnDoc guard → parse def XML (fork's public parse path) → splice into
      `convertedXml['word/styles.xml']` + register `translatedLinkedStyles.styles[id]` +
      STYLE_NAME_TO_ID/STYLE_ID_TO_NAME. Preview: mirror `bridge/style-preview.ts` EXACTLY
      (state snapshot, `tr.setMeta('addToHistory', false)`, run setTableStyle logic, restore via
      `editor.setState(snap)`, hop contract, keydown/beforeinput cancel).
- [ ] T004 `bridge/table.ts`: `tableSetStyle(id)` calls the materializer first;
      `getTableStyles()` returns catalog ∪ styles.xml (id-deduped, catalog names for unmaterialized);
      wire install in `bridge/index.ts`; expose preview verbs on WC.PM.
- [ ] T005 pm tests (scripts/test-suite-pm.js): (a) apply ListTable3 on blank → exported
      styles.xml carries the def once, basedOn TableNormal intact; (b) double-apply → still once;
      (c) open a docx that carries its own GridTable4-Accent1 → def NOT clobbered (byte-compare
      the w:style subtree); (d) preview enter/leave → undo depth unchanged + doc JSON identical;
      (e) GT4A1 fallback literals == locked-build values (guards T002).

## Phase C — Chrome (after T004; gallery/preview parallel-safe except tests)

- [ ] T006 Gallery UI: `table-tools-pm.js` td-styles group → `ribbon.js renderTableStylesGroup`
      (archive c498c6b adapted: makeGalleryCarousel strip + tableStyleThumb pure-DOM 4×5 thumbs;
      accent hue from WC._themeAccents via name-parsed accent index; active tile from
      tableInfo().styleId). More flyout: full grid with Plain/Grid/List section headers +
      footer (Modify Table Style… honest toast v1 / Clear → tableSetStyle('') / New Table Style…
      honest toast v1) — also port the footer into H.tblStyles (commands.js, 0ecbfd3 shape).
      CSS: .tblstyle-* classes into ribbon.css. Tiles wire mouseenter/leave → WC.PM preview verbs.
- [ ] T007 Teardown safety: contextual-tab hide path + flyout close call preview-leave
      (table-tools-pm.js syncContextualTabs + WC.closeFlyouts hook).

## Phase D — Measure & land (orchestrator)

- [ ] T008 Gates: build + pm + smoke + roundtrip + bundle.
- [ ] T009 Parity acceptance per quickstart.md: tb-style-listtable3 + tb-style-grid4a1
      (--capture-clone --import-leg), behavior re-run (style-gallery journey PASS), scorecard
      deep re-run (GALLERY_UNDERFILLED clears), VISUAL re-capture + re-judge
      (table-styles-gallery, doc-styled-table), feature ledger refresh.
- [ ] T010 Adversarial review (/code-review or workflow) + fix findings + commit per piece +
      checkpoint docs (last-point, execution-map) + SPEC_SEEDS refresh.
