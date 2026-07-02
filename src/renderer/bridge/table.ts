// Slice 6: table surface. Insertion + the legacy 9 ops mapped onto fork table commands.
//
// FORK API NOTES (verified against extensions/table/table.js):
// - addColumnBefore/After: internally call chain().run() from the fork's own command
//   context — calling editor.chain().addColumn*().run() double-wraps and misbehaves.
//   Use editor.commands.addColumnBefore/After() instead.
// - addRowBefore/After, deleteRow/Column, deleteTable, toggleHeaderRow/Column,
//   setCellAttr: safe to use via editor.commands.X() directly.
// - insertTable: safe to chain (does not internally chain).
//
// M1 (Critique-hardened): mergeCells (prosemirror-tables originalMergeCells) requires a
// CellSelection — it returns false silently on a plain TextSelection. Bridge tableMerge()
// detects non-CellSelection and toasts "Select cells first" + returns false rather than
// silently no-op. setCellBackground is NOT gated (T3 fix): the fork falls back to the
// caret-safe setCellAttr path when the caret sits in a table — Word shades the caret cell.

import { isCellSelection } from '@extensions/table/tableHelpers/isCellSelection.js'
// Spec 033: TableMap gives the rectangular grid (corner cell positions) for Layout → Select.
// prosemirror-tables is Vite-deduped to a single copy, so this is the SAME class the fork uses —
// NO fork edit (bridge-only import, mirrors isCellSelection above).
import { TableMap } from 'prosemirror-tables'
// Spec 030: the generated catalog (113 real-Word modern table-style defs) — getTableStyles unions
// it with the doc's styles.xml so the gallery is honest before any style is materialized.
import { TABLE_STYLE_DEFS } from '@/core/generated/table-style-defs'
// Spec 034: reuse the shared preview meta string so io.ts's dirty guard (which checks THIS key)
// covers the insert-grid hover preview — the paint-only insert must never flip the dirty flag.
import { PREVIEW_META as INSERT_PREVIEW_META } from './style-preview'

type AnyEditor = any

// Spec 030: installTable receives the table-style materializer (installTableStyles' return) so
// tableSetStyle can lazily register the def BEFORE setTableStyle applies it — Word DROPS an
// orphaned <w:tblStyle> ref on save (exporter-docx-defs.js:905-908), so the def must be in
// styles.xml first. Optional (pre-mount stubs pass nothing) → a no-op fallback keeps it safe.
// Spec 031: installTable also receives the conditional-format restamper (restampTableConditionalFormats,
// from installTableConditionalFormats) so the structural verbs + tableSetStyle re-derive Word's cnfStyle
// stamps for styled tables (and STRIP stale stamps when unstyled). Optional (pre-mount stubs pass nothing)
// → a no-op fallback keeps it safe.
export function installTable(
  editor: AnyEditor,
  ensureTableStyleMaterialized?: (id: string) => boolean,
  restampTableConditionalFormats?: (ed?: AnyEditor, tr?: any) => boolean,
) {
  const materialize = typeof ensureTableStyleMaterialized === 'function' ? ensureTableStyleMaterialized : () => false
  const restamp = typeof restampTableConditionalFormats === 'function' ? restampTableConditionalFormats : () => false
  // Restore PM focus after each verb (same invariant as commands.ts / insert.ts).
  function refocus() { editor.view?.focus() }

  // Guard: require a CellSelection before running merge (merge genuinely needs 2+ cells).
  // Uses the fork's isCellSelection helper (instanceof CellSelection). prosemirror-tables
  // is deduped to a single copy by Vite, so instanceof is reliable across the bundle.
  const requireCellSel = (title: string, body: string): boolean => {
    if (isCellSelection(editor.state?.selection)) return true
    ;(window as any).WC?.toast?.(title, body)
    return false
  }

  // Spec 034 — Word's uneven per-column width distribution: base = floor(total/N); the last
  // `rem` columns get base+1 (remainder pushed to the LATER columns). Verified 9350/3 →
  // [3116, 3117, 3117]. Total = the section's default table width in twips (see insertTable).
  function distributeWidths(total: number, N: number): number[] {
    const n = Math.max(1, Math.floor(N))
    const base = Math.floor(total / n)
    const rem = total - base * n
    return Array.from({ length: n }, (_, i) => (i < n - rem ? base : base + 1))
  }

  // The section's default full-width table width in twips: (pageW − Lm − Rm) in inches → twips,
  // minus Word's 10-twip fudge (the two ½-cell-margin default insets net out to ~10 twips at the
  // table edges). Falls back to 9350 (US Letter, 1in margins) when page styles are unreadable.
  function defaultTableWidthTwips(): number {
    try {
      const ps = (editor.getPageStyles && editor.getPageStyles()) || {}
      const wIn = ps?.pageSize?.width
      const lIn = ps?.pageMargins?.left
      const rIn = ps?.pageMargins?.right
      if (typeof wIn === 'number' && typeof lIn === 'number' && typeof rIn === 'number') {
        const t = Math.round((wIn - lIn - rIn) * 1440) - 10
        if (Number.isFinite(t) && t > 0) return t
      }
    } catch { /* fall through to the US-Letter default */ }
    return 9350
  }

  function insertTable(opts: { rows?: number; cols?: number; withHeaderRow?: boolean } = {}): boolean {
    const rows = Math.max(1, Math.min(1000, Math.floor(opts.rows ?? 3)))
    const cols = Math.max(1, Math.min(1000, Math.floor(opts.cols ?? 3)))
    const ok = editor.chain().insertTable({ rows, cols, withHeaderRow: !!opts.withHeaderRow }).run()
    if (ok !== false) seedInsertDefaults(cols)
    refocus()
    return ok !== false
  }

  // Spec 034 — write Word's exact hidden defaults onto the just-inserted table so a fresh insert
  // round-trips the F-class base delta (uneven gridCol/tcW, tblW auto, tblLook val, TableGrid pPr).
  // Runs AFTER insertTable committed (the caret is inside the new table → currentTableCtx resolves it).
  // ONE tr (all setNodeMarkup) + a follow-up restamp for tblLook — kept out of undo pollution
  // (addToHistory:false) so the user's single Insert stays one clean undo step.
  //   - table `grid` = [{col: twips}, …]     → the tblGrid decode reads grid[i].col twips FIRST → exact gridCol.
  //   - table tableProperties.tableWidth = {value:0, type:'auto'} → <w:tblW w:w="0" w:type="auto"/>.
  //   - per-cell tableCellProperties.cellWidth = {value: twips, type:'dxa'} AND CLEAR the cell's `colwidth`.
  //     Clearing colwidth is load-bearing for TWO reasons: (1) the decode's px→twips recompute
  //     (translate-table-cell.js:55-64) is skipped, so the seeded dxa twips survive → exact tcW; and (2)
  //     the fork's `tableColwidthGridSync` appendTransaction (table.js:2351) rebuilds `grid` from the
  //     first-row colwidths via pixelsToTwips(Math.round(px)) — it ROUNDS px to an INTEGER first, so 3116
  //     and 3117 twips (both ≈207.7px → round 208 → 3120) collapse to a uniform 3120 and CLOBBER our
  //     precise grid. Its `newGrid.length` guard means an EMPTY colwidth leaves our grid untouched, so
  //     clearing colwidth is the only way to preserve the exact per-column twips (populated colwidth
  //     cannot encode sub-pixel-distinct twips through the plugin's integer-px round).
  //   - tblLook val via restamp(editor) (the FIX-2 val writer seeds DEFAULT_TBL_LOOK '04A0').
  function seedInsertDefaults(cols: number): void {
    try {
      const ctx = currentTableCtx()
      if (!ctx) return
      const total = defaultTableWidthTwips()
      const widths = distributeWidths(total, cols)
      const grid = widths.map((w) => ({ col: w }))
      const tr = editor.state.tr
      tr.setMeta('addToHistory', false)
      // Table node: grid + tblW auto + tblLook (Word's fresh-table default 04A0 = firstRow 0x20 +
      // firstColumn 0x80 + noVBand 0x400; firstRow/firstColumn/noVBand flags on). Seeding it here
      // (in this addToHistory:false tr) keeps the whole defaults write to ONE undo-invisible step;
      // restamp() below then STRIPS any stale cnfStyle (a no-op for a fresh unstyled table).
      const prevLook = ctx.node.attrs?.tableProperties?.tblLook
      const tblLook = prevLook && prevLook.val
        ? prevLook
        : { firstRow: true, lastRow: false, firstColumn: true, lastColumn: false, noHBand: false, noVBand: true, val: '04A0' }
      const tblProps = { ...(ctx.node.attrs?.tableProperties || {}), tableWidth: { value: 0, type: 'auto' }, tblLook }
      tr.setNodeMarkup(ctx.pos, undefined, { ...ctx.node.attrs, grid, tableProperties: tblProps })
      // Per-cell: seed cellWidth twips (dxa) + CLEAR colwidth (see the note above — the grid-sync's
      // integer-px round would otherwise clobber the exact grid). Walk rows/cells like the borders walk
      // (positions accumulate nodeSize from tableStart).
      let rowPos = ctx.tableStart
      for (let r = 0; r < ctx.node.childCount; r++) {
        const row = ctx.node.child(r)
        let cellPos = rowPos + 1
        for (let c = 0; c < row.childCount; c++) {
          const cell = row.child(c)
          const twips = widths[Math.min(c, widths.length - 1)]
          const nextCellProps = { ...(cell.attrs?.tableCellProperties || {}), cellWidth: { value: twips, type: 'dxa' } }
          tr.setNodeMarkup(cellPos, undefined, { ...cell.attrs, colwidth: null, tableCellProperties: nextCellProps })
          cellPos += cell.nodeSize
        }
        rowPos += row.nodeSize
      }
      editor.view.dispatch(tr)
      // tblLook val (04A0) — the FIX-2 writer seeds DEFAULT_TBL_LOOK for a table with no tblLook yet.
      // It builds+dispatches its own (change-only) tr; harmless no-op when nothing changes.
      restamp(editor)
    } catch { /* best-effort — a robust insert never throws over the defaults seed */ }
  }

  function tableAddRow(dir: 'above' | 'below'): boolean {
    // addRowBefore/After: safe to call via commands directly (no internal chain())
    const ok = dir === 'above'
      ? editor.commands.addRowBefore()
      : editor.commands.addRowAfter()
    if (ok !== false) restamp(editor) // 031: re-derive cnfStyle stamps (banding renumbers on insert)
    refocus()
    return ok !== false
  }

  function tableAddColumn(dir: 'left' | 'right'): boolean {
    // addColumnBefore/After: fork's implementation uses chain().run() internally —
    // must NOT wrap in editor.chain().X().run() (double-wrap). Use commands.X() directly.
    const ok = dir === 'left'
      ? editor.commands.addColumnBefore()
      : editor.commands.addColumnAfter()
    if (ok !== false) restamp(editor) // 031: re-derive cnfStyle stamps (column banding renumbers)
    refocus()
    return ok !== false
  }

  function tableDeleteRow(): boolean {
    const ok = editor.commands.deleteRow()
    if (ok !== false) restamp(editor) // 031: re-derive cnfStyle stamps
    refocus()
    return ok !== false
  }

  function tableDeleteColumn(): boolean {
    const ok = editor.commands.deleteColumn()
    if (ok !== false) restamp(editor) // 031: re-derive cnfStyle stamps
    refocus()
    return ok !== false
  }

  function tableDeleteTable(): boolean {
    const ok = editor.commands.deleteTable()
    refocus()
    return ok !== false
  }

  function tableMerge(): boolean {
    // M1: mergeCells requires a CellSelection (multi-cell selection).
    // On a plain TextSelection (caret or collapsed range in one cell) it returns false
    // silently. Detect and toast so the user knows what to do.
    if (!requireCellSel('Select cells first', 'Select multiple cells to merge them — click and drag across cells in the table.')) return false
    const ok = editor.commands.mergeCells()
    if (ok !== false) restamp(editor) // 031: merged cells → re-derive stamps (banding counts grid columns)
    refocus()
    return ok !== false
  }

  function tableSplitCell(): boolean {
    const ok = editor.commands.splitCell()
    if (ok !== false) restamp(editor) // 031: split cells → re-derive stamps
    refocus()
    return ok !== false
  }

  function tableToggleHeaderRow(): boolean {
    const ok = editor.commands.toggleHeaderRow()
    refocus()
    return ok !== false
  }

  function tableToggleHeaderColumn(): boolean {
    const ok = editor.commands.toggleHeaderColumn()
    refocus()
    return ok !== false
  }

  function tableSetCellShading(color: string): boolean {
    // No CellSelection gate (T3 fix, Word parity): with a plain caret in a cell the
    // fork's setCellBackground falls back to setCellAttr (shades the caret cell, like
    // Word). A CellSelection still shades every selected cell. Outside a table the
    // fork returns false.
    const ok = editor.commands.setCellBackground(color)
    refocus()
    return ok !== false
  }

  function tableSetCellVAlign(v: 'top' | 'middle' | 'bottom'): boolean {
    const ok = editor.commands.setCellAttr('verticalAlign', v)
    refocus()
    return ok !== false
  }

  // Is the selection inside a table? (drives contextual-tab show/hide + Table Tools state)
  // Walk $from ancestors for a node of type 'table'.
  function isInTable(): boolean {
    try {
      const { $from } = editor.state.selection
      for (let d = $from.depth; d > 0; d--) {
        if ($from.node(d).type.name === 'table') return true
      }
    } catch { /* selection state the resolver can't read */ }
    return false
  }

  // ---------- 6b: net-new Table Tools commands (Task 9) ----------
  // All 14 fork commands use raw PM dispatch ({ state, tr, dispatch }) and work off
  // a plain caret-in-table — no CellSelection gate needed (confirmed by Task 8 tests).
  // Use editor.commands.X() directly (same pattern as addColumnBefore/After).

  function tableSetStyle(id: string): boolean {
    // Spec 030: materialize the catalog def FIRST (splice into styles.xml + register the
    // translated entry) so the exporter keeps the <w:tblStyle> ref and the in-app painter can
    // resolve visuals. A blank id (Clear) or an already-materialized/doc-owned def is a harmless
    // no-op here. Then apply via the fork command unchanged.
    if (id) materialize(id)
    const ok = editor.commands.setTableStyle(id)
    // 031: after the style applies (or clears), re-derive Word's cnfStyle stamps for the new style — a
    // styled table gets its per-row/cell markers, a cleared (TableGrid/none) table gets them STRIPPED.
    if (ok !== false) restamp(editor)
    refocus()
    return ok !== false
  }

  function tableSetAlignment(a: 'left' | 'center' | 'right'): boolean {
    const ok = editor.commands.setTableAlignment(a)
    refocus()
    return ok !== false
  }

  function tableSetIndent(px: number): boolean {
    const ok = editor.commands.setTableIndent(px)
    refocus()
    return ok !== false
  }

  function tableSetCellWidth(px: number): boolean {
    const ok = editor.commands.setCellWidth(px)
    refocus()
    return ok !== false
  }

  function tableSetRowHeight(px: number, rule?: string): boolean {
    const ok = editor.commands.setRowHeight(px, rule)
    refocus()
    return ok !== false
  }

  function tableSetCellMargins(m: { top?: number; right?: number; bottom?: number; left?: number }): boolean {
    const ok = editor.commands.setCellMargins(m)
    refocus()
    return ok !== false
  }

  // Returns the caret cell's explicit per-side margins in px ({top,right,bottom,left}) so the Cell
  // Margins flyout can PREFILL the current values (Word's Cell Options dialog pre-reads them) instead
  // of seeding stock defaults — otherwise tweaking one side and re-applying would clobber the others.
  // Returns null when not in a cell or the cell has no explicit margins (inherits the table default).
  function tableGetCellMargins(): { top: number; right: number; bottom: number; left: number } | null {
    if (!isInTable()) return null
    try {
      const { $from } = editor.state.selection
      for (let d = $from.depth; d > 0; d--) {
        const n = $from.node(d)
        if (n.type.name === 'tableCell' || n.type.name === 'tableHeader') {
          const cm = n.attrs?.cellMargins
          if (cm && typeof cm === 'object') {
            return {
              top: Number(cm.top) || 0,
              right: Number(cm.right) || 0,
              bottom: Number(cm.bottom) || 0,
              left: Number(cm.left) || 0,
            }
          }
          return null
        }
      }
    } catch { /* fall through */ }
    return null
  }

  // Spec 032: write the caret cell's borders CANONICALLY (attrs.tableCellProperties.borders + the
  // 'borders' inline key), matching the fork's own clear path (deleteCellAndTableBorders) — NOT via
  // setCellBorders/setCellAttr('borders'). Why: the fork's tableStyleNormalization appendTransaction, when a
  // cell ALREADY carries migrated tableCellProperties.borders, DISCARDS any freshly-set attrs.borders (it
  // treats it as stale legacy data) and keeps the old canonical value. So a SECOND setCellBorders (e.g. the
  // Borders dropdown merging Bottom onto an existing Top) would be silently dropped. Writing straight to the
  // canonical store side-steps that (the migration block is gated on `attrs.borders != null`, so leaving it
  // null means our write is never touched). Replace semantics are preserved: `b` fully replaces the cell's
  // border object (the chrome does any merge via tableGetCellBorders first). Falls back to the fork command if
  // the caret cell can't be resolved.
  function tableSetCellBorders(b: Record<string, unknown>): boolean {
    if (isInTable()) {
      try {
        const { $from } = editor.state.selection
        for (let d = $from.depth; d > 0; d--) {
          const n = $from.node(d)
          if (n.type.name === 'tableCell' || n.type.name === 'tableHeader') {
            const cellPos = $from.before(d)
            const nextInlineKeys = Array.from(new Set([...((n.attrs?.tableCellPropertiesInlineKeys as string[]) || []), 'borders']))
            const tr = editor.state.tr.setNodeMarkup(cellPos, undefined, {
              ...n.attrs,
              borders: null,
              tableCellProperties: { ...(n.attrs?.tableCellProperties ?? {}), borders: b },
              tableCellPropertiesInlineKeys: nextInlineKeys,
            })
            editor.view.dispatch(tr)
            refocus()
            return true
          }
        }
      } catch { /* fall through to the fork command */ }
    }
    const ok = editor.commands.setCellBorders(b)
    refocus()
    return ok !== false
  }

  // Spec 032: returns a DEEP COPY of the caret cell's explicit per-side borders so the Borders dropdown can
  // MERGE a single edge onto the current cell borders instead of REPLACING them (setCellBorders/
  // setCellAttr('borders') is a full replace). Mirrors tableGetCellMargins. Each side is
  // {val,color,size,space,themeColor?}; sides may include top/start/left/bottom/end/right/insideH/insideV/
  // tl2br/tr2bl. Returns null when not in a cell or the cell carries no explicit borders (inherits the
  // table/style default) — the chrome then starts from an empty object.
  // IMPORTANT: the fork's tableStyleNormalization plugin migrates a freshly-set attrs.borders into the
  // CANONICAL attrs.tableCellProperties.borders (and NULLS attrs.borders) on the next tick. So read BOTH:
  // prefer the live attrs.borders (just set, pre-migration), else fall back to the migrated
  // tableCellProperties.borders. Otherwise a merge would lose every previously-applied edge (they've
  // already migrated out of attrs.borders) — exactly the "Top then Bottom loses Top" failure.
  function tableGetCellBorders(): Record<string, any> | null {
    if (!isInTable()) return null
    try {
      const { $from } = editor.state.selection
      for (let d = $from.depth; d > 0; d--) {
        const n = $from.node(d)
        if (n.type.name === 'tableCell' || n.type.name === 'tableHeader') {
          const inline = n.attrs?.borders
          const migrated = n.attrs?.tableCellProperties?.borders
          const b = (inline && typeof inline === 'object' && Object.keys(inline).length) ? inline
            : (migrated && typeof migrated === 'object' && Object.keys(migrated).length) ? migrated
            : null
          if (b) {
            try { return JSON.parse(JSON.stringify(b)) } catch { return { ...b } }
          }
          return null
        }
      }
    } catch { /* fall through */ }
    return null
  }

  function tableDistributeColumns(): boolean {
    const ok = editor.commands.distributeColumnsEvenly()
    refocus()
    return ok !== false
  }

  function tableDistributeRows(): boolean {
    const ok = editor.commands.distributeRowsEvenly()
    refocus()
    return ok !== false
  }

  function tableSplit(): boolean {
    const ok = editor.commands.splitTableAtRow()
    refocus()
    return ok !== false
  }

  function tableToText(d?: string): boolean {
    const ok = editor.commands.convertTableToText(d)
    refocus()
    return ok !== false
  }

  function textToTable(d?: string): boolean {
    const ok = editor.commands.convertTextToTable(d)
    refocus()
    return ok !== false
  }

  function tableSetTextDirection(dir: string): boolean {
    const ok = editor.commands.setTextDirection(dir)
    refocus()
    return ok !== false
  }

  // Page text-column width (px) = page width − L/R margins, the cap for both AutoFit modes.
  function pageTextWidthPx(): number {
    const ps = (editor.getPageStyles && editor.getPageStyles()) || {}
    const wIn = ps?.pageSize?.width ?? 8.5
    const lIn = ps?.pageMargins?.left ?? 1
    const rIn = ps?.pageMargins?.right ?? 1
    return Math.max(40, Math.round((wIn - lIn - rIn) * 96))
  }

  // AutoFit Contents measurement: reflow the SELECTED table's DOM at `table-layout:auto`
  // (columns size to content, capped at the text width), read each column's natural width,
  // then restore. This is the in-app content-fit Word computes from text metrics; the change
  // is synchronous (no await), so the fork's TableView never re-renders mid-measure, and the
  // styles are restored before the colwidth transaction re-renders from the model.
  function measureColumnContentWidths(): number[] | undefined {
    let table: HTMLElement | null = null
    let firstRow: Element | null = null
    let cols: HTMLElement[] = []
    try {
      const $from = editor.state.selection.$from
      let tablePos = -1
      for (let d = $from.depth; d > 0; d--) {
        if ($from.node(d).type?.name === 'table') { tablePos = $from.before(d); break }
      }
      if (tablePos < 0) return undefined
      const dom: any = editor.view.nodeDOM(tablePos)
      table = dom && dom.tagName === 'TABLE' ? dom : dom?.querySelector?.('table') ?? null
      firstRow = table?.querySelector('tr') ?? null
      cols = Array.from(table?.querySelector('colgroup')?.children ?? []) as HTMLElement[]
    } catch {
      return undefined
    }
    if (!table || !firstRow) return undefined
    // Mutate the live table to content-sizing, read, and ALWAYS restore (finally) so a throw
    // mid-measure can never leave the table visually mis-sized.
    const savedLayout = table.style.tableLayout
    const savedW = table.style.width
    const savedMax = table.style.maxWidth
    const savedColW = cols.map((c) => c.style.width)
    try {
      table.style.tableLayout = 'auto'
      table.style.width = 'auto'
      // Cap at the page text column — Word's AutoFit Contents never grows the table past the page.
      table.style.maxWidth = pageTextWidthPx() + 'px'
      cols.forEach((c) => { c.style.width = 'auto' })
      // Under table-layout:auto each COLUMN is sized to its widest cell across ALL rows, so reading
      // row 0's per-cell widths yields the per-column content-fit width. getBoundingClientRect
      // forces the synchronous reflow. (Empty columns floor to 16px — Word likewise enforces a min.)
      return (Array.from(firstRow.children) as HTMLElement[]).map((cell) => Math.max(16, Math.ceil(cell.getBoundingClientRect().width)))
    } finally {
      table.style.tableLayout = savedLayout
      table.style.width = savedW
      table.style.maxWidth = savedMax
      cols.forEach((c, i) => { c.style.width = savedColW[i] })
    }
  }

  function tableAutoFit(mode: 'fixed' | 'contents' | 'window'): boolean {
    // AutoFit Window fills the table to the page text column (proportional scale); AutoFit
    // Contents shrinks each column to its measured content width. Both pass per-column geometry
    // to the fork command; 'fixed' just locks the layout.
    let targetWidthPx = 0
    let contentWidths: number[] | undefined
    if (mode === 'window') {
      targetWidthPx = pageTextWidthPx()
    } else if (mode === 'contents') {
      contentWidths = measureColumnContentWidths()
    }
    const ok = editor.commands.autoFitTable(mode, targetWidthPx, contentWidths)
    refocus()
    return ok !== false
  }

  // ---------- Spec 033 (PART A): Table Layout tab verbs (all NO-FORK) ----------

  // The table node + its document position + tableStart (1 past the opening token) for the caret.
  // Shared by the Select-scope / repeat-header / text-dir verbs below.
  function currentTableCtx(): { node: any; pos: number; tableStart: number } | null {
    try {
      const { $from } = editor.state.selection
      for (let d = $from.depth; d > 0; d--) {
        if ($from.node(d).type.name === 'table') {
          const pos = $from.before(d)
          return { node: $from.node(d), pos, tableStart: pos + 1 }
        }
      }
    } catch { /* unreadable selection */ }
    return null
  }

  // Layout → Table → Select: select the cell / row / column / whole table (Word's Select menu).
  // NO-FORK: resolve the caret cell's [row,col] via TableMap, then build a rectangular CellSelection
  // over the scope's two corner cells (anchor = top-left corner, head = bottom-right corner) and drive
  // the fork's existing setCellSelection({ anchorCell, headCell }). Selection-only (no doc change).
  function tableSelectScope(scope: 'cell' | 'column' | 'row' | 'table'): boolean {
    const ctx = currentTableCtx()
    if (!ctx) return false
    try {
      const { node, tableStart } = ctx
      const map = TableMap.get(node)
      // Caret cell position, DOC-absolute — the fork wants doc-absolute anchor/head.
      const { $from } = editor.state.selection
      let cellDocPos = -1
      for (let d = $from.depth; d > 0; d--) {
        const n = $from.node(d)
        if (n.type.name === 'tableCell' || n.type.name === 'tableHeader') { cellDocPos = $from.before(d); break }
      }
      if (cellDocPos < 0) return false
      // TableMap positions are RELATIVE to tableStart; convert the caret cell to a map-relative pos.
      const cellRel = cellDocPos - tableStart
      const rect = map.findCell(cellRel) // { left, top, right, bottom } in grid coords
      let aLeft: number, aTop: number, hRight: number, hBottom: number
      if (scope === 'cell') { aLeft = rect.left; aTop = rect.top; hRight = rect.right - 1; hBottom = rect.bottom - 1 }
      else if (scope === 'row') { aLeft = 0; aTop = rect.top; hRight = map.width - 1; hBottom = rect.bottom - 1 }
      else if (scope === 'column') { aLeft = rect.left; aTop = 0; hRight = rect.right - 1; hBottom = map.height - 1 }
      else { aLeft = 0; aTop = 0; hRight = map.width - 1; hBottom = map.height - 1 } // table
      // Corner cell relative positions → doc-absolute for setCellSelection.
      const anchorCell = tableStart + map.map[aTop * map.width + aLeft]
      const headCell = tableStart + map.map[hBottom * map.width + hRight]
      const ok = editor.commands.setCellSelection({ anchorCell, headCell })
      refocus()
      return ok !== false
    } catch { return false }
  }

  // Layout → Table → View Gridlines: toggle Word's non-printing table gridlines (a view-only CSS class
  // on the editor host — borderless cell edges show as faint dashed guides). View-only, never exported.
  function tableViewGridlines(): boolean {
    const host = document.getElementById('pm-editor')
    if (!host) return false
    return host.classList.toggle('wc-show-table-gridlines')
  }
  function tableGridlinesShown(): boolean {
    return !!document.getElementById('pm-editor')?.classList.contains('wc-show-table-gridlines')
  }

  // Layout → Alignment: Word's 9-way cell alignment (vertical vAlign, cell-level + horizontal jc on the
  // cell's paragraphs). 'left' CLEARS jc (Word's default) so Align-*-Left matches Word; center/right set it.
  // Ground truth: Align Bottom Right = vAlign bottom + jc right. NO-FORK (existing setCellAttr + setTextAlign).
  function tableSetCellAlign(v: 'top' | 'middle' | 'bottom', h: 'left' | 'center' | 'right'): boolean {
    const chain = editor.chain().setCellAttr('verticalAlign', v)
    const ok = (h === 'left' ? chain.unsetTextAlign() : chain.setTextAlign(h)).run()
    refocus()
    return ok !== false
  }

  // Layout → Data → Repeat Header Rows: mark the caret row as a header row that repeats at the top of
  // each page (<w:trPr><w:tblHeader/>). Uses dot-notation updateAttributes so ONLY the repeatHeader key
  // is merged into tableRowProperties (other row props — rowHeight, cantSplit — survive).
  function currentRowNode(): any {
    try {
      const { $from } = editor.state.selection
      for (let d = $from.depth; d > 0; d--) {
        if ($from.node(d).type.name === 'tableRow') return $from.node(d)
      }
    } catch { /* unreadable selection */ }
    return null
  }
  function tableRepeatHeaderState(): boolean {
    return currentRowNode()?.attrs?.tableRowProperties?.repeatHeader === true
  }
  function tableRepeatHeaderRows(on?: boolean): boolean {
    const row = currentRowNode()
    if (!row) return false
    const next = on === undefined ? !(row.attrs?.tableRowProperties?.repeatHeader === true) : !!on
    // Dot-notation key merges JUST repeatHeader into tableRowProperties → <w:trPr><w:tblHeader/>.
    const ok = editor.commands.updateAttributes('tableRow', { 'tableRowProperties.repeatHeader': next })
    refocus()
    return ok !== false
  }

  // Layout → Alignment → Cell Margins (Table Options): TABLE-LEVEL default cell margins → <w:tblCellMar>.
  // (The existing per-cell tableSetCellMargins stays for the cell-scope path.) m = {top,left,bottom,right}
  // in DXA (twips). The fork's tblPr encoder reads tableProperties.cellMargins as { marginTop:{value,type},
  // … } → <w:top w:w=… w:type="dxa"/>. Dot-notation writes just cellMargins onto tableProperties.
  function tableSetTableCellMargins(m: { top?: number; left?: number; bottom?: number; right?: number }): boolean {
    const dxa = (n: unknown) => ({ value: Math.max(0, Math.round(Number(n) || 0)), type: 'dxa' })
    const cellMargins = {
      marginTop: dxa(m.top), marginLeft: dxa(m.left), marginBottom: dxa(m.bottom), marginRight: dxa(m.right),
    }
    const ok = editor.commands.updateAttributes('table', { 'tableProperties.cellMargins': cellMargins })
    refocus()
    return ok !== false
  }

  // Layout → Alignment → Text Direction: cycle the caret cell's direction horizontal→tbRl→btLr→horizontal
  // (Word's 3-state button). The fork's setTextDirection accepts 'tbRl' | 'btLr' | null only. First click on
  // an un-rotated cell = tbRl (matches the tb-textdir ground truth).
  function currentCellTextDir(): string | null {
    try {
      const { $from } = editor.state.selection
      for (let d = $from.depth; d > 0; d--) {
        const n = $from.node(d)
        if (n.type.name === 'tableCell' || n.type.name === 'tableHeader') {
          return (n.attrs?.textDirection as string | null) ?? null
        }
      }
    } catch { /* unreadable selection */ }
    return null
  }
  function tableTextDirectionCycle(): boolean {
    const cur = currentCellTextDir()
    const next = cur == null ? 'tbRl' : cur === 'tbRl' ? 'btLr' : null
    const ok = editor.commands.setTextDirection(next)
    refocus()
    return ok !== false
  }

  // Layout → Data → Sort: the table's first-row cell texts (drive the Sort dialog's column dropdown —
  // PART B). Returns [{ index, label }]: header cell text when non-empty, else 'Column N'.
  function tableColumns(): Array<{ index: number; label: string }> {
    const ctx = currentTableCtx()
    if (!ctx || !ctx.node.childCount) return []
    const firstRow = ctx.node.child(0)
    const out: Array<{ index: number; label: string }> = []
    firstRow.forEach((cell: any, _off: number, i: number) => {
      const txt = (cell.textContent || '').trim()
      out.push({ index: i, label: txt || `Column ${i + 1}` })
    })
    return out
  }

  // ---------- Spec 033 (PART B): Sort + Formula (the 2 remaining NO-FORK verbs) ----------

  // The caret cell node (tableCell | tableHeader), walking $from ancestors. Shared by
  // formulaContext / tableFormulaDefault below.
  function currentCellNode(): any {
    try {
      const { $from } = editor.state.selection
      for (let d = $from.depth; d > 0; d--) {
        const name = $from.node(d).type.name
        if (name === 'tableCell' || name === 'tableHeader') return $from.node(d)
      }
    } catch { /* unreadable selection */ }
    return null
  }

  // Layout → Data → Sort: reorder the table's DATA rows by up to 3 levels (Word's Sort dialog).
  // Each level: { col (0-based), type 'text'|'number'|'date', asc }. hasHeader keeps row 0 FIXED (Word
  // pins the header row). NO-FORK: rebuild the table node with the data rows reordered (row/cell attrs
  // preserved via node.type.create), then replaceWith at the table's doc position. v1 reads child(col)
  // for the sort key — correct for non-merged tables (Word disables Sort on merged-cell tables too).
  // Lift of archive 61bf9e2 (adapted to PART A's currentTableCtx + the {asc} field name).
  function tableSort(levels: Array<{ col: number; type?: string; asc?: boolean; ascending?: boolean }>, hasHeader: boolean): boolean {
    const ctx = currentTableCtx()
    if (!ctx || !levels || !levels.length) return false
    const t = ctx.node
    const rows: any[] = []
    t.forEach((row: any) => rows.push(row))
    const header = hasHeader ? rows.slice(0, 1) : []
    const data = hasHeader ? rows.slice(1) : rows.slice()
    const keyOf = (row: any, col: number): string => {
      const cell = row.child(Math.min(col, row.childCount - 1))
      return cell ? (cell.textContent || '').trim() : ''
    }
    const ascOf = (lvl: { asc?: boolean; ascending?: boolean }): boolean =>
      lvl.asc !== undefined ? !!lvl.asc : lvl.ascending !== undefined ? !!lvl.ascending : true
    const cmpLevel = (a: any, b: any, lvl: { col: number; type?: string; asc?: boolean; ascending?: boolean }): number => {
      const ka = keyOf(a, lvl.col); const kb = keyOf(b, lvl.col)
      let r: number
      if (lvl.type === 'number') r = (parseFloat(ka) || 0) - (parseFloat(kb) || 0)
      else if (lvl.type === 'date') r = (Date.parse(ka) || 0) - (Date.parse(kb) || 0)
      else r = ka.localeCompare(kb, undefined, { numeric: true, sensitivity: 'base' })
      return ascOf(lvl) ? r : -r
    }
    data.sort((a: any, b: any) => { for (const lvl of levels) { const r = cmpLevel(a, b, lvl); if (r !== 0) return r } return 0 })
    const newTable = t.type.create(t.attrs, header.concat(data))
    editor.view.dispatch(editor.state.tr.replaceWith(ctx.pos, ctx.pos + t.nodeSize, newTable))
    refocus()
    return true
  }

  // Read the caret cell's [row,col] + the numeric values of the cells ABOVE / LEFT / BELOW / RIGHT.
  // Returns { row, col, hasAbove, hasLeft } plus the raw neighbor arrays (used by tableFormula compute).
  // NO-FORK. Lift of archive d5eb977's formulaContext (numeric read strips non-numeric chars per cell).
  function formulaContext(): {
    row: number; col: number; hasAbove: boolean; hasLeft: boolean
    above: (number | null)[]; left: (number | null)[]; below: (number | null)[]; right: (number | null)[]
  } | null {
    const ctx = currentTableCtx()
    const cell = currentCellNode()
    if (!ctx || !cell) return null
    const t = ctx.node
    const { $from } = editor.state.selection
    let cellDepth = -1
    for (let d = $from.depth; d > 0; d--) { const nm = $from.node(d).type.name; if (nm === 'tableCell' || nm === 'tableHeader') { cellDepth = d; break } }
    if (cellDepth < 2) return null
    const rowNode = $from.node(cellDepth - 1)
    let rowIdx = -1; t.forEach((r: any, _o: number, i: number) => { if (r === rowNode) rowIdx = i })
    let colIdx = -1; rowNode.forEach((c: any, _o: number, i: number) => { if (c === cell) colIdx = i })
    const numOf = (c: any): number | null => { if (!c) return null; const v = parseFloat(String(c.textContent || '').replace(/[^0-9.\-]/g, '')); return isNaN(v) ? null : v }
    const above: (number | null)[] = []; for (let r = 0; r < rowIdx; r++) { const row = t.child(r); above.push(numOf(row.child(Math.min(colIdx, row.childCount - 1)))) }
    const below: (number | null)[] = []; for (let r = rowIdx + 1; r < t.childCount; r++) { const row = t.child(r); below.push(numOf(row.child(Math.min(colIdx, row.childCount - 1)))) }
    const left: (number | null)[] = []; for (let c = 0; c < colIdx; c++) left.push(numOf(rowNode.child(c)))
    const right: (number | null)[] = []; for (let c = colIdx + 1; c < rowNode.childCount; c++) right.push(numOf(rowNode.child(c)))
    return { row: rowIdx, col: colIdx, hasAbove: above.some((v) => v !== null), hasLeft: left.some((v) => v !== null), above, left, below, right }
  }

  // Layout → Data → Formula: the default formula Word proposes for the caret cell (=SUM(ABOVE) when
  // there are numbers above, else =SUM(LEFT), else =SUM(ABOVE)). Seeds the dialog's Formula field.
  function tableFormulaDefault(): string {
    const ctx = formulaContext()
    if (!ctx) return '=SUM(ABOVE)'
    if (ctx.hasAbove) return '=SUM(ABOVE)'
    if (ctx.hasLeft) return '=SUM(LEFT)'
    return '=SUM(ABOVE)'
  }

  // Layout → Data → Formula: parse =FN(DIR) (FN ∈ SUM/AVERAGE/COUNT/PRODUCT/MAX/MIN, DIR ∈
  // ABOVE/LEFT/BELOW/RIGHT), read the numeric neighbor cells, compute, format (0 / 0.00 / 0% / $#,##0.00),
  // and INSERT the computed VALUE as text at the caret. v1 inserts the value (Word-visible) — NOT a live
  // <w:fldSimple w:instr> formula field (documented deviation; a real-Word formula field still round-trips
  // via import preservation). Lift of archive d5eb977.
  function tableFormula(formula: string, numFormat?: string): boolean {
    const ctx = formulaContext()
    if (!ctx) return false
    const m = /=\s*(SUM|AVERAGE|COUNT|PRODUCT|MAX|MIN)\s*\(\s*(ABOVE|LEFT|BELOW|RIGHT)\s*\)/i.exec(formula || '')
    const fn = (m ? m[1] : 'SUM').toUpperCase()
    const dir = (m ? m[2] : 'ABOVE').toUpperCase()
    const src = dir === 'ABOVE' ? ctx.above : dir === 'BELOW' ? ctx.below : dir === 'LEFT' ? ctx.left : ctx.right
    const nums = src.filter((v): v is number => v !== null)
    let result = 0
    if (fn === 'SUM') result = nums.reduce((a, b) => a + b, 0)
    else if (fn === 'AVERAGE') result = nums.length ? nums.reduce((a, b) => a + b, 0) / nums.length : 0
    else if (fn === 'COUNT') result = nums.length
    else if (fn === 'PRODUCT') result = nums.reduce((a, b) => a * b, 1)
    else if (fn === 'MAX') result = nums.length ? Math.max(...nums) : 0
    else if (fn === 'MIN') result = nums.length ? Math.min(...nums) : 0
    let text: string
    if (numFormat === '0') text = String(Math.round(result))
    else if (numFormat && /0\.00/.test(numFormat)) text = result.toFixed(2)
    else if (numFormat && /%/.test(numFormat)) text = Math.round(result * 100) + '%'
    else if (numFormat && /\$/.test(numFormat)) text = '$' + result.toFixed(2)
    else text = Number.isInteger(result) ? String(result) : String(Math.round(result * 100) / 100)
    editor.commands.insertContent(text)
    refocus()
    return true
  }

  // ---------- Spec 034: Insert-grid hover live preview (mirrors table-styles.ts) ----------
  // Paint-only preview of a pending rows×cols table at the caret: snapshot the WHOLE editor state
  // (incl. the history plugin), run the insert, and restore via editor.setState(snap) on leave/pick —
  // rolling BOTH the document and the undo stack back, so the preview never lands in undo or the saved
  // file. Restore MUST go through editor.setState (see table-styles.ts header — a raw view.updateState
  // leaves a mismatched-transaction trap).
  let previewSnap: { state: any; documentModified: any; documentGuid: any } | null = null

  function restoreInsertPreview() {
    if (!previewSnap) return
    editor.setState(previewSnap.state)
    if (editor.converter) {
      editor.converter.documentModified = previewSnap.documentModified
      editor.converter.documentGuid = previewSnap.documentGuid
    }
    previewSnap = null
    // Trailing no-op dispatch fires 'transaction' so state-sync re-reads the restored state.
    editor.view?.dispatch(editor.view.state.tr.setMeta(INSERT_PREVIEW_META, true))
  }

  function insertTablePreviewEnter(rows: number, cols: number): boolean {
    // Hop contract: always restore a live preview first (covers a missed leave), THEN paint the new size.
    restoreInsertPreview()
    const view = editor.view
    if (!view) return false
    const r = Math.max(1, Math.min(1000, Math.floor(rows)))
    const c = Math.max(1, Math.min(1000, Math.floor(cols)))
    // SNAPSHOT BEFORE the insert. The whole EditorState is captured (incl. the history plugin state),
    // so editor.setState(snap.state) on leave/pick rolls the DOCUMENT *and* the undo stack back — the
    // preview insert (even though it dispatches with history) leaves ZERO trace after restore. This is
    // the same net contract as table-styles.ts, without needing a startTr the fork Editor won't forward
    // (editor.chain() takes no args — fork is read-only). The keydown/beforeinput cancel-listeners below
    // still WIN over a real edit mid-preview, so the transient history is never observable to the user.
    previewSnap = {
      state: editor.state,
      documentModified: editor.converter?.documentModified,
      documentGuid: editor.converter?.documentGuid,
    }
    try {
      const before = editor.state.doc
      const ok = editor.commands.insertTable({ rows: r, cols: c, withHeaderRow: false })
      if (ok === false || editor.state.doc === before) { restoreInsertPreview(); return false }
      return true
    } catch {
      restoreInsertPreview()
      return false
    }
  }

  function insertTablePreviewLeave() {
    restoreInsertPreview()
  }

  // Real input mid-preview must WIN (same rationale as table-styles.ts): a keystroke landing on top of
  // the insert preview cancels it BEFORE the input applies, so the leave-restore never discards a real
  // edit. Capture phase = ahead of PM's handlers. Listeners die with the view on replaceEditor.
  editor.view?.dom?.addEventListener('keydown', () => { if (previewSnap) restoreInsertPreview() }, true)
  editor.view?.dom?.addEventListener('beforeinput', () => { if (previewSnap) restoreInsertPreview() }, true)

  // Test helper (Task 9 / Critique B3): build a CellSelection over the first two
  // @internal — test helper (CellSelection over the first row pair); not a stable public API
  // cells of the table's first row. Used by the [6b] merge test in test-suite-pm.js.
  // Calls the fork's setCellSelection({ anchorCell, headCell }) command with the
  // absolute positions of cells [0] and [1] in the first row.
  function tableSelectFirstRowPair(): boolean {
    try {
      const { selection, doc } = editor.state
      // Walk $from ancestors to find the table node.
      const { $from } = selection
      let tablePos = -1
      let tableNode: any = null
      for (let d = $from.depth; d > 0; d--) {
        if ($from.node(d).type.name === 'table') {
          tableNode = $from.node(d)
          tablePos = $from.before(d)
          break
        }
      }
      if (!tableNode || tablePos < 0) return false

      // tableStart is 1 past the table's opening token.
      const tableStart = tablePos + 1
      // First row is the first child of the table.
      const firstRow = tableNode.child(0)
      if (!firstRow || firstRow.childCount < 2) return false

      // Cell positions are relative to tableStart (prosemirror-tables convention).
      // cell[0] offset = 0 (right after row open token).
      // cell[1] offset = cell[0].nodeSize.
      const cell0RelPos = 1 // row open token = 1 offset inside tableStart
      const cell1RelPos = cell0RelPos + firstRow.child(0).nodeSize

      // Absolute positions inside the document (setCellSelection wants doc-absolute).
      const anchorCell = tableStart + cell0RelPos
      const headCell = tableStart + cell1RelPos

      const ok = editor.commands.setCellSelection({ anchorCell, headCell })
      refocus()
      return ok !== false
    } catch {
      return false
    }
  }

  // T4: honest dynamic Table Styles gallery. Lists the w:type="table" styles from
  // the RUNTIME catalog (converter.convertedXml['word/styles.xml'] — the same
  // in-memory part the exporter serializes back out, so every id offered here is
  // guaranteed to have a real definition in the saved file; the minted defaults
  // land there via addDefaultStylesIfMissing at parse time). Display name = the
  // definition's w:name w:val (e.g. 'Grid Table 4 Accent 1' — real Word writes no
  // dash); apply uses the id. semiHidden styles (TableNormal) are excluded, like
  // Word's gallery.
  // Spec 030: return the UNION of the doc's styles.xml table styles (existing logic) and the
  // generated catalog (TABLE_STYLE_DEFS) — so the gallery lists all 113 real-Word styles even
  // before any is materialized. Keeps the existing array-of-{id,name} shape (H.tblStyles keeps
  // working) and ADDS a `section` field when known (additive, non-breaking). Id-deduped: a
  // doc-owned def wins (its display name from styles.xml, section derived from the catalog if the
  // id is a catalog id).
  function getTableStyles(): Array<{ id: string; name: string; section?: 'plain' | 'grid' | 'list' }> {
    const out: Array<{ id: string; name: string; section?: 'plain' | 'grid' | 'list' }> = []
    const seen = new Set<string>()
    try {
      const styles = editor.converter?.convertedXml?.['word/styles.xml']
      const els: any[] = styles?.elements?.[0]?.elements || []
      for (const el of els) {
        if (
          el.name === 'w:style' &&
          el.attributes?.['w:type'] === 'table' &&
          el.attributes?.['w:styleId'] &&
          !(el.elements || []).some((c: any) => c.name === 'w:semiHidden')
        ) {
          const id = el.attributes['w:styleId'] as string
          if (seen.has(id)) continue
          seen.add(id)
          out.push({
            id,
            name: ((el.elements || []).find((c: any) => c.name === 'w:name')?.attributes?.['w:val'] as string) || id,
            ...(TABLE_STYLE_DEFS[id] ? { section: TABLE_STYLE_DEFS[id].section } : {}),
          })
        }
      }
    } catch { /* fall through — still add the catalog below */ }
    // Add every catalog style not already present on the doc (its catalog display name + section).
    for (const id of Object.keys(TABLE_STYLE_DEFS)) {
      if (seen.has(id)) continue
      seen.add(id)
      out.push({ id, name: TABLE_STYLE_DEFS[id].name, section: TABLE_STYLE_DEFS[id].section })
    }
    return out
  }

  // Returns { inTable, rows, cols, styleId, alignment } for Table Tools tab state.
  // Falls back to { inTable: false } when not in a table (safe for pre-mount stubs).
  function tableInfo(): { inTable: boolean; rows?: number; cols?: number; styleId?: string | null; alignment?: string | null } {
    if (!isInTable()) return { inTable: false }
    try {
      const { $from } = editor.state.selection
      for (let d = $from.depth; d > 0; d--) {
        if ($from.node(d).type.name === 'table') {
          const node = $from.node(d)
          const rows: number = node.childCount
          // cols = number of cells in first row (header or body).
          const cols: number = rows > 0 ? node.child(0).childCount : 0
          const styleId: string | null = node.attrs?.tableStyleId ?? null
          // Fork stores alignment as 'justification' attr (or inside tableProperties).
          const alignment: string | null =
            node.attrs?.justification ??
            node.attrs?.tableProperties?.justification ??
            null
          return { inTable: true, rows, cols, styleId, alignment }
        }
      }
    } catch { /* fall through */ }
    return { inTable: false }
  }

  return {
    insertTable,
    tableAddRow,
    tableAddColumn,
    tableDeleteRow,
    tableDeleteColumn,
    tableDeleteTable,
    tableMerge,
    tableSplitCell,
    tableToggleHeaderRow,
    tableToggleHeaderColumn,
    tableSetCellShading,
    tableSetCellVAlign,
    isInTable,
    tableInfo,
    // 6b: net-new Table Tools verbs
    tableSetStyle,
    getTableStyles,
    tableSetAlignment,
    tableSetIndent,
    tableSetCellWidth,
    tableSetRowHeight,
    tableSetCellMargins,
    tableGetCellMargins,
    tableSetCellBorders,
    tableGetCellBorders,
    tableDistributeColumns,
    tableDistributeRows,
    tableSplit,
    tableToText,
    textToTable,
    tableSetTextDirection,
    tableAutoFit,
    tableSelectFirstRowPair,
    // 034: insert-grid hover live preview (paint-only; snapshot/restore)
    insertTablePreviewEnter,
    insertTablePreviewLeave,
    // 033 (PART A): Table Layout tab verbs (all NO-FORK)
    tableSelectScope,
    tableViewGridlines,
    tableGridlinesShown,
    tableSetCellAlign,
    tableRepeatHeaderRows,
    tableRepeatHeaderState,
    tableSetTableCellMargins,
    tableTextDirectionCycle,
    tableColumns,
    // 033 (PART B): Sort + Formula (the 2 remaining NO-FORK verbs)
    tableSort,
    tableFormula,
    tableFormulaDefault,
    formulaContext,
  }
}
