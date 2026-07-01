(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 200 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  WC.PM.insertTable({ rows: 3, cols: 3 });
  await sleep(500);
  const B = { val: 'single', color: 'FF0000', size: 24, space: 0 }; // thick red (3pt)
  WC.PM.tableSetCellBorders({ top: B, bottom: B, left: B, right: B });
  await sleep(700);
  // inspect the FIRST rendered cell in the paged editor
  const cells = document.querySelectorAll('#pm-editor td, #pm-editor th');
  let info = null;
  if (cells.length) { const cs = getComputedStyle(cells[0]); info = { top: cs.borderTopWidth + '/' + cs.borderTopStyle + '/' + cs.borderTopColor, count: cells.length }; }
  // also check the model
  let modelBorders = null;
  try {
    const st = WC.editor.state; const { $from } = st.selection;
    for (let d = $from.depth; d > 0; d--) { const n = $from.node(d); if (n.type.name === 'tableCell' || n.type.name === 'tableHeader') { modelBorders = JSON.stringify(n.attrs.tableCellProperties && n.attrs.tableCellProperties.borders || n.attrs.borders || null); break; } }
  } catch (e) { modelBorders = 'ERR ' + e.message; }
  return JSON.stringify({ renderedCell: info, modelBorders }, null, 2);
})()
