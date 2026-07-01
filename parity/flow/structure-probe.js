/* Structure probe (clone side) — dump the clone's FULL ribbon structure for the STRUCTURE
   parity axis: every main tab verbatim from WC.RIBBON (the data that drives the renderer),
   plus the runtime-injected contextual tabs captured by intercepting
   WC.Ribbon.showContextualTab(def) and entering a table. Read-only chrome-wise: it edits only
   the scratch document (inserts a table to trigger the contextual tabs). JSON via --probe-out. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  const out = { ready: !!window.__WC_READY, mainTabs: [], contextualTabs: [], errors: [] };
  const ctrl = (c) => ({
    id: c.id || null, cmd: c.cmd || null, label: c.label || '', type: c.type || 'button',
    items: Array.isArray(c.items) ? c.items : null,
  });
  const tabShape = (t) => ({
    id: t.id, name: t.name, contextual: !!t.contextual,
    groups: (t.groups || []).map((g) => ({
      name: g.name || g.id || '', controls: (g.controls || []).map(ctrl),
      launcher: g.launcher ? ctrl(g.launcher) : null,
    })),
  });
  try {
    const tabs = (WC.RIBBON && (WC.RIBBON.tabs || WC.RIBBON)) || [];
    out.mainTabs = (Array.isArray(tabs) ? tabs : []).map(tabShape);
  } catch (e) { out.errors.push('mainTabs: ' + String(e && e.message)); }

  // Contextual tabs: intercept the injection point, then put the caret in a table.
  try {
    const captured = {};
    const orig = WC.Ribbon.showContextualTab.bind(WC.Ribbon);
    WC.Ribbon.showContextualTab = (def, opts) => { if (def && def.id) captured[def.id] = def; return orig(def, opts); };
    const ed = WC.editor, TS = window.__PM_TextSelection;
    ed.commands.selectAll(); ed.commands.insertContent('<p>z</p>');
    await sleep(60);
    WC.PM.insertTable({ rows: 2, cols: 2 });
    await sleep(300);
    let cell = 0; ed.state.doc.descendants((n, p) => { if (!cell && (n.type.name === 'tableCell' || n.type.name === 'tableHeader')) cell = p; });
    if (cell) ed.view.dispatch(ed.state.tr.setSelection(TS.create(ed.state.doc, cell + 2)));
    await sleep(400);
    WC.Ribbon.showContextualTab = orig;
    out.contextualTabs = Object.values(captured).map(tabShape);
  } catch (e) { out.errors.push('contextual: ' + String(e && e.message)); }

  return JSON.stringify(out, null, 1);
})();
