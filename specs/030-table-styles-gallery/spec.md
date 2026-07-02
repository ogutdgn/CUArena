# Feature Specification: Table Styles Catalog + Visual Gallery + Theme Palette

**Feature Branch**: `030-table-styles-gallery`

**Created**: 2026-07-02

**Status**: Draft

**Input**: User description: "Table Styles catalog + visual gallery + theme palette (FIX 1 of the Tables fix loop, Phase B ratified). Make the clone's Table Design > Table Styles surface match real Word for the locked build: catalog of all 113 modern table-style definitions, theme palette alignment (accent1 #156082 etc.), and Word's visual gallery UI with hover live-preview and the Modify/Clear/New footer."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Apply any modern table style (Priority: P1)

A user inserts a table, opens Table Design > Table Styles, and applies any of Word's
113 modern built-in styles (Grid Table / List Table / Plain Table / Table Grid families,
all accent variants). The table takes the style's look, and the saved document carries
the same style definition real Word writes — so the file opens identically in real Word
and survives a round-trip.

**Why this priority**: This is the 2/247 gallery gap — the most visible named gap of the
Phase B acceptance test, and the blocker for every downstream style feature (style
options, banding, theme fidelity). Without the catalog, only 2 styles exist.

**Independent Test**: Apply "List Table 3" (a style the clone does not have today) via
the gallery; save; the parity pipeline compares the file against the real-Word ground
truth capture and finds the full style definition present.

**Acceptance Scenarios**:

1. **Given** a 3×3 table with the caret inside it, **When** the user applies "List Table 3"
   from the gallery, **Then** the table repaints with that style and the saved file carries
   the same table-style definition real Word writes (`run.py --only tb-style-listtable3`
   reaches semantic-pass on the definition side; cnfStyle stamping is explicitly FIX 2).
2. **Given** any of the 113 modern styles, **When** it is applied by gallery click,
   **Then** the exported styles part contains its verbatim definition (basedOn chain intact)
   and re-opening the file preserves it (import round-trip loses nothing).
3. **Given** a document saved by real Word with any modern table style, **When** the clone
   opens and resaves it, **Then** the style definition and reference survive unchanged.

---

### User Story 2 - See Word's colors (theme palette) (Priority: P1)

A user applies a theme-linked table style (104 of the 113 are theme-linked) and sees the
SAME colors real Word shows on the locked build — e.g. Grid Table 4 Accent 1's header is
dark teal (#156082), not the legacy royal blue (#4472C4).

**Why this priority**: The VISUAL level-4 finding — same style id, different effective
palette — makes every styled table visibly wrong at a glance. The palette is load-bearing
for 104/113 styles; the gallery thumbnails would also render wrong colors without it.

**Independent Test**: Apply Grid Table 4 Accent 1; screenshot the document side-by-side
with real Word's render; the visual judge sees matching header/band colors.

**Acceptance Scenarios**:

1. **Given** a table with Grid Table 4 Accent 1 applied, **When** the document renders,
   **Then** the header row paints the locked build's accent1 (#156082 dark teal) and the
   banding tints derive from it — matching the real-Word side-by-side.
2. **Given** the clone's default new document, **When** its theme colors are exported,
   **Then** the color scheme matches the locked build's theme (dk2 #0E2841, lt2 #E8E8E8,
   accent1–6 = #156082/#E97132/#196B24/#0F9ED5/#A02B93/#4EA72E, hyperlink #467886).

---

### User Story 3 - Word's gallery experience (Priority: P2)

The user opens the Table Styles gallery and gets Word's experience: visual tile
thumbnails (mini-table previews rendered in each style's real colors), organized in
Plain Tables / Grid Tables / List Tables sections, a tooltip with the style name on
hover, live preview of the hovered style on the actual document table (recorded
real-Word behavior), and the footer actions Modify Table Style… / Clear / New Table Style….

**Why this priority**: P2 because file fidelity (P1) is the parity foundation; but this
story carries the SCORECARD gallery bar (>=100 items), the signed style-gallery journey
card, and the VISUAL gallery pair — the user-facing half of the named gap.

**Independent Test**: Open the gallery; count tiles (>=113); hover a tile the table
doesn't use and watch the document preview it live; click Clear and watch the style
reference vanish.

**Acceptance Scenarios**:

1. **Given** the caret in a table, **When** the user opens the Table Styles gallery,
   **Then** at least the 113 modern styles render as visual tiles grouped into Plain/Grid/
   List Tables sections, each with its name on hover.
2. **Given** an open gallery, **When** the user hovers a tile, **Then** the document table
   live-previews that style, and reverts when the pointer leaves without clicking
   (recorded real-Word behavior, 2026-07-02).
3. **Given** a styled table, **When** the user clicks the footer's "Clear", **Then** the
   table's style reference is removed (archive-oracle-verified semantics).
4. **Given** the footer, **When** the user clicks "Modify Table Style…" or "New Table
   Style…", **Then** a functional v1 dialog opens or an honest not-yet toast appears
   (decided in plan) — the items are present and never dead.

---

### Edge Cases

- Applying a style by NAME vs by ID must both work (Word display names use " - Accent N";
  style ids use "-AccentN"; the catalog ids are the dash form real OOXML uses).
- A document opened from real Word already CONTAINING a modern style definition: applying
  the same style must not duplicate the definition; the document's own definition wins.
- Hover live-preview must not pollute the undo history or the saved file (preview is
  paint-only; only a click commits).
- Clear on an unstyled table is a no-op (no error, no phantom undo step).
- Styles based on TableNormal (all 113): the export must keep the basedOn chain valid
  without duplicating TableNormal.
- The gallery opened with the caret OUTSIDE a table: Word disables apply behavior
  gracefully; the clone must not throw (tiles visible; hover previews nothing).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The style catalog MUST register all 113 modern table-style definitions from
  the real-Word ground truth (`parity/oracle/table_style_defs.json`, verbatim `<w:style>`
  subtrees) so each is applicable by id or display name.
- **FR-002**: Applying a catalog style MUST write the style reference on the table AND
  materialize the full verbatim definition into the exported styles part exactly once,
  with the basedOn chain intact.
- **FR-003**: Opening a document that carries its own definition for a catalog style MUST
  prefer the document's definition (no duplication, no clobbering) and survive resave.
- **FR-004**: The clone's default theme MUST match the locked build's theme palette
  (`parity/oracle/word_theme_palette.json`): color scheme dk1/lt1/dk2/lt2, accent1–6,
  hyperlink colors — so themeColor/themeFill-linked style content renders Word's colors.
- **FR-005**: The Table Styles gallery MUST present visual tile thumbnails for every
  catalog style, grouped into Plain Tables / Grid Tables / List Tables sections, with the
  style name available on hover.
- **FR-006**: Hovering a gallery tile MUST live-preview that style on the document table
  (paint-only: no model change, no undo entry, no dirty flag) and revert on pointer-out.
- **FR-007**: The gallery footer MUST offer Modify Table Style…, Clear, and New Table
  Style…; Clear MUST remove the table's style reference; Modify/New MUST be present and
  reactive (v1 scope decided in plan — functional minimal dialog or honest toast).
- **FR-008**: The currently applied style's tile MUST be visually marked as active in
  the gallery.
- **FR-009**: All existing behavior on the 2 legacy-known styles (Table Grid,
  Grid Table 4 Accent 1) MUST keep working unchanged (regression guard).

### Key Entities

- **Table style definition**: a verbatim Word `<w:style w:type="table">` subtree — id,
  display name, basedOn, conditional-format sections; ground truth per style.
- **Theme palette**: the document theme's color scheme + font scheme; referenced by
  definitions via theme color names (accent1…), resolved at render/export time.
- **Gallery tile**: a visual mini-table preview of one style rendered with the real
  palette; belongs to a section (Plain/Grid/List); knows its style id + display name.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The parity task `tb-style-listtable3` (apply a previously-absent style)
  reaches semantic-pass on the style-definition side — the file carries what real Word
  writes (cnfStyle row/cell stamping excluded, tracked as FIX 2).
- **SC-002**: The signed style-gallery journey card's "gallery has >= 100 items" step
  passes (today: fails at 2).
- **SC-003**: The live scorecard no longer flags the Table Styles gallery as under-filled
  (GALLERY_UNDERFILLED clears; 113+ items counted).
- **SC-004**: The re-captured side-by-side of the OPEN gallery and of a styled table's
  document render are re-judged with reasons; the styled-table pair's palette mismatch
  reason (teal vs royal blue) is gone.
- **SC-005**: The import round-trip leg on the style tasks loses nothing (no missing
  nodes on rw → clone → resave).
- **SC-006**: All three standing gates stay green (functional suite, smoke, docx
  round-trip) — no regression outside tables.

## Assumptions

- The 134 legacy styles (Colorful Grid etc.) are OUT of v1 scope; the extractor is proven
  and resumable, so they can be added later without design change.
- cnfStyle/tblLook stamping is FIX 2 scope; this feature only guarantees definitions,
  references, palette, and gallery UX.
- The archive branch's gallery UI work (visual tiles, footer) may be reused via
  cherry-pick where it fits the current codebase; the certified pipeline re-validates it
  either way (weak-axis history is irrelevant now).
- Word's gallery shows styles for the CURRENT theme; theme switching UI is out of scope
  (the clone has a Design > Themes surface separately — only the DEFAULT palette is in
  scope here).
- Live preview applies to the table containing the caret (recorded behavior); multi-table
  documents preview only that table.
