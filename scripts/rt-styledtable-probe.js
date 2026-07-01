(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 200 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  const out = { steps: [] };
  try {
    const r = await window.wordAPI.openBytes('tests/fixtures/realword-gridtable4-accent1.docx');
    if (!r || !r.bytes) return JSON.stringify({ err: 'openBytes failed', r: !!r });
    out.steps.push('openBytes ' + r.bytes.length + ' bytes');
    const ok = await WC.PM.openDocx(r.bytes);
    out.imported = ok; await sleep(500);
    const bytes = await WC.PM.exportDocxBytes();
    await window.wordAPI.saveBytes({ filePath: 'C:/tmp/wc-rt-gt4.docx', bytes });
    out.steps.push('re-exported ' + bytes.length + ' bytes');
  } catch (e) { out.err = String((e && e.message) || e); }
  return JSON.stringify(out, null, 2);
})()
