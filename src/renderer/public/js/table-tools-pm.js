/* table-tools-pm.js — PM Table Tools chrome (slice 6, Task 10).

   Two runtime-injected contextual ribbon tabs (Table Layout + Table Design) that
   mirror header-footer.js's contextualTab() + WC.Ribbon.showContextualTab(def).
   CRITICAL: the ribbon renderer dispatches controls by { cmd, label, type } →
   WC.Commands.run/dropdown({cmd}) → H[cmd]; it IGNORES inline onClick. So every
   control here is a cmd-dispatch control pointing at an H.tbl* handler (commands.js).

   syncContextualTabs(inTable) shows BOTH tabs when the caret enters a table and
   hides them when it leaves (driven from bridge/state-sync.ts). Plus an OPTIONAL,
   narrowly-scoped PM right-click context menu on #pm-editor (B4). */
(function () {
  window.WC = window.WC || {};
  const WC = window.WC;
  const el = WC.el;
  const PM = () => (WC.PM && WC.PM.active && WC.PM.ready) ? WC.PM : null;
  let shown = false;

  // ---- Table Layout contextual tab (Word Mac displays it as plain 'Layout' —
  // .oracle-probes/slice6/results.md shows 'Table Design' + 'Layout'; id stays
  // 'table-layout' so it can't collide with the standard Layout tab id) ----
  function layoutTab() {
    return {
      id: 'table-layout', name: 'Layout', contextual: true, groups: [
        { id: 'tl-rowscols', name: 'Rows & Columns', controls: [
          { cmd: 'tblInsertAbove', label: 'Insert Above', type: 'button' },
          { cmd: 'tblInsertBelow', label: 'Insert Below', type: 'button' },
          { cmd: 'tblInsertLeft', label: 'Insert Left', type: 'button' },
          { cmd: 'tblInsertRight', label: 'Insert Right', type: 'button' },
          { cmd: 'tblDeleteRow', label: 'Delete Row', type: 'button' },
          { cmd: 'tblDeleteColumn', label: 'Delete Column', type: 'button' },
          { cmd: 'tblDeleteTable', label: 'Delete Table', type: 'button' },
        ] },
        { id: 'tl-merge', name: 'Merge', controls: [
          { cmd: 'tblMerge', label: 'Merge Cells', type: 'button' },
          { cmd: 'tblSplitCell', label: 'Split Cells', type: 'button' },
          { cmd: 'tblSplitTable', label: 'Split Table', type: 'button' },
        ] },
        { id: 'tl-cellsize', name: 'Cell Size', controls: [
          { cmd: 'tblRowHeight', label: 'Row Height', type: 'dropdown' },
          { cmd: 'tblColWidth', label: 'Column Width', type: 'dropdown' },
          { cmd: 'tblDistRows', label: 'Distribute Rows', type: 'button' },
          { cmd: 'tblDistCols', label: 'Distribute Columns', type: 'button' },
          { cmd: 'tblAutoFit', label: 'AutoFit', type: 'dropdown' },
        ] },
        { id: 'tl-align', name: 'Alignment', controls: [
          { cmd: 'tblVAlignTop', label: 'Align Top', type: 'button' },
          { cmd: 'tblVAlignMid', label: 'Align Middle', type: 'button' },
          { cmd: 'tblVAlignBottom', label: 'Align Bottom', type: 'button' },
          { cmd: 'tblTextDir', label: 'Text Direction', type: 'button' },
          { cmd: 'tblCellMargins', label: 'Cell Margins', type: 'button' },
        ] },
        { id: 'tl-data', name: 'Data', controls: [
          { cmd: 'tblToText', label: 'Convert to Text', type: 'button' },
          { cmd: 'tblHeaderRow', label: 'Header Row', type: 'button' },
          { cmd: 'tblHeaderCol', label: 'Header Column', type: 'button' },
        ] },
      ],
    };
  }

  // ---- Table Design contextual tab ----
  function designTab() {
    return {
      id: 'table-design', name: 'Table Design', contextual: true, groups: [
        { id: 'td-styles', name: 'Table Styles', controls: [
          { cmd: 'tblStyles', label: 'Table Styles', type: 'dropdown' },
          { cmd: 'tblShading', label: 'Shading', type: 'dropdown' },
          { cmd: 'tblBorders', label: 'Borders', type: 'dropdown' },
        ] },
        { id: 'td-align', name: 'Alignment', controls: [
          { cmd: 'tblAlignLeft', label: 'Align Left', type: 'button' },
          { cmd: 'tblAlignCenter', label: 'Align Center', type: 'button' },
          { cmd: 'tblAlignRight', label: 'Align Right', type: 'button' },
          { cmd: 'tblIndent', label: 'Indent', type: 'dropdown' },
        ] },
      ],
    };
  }

  // Show/hide BOTH contextual tabs as the caret enters/leaves a table. Idempotent:
  // the `shown` guard prevents re-injection; the multi-tab ribbon API (ribbon.js)
  // lets Design + Layout coexist, and hideContextualTab(id) removes one at a time.
  function syncContextualTabs(inTable) {
    if (!WC.Ribbon || !WC.Ribbon.showContextualTab) return;
    if (inTable && !shown) {
      // PASSIVE, like real Word: the tabs appear but never steal the active tab
      // (probe S1.x — Word's active ribbon tab is unchanged on caret entry).
      WC.Ribbon.showContextualTab(designTab(), { activate: false });
      WC.Ribbon.showContextualTab(layoutTab(), { activate: false });
      shown = true;
    } else if (!inTable && shown) {
      // Teardown safety (spec 030 T007): the Table Design tab (with the styles gallery) is about to
      // be removed — if a hover live-preview is still active, restore the pre-preview state first so
      // the transient bake isn't left applied when the tab disappears mid-hover.
      try { if (WC.PM && WC.PM.tableStylePreviewLeave) WC.PM.tableStylePreviewLeave(); } catch (e) { /* preview verb absent pre-mount */ }
      WC.Ribbon.hideContextualTab('table-design');
      WC.Ribbon.hideContextualTab('table-layout');
      shown = false;
    }
  }

  // PM right-click table context menu (the legacy WC.Table menu is bound to the
  // hidden #editor in PM mode). B4: preventDefault ONLY when the right-click target
  // is inside a td/th AND a table is active, so ProseMirror's native cell-selection
  // / column-resize / gapcursor on the rest of the editor are never blocked.
  function installContextMenu() {
    const mount = document.getElementById('pm-editor');
    if (!mount || mount.__tblMenuBound) return;
    mount.__tblMenuBound = true;
    mount.addEventListener('contextmenu', (e) => {
      const p = PM();
      if (!p || !p.isInTable || !p.isInTable()) return;
      const inCell = e.target && e.target.closest && e.target.closest('td,th');
      if (!inCell) return;
      e.preventDefault();
      WC.closeFlyouts();
      const fly = el('div', { class: 'flyout' });
      const item = (label, fn) => fly.appendChild(WC.flyItem(label, { onClick: () => { WC.closeFlyouts(); fn(); } }));
      item('Insert Row Above', () => { const q = PM(); if (q) q.tableAddRow('above'); });
      item('Insert Row Below', () => { const q = PM(); if (q) q.tableAddRow('below'); });
      item('Insert Column Left', () => { const q = PM(); if (q) q.tableAddColumn('left'); });
      item('Insert Column Right', () => { const q = PM(); if (q) q.tableAddColumn('right'); });
      fly.appendChild(WC.flySep());
      item('Delete Row', () => { const q = PM(); if (q) q.tableDeleteRow(); });
      item('Delete Column', () => { const q = PM(); if (q) q.tableDeleteColumn(); });
      item('Delete Table', () => { const q = PM(); if (q) q.tableDeleteTable(); });
      fly.appendChild(WC.flySep());
      item('Merge Cells', () => { const q = PM(); if (q) q.tableMerge(); });
      item('Split Cell', () => { const q = PM(); if (q) q.tableSplitCell(); });
      document.body.appendChild(fly);
      fly.style.left = Math.min(e.clientX, window.innerWidth - fly.offsetWidth - 4) + 'px';
      fly.style.top = Math.min(e.clientY, window.innerHeight - fly.offsetHeight - 4) + 'px';
      const close = (ev) => { if (!fly.contains(ev.target)) { fly.remove(); document.removeEventListener('mousedown', close, true); } };
      setTimeout(() => document.addEventListener('mousedown', close, true), 0);
    });
  }

  // Teardown safety (spec 030 T007): closing any flyout must also cancel an active table-style
  // hover live-preview. Rather than change WC.closeFlyouts's semantics for every caller (util.js),
  // COMPOSE over it once: wrap the current closeFlyouts so it calls tableStylePreviewLeave first,
  // then delegates to the original. Idempotent (a __tblPreviewWrapped guard prevents double-wrap).
  // Mirrors util.js closeFly's own drawing-preview cleanup (pm.dePreviewEnd) — same intent, no core edit.
  function wrapCloseFlyouts() {
    if (!WC.closeFlyouts || WC.closeFlyouts.__tblPreviewWrapped) return;
    const orig = WC.closeFlyouts;
    const wrapped = function () {
      try { if (WC.PM && WC.PM.active && WC.PM.ready && WC.PM.tableStylePreviewLeave) WC.PM.tableStylePreviewLeave(); } catch (e) { /* preview verb absent */ }
      return orig.apply(this, arguments);
    };
    wrapped.__tblPreviewWrapped = true;
    WC.closeFlyouts = wrapped;
  }

  function install() { installContextMenu(); wrapCloseFlyouts(); }

  WC.TableToolsPM = { syncContextualTabs, installContextMenu, layoutTab, designTab };
  if (document.readyState !== 'loading') setTimeout(install, 0);
  else document.addEventListener('DOMContentLoaded', install);
})();
