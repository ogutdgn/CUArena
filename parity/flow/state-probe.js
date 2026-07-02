/* State probe (clone side of rubric D2.4) — put the clone into the SAME canonical contexts as
   capture_enabled_states.ps1 and record every rendered control's enabled/disabled state
   (class `wc-disabled`, applied by the state-sync tick from each control's enabled(st)
   predicate). Returns {contexts: {ctx1: {cmd: enabledBool}, ctx2, ctx3}} via --probe-out. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC, ed = () => WC.editor, TS = window.__PM_TextSelection;
  const out = { ready: !!window.__WC_READY, contexts: {}, errors: [] };

  const readStates = () => {
    const m = {};
    document.querySelectorAll('[data-cmd]').forEach((n) => {
      const cmd = n.dataset.cmd;
      if (cmd && !(cmd in m)) m[cmd] = !n.classList.contains('wc-disabled');
    });
    return m;
  };
  const findText = (needle) => {
    let f = null;
    ed().state.doc.descendants((n, p) => {
      if (f || !n.isText || !n.text) return;
      const i = n.text.indexOf(needle);
      if (i >= 0) f = { from: p + i, to: p + i + needle.length };
    });
    return f;
  };

  try {
    // ctx1 — caret in text
    ed().commands.selectAll();
    ed().commands.insertContent('<p>Revenue increased in the second quarter.</p>');
    await sleep(120);
    const f = findText('Revenue');
    if (f) ed().view.dispatch(ed().state.tr.setSelection(TS.create(ed().state.doc, f.from + 3)));
    await sleep(400);
    out.contexts.ctx1 = readStates();

    // ctx2 — text selected
    if (f) ed().view.dispatch(ed().state.tr.setSelection(TS.create(ed().state.doc, f.from, f.to)));
    await sleep(400);
    out.contexts.ctx2 = readStates();

    // ctx3 — caret inside a table (contextual tabs appear)
    WC.PM.insertTable({ rows: 2, cols: 2 });
    await sleep(300);
    let cell = 0;
    ed().state.doc.descendants((n, p) => { if (!cell && (n.type.name === 'tableCell' || n.type.name === 'tableHeader')) cell = p; });
    if (cell) ed().view.dispatch(ed().state.tr.setSelection(TS.create(ed().state.doc, cell + 2)));
    await sleep(500);
    out.contexts.ctx3 = readStates();
  } catch (e) { out.errors.push(String(e && e.message)); }

  return JSON.stringify(out, null, 1);
})();
