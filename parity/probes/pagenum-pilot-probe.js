/* Page Number task — clone side. Insert a bottom page-number field, export docx. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const ed = window.WC.editor, PM = window.WC.PM;
  const OUT = 'C:/Users/ogutd/OneDrive/Desktop/new-coding/ms-word-clone/parity/fixtures/wc-pagenum.docx';
  const out = { ready: !!window.__WC_READY };
  try {
    // Start from the SAME clean empty doc as the blank baseline so blank-document
    // boilerplate (the clone's demo ListParagraph nodes) cancels under subtraction.
    ed.commands.selectAll(); ed.commands.insertContent('<p></p>');
    ed.commands.selectAll(); ed.commands.unsetAllMarks(); await sleep(80);
    PM.insertPageNumber({ position: 'bottom' });
    await sleep(400);
    const bytes = await PM.exportDocxBytes();
    out.save = await window.wordAPI.saveBytes({ filePath: OUT, bytes });
  } catch (e) { out.err = String(e && e.message) + '\n' + String(e && e.stack); }
  return JSON.stringify(out, null, 2);
})();
