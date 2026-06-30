# Visual Ledger — clone rendering vs Microsoft Word (light, clone-only LLM judge)

Auto-generated from the visual-judge workflow (see parity/visual/README.md). Each T0/T1 result screenshot was judged: is the feature visibly applied + does it look like real Word? **concern** = a visual bug; **not-visually-distinguishable** = a single-line sample where alignment/spacing cannot be assessed visually (OOXML verified separately).

**Controls:** 13 · **pass:** 11 · **not-distinguishable:** 2 · **concern:** 0 · **judge discrimination golden:** 2/2 (wrong-feature correctly reported absent)

| Control | verdict | applied | Word-like | observed |
|---|---|---|---|---|
| `bold` | ✅ pass | True | True | The word "Revenue" appears in heavy/thick strokes consistent with bold weight, and it is selected (blue highlight). The Bold (B) button in t |
| `italic` | ✅ pass | True | True | The word "Revenue" is rendered in slanted/oblique glyphs â€” clearly italic â€” and is selected (blue highlight). The Italic (I) button in t |
| `underline` | ✅ pass | True | True | "Revenue" shows a single horizontal underline beneath the full word. The text is selected (blue highlight) and the Underline (U) button in t |
| `fontface` | ✅ pass | True | True | "Revenue" is rendered in a clean sans-serif typeface (consistent with Arial) and is selected (blue highlight). The Font name box in the ribb |
| `fontsize` | ✅ pass | True | True | The word "Revenue" is selected (blue highlight) and rendered in a normal upright sans-serif font at a size that looks slightly larger than t |
| `bullets` | ✅ pass | True | True | "Revenue" (highlighted/selected) sits as a bulleted list item: a round bullet â€¢ appears to its left and the text is indented from the marg |
| `alignleft` | ✅ pass | True | True | "Revenue" sits flush against the left margin, selected (highlighted blue), in the default body font (Aptos 12). The Align Left button in the |
| `center` | ✅ pass | True | True | "Revenue" (selected, highlighted blue) sits horizontally centered on the page, roughly at the page's horizontal midpoint between the left an |
| `fontcolor` | ✅ pass | True | True | The word "Revenue" is rendered in red font color. It is currently selected (blue selection highlight over it), through which the red glyph c |
| `highlight` | ✅ pass | True | True | The word "Revenue" has a solid yellow highlight swatch behind the text, covering the full word. Text remains default black on the yellow bac |
| `numbering` | ✅ pass | True | True | "Revenue" (selected/highlighted blue) appears as a numbered list item with a "1." marker to its left and the text indented from the margin.  |
| `justify` | ⚪ n/a (1 line) | True | True | "Revenue" appears as a single selected (highlighted) word at the top-left of the page in the default Aptos 12pt font. It sits flush at the l |
| `linespacing` | ⚪ n/a (1 line) | True | True | The single word "Revenue" sits on one line near the top of the page, selected (blue highlight), in the default Aptos 12pt left-aligned style |