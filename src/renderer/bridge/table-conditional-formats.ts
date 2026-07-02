// Spec 031 — Table Style Options + tblLook/cnfStyle writer.
//
// A single bridge-side writer derives Word's conditional-format markers from the table's
// `tableProperties.tblLook` (the single source of truth: 6 boolean flags) plus its geometry:
//   - `tblLook.val` — the 4-hex-UPPER bitmask (bridge-computed; the fork's `w:val` handler passes
//     it through unchanged — NO fork edit, research-verified).
//   - per-row `trPr.cnfStyle` + per-cell `tcPr.cnfStyle` — 12-boolean-flag objects + a 12-char
//     `val` string, stamped ONLY where a conditional role exists, the key REMOVED elsewhere.
//
// The stamping rules and the 12-position val order were derived EMPIRICALLY from the rw fixtures
// (parity/fixtures/rw-tb-style-grid4a1.docx + the 6 rw-tb-styleopt-*.docx) — each observed w:cnfStyle
// carries all 12 named attributes with 0/1, so matching "which named attr is 1" against each val
// string gave the val-position↔attr-name mapping directly. VERIFIED against all 7 fixtures (row +
// cell placement) by scripts/ replay; see the mapping table in the 12-position VAL_ORDER below.
//
// tr-building follows bridge/table-styles.ts applyTableStyleToTr (the fork setTableStyle position-walk:
// tableStart = table.pos + 1; rowPos/cellPos accumulate nodeSize). One tr → one undo step.

// DEFAULT_TBL_LOOK from the fork's style-engine — the seed when a table carries no tblLook yet
// (firstRow/firstColumn on, banded rows on i.e. noHBand=false, noVBand=true → val '04A0'). Read-only.
// @ts-ignore - vendored fork TS helper (aliased)
import { DEFAULT_TBL_LOOK } from '@superdoc/style-engine/ooxml'

type AnyEditor = any

// tblLook flag → bitmask bit (FR-001; verified against 4 rw fixtures).
const TBL_LOOK_BITS: Record<string, number> = {
  firstRow: 0x20,
  lastRow: 0x40,
  firstColumn: 0x80,
  lastColumn: 0x100,
  noHBand: 0x200,
  noVBand: 0x400,
}

// The 12-char `w:val` bit order for w:cnfStyle, derived empirically from the rw fixtures (see header).
// Position 0..11 ↔ the named boolean attr the translator emits (cnfStyle-translator.js keys). Only the
// six starred roles are ever set to 1 by Word's measured patterns; the rest are always 0 (Assumptions §).
const VAL_ORDER = [
  'firstRow', // 0 *
  'lastRow', // 1 *
  'firstColumn', // 2 *
  'lastColumn', // 3 *
  'oddVBand', // 4 * (band1Vert)
  'evenVBand', // 5   (band2Vert — never stamped)
  'oddHBand', // 6 * (band1Horz)
  'evenHBand', // 7   (band2Horz — never stamped)
  'firstRowFirstColumn', // 8  (nw corner — never stamped)
  'firstRowLastColumn', // 9  (ne corner — never stamped)
  'lastRowFirstColumn', // 10 (sw corner — never stamped)
  'lastRowLastColumn', // 11 (se corner — never stamped)
] as const

type Role = (typeof VAL_ORDER)[number]

// The 6 checkbox → tblLook-flag mapping (archive-verified). bandedRows/bandedColumns are INVERTED
// (checkbox ON ⇔ banding on ⇔ the noHBand/noVBand flag OFF).
type Option = 'headerRow' | 'totalRow' | 'bandedRows' | 'firstColumn' | 'lastColumn' | 'bandedColumns'

// Build the { firstRow, lastRow, firstColumn, lastColumn, noHBand, noVBand } flags object, seeding
// absent tables from DEFAULT_TBL_LOOK (a fresh object copy — never mutate the shared const).
function seedFlags(tblLook: any): Record<string, boolean> {
  const src = tblLook && typeof tblLook === 'object' ? tblLook : DEFAULT_TBL_LOOK
  return {
    firstRow: !!src.firstRow,
    lastRow: !!src.lastRow,
    firstColumn: !!src.firstColumn,
    lastColumn: !!src.lastColumn,
    noHBand: !!src.noHBand,
    noVBand: !!src.noVBand,
  }
}

// val = OR of the set bits, formatted as a 4-hex-UPPER string (leading-zero padded, e.g. '04A0').
function computeTblLookVal(flags: Record<string, boolean>): string {
  let v = 0
  for (const k of Object.keys(TBL_LOOK_BITS)) if (flags[k]) v |= TBL_LOOK_BITS[k]
  return v.toString(16).toUpperCase().padStart(4, '0')
}

// A full { flags..., val } tblLook object ready to write onto tableProperties.
function makeTblLook(flags: Record<string, boolean>): any {
  return { ...flags, val: computeTblLookVal(flags) }
}

// --- cnfStyle role computation (all fixture-verified; see the replay in scripts/) ---

// Row-level role for row r of R (trPr cnfStyle), or null (no element).
function rowRole(r: number, R: number, f: Record<string, boolean>): Role | null {
  if (f.firstRow && r === 0) return 'firstRow'
  if (f.lastRow && r === R - 1) return 'lastRow'
  if (!f.noHBand) {
    const firstBanded = f.firstRow ? 1 : 0
    const lastBanded = f.lastRow ? R - 2 : R - 1
    if (r >= firstBanded && r <= lastBanded && (r - firstBanded) % 2 === 0) return 'oddHBand'
  }
  return null
}

// Does the table have ANY column-level role? When it doesn't, Word emits NO cell cnfStyle at all
// (fixture rw-tb-styleopt-firstcol-off: firstColumn/lastColumn off + noVBand → cells carry nothing,
// even though the rows carry firstRow/oddHBand).
function hasColumnRoles(f: Record<string, boolean>): boolean {
  return !!(f.firstColumn || f.lastColumn || !f.noVBand)
}

// Cell-level role for cell (r, c) in an R×C grid (tcPr cnfStyle):
//   - null  → NO cnfStyle element (only when the table has no column roles at all)
//   - 'EMPTY' → an all-zeros element (present, all 12 flags 0) — Word emits this on cells with no role
//     once ANY column role exists in the table.
//   - a Role → the single set role.
function cellRole(r: number, c: number, R: number, C: number, f: Record<string, boolean>): Role | 'EMPTY' | null {
  if (!hasColumnRoles(f)) return null
  if (f.firstColumn && c === 0) return 'firstColumn'
  if (f.lastColumn && c === C - 1) return 'lastColumn'
  if (!f.noVBand) {
    const firstVBand = f.firstColumn ? 1 : 0
    const lastVBand = f.lastColumn ? C - 2 : C - 1
    if (c >= firstVBand && c <= lastVBand && (c - firstVBand) % 2 === 0) return 'oddVBand'
  }
  // Non-column cell → inherit the row role (firstRow/lastRow/oddHBand); else an explicit all-zeros element.
  return rowRole(r, R, f) ?? 'EMPTY'
}

// Build the 12-key cnfStyle object (all keys explicit booleans so the translator's booleanToString(false)
// emits explicit "0" attrs — verified: cnfStyle-translator decode maps false→"0", true→"1") + the 12-char
// `val` string. `role` = 'EMPTY' → all-zero object; a Role → that one bit set.
function makeCnfStyle(role: Role | 'EMPTY'): any {
  const obj: any = {}
  let val = ''
  for (const key of VAL_ORDER) {
    const on = role !== 'EMPTY' && key === role
    obj[key] = on
    val += on ? '1' : '0'
  }
  obj.val = val
  return obj
}

export function installTableConditionalFormats(editor: AnyEditor) {
  // Walk the caret's ancestors for the table node + its doc position (same resolver as table-styles.ts).
  function caretTable(state: any): { node: any; pos: number } | null {
    try {
      const { $from } = state.selection
      for (let d = $from.depth; d > 0; d--) {
        if ($from.node(d).type.name === 'table') return { node: $from.node(d), pos: $from.before(d) }
      }
    } catch {
      /* selection the resolver can't read */
    }
    return null
  }

  // A table carries conditional formats when its style's translated entry declares tblStylePr conditional
  // bands. The v3 style-translator encodes those under `tableStyleProperties` (keyed by band `type`, e.g.
  // firstRow / band1Horz) — see style-translator.js encodePropertiesByKey('w:tblStylePr',
  // 'tableStyleProperties', …). Any non-empty tableStyleProperties ⇒ conditional formats.
  // TableGrid / no style / a style without bands → false (strip all stamps).
  function styleHasConditionalFormats(styleId: string | null | undefined): boolean {
    if (!styleId) return false
    try {
      const entry = editor.converter?.translatedLinkedStyles?.styles?.[styleId]
      if (!entry) return false
      const bands = entry.tableStyleProperties
      if (Array.isArray(bands)) return bands.length > 0
      if (bands && typeof bands === 'object') return Object.keys(bands).length > 0
      return false
    } catch {
      return false
    }
  }

  // Set (or delete) a row's / cell's cnfStyle on the given tr via setNodeMarkup. `role`:
  //   null  → remove the cnfStyle key (Word emits no element)
  //   Role|'EMPTY' → write the computed cnfStyle object as the FIRST key of the props object (trPr has
  //     no xmlOrder — key-insertion order wins; tcPr enforces cnfStyle-first via TCPR_XML_ORDER anyway).
  function stampNode(tr: any, pos: number, node: any, propsAttrKey: string, role: Role | 'EMPTY' | null): void {
    const curProps = node.attrs[propsAttrKey] || {}
    const hadCnf = curProps.cnfStyle != null
    if (role == null) {
      if (!hadCnf) return // nothing to strip
      const nextProps = { ...curProps }
      delete nextProps.cnfStyle
      tr.setNodeMarkup(pos, undefined, { ...node.attrs, [propsAttrKey]: nextProps })
      return
    }
    const cnf = makeCnfStyle(role)
    // cnfStyle FIRST (spread the object with cnfStyle as the leading key), then the rest of the props.
    const rest = { ...curProps }
    delete rest.cnfStyle
    const nextProps = { cnfStyle: cnf, ...rest }
    tr.setNodeMarkup(pos, undefined, { ...node.attrs, [propsAttrKey]: nextProps })
  }

  // Single source of truth for the walk: stamp `table`'s tblLook + every row/cell cnfStyle onto `tr`,
  // deriving roles from `flags` (the resolved tblLook flags). `styled` gates conditional-format stamping
  // (unstyled → strip all cnfStyle; tblLook is written regardless — Word always emits it). The tblLook
  // node markup is written only when it actually changes (no gratuitous doc change / re-stamp on open).
  function stampTableOnTr(tr: any, table: { node: any; pos: number }, flags: Record<string, boolean>, styled: boolean): void {
    const props = table.node.attrs.tableProperties || {}
    const nextTblLook = makeTblLook(flags)
    const curTblLook = props.tblLook
    const tblLookChanged =
      !curTblLook ||
      curTblLook.val !== nextTblLook.val ||
      Object.keys(TBL_LOOK_BITS).some((k) => !!curTblLook[k] !== !!nextTblLook[k])
    if (tblLookChanged) {
      tr.setNodeMarkup(table.pos, undefined, { ...table.node.attrs, tableProperties: { ...props, tblLook: nextTblLook } })
    }
    const R = table.node.childCount
    // Walk rows/cells computing absolute positions (identical to the fork setTableStyle walk).
    let rowPos = table.pos + 1
    for (let r = 0; r < R; r++) {
      const row = table.node.child(r)
      const C = row.childCount
      stampNode(tr, rowPos, row, 'tableRowProperties', styled ? rowRole(r, R, flags) : null)
      let cellPos = rowPos + 1
      for (let c = 0; c < C; c++) {
        const cell = row.child(c)
        stampNode(tr, cellPos, cell, 'tableCellProperties', styled ? cellRole(r, c, R, C, flags) : null)
        cellPos += cell.nodeSize
      }
      rowPos += row.nodeSize
    }
  }

  // Re-derive every row/cell stamp for the caret's table on `tr` (or a fresh tr). Returns true when a
  // mutating tr was produced/dispatched. No-ops cleanly when the caret isn't in a table; STRIPS stale
  // stamps (writes tblLook val but removes all cnfStyle) when the table is unstyled.
  //
  // When `tr` is passed the caller owns dispatch (one-undo-step composition). When omitted we
  // build+dispatch our own tr. The bridge structural verbs call this AFTER their command committed, so
  // reading flags off editor.state's caret table is correct.
  function restampTableConditionalFormats(ed: AnyEditor = editor, tr?: any): boolean {
    const view = ed?.view
    const state = ed?.state
    if (!view || !state) return false
    const table = caretTable(state)
    if (!table) return false

    const ownTr = !tr
    const t = tr || state.tr
    const props = table.node.attrs.tableProperties || {}
    const styleId: string | null = table.node.attrs.tableStyleId ?? props.tableStyleId ?? null
    stampTableOnTr(t, table, seedFlags(props.tblLook), styleHasConditionalFormats(styleId))

    if (ownTr) {
      // Only dispatch when something actually changed (docChanged drives the dirty flag + repaint).
      if (t.docChanged) view.dispatch(t)
      return t.docChanged
    }
    return true
  }

  // Flip a Table Style Options checkbox (option, on) and re-derive stamps in ONE tr (one undo step):
  // the tr sets the tblLook flag change on the table node AND every row/cell stamp, then dispatches once.
  function tableStyleOption(option: Option, on: boolean): boolean {
    const view = editor.view
    const state = editor.state
    if (!view || !state) return false
    const table = caretTable(state)
    if (!table) return false

    const props = table.node.attrs.tableProperties || {}
    const flags = seedFlags(props.tblLook)
    // Map the checkbox to its tblLook flag (bandedRows/bandedColumns invert to noHBand/noVBand).
    switch (option) {
      case 'headerRow': flags.firstRow = on; break
      case 'totalRow': flags.lastRow = on; break
      case 'bandedRows': flags.noHBand = !on; break
      case 'firstColumn': flags.firstColumn = on; break
      case 'lastColumn': flags.lastColumn = on; break
      case 'bandedColumns': flags.noVBand = !on; break
      default: return false
    }

    // ONE tr → ONE undo step: stampTableOnTr writes the new tblLook (from the flipped flags) AND all
    // row/cell stamps together, derived from the SAME flags object. It reads the pre-tr `table.node`
    // attrs for positions/props (positions are stable — no doc mutation before this) and computes roles
    // from `flags`, so the new-flag stamping is correct even though editor.state hasn't advanced yet.
    const tr = state.tr
    const styleId: string | null = table.node.attrs.tableStyleId ?? props.tableStyleId ?? null
    stampTableOnTr(tr, table, flags, styleHasConditionalFormats(styleId))
    if (tr.docChanged) view.dispatch(tr)
    editor.view?.focus()
    return true
  }

  // The 6 checkbox states from the caret table's tblLook (banding flags inverted). Defaults (no table /
  // no tblLook) mirror Word's fresh-styled-table defaults (headerRow + firstColumn + bandedRows on).
  function tableStyleOptionState(): {
    headerRow: boolean
    totalRow: boolean
    bandedRows: boolean
    firstColumn: boolean
    lastColumn: boolean
    bandedColumns: boolean
  } {
    const table = caretTable(editor.state)
    const props = table?.node?.attrs?.tableProperties || {}
    const f = seedFlags(props.tblLook)
    return {
      headerRow: !!f.firstRow,
      totalRow: !!f.lastRow,
      bandedRows: !f.noHBand,
      firstColumn: !!f.firstColumn,
      lastColumn: !!f.lastColumn,
      bandedColumns: !f.noVBand,
    }
  }

  return { restampTableConditionalFormats, tableStyleOption, tableStyleOptionState }
}
