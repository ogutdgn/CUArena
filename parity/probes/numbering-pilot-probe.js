/* Numbering task — clone side. Type "Revenue", select it, apply a default numbered list, export docx. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const ed = window.WC.editor, PM = window.WC.PM, TS = window.__PM_TextSelection;
  const OUT = 'C:/Users/ogutd/OneDrive/Desktop/new-coding/ms-word-clone/parity/fixtures/wc-numbering.docx';
  const out = { ready: !!window.__WC_READY };
  try {
    ed.commands.selectAll(); ed.commands.insertContent('<p>Revenue</p>');
    ed.commands.selectAll(); ed.commands.unsetAllMarks(); await sleep(80);
    let f = null;
    ed.state.doc.descendants((n, p) => { if (f || !n.isText || !n.text) return; const i = n.text.indexOf('Revenue'); if (i >= 0) f = { from: p + i, to: p + i + 7 }; });
    ed.view.dispatch(ed.view.state.tr.setSelection(TS.create(ed.state.doc, f.from, f.to)));
    PM.cmd('toggleOrderedList'); await sleep(120);
    const bytes = await PM.exportDocxBytes();
    out.save = await window.wordAPI.saveBytes({ filePath: OUT, bytes });
  } catch (e) { out.err = String(e && e.message) + '\n' + String(e && e.stack); }
  return JSON.stringify(out, null, 2);
})();
