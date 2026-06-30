// 017 (List authoring) — Set Numbering Value (start-at / arbitrary value) + Continue on the PM/paged engine.
//
// The fork already ships every numbering primitive these controls need, all reachable via WC.PM.cmd:
//   restartNumbering() / continueNumbering()  (extensions/paragraph/paragraph.js → addCommands)
//   changeListLevelBy(delta) / applyListDefinition({listType, levels})  (core commands)
// The ONE thing the existing API can't do directly is set the start value to an ARBITRARY N — restartNumbering
// hardcodes startOverride:1. We do it NO-FORK in two SYNCHRONOUS steps:
//   1. editor.commands.restartNumbering() — the structural work: first item ⇒ pin a startOverride on the existing
//      numId; mid-list ⇒ mint a NEW numId sharing the abstractId + remap the caret-onward paragraphs to it (so the
//      items BEFORE the caret keep their numbering). That remap rides the tr CommandService dispatches before the
//      command returns, so the caret paragraph's numId is final on return.
//   2. re-resolve the caret's (possibly new) numId/ilvl and OVERWRITE the override value via
//      ListHelpers.setLvlOverride(editor, numId, ilvl, {startOverride: N}).
// setLvlOverride fires partChanged → handleNumberingInvalidation, which dispatches SYNCHRONOUSLY
// (core/parts/invalidation/invalidation-handlers.ts), so the re-resolve in step 2 sees the final state. NO fork
// edit — the bridge merely USES ListHelpers; the WC.PM bridge stays the only doc-write path.
import { ListHelpers } from '@core/helpers/list-numbering-helpers.js'

type AnyEditor = any

export function installLists(editor: AnyEditor) {
  const w = window as any
  const markDirty = () => { try { w.WC?.PM?.markDirty?.() } catch { /* none */ } }

  // The caret paragraph's resolved numbering props ({numId, ilvl}), or null when the caret is not on a list.
  function numbering(): { numId: number; ilvl: number } | null {
    try {
      const np = w.WC?.PM?.getResolvedParaProps?.()?.numberingProperties
      return np && np.numId != null ? { numId: np.numId, ilvl: np.ilvl ?? 0 } : null
    } catch { return null }
  }

  // Set Numbering Value — Word's "Start new list" + "Set value to N". Restarts the list at the caret (a NEW numId
  // for a mid-list item, so preceding items keep their numbering) and pins the start at N. value ≤ 1 is exactly a
  // restart (restartNumbering already sets startOverride:1). Returns false (silent no-op, like Change List Level)
  // when the caret is not on a list.
  function setNumberingValue(value: number): boolean {
    // Validate to Word's list-value range (0..32767) BEFORE touching the doc, so an out-of-range / NaN value can't
    // leave a half-applied restart-at-1 nor emit an invalid <w:startOverride> that Word would reject on open.
    const v = Math.floor(Number(value))
    if (!Number.isFinite(v) || v < 0 || v > 32767) return false
    if (!numbering()) return false
    if (editor?.commands?.restartNumbering?.() !== true) return false
    if (v !== 1) { // restartNumbering already pins startOverride:1 — only override when a different value is wanted
      const cur = numbering() // mid-list restart minted a new numId — re-resolve it
      if (cur) {
        try { ListHelpers.setLvlOverride(editor, cur.numId, cur.ilvl, { startOverride: v }) }
        catch { /* override is best-effort; the restart already applied */ }
      }
    }
    markDirty()
    return true
  }

  // "Continue from previous list" — drop the startOverride so the counter rejoins the prior chain.
  function continueListNumbering(): boolean {
    if (!numbering()) return false
    if (editor?.commands?.continueNumbering?.() !== true) return false
    markDirty()
    return true
  }

  // 023 (List authoring, NO-FORK, parity): the fork's toggleList applies the numbering but never seeds
  // pStyle=ListParagraph (it only STRIPS it on the remove path), and builds <w:numPr> as numId-then-ilvl;
  // real Word attaches <w:pStyle w:val="ListParagraph"/> (BEFORE <w:numPr>) to every list item and orders
  // numPr children ilvl-then-numId. We fix both in the SAME transaction as the toggle via a raw chain
  // `.command` step (one undo step), so the ribbon Bullets/Numbering + the style gallery all become
  // Word-faithful. The fork toggle is the ONLY doc-write; this step just normalizes the resulting attrs.
  function fixListParagraphs({ tr }: any): boolean {
    const sel = tr.selection
    const edits: Array<{ pos: number; attrs: any }> = []
    tr.doc.nodesBetween(sel.from, sel.to, (node: any, pos: number) => {
      if (node.type?.name !== 'paragraph') return
      const pp = node.attrs?.paragraphProperties || {}
      const np = pp.numberingProperties
      if (np && np.numId != null) {
        // a list item → ensure pStyle + numPr {ilvl, numId}, both at their CT_PPr slots. The pPr exporter emits
        // children in paragraphProperties KEY-INSERTION order (no xmlOrder), so we must rebuild in schema order:
        // pStyle, then the pre-numPr keys (keepNext/keepLines/pageBreakBefore/framePr/widowControl), then numPr,
        // then everything else (spacing/ind/jc/shd/… all sort AFTER numPr in CT_PPr). Destructure styleId out
        // first: a fresh paragraph carries `styleId: null` as a PRESENT key, so a spread would clobber it back.
        // Keep the user's explicit style if any, else ListParagraph. (Putting numPr LAST would make Word reject a
        // list item that also carries direct jc/spacing/ind/shd as out-of-order CT_PPr.)
        const orderedNp = { ilvl: np.ilvl ?? 0, numId: np.numId }
        const { styleId: existingStyle, numberingProperties: _np, ...rest } = pp
        const rebuilt: any = { styleId: existingStyle || 'ListParagraph' }
        for (const k of ['keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl']) {
          if (k in rest) { rebuilt[k] = (rest as any)[k]; delete (rest as any)[k] }
        }
        rebuilt.numberingProperties = orderedNp
        Object.assign(rebuilt, rest)
        edits.push({ pos, attrs: { ...node.attrs, paragraphProperties: rebuilt } })
      } else if (pp.styleId === 'ListParagraph') {
        // list toggled OFF but our ListParagraph remained → strip it (defensive; Word leaves no pStyle here)
        const { styleId, ...rest } = pp
        edits.push({ pos, attrs: { ...node.attrs, paragraphProperties: rest } })
      }
    })
    edits.forEach(({ pos, attrs }) => tr.setNodeMarkup(pos, undefined, attrs))
    return true
  }

  function applyListThenFix(forkCmd: string, arg?: unknown): boolean {
    const ch: any = editor.chain()
    if (typeof ch[forkCmd] !== 'function' || typeof ch.command !== 'function') return false
    const step = arg === undefined ? ch[forkCmd]() : ch[forkCmd](arg)
    const ok = step.command(fixListParagraphs).run()
    if (ok !== false) markDirty()
    return ok !== false
  }

  const toggleBulletList = () => applyListThenFix('toggleBulletList')
  const toggleOrderedList = () => applyListThenFix('toggleOrderedList')
  const toggleBulletListStyle = (style: unknown) => applyListThenFix('toggleBulletListStyle', style)
  const toggleOrderedListStyle = (style: unknown) => applyListThenFix('toggleOrderedListStyle', style)

  return { setNumberingValue, continueListNumbering, toggleBulletList, toggleOrderedList, toggleBulletListStyle, toggleOrderedListStyle }
}
