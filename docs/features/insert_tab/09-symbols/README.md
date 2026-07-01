# Insert > Symbols — feasibility group index

Button-by-button feasibility for the **Insert > Symbols** ribbon group. Each row links the per-button doc with its verdict, rough size, and the one key engine structure it needs. Verdicts are grounded in the actual SuperDoc fork (node extensions, super-converter handlers, the WC.PM bridge), not assumptions.

| Button | Verdict | Size | Key required structure |
|--------|---------|------|------------------------|
| [Equation](./equation.md) | 🟡 Buildable with additive fork edits | M (presets) / XL (full editor) | OMML subsystem ALREADY exists (`mathInline`/`mathBlock` nodes + `omml-to-mathml` renderer + passthrough export); insert real `<m:oMath>` via `insertContent` — NO-FORK plumbing. Full editor (UnicodeMath→OMML parser + 2-D editing + contextual tab) = new authoring surface. Ink = ⛔ external runtime. |
| [Symbol](./symbol.md) | ✅ Buildable NO-FORK (core) | S–M | `WC.PM.insertSymbol` + text-run round-trip already work for Unicode; add Special Characters tab + Font selector + code-point/Alt+X + persisted MRU (UI). Additive `w:softHyphen` + `w:sym`/Wingdings handlers for full fidelity. |

## Key engine facts (verified)
- **The fork already has a complete OMML math pipeline** the current bridge ignores: import (`v2/importer/math/math-importer.js`) → registered PM nodes `mathInline`/`mathBlock` (`extensions/index.js:137-138`) → paged MathML render (`painter-dom/src/runs/math-run.ts` + `features/math/omml-to-mathml.ts`, ~20 converters) → verbatim OMML export (`v2/exporter` passthrough on `originalXml`). The bridge `insertEquation` (insert.ts:177) inserts **Cambria-Math styled text instead** (explicit KNOWN DEVIATION). Inserting real OMML is therefore a NO-FORK swap; the build-up parser and editable editor are the expensive parts.
- **Symbol is the strongest area:** `insertSymbol` (insert.ts:166) is a real mutation, and Unicode glyphs round-trip as plain `<w:t>` text. The nonbreaking hyphen has a real round-tripping node (`noBreakHyphen` + v3 handler). Gaps are UI (Special Characters tab, Font selector, code-point entry, persisted MRU) plus two small additive handlers: `<w:softHyphen/>` and `<w:sym>`/symbol-font (both absent — grep-confirmed).

## Verdict legend
- ✅ **Already works** — shipped and faithful.
- ✅ **Buildable NO-FORK** — achievable with bridge + UI only; no fork-source edits.
- 🟡 **Buildable with additive fork edits** — needs new, purely additive code in the fork (new node/handler), no risky rewrites.
- 🔴 **Needs a NEW subsystem/engine** — a substantial new authoring/render subsystem.
- ⛔ **Needs an external runtime we don't have** — e.g. handwriting recognition (Ink Equation).
