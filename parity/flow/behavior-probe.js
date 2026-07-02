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
  // The VISIBLE (painted) table cells — wherever the paged engine renders them. The
  // getClientRects filter excludes any hidden/model-side duplicates: what the USER sees.
  const paintedCells = () => Array.from(document.querySelectorAll('td, th'))
    .filter((n) => n.getClientRects().length > 0);
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
            } else if (step.do === 'typeText') {
              ed().commands.insertContent(step.text); await sleep(150);
            } else if (step.do === 'gridHover') {
              // Insert>Table grid picker: hover the (rows x cols) cell — drives the live label.
              const cell = document.querySelector(`.tablegrid .cell[data-r="${step.rows - 1}"][data-c="${step.cols - 1}"]`);
              if (!cell) throw new Error('no grid picker cell ' + step.rows + 'x' + step.cols);
              cell.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true })); await sleep(150);
            } else if (step.do === 'gridPick') {
              const cell = document.querySelector(`.tablegrid .cell[data-r="${step.rows - 1}"][data-c="${step.cols - 1}"]`);
              if (!cell) throw new Error('no grid picker cell ' + step.rows + 'x' + step.cols);
              lastDoc = docJson(); cell.click(); await sleep(400);
            } else if (step.do === 'clickCellPainted' || step.do === 'shiftClickCellPainted') {
              // Mouse-click the center of visible cell #index — moves the caret like a user.
              // shift variant extends to a CellSelection (Word's click+shift-click cell range).
              const cells = paintedCells();
              const c = cells[step.index];
              if (!c) throw new Error('no painted cell #' + step.index + ' (visible: ' + cells.length + ')');
              const r = c.getBoundingClientRect();
              const opts = { bubbles: true, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2,
                shiftKey: step.do === 'shiftClickCellPainted' };
              c.dispatchEvent(new MouseEvent('mousedown', opts));
              c.dispatchEvent(new MouseEvent('mouseup', opts));
              c.dispatchEvent(new MouseEvent('click', opts));
              await sleep(250);
            } else if (step.do === 'selectCellRange') {
              // Programmatic CellSelection fallback (first-row pair) where synthetic shift-click
              // can't build one — mirrors the UI's cell-range selection result.
              if (!(WC.PM && WC.PM.tableSelectFirstRowPair && WC.PM.tableSelectFirstRowPair())) {
                throw new Error('could not build a cell selection');
              }
              await sleep(150);
            } else if (step.do === 'clickShadeSwatch') {
              const sws = Array.from(document.querySelectorAll('.flyout .tbl-shade-sw'));
              const sw = sws[step.index];
              if (!sw) throw new Error('no shading swatch #' + step.index + ' (have ' + sws.length + ')');
              lastDoc = docJson(); sw.click(); await sleep(300);
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
            } else if (ex === 'caretInTable') {
              sr.result = (WC.PM && WC.PM.isInTable && WC.PM.isInTable()) ? 'ok' : 'FAIL(caret not in table)';
            } else if (ex === 'gridLabelIs') {
              const lbl = document.querySelector('.tablegrid-label');
              sr.result = (lbl && new RegExp(step.match, 'i').test(lbl.textContent || '')) ? 'ok'
                : 'FAIL(label: ' + (lbl ? lbl.textContent : 'none') + ')';
            } else if (ex === 'paintedCellCount') {
              const n = paintedCells().length;
              sr.result = n === step.equals ? 'ok' : `FAIL(visible cells=${n}, want ${step.equals})`;
            } else if (ex === 'paintedCellBg') {
              const c = paintedCells()[step.index];
              if (!c) { sr.result = 'FAIL(no painted cell #' + step.index + ')'; }
              else {
                const v = getComputedStyle(c).backgroundColor;
                sr.result = (step.anyOf || [step.value]).some((want) => String(v).replace(/\s/g, '') === String(want).replace(/\s/g, ''))
                  ? 'ok' : `FAIL(bg=${v})`;
              }
            } else if (ex === 'paintedCellBorder') {
              // The live-paint border check (the border-collapse instrument): edge must be a
              // visible line at least minPx wide ON SCREEN — file-clean-but-screen-wrong catcher.
              const c = paintedCells()[step.index];
              if (!c) { sr.result = 'FAIL(no painted cell #' + step.index + ')'; }
              else {
                const cs = getComputedStyle(c);
                const w = parseFloat(cs.getPropertyValue('border-' + step.edge + '-width')) || 0;
                const st = cs.getPropertyValue('border-' + step.edge + '-style');
                const okEdge = st !== 'none' && st !== 'hidden' && w >= (step.minPx || 1);
                sr.result = okEdge ? 'ok' : `FAIL(border-${step.edge}: ${st} ${w}px, want >=${step.minPx || 1}px)`;
              }
            } else if (ex === 'galleryItemCount') {
              const n = document.querySelectorAll('.flyout .fly-item').length;
              const okMin = step.min == null || n >= step.min;
              const okMax = step.max == null || n <= step.max;
              sr.result = (okMin && okMax) ? 'ok'
                : `FAIL(flyout items=${n}, want ${step.min != null ? '>=' + step.min : ''}${step.max != null ? ' <=' + step.max : ''})`;
            } else if (ex === 'toastShown') {
              const t = document.querySelector('.toast');
              sr.result = (t && (!step.match || new RegExp(step.match, 'i').test(t.textContent || ''))) ? 'ok'
                : 'FAIL(' + (t ? 'toast: ' + (t.textContent || '').slice(0, 60) : 'no toast') + ')';
            } else if (ex === 'tabShown') {
              sr.result = document.querySelector('.ribbon-tab[data-tab="' + step.tab + '"]') ? 'ok'
                : 'FAIL(no ribbon tab ' + step.tab + ')';
            } else if (ex === 'tabHidden') {
              sr.result = !document.querySelector('.ribbon-tab[data-tab="' + step.tab + '"]') ? 'ok'
                : 'FAIL(ribbon tab ' + step.tab + ' still shown)';
            } else if (ex === 'paintedTableCount') {
              const n = Array.from(document.querySelectorAll('table'))
                .filter((t) => t.getClientRects().length > 0).length;
              sr.result = n === step.equals ? 'ok' : `FAIL(visible tables=${n}, want ${step.equals})`;
            } else if (ex === 'paintedCellBorderAbsent') {
              const c = paintedCells()[step.index];
              if (!c) { sr.result = 'FAIL(no painted cell #' + step.index + ')'; }
              else {
                const cs = getComputedStyle(c);
                const w = parseFloat(cs.getPropertyValue('border-' + step.edge + '-width')) || 0;
                const st = cs.getPropertyValue('border-' + step.edge + '-style');
                const gone = st === 'none' || st === 'hidden' || w === 0;
                sr.result = gone ? 'ok' : `FAIL(border-${step.edge} still painted: ${st} ${w}px)`;
              }
            } else if (ex === 'paintedCellMinHeight') {
              const c = paintedCells()[step.index];
              if (!c) { sr.result = 'FAIL(no painted cell #' + step.index + ')'; }
              else {
                const h = c.getBoundingClientRect().height;
                sr.result = h >= step.minPx ? 'ok' : `FAIL(cell height ${h}px, want >=${step.minPx}px)`;
              }
            } else if (ex === 'paintedCellStyleIs') {
              const c = paintedCells()[step.index];
              if (!c) { sr.result = 'FAIL(no painted cell #' + step.index + ')'; }
              else {
                const v = getComputedStyle(c).getPropertyValue(step.prop);
                sr.result = (step.anyOf || [step.value]).some((want) => String(v).includes(want))
                  ? 'ok' : `FAIL(${step.prop}=${v})`;
              }
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
