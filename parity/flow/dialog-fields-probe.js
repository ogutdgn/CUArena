/* Dialog-fields probe (clone side of rubric D2.2) — open each locked-feature dialog in the live
   clone and dump its fields (labels, control types, tabs) so the Python differ can compare
   against the Word UIA dump. Dialogs open via WC.Dialogs.<fn>() (the map in dialog_targets).
   Returns {dialogs: {key: {found, title, tabs[], fields:[{name,type}]}}} via --probe-out. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC, ed = () => WC.editor;
  const out = { ready: !!window.__WC_READY, dialogs: {}, errors: [] };
  // logical key -> clone opener (WC.Dialogs fn name). Keys match dump_dialog_uia.ps1 -Key.
  const TARGETS = {
    font: 'font', paragraph: 'paragraph', findadv: 'findPane', wordcount: 'wordCount',
    paste_special: 'setDefaultPaste', insert_table: 'insertTable', page_setup: null,
  };
  const dialogSel = '.dialog, .wc-dialog, .modal, #styles-pane, .task-pane, [class*="pane"]';

  const dumpOpen = () => {
    const dlg = document.querySelector('.dialog, .wc-dialog, .modal') || document.querySelector(dialogSel);
    if (!dlg) return null;
    const fields = [];
    dlg.querySelectorAll('input, select, textarea, button').forEach((n) => {
      let name = '';
      // label: wrapping <label>, preceding sibling text, aria-label, placeholder, or button text.
      const lab = n.closest('label');
      if (lab) name = lab.textContent.trim();
      if (!name && n.previousElementSibling) name = (n.previousElementSibling.textContent || '').trim();
      if (!name) name = n.getAttribute('aria-label') || n.getAttribute('placeholder') || '';
      if (!name && n.tagName === 'BUTTON') name = n.textContent.trim();
      const type = n.tagName === 'INPUT' ? (n.type || 'text')
        : n.tagName === 'SELECT' ? 'select' : n.tagName === 'TEXTAREA' ? 'textarea' : 'button';
      if (name) fields.push({ name: name.slice(0, 60), type });
    });
    const tabs = Array.from(dlg.querySelectorAll('.bs-tab, .tab, [role="tab"]')).map((t) => (t.textContent || '').trim()).filter(Boolean);
    const titleEl = dlg.querySelector('.dialog-title, .title, h2, header');
    return { title: titleEl ? titleEl.textContent.trim() : '', tabs, fields };
  };
  const closeAll = async () => {
    document.querySelectorAll('.dialog, .wc-dialog, .modal, #styles-pane, .task-pane').forEach((d) => {
      const b = Array.from(d.querySelectorAll('button')).find((x) => /cancel|close|✕/i.test((x.textContent || '').trim()));
      if (b) b.click(); else d.remove();
    });
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    await sleep(80);
  };

  ed().commands.selectAll(); ed().commands.insertContent('<p>Revenue</p>');
  await sleep(120);
  for (const [key, fn] of Object.entries(TARGETS)) {
    const rec = { found: false };
    try {
      if (fn && WC.Dialogs && typeof WC.Dialogs[fn] === 'function') {
        await closeAll();
        // reselect a word so dialogs that read selection populate
        try { const f = (() => { let r = null; ed().state.doc.descendants((n, p) => { if (!r && n.isText && n.text && n.text.includes('Revenue')) r = { from: p, to: p + 7 }; }); return r; })();
          if (f) ed().view.dispatch(ed().state.tr.setSelection(window.__PM_TextSelection.create(ed().state.doc, f.from, f.to))); } catch (e) {}
        WC.Dialogs[fn]();
        await sleep(250);
        const d = dumpOpen();
        if (d) { rec.found = true; Object.assign(rec, d); }
        await closeAll();
      } else {
        rec.note = fn ? 'WC.Dialogs.' + fn + ' absent' : 'no clone opener mapped';
      }
    } catch (e) { rec.error = String(e && e.message); }
    out.dialogs[key] = rec;
  }
  return JSON.stringify(out, null, 1);
})();
