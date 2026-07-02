/* VISUAL pair probe — clone side: contextual Table Layout ribbon (level 1).
   Inserts a table (contextual tabs appear) and activates table-layout; the --shot
   PNG fires after this evalfile returns. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  const out = { ready: !!window.__WC_READY, pair: 'tablelayout' };
  try {
    WC.PM.insertTable({ rows: 3, cols: 3 });
    await sleep(600);
    WC.Ribbon.activate('table-layout');
    await sleep(600);
  } catch (e) { out.err = String(e && e.message); }
  return JSON.stringify(out);
})();
