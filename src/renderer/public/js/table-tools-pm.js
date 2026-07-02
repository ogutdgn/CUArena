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
    // Spec 033: Word's Table Layout tab, 7 groups in order — Table | Rows & Columns | Merge |
    // Cell Size | Alignment | Data | Draw. Labels mirror Word's idMso labels (parity/oracle/
    // word_ribbon_inventory.json → tab TabTableToolsLayout). The misplaced Header Row/Header Column
    // buttons were REMOVED (they are Design-tab Table Style Options, already on the Design tab).
    return {
      id: 'table-layout', name: 'Layout', contextual: true, groups: [
        { id: 'tl-table', name: 'Table', controls: [
          { cmd: 'tblSelect', label: 'Select', type: 'dropdown' },
          { cmd: 'tblViewGridlines', label: 'View Gridlines', type: 'toggle' },
          { cmd: 'tblProperties', label: 'Properties', type: 'button' },
        ] },
        { id: 'tl-rowscols', name: 'Rows & Columns', controls: [
          { cmd: 'tblDelete', label: 'Delete', type: 'dropdown' },
          { cmd: 'tblInsertAbove', label: 'Insert Above', type: 'button' },
          { cmd: 'tblInsertBelow', label: 'Insert Below', type: 'button' },
          { cmd: 'tblInsertLeft', label: 'Insert Left', type: 'button' },
          { cmd: 'tblInsertRight', label: 'Insert Right', type: 'button' },
          { cmd: 'tblInsertCells', label: 'Insert Cells', type: 'button' },
        ] },
        { id: 'tl-merge', name: 'Merge', controls: [
          { cmd: 'tblMerge', label: 'Merge Cells', type: 'button' },
          { cmd: 'tblSplitCell', label: 'Split Cells', type: 'button' },
          { cmd: 'tblSplitTable', label: 'Split Table', type: 'button' },
        ] },
        { id: 'tl-cellsize', name: 'Cell Size', controls: [
          { cmd: 'tblAutoFit', label: 'AutoFit', type: 'dropdown' },
          { cmd: 'tblRowHeight', label: 'Height:', type: 'dropdown' },
          { cmd: 'tblColWidth', label: 'Width:', type: 'dropdown' },
          { cmd: 'tblDistRows', label: 'Distribute Rows', type: 'button' },
          { cmd: 'tblDistCols', label: 'Distribute Columns', type: 'button' },
        ] },
        { id: 'tl-align', name: 'Alignment', controls: [
          // Word's 3×3 cell-alignment grid (vertical vAlign × horizontal jc).
          { cmd: 'tblAlignTL', label: 'Align Top Left', type: 'button' },
          { cmd: 'tblAlignTC', label: 'Align Top Center', type: 'button' },
          { cmd: 'tblAlignTR', label: 'Align Top Right', type: 'button' },
          { cmd: 'tblAlignML', label: 'Align Center Left', type: 'button' },
          { cmd: 'tblAlignMC', label: 'Align Center', type: 'button' },
          { cmd: 'tblAlignMR', label: 'Align Center Right', type: 'button' },
          { cmd: 'tblAlignBL', label: 'Align Bottom Left', type: 'button' },
          { cmd: 'tblAlignBC', label: 'Align Bottom Center', type: 'button' },
          { cmd: 'tblAlignBR', label: 'Align Bottom Right', type: 'button' },
          { cmd: 'tblTextDir', label: 'Text Direction', type: 'button' },
          { cmd: 'tblCellMargins', label: 'Cell Margins', type: 'button' },
        ] },
        { id: 'tl-data', name: 'Data', controls: [
          { cmd: 'tblSort', label: 'Sort', type: 'dropdown' },
          { cmd: 'tblRepeatHeader', label: 'Repeat Header Rows', type: 'toggle' },
          { cmd: 'tblToText', label: 'Convert to Text', type: 'button' },
          { cmd: 'tblFormula', label: 'Formula', type: 'button' },
        ] },
        { id: 'tl-draw', name: 'Draw', controls: [
          { cmd: 'tblDrawTable', label: 'Draw Table', type: 'button' },
          { cmd: 'tblEraser', label: 'Eraser', type: 'button' },
        ] },
      ],
    };
  }

  // ---- Table Design contextual tab ----
  function designTab() {
    return {
      id: 'table-design', name: 'Table Design', contextual: true, groups: [
        // Spec 031: Word's FIRST Table Design group — six labeled checkboxes (2 cols x 3 rows:
        // Header Row/First Column, Total Row/Last Column, Banded Rows/Banded Columns). Each is a
        // cmd-dispatch control → H.tblStyle* (commands.js) → WC.PM.tableStyleOption(opt, checked).
        { id: 'td-styleopts', name: 'Table Style Options', controls: [
          { cmd: 'tblStyleHeaderRow', label: 'Header Row', type: 'checkbox' },
          { cmd: 'tblStyleTotalRow', label: 'Total Row', type: 'checkbox' },
          { cmd: 'tblStyleBandedRows', label: 'Banded Rows', type: 'checkbox' },
          { cmd: 'tblStyleFirstCol', label: 'First Column', type: 'checkbox' },
          { cmd: 'tblStyleLastCol', label: 'Last Column', type: 'checkbox' },
          { cmd: 'tblStyleBandedCols', label: 'Banded Columns', type: 'checkbox' },
        ] },
        { id: 'td-styles', name: 'Table Styles', controls: [
          { cmd: 'tblStyles', label: 'Table Styles', type: 'dropdown' },
          { cmd: 'tblShading', label: 'Shading', type: 'dropdown' },
        ] },
        // Spec 032 T4: Word's Table Design → Borders group. Layout = Border Styles / (Pen Style + Pen Weight +
        // Pen Color stacked) / Borders / Border Painter. The pen dropdowns MUTATE the shared tblPen (commands.js);
        // the Borders dropdown + Border Painter DRAW with it. Word labels: Line Style→"Pen Style",
        // Line Weight→"Pen Weight". Borders MOVED here from td-styles to match Word's grouping.
        { id: 'td-borders', name: 'Borders', controls: [
          { cmd: 'tblBorderStyles', label: 'Border Styles', type: 'dropdown' },
          { cmd: 'tblLineStyle', label: 'Pen Style', type: 'dropdown' },
          { cmd: 'tblLineWeight', label: 'Pen Weight', type: 'dropdown' },
          { cmd: 'tblPenColor', label: 'Pen Color', type: 'dropdown' },
          { cmd: 'tblBorders', label: 'Borders', type: 'dropdown' },
          { cmd: 'tblBorderPainter', label: 'Border Painter', type: 'toggle' },
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
