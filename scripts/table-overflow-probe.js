(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 200 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  WC.PM.insertTable({ rows: 2, cols: 3 });
  await sleep(500);
  for (let k = 0; k < 10; k++) { try { WC.PM.tableAddColumn('right'); } catch (e) {} await sleep(150); }
  await sleep(700);
  // find the widest rendered table + the page content box
  let tw = 0, tr = 0;
  document.querySelectorAll('table').forEach((t) => { const r = t.getBoundingClientRect(); if (r.width > tw) { tw = r.width; tr = r.right; } });
  const page = document.querySelector('.superdoc-page') || document.querySelector('#pages > *');
  const pr = page ? page.getBoundingClientRect() : null;
  // export + sum gridCol
  const xml = await WC.editor.exportDocx({ exportXmlOnly: true });
  const cols = (xml.match(/<w:gridCol\b[^>]*w:w="(\d+)"/g) || []).map((s) => parseInt(s.match(/w:w="(\d+)"/)[1], 10));
  const tblW = (xml.match(/<w:tblW\b[^>]*\/?>/) || ['none'])[0];
  return JSON.stringify({
    renderedTableW: Math.round(tw), renderedRight: Math.round(tr),
    pageRight: pr ? Math.round(pr.right) : null, overflowPx: pr ? Math.round(tr - pr.right) : null,
    gridColCount: cols.length, gridColSumTwips: cols.reduce((a, b) => a + b, 0),
    pageTextWidthTwips_letter1in: 9360, tblW,
  }, null, 2);
})()
