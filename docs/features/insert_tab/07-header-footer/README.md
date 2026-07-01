# Insert > Header & Footer — feasibility index

Button-by-button feasibility for the **Insert > Header & Footer** ribbon group. Each file grounds
its verdict in the actual fork (PM nodes, super-converter handlers, the `WC.PM` bridge). Decisions
are deferred to a joint build/keep/remove discussion.

| Button | Verdict | Size | Key required structure |
|--------|---------|------|------------------------|
| [Header](./header.md) | 🟡 Buildable with additive fork edits | S (edit/remove) · L (gallery) | Header part round-trips as a full PM `doc` story (exists); Edit/Remove NO-FORK; gallery needs a bundled Building-Blocks catalog + glossary `<w:docPart>` handler |
| [Footer](./footer.md) | 🟡 Buildable with additive fork edits | S (edit/remove) · L (gallery) | Footer part + PAGE field (`sd:autoPageNumber`) round-trip (exists); Edit/Remove NO-FORK; same gallery/glossary additions as Header — build together |
| [Page Number](./page-number.md) | ✅ Buildable NO-FORK (Format/galleries) · 🟡 additive (Page Margins) | M (Format dialog) · S (fix Current) · M-L (Page Margins) | `page-number` node + `sd:autoPageNumber` PAGE field + `sections.setPageNumbering` (`w:pgNumType`) all exist; Format Page Numbers is wiring-only; Page Margins rides the textbox/`wp:anchor` engine |

## Cross-cutting notes
- **The bridge is real, the UI is shallow.** `src/renderer/bridge/header-footer.ts` is the sole
  write path and it genuinely mutates OOXML (`word/headerN.xml`/`footerN.xml`, `sectPr` refs +
  `titlePg`, `settings.xml evenAndOddHeaders`, PAGE fields) — Word-COM-validated (spec-kit 002).
  The gaps are mostly in the UI layer: the Header/Footer dropdowns expose only a plain-text Edit
  modal, and the Page Number flyout lacks design galleries / Format / Page Margins.
- **Already-working neighbors** (context for scope): the **Header & Footer Tools** contextual tab —
  Go to Header, Go to Footer, Close, Different First Page, Different Odd & Even — are real and
  Word-validated; **Remove Page Numbers** works. The cheap high-value wins are re-pointing the
  Header/Footer dropdown "Edit" at the real on-page band (`enterHeaderFooter`) and adding
  **Remove Header/Footer** + a **Format Page Numbers** dialog (all NO-FORK).
- **The recurring missing subsystem** is the **Building Blocks / glossary store**
  (`word/glossary/document.xml`, `<w:docPart>` galleries) behind the built-in design galleries and
  Save-Selection — a real additive feature, not a new engine.
