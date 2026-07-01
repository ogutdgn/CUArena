/* Insert Table task — clone side. Insert a plain 3x3 table, export docx. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const ed = window.WC.editor, PM = window.WC.PM;
  const OUT = 'C:/Users/ogutd/OneDrive/Desktop/new-coding/ms-word-clone/parity/fixtures/wc-table.docx';
  const out = { ready: !!window.__WC_READY };
  try {
    ed.commands.selectAll(); ed.commands.insertContent('<p></p>'); await sleep(60);
    out.insertOk = PM.insertTable({ rows: 3, cols: 3 }); await sleep(300);
    const bytes = await PM.exportDocxBytes();
    out.save = await window.wordAPI.saveBytes({ filePath: OUT, bytes });
  } catch (e) { out.err = String(e && e.message) + '\n' + String(e && e.stack); }
  return JSON.stringify(out, null, 2);
})();
