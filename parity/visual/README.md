# Visual axis — the THIRD parity axis (light, clone-only LLM judge)

Confirms the clone *renders* each feature broadly like Microsoft Word (not just that the OOXML is right).
Deliberately LIGHT (per the locked scope): clone-only screenshots + an LLM "looks-correct + Word-like" judgment,
no pixel-exact Word reference. It catches GROSS visual bugs (a feature not rendering, the wrong color, a broken
menu) — full design polish is a later concern.

## How it runs

1. **Capture** (clone screenshots) — re-run each T0/T1 parity probe with Electron's `--shot`, which applies the
   action to the word "Revenue" and screenshots the painted window:
   ```bash
   for id in bold italic underline fontface fontsize bullets alignleft center fontcolor highlight numbering justify linespacing; do
     node_modules/electron/dist/electron.exe --user-data-dir=C:/tmp/wc-visual-profile --disable-http-cache . \
       --shot-delay=1400 "--shot=parity/visual/shots/$id.png" "--shot-evalfile=parity/probes/$id-pilot-probe.js"
   done
   git checkout -- parity/fixtures/   # discard the incidental docx re-saves
   ```
   Shots land in `parity/visual/shots/<id>.png`.

2. **Judge** (LLM) — a Workflow fans out one judge per screenshot: "is `<feature>` visibly applied to 'Revenue',
   and does the rendering look like real Microsoft Word?" → `{applied_correctly, looks_word_like, observed_formatting,
   verdict}`. Single-line-only features (alignment, line spacing) are honestly marked `not-visually-distinguishable`.

3. **Regression-lock** — DISCRIMINATION GOLDENS: the judge is also asked to test a screenshot against the WRONG
   feature (e.g. is the *bold* shot *italic*? is the *center* shot *red*?); it MUST report the wrong feature ABSENT.
   This proves the judge discriminates rather than rubber-stamping. (The capture is deterministic — same app, same render.)

4. **Aggregate** → `parity/results/VISUAL_LEDGER.md` (+ `visual_judge.json`).

## Scope / honesty
- Clone-only (no real-Word screenshot) — the lightest option, per the locked scope.
- Single-line samples make alignment/justify/line-spacing visually ambiguous; those are reported honestly, not guessed.
- The clone UI is a faithful Word replica (same ribbon/chrome), so "Word-like" is about the RESULT rendering, not the chrome.
