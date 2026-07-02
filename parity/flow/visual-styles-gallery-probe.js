/* VISUAL pair probe — clone side: the OPEN Table Styles gallery (level 2 — the 2/247
   gap made visible). Caret in a table, Table Design active, tblStyles flyout open. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  const out = { ready: !!window.__WC_READY, pair: 'table-styles-gallery' };
  try {
    window.WC.editor.commands.selectAll(); window.WC.editor.commands.insertContent('<p></p>'); await sleep(200);
    WC.PM.insertTable({ rows: 3, cols: 3 });
    await sleep(600);
    WC.Ribbon.activate('table-design');
    await sleep(400);
    const n = document.querySelector('[data-cmd="tblStyles"]');
    if (!n) throw new Error('no tblStyles control');
    WC.Commands.dropdown({ cmd: 'tblStyles', type: 'dropdown' }, n);
    await sleep(600);
    out.items = document.querySelectorAll('.flyout .fly-item').length;
  } catch (e) { out.err = String(e && e.message); }
  return JSON.stringify(out);
})();
