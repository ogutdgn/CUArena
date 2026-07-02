# Paged-painter cell-paint gaps (surfaced by the FIX-3 harness fix)

> 2026-07-02. When FIX 3 corrected the BEHAVIOR twin harness to read the real PAINTER layer
> (.presentation-editor__pages cell divs) instead of the off-screen hidden ProseMirror model host
> (td/th @ x≈-10004, whose real-HTML-table CSS reflects everything), three cell-paint behaviors that
> the OOXML export writes CORRECTLY turned out NOT to be fully reflected on the paged painter:

| Aspect | OOXML (export) | Painter (on-screen) | Twin |
|---|---|---|---|
| Horizontal cell alignment (jc) | ✅ w:jc | ✅ inner flex justify-content:flex-end | (passes) |
| Vertical cell alignment (vAlign) | ✅ w:vAlign | ❌ inner flex align-items stays 'normal' | tb-cellalign-* FAIL |
| Row height (atLeast/exact) | ✅ w:trHeight | ❌ cell paints content-height (~18px), not the set min | tb-rowheight-05in FAIL |
| Cell text direction (tbRl/btLr) | ✅ w:textDirection | ❌ writing-mode stays horizontal-tb | tb-textdir FAIL |

Probe evidence (2026-07-02, /tmp/valign-probe): painter cell = outer `display:block` div (h=18,
vertical-align:baseline, writing-mode:horizontal-tb) with an inner `display:flex` content div that
DOES carry justify-content for jc but NOT align-items for vAlign.

**These are genuine PAGED-ENGINE paint gaps, NOT table-feature gaps** — the Layout tab controls +
the OOXML they write are correct (specs 031/033). Fixing them is a layout-adapter concern (how the
paged PresentationEditor paints cell-content vertical alignment, enforces row min-height, and applies
per-cell writing-mode) that affects ALL tables, cross-cutting — a dedicated layout-engine follow-up,
not table-specific. The twins stay as HONEST FAILs documenting the gap (D6.4: every gap is a twin);
they measure what the USER sees, correctly, now that the harness reads the painter.

Deferred to a post-loop layout-engine pass (or FIX 6 if scoped in). Recorded so nobody mistakes
these for a regression: they were ALWAYS gaps — the old harness hid them by reading the model host.
