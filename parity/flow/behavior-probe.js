/* Behavior probe — the BEHAVIOR axis runner (rubric D6). Executes flow CARDS (journey flows
   D6.1 + generated micro-twins D6.2) inside the live clone: each card = steps (drive the REAL
   ribbon UI — clicks, not API calls) + expectations checked live (document, PAINT, chrome).
   ❓ from-recording expectations report PENDING until a real-Word recording fills them (D6.3
   — never guessed). Cards arrive via window.__BEHAVIOR_CARDS (wrapper evalfile). */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC, ed = () => WC.editor, TS = window.__PM_TextSelection;
  const cards = window.__BEHAVIOR_CARDS || [];
  const out = { ready: !!window.__WC_READY, cards: [], errors: [] };
  const docJson = () => JSON.stringify(ed().state.doc.toJSON());

  const findText = (needle) => {
    let f = null;
    ed().state.doc.descendants((n, p) => {
      if (f || !n.isText || !n.text) return;
      const i = n.text.indexOf(needle);
      if (i >= 0) f = { from: p + i, to: p + i + needle.length };
    });
    return f;
  };
  const paintedNode = (needle) => {
    const walker = document.createTreeWalker(document.querySelector('#pm-editor') || document.body,
      NodeFilter.SHOW_TEXT);
    let t;
    while ((t = walker.nextNode())) if (t.textContent.includes(needle)) return t.parentElement;
    return null;
  };
  const closeAll = async () => {
    try { WC.closeFlyouts && WC.closeFlyouts(); } catch (e) {}
    document.querySelectorAll('.dialog, .wc-dialog, .modal').forEach((d) => {
      const b = Array.from(d.querySelectorAll('button')).find((x) => /cancel|close/i.test((x.textContent || '').trim()));
      if (b) b.click(); else d.remove();
    });
    await sleep(60);
  };

  for (const card of cards) {
    const cr = { id: card.id, kind: card.kind, steps: [], verdict: 'pass' };
    let lastDoc = docJson();
    let ctx = { selText: null };
    try {
      await closeAll();
      for (const step of card.steps) {
        const sr = { step: JSON.stringify(step).slice(0, 90) };
        try {
          if (step.do) {
            if (step.do === 'setupText') {
              ed().commands.selectAll(); ed().commands.insertContent('<p>' + step.text + '</p>');
              await sleep(120); lastDoc = docJson();
            } else if (step.do === 'select') {
              const f = findText(step.text);
              if (!f) throw new Error('text not found: ' + step.text);
              ed().view.dispatch(ed().state.tr.setSelection(TS.create(ed().state.doc, f.from, f.to)));
              ctx.selText = step.text; await sleep(150);
            } else if (step.do === 'activateTab') {
              WC.Ribbon.activate(step.tab); await sleep(150);
            } else if (step.do === 'clickCmd') {
              const n = document.querySelector('[data-cmd="' + step.cmd + '"]');
              if (!n) throw new Error('no control node: ' + step.cmd);
              lastDoc = docJson(); n.click(); await sleep(300);
            } else if (step.do === 'openDropdown') {
              const n = document.querySelector('[data-cmd="' + step.cmd + '"]');
              if (!n) throw new Error('no control node: ' + step.cmd);
              const cdef = { cmd: step.cmd, type: 'dropdown' };
              try { WC.Commands.dropdown(cdef, n); } catch (e) { n.click(); }
              await sleep(250);
            } else if (step.do === 'clickItem') {
              const items = Array.from(document.querySelectorAll('.flyout .fly-item'));
              const node = items.find((x) => new RegExp(step.match, 'i').test((x.textContent || '').trim()));
              if (!node) throw new Error('no flyout item matching: ' + step.match);
              lastDoc = docJson(); node.click(); await sleep(300);
            } else if (step.do === 'undo') {
              ed().commands.undo(); await sleep(200);
            } else { throw new Error('unknown step.do: ' + step.do); }
            sr.result = 'ok';
          } else if (step.expect) {
            const ex = step.expect;
            if (ex === 'docChanged') {
              sr.result = docJson() !== lastDoc ? 'ok' : 'FAIL(doc unchanged)';
            } else if (ex === 'flyoutOpen') {
              sr.result = document.querySelector('.flyout') ? 'ok' : 'FAIL(no flyout)';
            } else if (ex === 'dialogOpen') {
              sr.result = document.querySelector('.dialog, .wc-dialog, .modal') ? 'ok' : 'FAIL(no dialog)';
            } else if (ex === 'flyoutHasItem') {
              const items = Array.from(document.querySelectorAll('.flyout .fly-item')).map((x) => (x.textContent || '').trim());
              sr.result = items.some((s) => new RegExp(step.match, 'i').test(s)) ? 'ok'
                : 'FAIL(items: ' + items.slice(0, 6).join('|') + ')';
            } else if (ex === 'paintedStyle') {
              const el = paintedNode(step.text);
              if (!el) { sr.result = 'FAIL(painted text not found)'; }
              else {
                const v = getComputedStyle(el).getPropertyValue(step.prop);
                sr.result = (step.anyOf || [step.value]).some((want) => String(v).includes(want))
                  ? 'ok' : `FAIL(${step.prop}=${v})`;
              }
            } else if (ex === 'selectionSurvives') {
              const f = findText(step.text);
              const s = ed().state.selection;
              sr.result = (f && s.from === f.from && s.to === f.to) ? 'ok' : `FAIL(sel ${s.from}-${s.to})`;
            } else if (ex === 'tableExists') {
              let found = null;
              ed().state.doc.descendants((n) => { if (!found && n.type.name === 'table') found = n; });
              sr.result = found ? 'ok' : 'FAIL(no table)';
            } else if (ex === 'contextualTabsShown') {
              sr.result = document.querySelector('.ribbon-tab.contextual-tab') ? 'ok' : 'FAIL(no contextual tabs)';
            } else if (ex === 'fromRecording') {
              sr.result = 'PENDING(❓ needs real-Word recording: ' + (step.q || '') + ')';
            } else { sr.result = 'FAIL(unknown expect: ' + ex + ')'; }
          }
        } catch (e) { sr.result = 'FAIL(' + String(e && e.message) + ')'; }
        cr.steps.push(sr);
        if (String(sr.result).startsWith('FAIL')) { cr.verdict = 'fail'; break; }
        if (String(sr.result).startsWith('PENDING') && cr.verdict === 'pass') cr.verdict = 'pending';
      }
    } catch (e) { cr.verdict = 'fail'; cr.err = String(e && e.message); }
    await closeAll();
    out.cards.push(cr);
  }
  return JSON.stringify(out, null, 1);
})();
