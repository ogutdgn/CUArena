/* VISUAL pair probe — clone side: LEVEL 4 document render — a Grid Table 4 Accent 1
   styled 3x3 table on the page (100% zoom). The most important level for the RL
   environment: does the RESULT look like Word's? */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC, PM = WC.PM;
  const out = { ready: !!window.__WC_READY, pair: 'doc-styled-table' };
  try {
    PM.insertTable({ rows: 3, cols: 3 });
    await sleep(500);
    const styles = (PM.getTableStyles && PM.getTableStyles()) || [];
    const hit = styles.find((s) => s.id === 'GridTable4-Accent1' || s.name === 'Grid Table 4 Accent 1');
    if (hit) { PM.tableSetStyle(hit.id); out.applied = hit.id; }
    else { out.applied = null; }
    await sleep(800);
  } catch (e) { out.err = String(e && e.message); }
  return JSON.stringify(out);
})();
