/* Ribbon UI capture probe (Tables parity loop). Boots the app, inserts a table so the
   contextual Table tabs appear, activates the requested tab (WC_RIBBON_TAB or table-design),
   and dumps the visible table controls. The --shot=PNG captures the visual for eyeballing.
   Run: electron . --shot=C:/tmp/wc-ribbon-design.png --shot-evalfile=scripts/ribbon-shot-probe.js --shot-delay=1400 --probe-out=/tmp/wc-ribbon.json */
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < 200 && !window.__WC_READY; i++) await sleep(50);
  const WC = window.WC;
  const out = { steps: [], mode: (window.WC_LAYOUT || '') };
  const tabId = window.localStorage.getItem('WC_RIBBON_TAB') || 'table-design';
  try {
    WC.PM.insertTable({ rows: 3, cols: 3 });
    out.steps.push('inserted 3x3 table');
    await sleep(600);
    if (WC.Ribbon && WC.Ribbon.activate) { WC.Ribbon.activate(tabId); out.steps.push('activated ' + tabId); }
    await sleep(600);
    // Which tabs exist + which is active
    out.tabs = Array.from(document.querySelectorAll('.ribbon-tabs .tab, .ribbon-tab, [data-ribbon-tab]')).map((n) => ({
      text: n.textContent.trim(), active: /active/.test(n.className),
    }));
    // The table controls currently rendered + how (label vs icon-only, checkbox?)
    out.tableControls = Array.from(document.querySelectorAll('.rbtn, .rsplit')).map((n) => ({
      cmd: n.dataset && n.dataset.cmd,
      lbl: (n.querySelector('.lbl') && n.querySelector('.lbl').textContent) || '',
      iconOnly: n.classList.contains('icononly'),
      hasCheckbox: !!n.querySelector('input[type="checkbox"]'),
    })).filter((c) => c.cmd && /^tbl/.test(c.cmd));
    out.groups = Array.from(document.querySelectorAll('.ribbon-group-label')).map((n) => n.textContent.trim());
  } catch (e) { out.error = String((e && e.message) || e); }
  return JSON.stringify(out, null, 2);
})()
