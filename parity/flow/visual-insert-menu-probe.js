/* VISUAL pair probe — clone side: the OPEN Insert > Table dropdown (level 2 menus).
   Opens the table dropdown and LEAVES IT OPEN for the --shot. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  const out = { ready: !!window.__WC_READY, pair: 'insert-table-menu' };
  try {
    window.WC.editor.commands.selectAll(); window.WC.editor.commands.insertContent('<p></p>'); await sleep(200);
    WC.Ribbon.activate('insert');
    await sleep(400);
    const n = document.querySelector('[data-cmd="table"]');
    if (!n) throw new Error('no insert.table control');
    WC.Commands.dropdown({ cmd: 'table', type: 'dropdown' }, n);
    await sleep(600);
    out.flyoutOpen = !!document.querySelector('.flyout');
  } catch (e) { out.err = String(e && e.message); }
  return JSON.stringify(out);
})();
