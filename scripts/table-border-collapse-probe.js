/* Border-collapse thicker-wins probe (fork edit — Tables B borders, 2026-07-01).
   Applying "All Borders" to a SINGLE cell must paint all FOUR sides thick (Word's collapse
   resolves a shared edge to the thicker adjoining border). Verifies via the visible presentation
   layer (the painted DOM), plus the whole-table + default-grid cases stay intact. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 200 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC, ed = () => WC.editor, TS = window.__PM_TextSelection, results = [];
  const t = (name, pass, detail) => results.push({ name, pass: !!pass, detail: pass ? '' : (detail || '') });
  const caret1 = () => { let f = 0; ed().state.doc.descendants((n, p) => { if ((n.type.name === 'tableCell' || n.type.name === 'tableHeader') && !f) f = p; }); if (f) ed().view.dispatch(ed().state.tr.setSelection(TS.create(ed().state.doc, f + 2))); };
  const RED = (sz) => ({ val: 'single', color: 'FF0000', size: sz, space: 0 });
  const scanRed = (minW) => { const pages = document.querySelector('.presentation-editor__pages') || document.body; const s = { Top: 0, Bottom: 0, Left: 0, Right: 0 }; pages.querySelectorAll('*').forEach((e) => { const cs = getComputedStyle(e); ['Top', 'Bottom', 'Left', 'Right'].forEach((side) => { if (/255,\s*0,\s*0/.test(cs['border' + side + 'Color']) && parseFloat(cs['border' + side + 'Width']) >= (minW || 2)) s[side]++; }); }); return s; };
  const freshTable = async (r, c) => { ed().commands.selectAll(); ed().commands.insertContent('<p>zz</p>'); await sleep(50); WC.PM.insertTable({ rows: r, cols: c }); await sleep(350); caret1(); await sleep(60); };

  // 1) SINGLE cell (top-left of a 2x2): all four VISUAL sides must paint thick red. In the
  // collapse model the painter draws each cell's top+left, so cell(0,0)'s bottom edge is drawn
  // as cell(1,0)'s top and its right edge as cell(0,1)'s left. All four visual sides red ⇒
  // two red Tops (own + below) AND two red Lefts (own + right). Before the fix: Top=1, Left=1.
  await freshTable(2, 2);
  WC.PM.tableSetCellBorders({ top: RED(48), bottom: RED(48), left: RED(48), right: RED(48) });
  await sleep(500);
  const s1 = scanRed(6);
  t('single cell — all 4 visual sides paint thick (collapse thicker-wins)', s1.Top >= 2 && s1.Left >= 2, 'sides=' + JSON.stringify(s1) + ' (need Top>=2 && Left>=2)');

  // 2) whole-table thick borders still fully render (no regression).
  await freshTable(2, 2);
  try { WC.PM.tableSelectScope('table'); } catch (e) {}
  await sleep(80);
  WC.PM.tableSetCellBorders({ top: RED(48), bottom: RED(48), left: RED(48), right: RED(48), insideH: RED(48), insideV: RED(48) });
  await sleep(500);
  const s2 = scanRed(6); const total2 = s2.Top + s2.Bottom + s2.Left + s2.Right;
  t('whole-table thick borders fully render', total2 >= 10, 'total red sides=' + total2 + ' ' + JSON.stringify(s2));

  // 3) default grid (no user borders) still shows a thin grid (no thick red spuriously added).
  await freshTable(2, 2); await sleep(200);
  const s3 = scanRed(6);
  t('default grid: no spurious thick-red borders', s3.Top + s3.Bottom + s3.Left + s3.Right === 0, 'unexpected red=' + JSON.stringify(s3));

  const pass = results.filter((r) => r.pass).length;
  return JSON.stringify({ summary: { total: results.length, pass, fail: results.length - pass }, results }, null, 2);
})()
