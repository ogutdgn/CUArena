/* Scorecard probe — the SCORECARD parity axis: click EVERY top-level ribbon control in the
   live app (all main tabs + the table contextual tabs) and classify what actually happens:
     flyout (with real items?) / dialog / doc-change / toast (honest stub) / SILENT (nothing).
   Generalizes scripts/table-scorecard.js — the audit that caught the 6 dead "(no options)"
   dropdowns — to the whole ribbon. Native-shell commands (open/save/print/...) are skipped.
   Returns JSON via --probe-out; parity/engines/scorecard_verify.py writes the ledger. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC, ed = () => WC.editor, TS = window.__PM_TextSelection;
  const DEEP = !!window.__SC_DEEP;   // deep mode: also click every menu ITEM (D3.2)
  const out = { ready: !!window.__WC_READY, deep: DEEP, controls: [], errors: [] };
  const docJson = () => JSON.stringify(ed().state.doc.toJSON());
  // D3.3 — UI fingerprint: invisible-but-real effects (panes, view classes, zoom, selection,
  // ruler) so working controls stop landing in SILENT.
  const uiFingerprint = () => {
    let sel = '';
    try { sel = ed().state.selection.from + '-' + ed().state.selection.to; } catch (e) {}
    const zoomEl = document.querySelector('#pages, .pages, .editor-scale');
    return JSON.stringify({
      body: document.body.className,
      panes: document.querySelectorAll('.pane, .wc-pane, .task-pane, .sidebar, [data-pane], .wc-sidebar').length,
      zoom: zoomEl ? (zoomEl.style.transform || '') + (zoomEl.style.zoom || '') : '',
      ruler: !!document.querySelector('.ruler, .wc-ruler'),
      sel,
    });
  };
  const clipText = async () => { try { return await navigator.clipboard.readText(); } catch (e) { return null; } };
  // Menu items that reach the native shell (file pickers etc.) — never click in deep mode.
  const NATIVE_ITEM = /from file|this device|browse|open|save|print|excel spreadsheet/i;

  // Commands that reach the native shell / window chrome — never click these headlessly.
  const NATIVE = /^(open|save|saveas|savecopy|print|share|export|publish|closedoc|close|quit|exit|newblank|new|recent|fullscreen|focus(mode)?|zoomdialog|switchwindows|newwindow|dictate)$/i;
  const NATIVE_LABEL = /open|save|print|share|export|new window|switch windows|full.?screen|focus/i;

  const closeAll = async () => {
    try { WC.closeFlyouts && WC.closeFlyouts(); } catch (e) {}
    document.querySelectorAll('.dialog, .wc-dialog, .modal').forEach((d) => {
      const b = Array.from(d.querySelectorAll('button')).find((x) => /cancel|close|✕|x/i.test((x.textContent || '').trim()));
      if (b) b.click(); else d.remove();
    });
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    await sleep(40);
  };

  const freshDoc = async (needTable) => {
    await closeAll();
    ed().commands.selectAll();
    ed().commands.insertContent('<p>Revenue</p>');
    await sleep(40);
    if (needTable) {
      WC.PM.insertTable({ rows: 2, cols: 2 });
      await sleep(200);
      let cell = 0; ed().state.doc.descendants((n, p) => { if (!cell && (n.type.name === 'tableCell' || n.type.name === 'tableHeader')) cell = p; });
      if (cell) ed().view.dispatch(ed().state.tr.setSelection(TS.create(ed().state.doc, cell + 2)));
    } else {
      let f = null; ed().state.doc.descendants((n, p) => { if (f || !n.isText || !n.text) return; const i = n.text.indexOf('Revenue'); if (i >= 0) f = { from: p + i, to: p + i + 7 }; });
      if (f) ed().view.dispatch(ed().state.tr.setSelection(TS.create(ed().state.doc, f.from, f.to)));
    }
    await sleep(60);
  };

  // Collect: [tabId, needTable, control] for every top-level control + group launcher.
  const plan = [];
  const tabs = (WC.RIBBON && (WC.RIBBON.tabs || WC.RIBBON)) || [];
  (Array.isArray(tabs) ? tabs : []).forEach((t) => (t.groups || []).forEach((g) => {
    (g.controls || []).forEach((c) => plan.push([t.id, false, c, g.id]));
    if (g.launcher) plan.push([t.id, false, { ...g.launcher, type: g.launcher.type || 'button', _launcher: true }, g.id]);
  }));
  // Contextual table tabs: capture defs via the injection intercept.
  try {
    const captured = {};
    const orig = WC.Ribbon.showContextualTab.bind(WC.Ribbon);
    WC.Ribbon.showContextualTab = (def, opts) => { if (def && def.id) captured[def.id] = def; return orig(def, opts); };
    await freshDoc(true);
    await sleep(300);
    WC.Ribbon.showContextualTab = orig;
    Object.values(captured).forEach((t) => (t.groups || []).forEach((g) =>
      (g.controls || []).forEach((c) => plan.push([t.id, true, c, g.id]))));
  } catch (e) { out.errors.push('contextual: ' + String(e && e.message)); }

  let curTab = null;
  for (const [tabId, needTable, c, gid] of plan) {
    const rec = { tab: tabId, group: gid || null, cmd: c.cmd || null, label: c.label || '', type: c.type || 'button', launcher: !!c._launcher };
    try {
      if (!c.cmd || NATIVE.test(c.cmd) || NATIVE_LABEL.test(c.label || '')) {
        rec.result = 'SKIPPED_NATIVE'; out.controls.push(rec); continue;
      }
      await freshDoc(needTable);
      if (curTab !== tabId) { WC.Ribbon.activate(tabId); await sleep(120); curTab = tabId; }
      const groupSel = gid ? '.ribbon-group[data-group="' + gid + '"] ' : '';
      let elc = document.querySelector('[data-cmd="' + c.cmd + '"]')
        || (c.id && document.querySelector('[data-id="' + c.id + '"]'));
      // Launchers render as a bare span.launcher in the group label (no data attrs).
      if (!elc && c._launcher && gid) elc = document.querySelector(groupSel + '.launcher');
      // Some declared dropdowns/galleries render as INLINE strips (Home Styles, Pens,
      // Table Styles) — presence + populated tiles is the pass criterion; don't click
      // (hover/live-preview side effects).
      if (!elc && gid) {
        const inline = document.querySelector(groupSel + '.rgallery, ' + groupSel + '.pens-gallery, '
          + groupSel + '.styles-gallery, ' + groupSel + '.tblstyle-cell');
        if (inline) {
          const groupEl = document.querySelector('.ribbon-group[data-group="' + gid + '"]');
          const tiles = groupEl.querySelectorAll('.rgallery-track > *, .pen-tile, .style-tile, .tblstyle-cell, [data-style]').length;
          rec.itemCount = tiles;
          rec.result = tiles > 0 ? 'OK_GALLERY_INLINE' : 'SUSPECT_EMPTY_GALLERY';
          out.controls.push(rec); continue;
        }
      }
      if (!elc) { rec.result = 'NO_NODE'; out.controls.push(rec); continue; }
      const before = docJson();
      if (c.type === 'dropdown' || c.type === 'split' || c.type === 'gallery') {
        try { WC.Commands.dropdown(c, elc); } catch (e) { elc.click(); }
        await sleep(220);
        const fly = document.querySelector('.flyout');
        const items = Array.from(document.querySelectorAll('.flyout .fly-item')).map((n) => (n.textContent || '').trim()).filter(Boolean);
        const rich = document.querySelector('.flyout .wc-color-palette, .flyout .color-swatch, .flyout .swatch, .flyout .sw, .flyout [data-color], .flyout input, .flyout .rspinner, .flyout .gallery, .flyout img, .flyout svg');
        const dead = items.length === 1 && /no options/i.test(items[0]);
        rec.itemCount = items.length; rec.items = items.slice(0, 12);
        rec.result = !fly ? (document.querySelector('.dialog, .wc-dialog, .modal') ? 'DIALOG' : 'DEAD_NO_FLYOUT')
          : dead ? 'DEAD_NO_OPTIONS'
            : (items.length > 0 || rich) ? 'OK_FLYOUT' : 'SUSPECT_EMPTY_FLYOUT';
        // D3.2 deep mode — click every item of a healthy flyout, classify each.
        if (DEEP && rec.result === 'OK_FLYOUT' && items.length > 0) {
          rec.itemResults = [];
          for (let ii = 0; ii < items.length; ii++) {
            const ir = { label: items[ii] };
            try {
              if (NATIVE_ITEM.test(items[ii])) { ir.result = 'SKIPPED_NATIVE'; rec.itemResults.push(ir); continue; }
              await freshDoc(needTable);
              if (curTab !== tabId) { WC.Ribbon.activate(tabId); await sleep(100); curTab = tabId; }
              try { WC.Commands.dropdown(c, elc); } catch (e) { elc.click(); }
              await sleep(180);
              const nodes = Array.from(document.querySelectorAll('.flyout .fly-item'));
              const node = nodes.find((n) => (n.textContent || '').trim() === items[ii]) || nodes[ii];
              if (!node) { ir.result = 'NO_NODE'; rec.itemResults.push(ir); continue; }
              const b4 = docJson(); const fp4 = uiFingerprint();
              const flyB4 = Array.from(document.querySelectorAll('.flyout')).map((f) => f.innerText).join('§');
              node.click();
              await sleep(220);
              const dlg2 = document.querySelector('.dialog, .wc-dialog, .modal');
              const toast2 = document.querySelector('.toast');
              const flyNow = Array.from(document.querySelectorAll('.flyout')).map((f) => f.innerText).join('§');
              ir.result = dlg2 ? 'DIALOG' : (docJson() !== b4 ? 'OK_DOC_CHANGED'
                : toast2 ? 'STUB_TOAST'
                  : (flyNow && flyNow !== flyB4) ? 'OK_SUBMENU'
                    : (uiFingerprint() !== fp4 ? 'OK_UI_EFFECT' : 'ITEM_SILENT'));
              await closeAll();
            } catch (e) { ir.result = 'ERROR'; ir.err = String(e && e.message); }
            rec.itemResults.push(ir);
          }
        }
      } else if (c.type === 'combo' || c.type === 'spinner') {
        rec.result = (elc.querySelector('input, select') || /input|select/i.test(elc.tagName)) ? 'OK_INPUT' : 'SUSPECT_NO_INPUT';
      } else {
        const fpBefore = uiFingerprint();
        const clipBefore = /^(copy|cut)$/i.test(c.cmd) ? await clipText() : null;
        elc.click();
        await sleep(260);
        const dlg = document.querySelector('.dialog, .wc-dialog, .modal');
        const toast = document.querySelector('.toast');
        const fly = document.querySelector('.flyout');
        const after = docJson();
        rec.result = dlg ? 'DIALOG' : (after !== before ? 'OK_DOC_CHANGED'
          : toast ? 'STUB_TOAST' : fly ? 'OK_FLYOUT' : 'SILENT');
        if (toast) rec.toast = (toast.textContent || '').trim().slice(0, 80);
        // D3.3 — SILENT rescue: clipboard readback, then the UI fingerprint.
        if (rec.result === 'SILENT') {
          if (/^(copy|cut)$/i.test(c.cmd)) {
            const clipAfter = await clipText();
            if (clipAfter !== null && clipAfter !== clipBefore && clipAfter.length > 0) rec.result = 'OK_CLIPBOARD';
          }
          if (rec.result === 'SILENT' && uiFingerprint() !== fpBefore) rec.result = 'OK_UI_EFFECT';
        }
      }
      await closeAll();
    } catch (e) { rec.result = 'ERROR'; rec.err = String(e && e.message); }
    out.controls.push(rec);
  }
  return JSON.stringify(out, null, 1);
})();
