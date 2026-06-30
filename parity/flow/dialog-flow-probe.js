/* Dialog flow probe (clone side) — the FLOW axis for the deep T0/T1 dialog enumeration.
   Opens each T0/T1 dialog at runtime and records (a) does it OPEN, (b) which fields are PRESENT
   (so the Python verifier can flag Word-has-but-clone-lacks fields), (c) is an OK/apply control present.
   Read-only: opens then immediately closes each dialog; never commits. Returns JSON via --probe-out. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC, ed = WC.editor, PM = WC.PM;
  const out = { ready: !!window.__WC_READY, dialogs: [] };

  const closeAll = () => {
    try { document.querySelectorAll('#modal-root .modal-backdrop').forEach((b) => b.remove()); } catch (e) {}
    try { document.querySelectorAll('#find-pane').forEach((p) => p.remove()); } catch (e) {}
    try { WC.closeFlyouts && WC.closeFlyouts(); } catch (e) {}
    try { PM && PM.clearFind && PM.clearFind(); } catch (e) {}
  };

  // collect labels/control signatures from a root element (a .dialog or a pane)
  const collect = (root) => {
    if (!root) return null;
    const labels = Array.from(root.querySelectorAll('label, span, .t, .color-section-title, option'))
      .map((n) => (n.textContent || '').trim()).filter((t) => t && t.length < 40);
    // input placeholders carry the field name in some dialogs (Find/Replace boxes)
    root.querySelectorAll('input[placeholder]').forEach((i) => { const p = (i.placeholder || '').trim(); if (p && p.length < 40) labels.push(p); });
    const inputs = {};
    root.querySelectorAll('input').forEach((i) => { const t = i.type || 'text'; inputs[t] = (inputs[t] || 0) + 1; });
    const buttons = Array.from(root.querySelectorAll('button')).map((b) => (b.textContent || '').trim()).filter(Boolean);
    return {
      labels: Array.from(new Set(labels)),
      inputs,
      selects: root.querySelectorAll('select').length,
      checkboxes: root.querySelectorAll('input[type=checkbox]').length,
      buttons,
      ok_present: buttons.some((b) => /^OK$/i.test(b)) || buttons.some((b) => /Replace/i.test(b)),
    };
  };

  // give the controls a selection so dialogs prefill / enable
  const seed = () => {
    ed.commands.selectAll(); ed.commands.insertContent('<p>Revenue</p>');
    let f = null; ed.state.doc.descendants((n, p) => { if (f || !n.isText || !n.text) return; const i = n.text.indexOf('Revenue'); if (i >= 0) f = { from: p + i, to: p + i + 7 }; });
    if (f) ed.view.dispatch(ed.view.state.tr.setSelection(window.__PM_TextSelection.create(ed.state.doc, f.from, f.to)));
  };

  // run one dialog spec: open(), snapshot the .dialog (+ optional extra tab clicks), close
  const probe = async (id, open, opts = {}) => {
    const rec = { id, opened: false };
    closeAll(); await sleep(40);
    try {
      seed(); await sleep(40);
      open();
      await sleep(150);
      const root = document.querySelector(opts.paneSelector || '#modal-root .dialog');
      rec.opened = !!root;
      if (root) {
        rec.snapshot = collect(root);
        // tabbed dialogs (Font has an Advanced tab) — click each .t and merge labels
        if (opts.tabs) {
          const tabEls = Array.from(root.querySelectorAll('.tabs .t'));
          for (const te of tabEls) {
            try { te.click(); await sleep(60); const more = collect(root); if (more) rec.snapshot.labels = Array.from(new Set(rec.snapshot.labels.concat(more.labels))); } catch (e) {}
          }
        }
      }
    } catch (e) { rec.err = String(e && e.message); }
    closeAll(); await sleep(40);
    out.dialogs.push(rec);
  };

  try {
    await probe('font', () => WC.Dialogs.font(), { tabs: true });
    await probe('paragraph', () => WC.Dialogs.paragraph(), { tabs: true });
    await probe('find-replace', () => WC.Dialogs.findPane(true, true), { paneSelector: '#find-pane' });
    await probe('insert-table', () => WC.Dialogs.insertTable());
    await probe('insert-hyperlink', () => WC.Dialogs.insertLink());
    // Margins: customMarginsDialog is local to commands.js (not on WC.Dialogs) — drive the Layout>Margins
    // flyout > "Custom Margins…". Best-effort; if unreachable the verifier falls back to the code trace.
    await probe('page-margins', () => {
      try {
        if (WC.Commands && WC.Commands.H && WC.Commands.H.margins) { WC.Commands.H.margins(null, document.body); }
        else if (WC.Commands && WC.Commands.run) { WC.Commands.run('margins'); }
      } catch (e) {}
      const item = Array.from(document.querySelectorAll('.flyout .fly-item, .flyout .fi-label'))
        .find((n) => /Custom Margins/i.test(n.textContent || ''));
      if (item) (item.closest('.fly-item') || item).click();
    });
  } catch (e) { out.err = String(e && e.message) + '\n' + String(e && e.stack); }

  closeAll();
  return JSON.stringify(out, null, 2);
})();
