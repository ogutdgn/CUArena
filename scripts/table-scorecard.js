(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 200 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC, ed = () => WC.editor, TS = window.__PM_TextSelection, results = [];
  const doc = () => JSON.stringify(ed().state.doc.toJSON());
  const caret1 = () => { let f = 0; ed().state.doc.descendants((n, p) => { if ((n.type.name === 'tableCell' || n.type.name === 'tableHeader') && !f) f = p; }); if (f) ed().view.dispatch(ed().state.tr.setSelection(TS.create(ed().state.doc, f + 2))); };
  const selectTwoCells = () => { const cells = []; ed().state.doc.descendants((n, p) => { if (n.type.name === 'tableCell' || n.type.name === 'tableHeader') cells.push(p); }); if (cells.length >= 2 && window.__PM_CellSelection) { try { ed().view.dispatch(ed().state.tr.setSelection(new window.__PM_CellSelection(ed().state.doc.resolve(cells[0] + 1), ed().state.doc.resolve(cells[1] + 1)))); } catch (e) { caret1(); } } };
  const fresh = async (multi) => { WC.closeFlyouts && WC.closeFlyouts(); document.querySelectorAll('.dialog').forEach((d) => { const b = Array.from(d.querySelectorAll('button')).find((x) => /cancel|close/i.test(x.textContent)); if (b) b.click(); }); await sleep(60); ed().commands.selectAll(); ed().commands.insertContent('<p>z</p>'); await sleep(50); WC.PM.insertTable({ rows: 3, cols: 3 }); await sleep(250); multi ? selectTwoCells() : caret1(); await sleep(50); };
  const activate = async (tab) => { WC.Ribbon.activate(tab); await sleep(120); };
  const clickCmd = async (cmd) => { const n = document.querySelector('[data-cmd="' + cmd + '"]'); if (!n) return 'NO_NODE'; const before = doc(); n.click(); await sleep(250); return { before, fly: document.querySelector('.flyout'), dlg: document.querySelector('.dialog'), toast: document.querySelector('.toast'), after: doc() }; };
  const flyItems = () => Array.from(document.querySelectorAll('.flyout .fly-item')).map((i) => (i.textContent || '').trim());

  // group 1: direct-action buttons — expect doc change (caret or 2-cell sel)
  const DIRECT = { tblInsertAbove: 1, tblInsertBelow: 1, tblInsertLeft: 1, tblInsertRight: 1, tblSplitCell: 1, tblAlignTopLeft: 1, tblAlignMidCenter: 1, tblAlignBotRight: 1, tblTextDir: 1, tblToText: 1, tblRepeatHeader: 1, tblStyleHeaderRow: 1, tblStyleBandedRows: 1, tblStyleFirstCol: 1 };
  const MERGE = { tblMerge: 1 };
  const FLYOUT = { tblSelect: 'Select Table', tblDelete: 'Delete Rows', tblShading: null, tblBorders: 'All Borders', tblLineStyle: 'Double', tblLineWeight: '3 pt', tblPenColor: null, tblBorderStyles: 'Single, 1 pt', tblAutoFit: 'AutoFit Window', tblRowHeight: null, tblColWidth: null };
  const DIALOG = { tblProperties: 1, tblSort: 1, tblFormula: 1, tblCellMargins: 1 };
  const STUB = { tblDrawTable: 1, tblEraser: 1, tblBorderPainter: 1 };
  const tabOf = (cmd) => (/^tblStyle|^tblShading|^tblBorders|^tblLine|^tblPen|^tblStyles/.test(cmd)) ? 'table-design' : 'table-layout';

  for (const cmd of Object.keys(DIRECT)) { await fresh(false); await activate(tabOf(cmd)); caret1(); const r = await clickCmd(cmd); results.push(cmd + ' = ' + (r === 'NO_NODE' ? 'NO_NODE' : (r.after !== r.before ? 'OK (doc changed)' : 'DEAD (no change)'))); }
  for (const cmd of Object.keys(MERGE)) { await fresh(true); await activate('table-layout'); selectTwoCells(); const r = await clickCmd(cmd); results.push(cmd + ' = ' + (r === 'NO_NODE' ? 'NO_NODE' : (r.after !== r.before ? 'OK (doc changed)' : (r.toast ? 'toast (needs 2-cell sel)' : 'DEAD')))); }
  for (const cmd of Object.keys(FLYOUT)) { await fresh(false); await activate(tabOf(cmd)); caret1(); const r = await clickCmd(cmd); if (r === 'NO_NODE') { results.push(cmd + ' = NO_NODE'); continue; } const items = flyItems(); const dead = items.length === 1 && /no options/i.test(items[0]); const needle = FLYOUT[cmd]; const hasNeedle = needle ? items.some((x) => x.includes(needle)) : (items.length > 0 || !!document.querySelector('.flyout .wc-color-palette, .flyout .color-swatch, .flyout .swatch, .flyout .rspinner, .flyout input')); results.push(cmd + ' = ' + (dead ? 'DEAD "(no options)"' : (hasNeedle ? 'OK (real menu)' : 'SUSPECT items=[' + items.slice(0, 4).join('|') + ']'))); WC.closeFlyouts(); }
  for (const cmd of Object.keys(DIALOG)) { await fresh(false); await activate('table-layout'); caret1(); const r = await clickCmd(cmd); results.push(cmd + ' = ' + (r === 'NO_NODE' ? 'NO_NODE' : (r.dlg ? 'OK (dialog opens)' : (r.after !== r.before ? 'OK (applied直)' : 'DEAD (no dialog)')))); document.querySelectorAll('.dialog button').forEach((b) => { if (/cancel|close/i.test(b.textContent)) b.click(); }); }
  for (const cmd of Object.keys(STUB)) { await fresh(false); await activate('table-layout'); caret1(); const r = await clickCmd(cmd); results.push(cmd + ' = ' + (r === 'NO_NODE' ? 'NO_NODE' : (r.toast ? 'STUB (honest toast)' : (r.after !== r.before ? 'OK (doc changed)' : 'SILENT (no toast/change)')))); }

  return JSON.stringify(results, null, 1);
})()
