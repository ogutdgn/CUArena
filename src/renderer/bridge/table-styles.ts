// Spec 030 (CATALOG) — the lazy table-style materializer + hover live-preview.
//
// TWO jobs, mirroring bridge/style-preview.ts (READ IT — this file copies its snapshot/
// restore mechanics, hop contract, and input-cancel listeners verbatim in spirit):
//
//  1. ensureTableStyleMaterialized(id): the 113 real-Word modern table-style defs
//     (TABLE_STYLE_DEFS, generated from the locked-build oracle) are NOT shipped in every
//     blank doc — Word registers them lazily too. When a style is first applied/previewed we
//     splice its verbatim <w:style> into the in-memory word/styles.xml AND register the fork's
//     translated entry so BOTH consumers work: the exporter (serializes styles.xml → Word keeps
//     the <w:tblStyle> ref, exporter-docx-defs.js:905-908 drops orphans) and the in-app painter
//     (resolveTableStyleVisuals reads converter.translatedLinkedStyles.styles[id]).
//     The existsOnDoc guard mirrors addDefaultStylesIfMissing (docxImporter.js:770-776):
//     a def already on the doc WINS (import precedence — the document's own def is never clobbered).
//
//  2. tableStylePreviewEnter/Leave: hover live-preview, EXACTLY the style-preview.ts pattern.
//     Snapshot editor.state + converter dirty flags, materialize the style (see the note below),
//     build tr with tr.setMeta('addToHistory', false), REPLICATE setTableStyle's tr mutations
//     (fork table.js:1617-1685), dispatch. Restore via editor.setState(snap) — NEVER
//     view.updateState (the mismatched-transaction trap documented in style-preview.ts:4-9).
//
// TRAP (from style-preview.ts): the restore MUST go through editor.setState (Editor writes
// _state AND the view; a raw view.updateState restores only the VIEW and the next dispatch
// throws RangeError('Applying a mismatched transaction')). We never route the preview through
// editor.commands.* — that dispatches its own tr WITH history. We build the tr ourselves and
// replicate the command's mutations so tr.setMeta('addToHistory', false) survives.

import { TABLE_STYLE_DEFS } from '@/core/generated/table-style-defs'
import { STYLE_NAME_TO_ID, STYLE_ID_TO_NAME } from './style-names'
// Fork PUBLIC parse path — the same xml2json wrapper the importer itself feeds styles.xml through
// (SuperConverter.parseXmlToJson / docxHelper.parseXmlToJson). Read-only usage.
// @ts-ignore - vendored fork JS helper (no ambient types)
import { parseXmlToJson } from '@converter/v2/docxHelper.js'
// Fork PUBLIC translator — re-translate the (now spliced) styles.xml so translatedLinkedStyles.styles[id]
// has the EXACT native shape resolveTableProperties/resolveTableCellProperties consume (no hand-rolled
// approximation). This is the same call the importer runs at open (docxImporter.js:265). Read-only.
// @ts-ignore - vendored fork JS helper (no ambient types)
import { translateStyleDefinitions } from '@converter/v2/importer/docxImporter.js'
// Fork PUBLIC resolver + border projector — replicate setTableStyle's bake for the preview tr.
// Read-only imports (the exact primitives the fork command uses).
// @ts-ignore - vendored fork JS helper (no ambient types)
import { resolveTableStyleVisuals } from '@extensions/table/tableHelpers/resolveTableStyleVisuals.js'
// @ts-ignore - vendored fork JS helper (no ambient types)
import { _processTableBorders } from '@converter/v3/handlers/w/tbl/tbl-translator.js'

type AnyEditor = any

export const TABLE_STYLE_PREVIEW_META = 'wcTableStylePreview'

export function installTableStyles(editor: AnyEditor) {
  // ---- Materialization ---------------------------------------------------------------

  // Read the live word/styles.xml element list (converter.convertedXml is the in-memory tree
  // the exporter serializes back out; elements[0] is the <w:styles> root).
  function stylesElements(): any[] | null {
    const styles = editor.converter?.convertedXml?.['word/styles.xml']
    const list = styles?.elements?.[0]?.elements
    return Array.isArray(list) ? list : null
  }

  function existsOnDoc(id: string): boolean {
    const list = stylesElements()
    if (!list) return false
    return list.some((el: any) => el?.attributes?.['w:styleId'] === id)
  }

  /**
   * Lazily register a catalog table style so BOTH the exporter and the in-app painter see it.
   * Returns false when the id is unknown to the catalog; true when the def is present on the
   * doc afterward (either already there — import precedence — or freshly spliced).
   */
  function ensureTableStyleMaterialized(id: string): boolean {
    if (!id || !TABLE_STYLE_DEFS[id]) return false
    // existsOnDoc guard: the doc's own def wins (mirrors addDefaultStylesIfMissing). Already
    // present → nothing to do; the entry is authoritative and translatedLinkedStyles already
    // carries it (it was translated at import).
    if (existsOnDoc(id)) return true

    const list = stylesElements()
    if (!list) return false

    const def = TABLE_STYLE_DEFS[id]
    // Parse the verbatim <w:style> XML into the fork's xml-js element shape via the SAME public
    // parser the importer uses. parseXmlToJson wraps a fragment in a root doc: elements[0] is
    // our <w:style>.
    let styleEl: any = null
    try {
      const parsed = parseXmlToJson(def.xml)
      styleEl = parsed?.elements?.find((el: any) => el?.name === 'w:style') || parsed?.elements?.[0] || null
    } catch {
      return false
    }
    if (!styleEl || styleEl.name !== 'w:style') return false

    // Splice the parsed element into the live styles.xml (mutates the in-memory catalog the
    // exporter serializes — exactly what addDefaultStylesIfMissing does at import, minus the
    // carbonCopy since we WANT the live doc mutated here, lazily, on first use).
    list.push(styleEl)

    // Re-translate the whole (now-spliced) styles.xml so translatedLinkedStyles.styles[id] has
    // the native shape resolveTableStyleVisuals depends on. translateStyleDefinitions reads
    // convertedXml['word/styles.xml'] → wStylesTranslator.encode → { docDefaults, latentStyles,
    // styles }. Merge just the new entry (keep any doc-authored entries + docDefaults intact).
    try {
      const translated = translateStyleDefinitions(editor.converter.convertedXml)
      const conv = editor.converter
      if (!conv.translatedLinkedStyles) conv.translatedLinkedStyles = { docDefaults: {}, latentStyles: {}, styles: {} }
      if (!conv.translatedLinkedStyles.styles) conv.translatedLinkedStyles.styles = {}
      if (translated?.styles?.[id]) conv.translatedLinkedStyles.styles[id] = translated.styles[id]
    } catch {
      // A translation failure leaves the splice in place (the exporter still works; only the
      // in-app paint is degraded until reopen). Non-fatal — never break the apply.
    }

    // Register the display-name ↔ id mapping for the styles UI vocabulary.
    if (def.name && !STYLE_NAME_TO_ID[def.name]) STYLE_NAME_TO_ID[def.name] = id
    if (!STYLE_ID_TO_NAME[id]) STYLE_ID_TO_NAME[id] = def.name

    return true
  }

  /**
   * The full catalog for the gallery: id, display name, section, and whether it is already
   * materialized on THIS document (materialized = present in styles.xml).
   */
  function listCatalogStyles(): Array<{ id: string; name: string; section: 'plain' | 'grid' | 'list'; materialized: boolean }> {
    return Object.keys(TABLE_STYLE_DEFS).map((id) => {
      const def = TABLE_STYLE_DEFS[id]
      return { id, name: def.name, section: def.section, materialized: existsOnDoc(id) }
    })
  }

  // ---- Live preview (mirrors bridge/style-preview.ts) ---------------------------------

  // Snapshot = the authoritative editor state PLUS the converter metadata the docChanged path
  // mutates (documentModified/documentGuid live on the converter, OUTSIDE EditorState — Editor.ts
  // ~3205 — so setState alone can't revert them). activeStyleId drives the hop contract.
  let snap: { state: any; documentModified: any; documentGuid: any; activeStyleId: string | null } | null = null

  function restore() {
    if (!snap) return
    editor.setState(snap.state) // restores _state AND the view (see header note)
    if (editor.converter) {
      editor.converter.documentModified = snap.documentModified
      editor.converter.documentGuid = snap.documentGuid
    }
    snap = null
    // setState emits NOTHING (documented) — this trailing no-op dispatch fires the 'transaction'
    // event that schedules state-sync's rAF tick so the ribbon/tab re-reads the restored state.
    // docChanged=false → dirty untouched; applies cleanly (prevState === snap.state).
    editor.view?.dispatch(editor.view.state.tr.setMeta(TABLE_STYLE_PREVIEW_META, true))
  }

  // Walk the caret's ancestors for the table node + its document position (the normal
  // caret-in-table case setTableStyle targets via resolveCommandTargetTable → findParentNode;
  // the structuredContentBlock branch is not reachable from a hover-preview caret).
  function caretTable(state: any): { node: any; pos: number } | null {
    try {
      const { $from } = state.selection
      for (let d = $from.depth; d > 0; d--) {
        if ($from.node(d).type.name === 'table') return { node: $from.node(d), pos: $from.before(d) }
      }
    } catch { /* selection the resolver can't read */ }
    return null
  }

  // Replicate setTableStyle's tr mutations (fork table.js:1617-1685) onto OUR tr so the
  // addToHistory:false meta survives. Baked visuals are byte-identical to the command's (same
  // resolveTableStyleVisuals + _processTableBorders primitives). Returns false when no target table.
  function applyTableStyleToTr(tr: any, table: { node: any; pos: number }, styleId: string | null): boolean {
    const id = styleId || null
    const nextProps = { ...(table.node.attrs.tableProperties || {}) }
    if (id) nextProps.tableStyleId = id
    else delete nextProps.tableStyleId
    const visuals = id ? resolveTableStyleVisuals(editor, id, nextProps.tblLook || null) : null
    const nextAttrs = {
      ...table.node.attrs,
      tableStyleId: id,
      tableProperties: nextProps,
    }
    const directBorders = _processTableBorders(nextProps.borders || {})
    if (visuals) nextAttrs.borders = { ...visuals.borders, ...directBorders }
    else if (!id) nextAttrs.borders = directBorders
    tr.setNodeMarkup(table.pos, undefined, nextAttrs)

    // Bake/clear first-row cell fills (identical walk to the fork command).
    const tblLook = nextProps.tblLook
    const firstRowOn = !tblLook || tblLook.firstRow !== false
    const fill = firstRowOn && visuals ? visuals.firstRowFill : null
    let rowPos = table.pos + 1
    for (let r = 0; r < table.node.childCount; r++) {
      const row = table.node.child(r)
      let cellPos = rowPos + 1
      for (let c = 0; c < row.childCount; c++) {
        const cell = row.child(c)
        const baked = cell.attrs.styleBakedBackground || null
        const current = cell.attrs.background?.color || null
        const isUserOverride =
          current != null && (baked == null || String(current).toUpperCase() !== String(baked).toUpperCase())
        if (!isUserOverride) {
          const nextFill = r === 0 ? fill : null
          const changed = (current || null) !== (nextFill || null) || baked !== (nextFill || null)
          if (changed) {
            tr.setNodeMarkup(cellPos, undefined, {
              ...cell.attrs,
              background: nextFill ? { color: nextFill } : null,
              styleBakedBackground: nextFill || null,
            })
          }
        } else if (baked != null) {
          tr.setNodeMarkup(cellPos, undefined, { ...cell.attrs, styleBakedBackground: null })
        }
        cellPos += cell.nodeSize
      }
      rowPos += row.nodeSize
    }
    return true
  }

  function tableStylePreviewEnter(id: string): boolean {
    // Hop contract: ALWAYS restore a live preview first (covers a missed mouseleave), THEN
    // evaluate the new tile — an unresolvable style must never strand the previous tile's preview.
    restore()
    const view = editor.view
    if (!view || !id || !TABLE_STYLE_DEFS[id]) return false
    const table = caretTable(editor.state)
    if (!table) return false

    // Materialize FIRST so resolveTableStyleVisuals can paint. NOTE: materialization mutates the
    // converter maps (styles.xml splice + translatedLinkedStyles entry), which the snapshot below
    // does NOT cover. That is ACCEPTABLE: a materialized-but-unused def is harmless and matches
    // Word's lazy semantics — a hovered style that stays registered is exactly what a later click
    // (or reopen) would produce anyway. The preview only rolls back the DOCUMENT (state), never
    // the catalog registration.
    ensureTableStyleMaterialized(id)

    snap = {
      state: editor.state,
      documentModified: editor.converter?.documentModified,
      documentGuid: editor.converter?.documentGuid,
      activeStyleId: id,
    }
    const tr = editor.state.tr
    tr.setMeta('addToHistory', false) // prosemirror-history: never an undo step
    tr.setMeta(TABLE_STYLE_PREVIEW_META, true) // io.ts dirty guard
    // Re-locate the table against the CURRENT state's doc (positions match — no doc mutation yet).
    const t2 = caretTable(editor.state)
    if (!t2 || !applyTableStyleToTr(tr, t2, id)) { snap = null; return false }
    view.dispatch(tr)
    return true
  }

  function tableStylePreviewLeave() {
    restore()
  }

  // Real input mid-preview must WIN (same rationale as style-preview.ts): the gallery never blurs
  // the view, so a keystroke can land on top of the preview — cancel it BEFORE the input applies
  // or the leave-restore would silently discard the user's edit (Word drops the preview on typing
  // too). Capture phase = ahead of PM's own handlers. Listeners die with the view on replaceEditor.
  editor.view?.dom?.addEventListener('keydown', () => { if (snap) restore() }, true)
  editor.view?.dom?.addEventListener('beforeinput', () => { if (snap) restore() }, true)

  return {
    ensureTableStyleMaterialized,
    listCatalogStyles,
    tableStylePreviewEnter,
    // Exported so chrome teardown paths (contextual-tab hide, flyout close) can cancel an
    // active preview.
    tableStylePreviewLeave,
  }
}
