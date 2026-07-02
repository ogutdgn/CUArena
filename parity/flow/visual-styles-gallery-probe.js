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
    // 030: the tblStyles dropdown is REPLACED by the in-ribbon tile gallery — open the full
    // sectioned gallery via the carousel's More chevron (the same surface Word's shot shows).
    const more = document.querySelector('.ribbon-panel[data-tab="table-design"] .rgallery-more')
      || document.querySelector('.ribbon-panel.active .rgallery-more');
    if (!more) throw new Error('no table-styles More chevron');
    more.click();
    await sleep(700);
    out.items = document.querySelectorAll('.flyout .tblstyle-cell').length;
  } catch (e) { out.err = String(e && e.message); }
  return JSON.stringify(out);
})();
