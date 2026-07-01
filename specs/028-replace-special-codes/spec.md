# 028 — Special codes in the Replace box (group 4b)

**Source:** deep T0/T1 fidelity identification (`DEEP_T0_T1_REPORT.md` §4a). `fd-special-replace` — the clone's
Replace-With box inserted `^p`/`^t`/`^l` as **literal text**; real Word translates them (paragraph mark / tab /
manual line break). The FIND side already interprets them (`search.ts specialToRegexSource`); only the REPLACE
side passed the string through verbatim to the fork replace command, which inserted a single text node.

Branch: `parity-pipeline`. FIX phase.

## FR-028 — parse the Replace-With payload into a Slice (fork edit, additive)
- `extensions/search/search.js` `buildReplacementSlice(schema, replacement)`: `^p` → paragraph split (paragraph
  nodes; Slice `openStart/openEnd = 1` so a mid-paragraph break splits the surrounding paragraph and the ends
  merge), `^t` → a `tab` node, `^l`/`^n` → a `lineBreak`/`hardBreak` node, `^^` → literal `^`, unknown `^x` → literal
  `x`. A no-codes replacement returns the same single-text-node inline Slice as before (ordinary replaces unchanged).
  Both `replaceSearchMatch` + `replaceAllSearchMatches` call it.

### Acceptance
`test:pm` regression `028 Replace box ^p/^t/^l → paragraph break / tab / line break` — `A^pB` → two paragraphs
(A, B), `E^tF` → `<w:tab/>`, `C^lD` → `<w:br/>`, plain `Income` → a plain `<w:t>`. Gates: test:pm 514/514,
test:roundtrip 27/0. Adversarial review of the core replace path.

## v1 limitation (logged, review-noted)
`^n` (Word = COLUMN break) and `^m` (Word = PAGE break) are NOT handled — they degrade to their literal char. A
follow-up (map `^n` → a column-break `hardBreak{lineBreakType:'column'}` per feature 003, `^m` → a page break) if
broader Replace-code parity is wanted. The 028 scope (`^p`/`^t`/`^l`/`^^`) is faithful.

## Group 4 COMPLETE (with 027 margins). Remaining overall: group 3b `fd-bullet-font` / `fd-bullet-align`.
