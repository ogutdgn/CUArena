/* Flow verifier probe (clone side) — introspect the live ribbon DOM for each T0/T1 control:
   open it and capture WHAT happens (flyout + its items / a dialog / a plain apply-button), so the
   Python harness can compare against the ribbon-data spec (control type + items[]). Read-only: it
   opens and closes menus, never commits an action. Returns JSON via --probe-out. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC, ed = WC.editor;
  const out = { ready: !!window.__WC_READY, controls: [] };
  const T0T1 = [
    'home.font.bold', 'home.font.italic', 'home.font.underline', 'home.font.font', 'home.font.font-size',
    'home.paragraph.bullets', 'home.paragraph.align-left', 'home.paragraph.center',
    'home.font.font-color', 'home.font.text-highlight-color', 'home.paragraph.numbering',
    'home.paragraph.justify', 'home.paragraph.line-and-paragraph-spacing',
  ];
  const closeAll = () => { try { WC.closeFlyouts && WC.closeFlyouts(); } catch (e) {} };
  try {
    // Give controls a non-empty selection so they enable.
    ed.commands.selectAll(); ed.commands.insertContent('<p>Revenue</p>');
    let f = null; ed.state.doc.descendants((n, p) => { if (f || !n.isText || !n.text) return; const i = n.text.indexOf('Revenue'); if (i >= 0) f = { from: p + i, to: p + i + 7 }; });
    if (f) ed.view.dispatch(ed.view.state.tr.setSelection(window.__PM_TextSelection.create(ed.state.doc, f.from, f.to)));
    await sleep(80);

    // Flatten WC.RIBBON -> control by id.
    const byId = {};
    const tabs = (WC.RIBBON && (WC.RIBBON.tabs || WC.RIBBON)) || [];
    (Array.isArray(tabs) ? tabs : []).forEach((tab) => ((tab.groups || []).forEach((g) => (g.controls || []).forEach((c) => { if (c && c.id) byId[c.id] = c; }))));
    out.ribbonControlCount = Object.keys(byId).length;

    for (const id of T0T1) {
      const c = byId[id];
      const rec = { id, found: !!c };
      if (c) { rec.cmd = c.cmd; rec.type = c.type; rec.items = c.items || null; }
      const cmd = c && c.cmd;
      const elc = (cmd && document.querySelector('[data-cmd="' + cmd + '"]')) || document.querySelector('[data-id="' + id + '"]');
      rec.rendered = !!elc;
      try {
        if (c && (c.type === 'split' || c.type === 'dropdown')) {
          closeAll(); await sleep(20);
          WC.Commands.dropdown(c, elc || document.body);
          await sleep(100);
          const fly = document.querySelector('.flyout');
          const labels = Array.from(document.querySelectorAll('.flyout .fly-item .fi-label')).map((n) => n.textContent.trim()).filter(Boolean);
          const swatches = document.querySelectorAll('.flyout .sw, .flyout .swatch, .flyout [data-color], .flyout .color-cell').length;
          rec.kind = fly ? 'flyout' : (document.querySelector('.wc-dialog, .dialog-overlay, .modal') ? 'dialog' : 'nothing');
          rec.actual_items = labels;
          rec.actual_item_count = labels.length;
          rec.swatch_count = swatches;
          closeAll();
        } else if (c && c.type === 'combo') {
          rec.kind = elc ? 'combo' : 'nothing';
          rec.actual_items = [];
        } else if (c) {
          rec.kind = elc ? 'apply' : 'nothing';  // toggle/button: applies on click, no menu
          rec.actual_items = [];
        } else {
          rec.kind = 'missing-control';
        }
      } catch (e) { rec.err = String(e && e.message); rec.kind = 'error'; }
      out.controls.push(rec);
      await sleep(30);
    }
  } catch (e) { out.err = String(e && e.message) + '\n' + String(e && e.stack); }
  return JSON.stringify(out, null, 2);
})();
