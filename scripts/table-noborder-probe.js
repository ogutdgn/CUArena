(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 200 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  WC.PM.insertTable({ rows: 3, cols: 3 });
  await sleep(500);
  const NIL = { val: 'none', color: 'auto', size: 0, space: 0 };
  // No Border on the caret cell (1,1)
  WC.PM.tableSetCellBorders({ top: NIL, bottom: NIL, left: NIL, right: NIL, insideH: NIL, insideV: NIL }, { merge: false });
  await sleep(700);
  const xml = await WC.editor.exportDocx({ exportXmlOnly: true });
  const firstTc = (xml.match(/<w:tc>[\s\S]*?<\/w:tcPr>/) || [''])[0];
  return JSON.stringify({ tcBorders: (firstTc.match(/<w:tcBorders>[\s\S]*?<\/w:tcBorders>/) || ['none'])[0].replace(/\s+/g, ' ') }, null, 2);
})()
