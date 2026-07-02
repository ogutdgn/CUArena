/* Blank baseline — clone side. Clear to ONE empty paragraph and export docx.
   This is the clone's empty-doc baseline that the v2 differ subtracts from every
   feature task, so blank-document boilerplate cancels and only the feature delta
   remains. It must match how the feature probes START (selectAll + insertContent
   '<p></p>'), so the shared boilerplate is identical and cancels exactly. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const ed = window.WC.editor, PM = window.WC.PM;
  const OUT = 'C:/Users/ogutd/OneDrive/Desktop/new-coding/ms-word-clone/parity/fixtures/wc-blank.docx';
  const out = { ready: !!window.__WC_READY };
  try {
    ed.commands.selectAll(); ed.commands.insertContent('<p></p>');
    ed.commands.selectAll(); ed.commands.unsetAllMarks(); await sleep(80);
    const bytes = await PM.exportDocxBytes();
    out.save = await window.wordAPI.saveBytes({ filePath: OUT, bytes });
  } catch (e) { out.err = String(e && e.message) + '\n' + String(e && e.stack); }
  return JSON.stringify(out, null, 2);
})();
