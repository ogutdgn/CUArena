(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 200 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  WC.PM.insertTable({ rows: 3, cols: 3 });
  await sleep(500);
  const out = { steps: [] };
  // 1) set a distinctive pen (red, thick) via the ribbon handlers' flyouts is hard; instead open Borders flyout
  const node = document.querySelector('[data-cmd="tblBorders"]') || document.body;
  out.hasBordersBtn = !!document.querySelector('[data-cmd="tblBorders"]');
  try { WC.Commands.dropdown({ cmd: 'tblBorders', type: 'dropdown', label: 'Borders' }, node); out.steps.push('opened flyout'); } catch (e) { out.err = 'open: ' + e.message; }
  await sleep(300);
  const items = Array.from(document.querySelectorAll('.flyout *')).filter((n) => n.children.length === 0 && n.textContent);
  out.itemTexts = items.map((n) => n.textContent.trim()).filter((t) => t && t.length < 40).slice(0, 20);
  const allB = items.find((n) => /^All Borders$/i.test(n.textContent.trim()));
  if (allB) { allB.click(); out.steps.push('clicked All Borders'); } else out.steps.push('All Borders item NOT FOUND');
  await sleep(500);
  // read the caret cell model borders
  try {
    const st = WC.editor.state; const { $from } = st.selection;
    for (let d = $from.depth; d > 0; d--) { const n = $from.node(d); if (n.type.name === 'tableCell' || n.type.name === 'tableHeader') { out.modelBorders = JSON.stringify(n.attrs.tableCellProperties && n.attrs.tableCellProperties.borders || null); break; } }
    out.selInTable = (function(){ for (let d=$from.depth; d>0; d--){ if ($from.node(d).type.name==='table') return true; } return false; })();
  } catch (e) { out.modelErr = e.message; }
  return JSON.stringify(out, null, 2);
})()
