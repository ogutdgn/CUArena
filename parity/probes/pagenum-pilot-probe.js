/* Page Number task — clone side. Insert a bottom page-number field, export docx. */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 600 && !window.__WC_READY; i++) await sleep(50);
  const PM = window.WC.PM;
  const OUT = 'C:/Users/ogutd/OneDrive/Desktop/new-coding/ms-word-clone/parity/fixtures/wc-pagenum.docx';
  const out = { ready: !!window.__WC_READY };
  try {
    PM.insertPageNumber({ position: 'bottom' });
    await sleep(400);
    const bytes = await PM.exportDocxBytes();
    out.save = await window.wordAPI.saveBytes({ filePath: OUT, bytes });
  } catch (e) { out.err = String(e && e.message) + '\n' + String(e && e.stack); }
  return JSON.stringify(out, null, 2);
})();
