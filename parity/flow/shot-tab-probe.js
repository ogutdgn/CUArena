/* Visual-axis capture probe — put the clone in a canonical state and let --shot photograph it.
   Tab comes from the WC_SHOT_TAB define-ish global or defaults to 'home'; types a line of text
   so the ribbon reflects a normal editing context. Used with:
   electron . --shot=C:/tmp/wc-<tab>.png --shot-evalfile=parity/flow/shot-tab-probe.js --shot-delay=1600 --probe-out=C:/tmp/wc-shot.json */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 300 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  const tab = (window.localStorage && window.localStorage.getItem('WC_SHOT_TAB')) || 'home';
  try {
    WC.editor.commands.selectAll();
    WC.editor.commands.insertContent('<p>Revenue increased in the second quarter.</p>');
    await sleep(100);
    if (tab === 'table-design' || tab === 'table-layout') {
      WC.PM.insertTable({ rows: 3, cols: 3 });
      await sleep(400);
    }
    if (WC.Ribbon && WC.Ribbon.activate) WC.Ribbon.activate(tab);
    await sleep(300);
  } catch (e) { /* shot still fires */ }
  return JSON.stringify({ tab, ready: !!window.__WC_READY });
})();
