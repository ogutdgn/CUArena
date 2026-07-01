# Chart — Insert > Illustrations

## What real Word does
Chart opens the "Insert Chart" dialog (categories: Column / Line / Pie / Doughnut / Bar /
Area / X Y Scatter / Bubble / Stock / Surface / Radar / Treemap / Sunburst / Histogram /
Box & Whisker / Waterfall / Funnel / Combo / Map, each with subtypes; plus a Recommended
tab). After OK, Word inserts a sample chart AND opens a small embedded "Chart in Microsoft
Word" Excel grid to edit the data; three floating buttons (Chart Elements / Styles / Filters)
appear by a selected chart, which raises **two** tabs — **Chart Design** (Add Chart Element /
Quick Layout / Change Colors / Chart Styles / Switch Row-Column / Select Data / Edit Data /
Change Chart Type) and **Format**. Storage: `w:drawing > wp:inline > a:graphic >
a:graphicData uri=.../chart > c:chart r:id` → `word/charts/chart1.xml`
(`c:chartSpace/c:chart/c:plotArea/c:barChart|c:pieChart|…`), with the data in an embedded
`word/embeddings/*.xlsx` workbook (referenced via `c:externalData`) and cached values in
`c:numCache/c:strCache`. KeyTips Alt, N, C.

## Current clone state
**stub** (authoring) / **real** (import + round-trip) — `H.chart` (`commands.js:441`) →
`WC.Insert.chartDialog` (`insert-features.js:155`) gathers a chart type + data rows, then
calls `WC.PM.xeChart()`. The live ribbon path's `xeChart` (`bridge/insert-exotica.ts:198`)
inserts a static SVG as an image **only if** an SVG string is passed; the dialog passes none,
so it falls to `toast("Charts (live c:chartSpace + data) need a chart subsystem …")` and the
collected type/data are discarded (`Insert.chartSVG` exists but is dead code). **BUT the
engine already has a real `chart` node:** `extensions/chart/chart.js` is registered, imports
parse real chart XML — `chart-helpers.js` (`parseChartXml`) supports bar/line/area/pie/
doughnut/scatter/bubble/radar/stock/surface from `c:numCache/c:strCache`
(`handleChartDrawing`, `encode-image-node-helpers.js:949`) — and the export router maps
`chart → wDrawingNodeTranslator`, which **replays the chart's `originalXml`**
(`drawing-translator.js:66`). So **opening a .docx with a chart works and round-trips**; only
*authoring a new chart from the dialog* is unwired.

## Can we build it in our engine?
**Verdict:** 🟡 Buildable with additive fork edits
**Why:** Far more is in place than the stub suggests. The `chart` node exists and renders
parsed `chartData`; the import handler (`handleChartDrawing` + `parseChartXml`) is mature and
tested; and export round-trips imported charts by replaying `originalXml`. The gap is the
**create-from-scratch** path: there is no synthesizer that turns the dialog's
{type, rows} into a `chartData` model + a `c:chartSpace` XML part (and ideally an embedded
`.xlsx`). That is an **additive** edit — write a `synthesizeChartXml(type, data)` (the inverse
of `parseChartXml`, emitting `c:barChart`/`c:pieChart` + `c:numCache/c:strCache`), stash it as
the new chart node's `chartData` + `originalXml`/`drawingContent` so the existing
`wDrawingNodeTranslator` replays it on export — mirroring exactly how `vectorShape`
synthesizes WordArt. The embedded Excel workbook (`word/embeddings/*.xlsx` +
`c:externalData`) is the one genuinely heavy sub-piece; Word tolerates charts with only
cached values (no live workbook), so v1 can emit cache-only charts. NOT a new subsystem — the
node, the model, the renderer, and the export pipe already exist.

## Required structures to build it
- **PM node/extension:** reuse `chart` (`extensions/chart/chart.js`) — already registered, renders `chartData`.
- **Converter handler (super-converter):** import exists (`handleChartDrawing` + `parseChartXml`, `chart-helpers.js`); export exists (`wDrawingNodeTranslator` replays `originalXml`, `drawing-translator.js:66`). ADD a `synthesizeChartXml(type, data)` (inverse of `parseChartXml`) + emit the `word/charts/chartN.xml` part + relationship.
- **OOXML target:** `a:graphicData(.../chart)/c:chart r:id` → `word/charts/chartN.xml` (`c:chartSpace/c:plotArea/c:barChart|c:pieChart…` + `c:numCache/c:strCache`); optional `word/embeddings/*.xlsx`.
- **Bridge verb(s):** replace the dead toast `xeChart` with a real `insertChart(type, data)` that builds the node + part; wire `Insert.chartDialog` to it.
- **Fork edit?** additive (a new chart synthesizer + part/relationship emit; no schema break).
- **Rough size:** L (cache-only charts for the common types) • **Dependencies:** rides the existing `chart` node + `parseChartXml` model + `wDrawingNodeTranslator` replay; the live Excel workbook is the only optional heavy add-on.

## Open questions for our discussion
- Cache-only charts (`c:numCache/c:strCache`, no embedded workbook) for v1 — acceptable? Word renders them fine and "Edit Data" can be a degrade. The full embedded `.xlsx` + `c:externalData` is a separate, larger effort.
- Which chart types first? bar / line / pie / doughnut / area cover most use and all already import.
- In-app rendering: the `chart` node renders parsed `chartData` — confirm the NodeView paints synthesized charts, or do we ship an SVG snapshot as the in-app preview while exporting real `c:chartSpace`?
- Build the Chart Design/Format contextual tabs, or insert-only first?

## Decision
**TBD — to be decided together.**
