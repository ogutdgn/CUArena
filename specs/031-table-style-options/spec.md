# Feature Specification: Table Style Options + tblLook/cnfStyle Writer

**Feature Branch**: `031-table-style-options`

**Created**: 2026-07-02

**Status**: Draft

**Input**: FIX 2 of the ratified Tables fix loop — Phase B named gap §2 (cnfStyle + tblLook val).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Styled tables carry Word's conditional-format markers (Priority: P1)

When a user applies a table style (or toggles a style option), the saved file carries
exactly what real Word writes: the `w:tblLook` element with BOTH the six flag attributes
AND the `w:val` bitmask, plus the per-row/per-cell `w:cnfStyle` role markers (header row,
banded rows, first column, banded columns…) that let Word/consumers resolve conditional
formatting without recomputing it.

**Why this priority**: The named §2 acceptance gap; 7 OOXML tasks currently fail on it.
CUA/RL consumers and real Word both read these markers.

**Independent Test**: Apply Grid Table 4 Accent 1 to a 3×3; export; the parity diff vs
the real-Word capture shows zero missing cnfStyle/tblLook nodes.

**Acceptance Scenarios** (ground truth = the rw fixtures, patterns verified 2026-07-02):

1. **Given** a 3×3 with GT4A1 (defaults firstRow=1 firstColumn=1 banded rows on),
   **When** exported, **Then** `w:tblLook w:val="04A0"` + 6 flags; row0 trPr cnfStyle
   `100000000000`, row1 `000000100000` (band1Horz), row2 none; every row's first cell
   tcPr cnfStyle `001000000000`.
2. **Given** Total Row toggled ON, **Then** tblLook `04E0`/lastRow=1 and row2 trPr
   cnfStyle `010000000000`.
3. **Given** Header Row toggled OFF, **Then** tblLook `0480`/firstRow=0; banding recounts
   from row0 (`000000100000` on rows 0 and 2, nothing on row 1).
4. **Given** Banded Columns ON, **Then** tblLook `00A0`/noVBand=0 and the SECOND cell of
   every row gains tcPr cnfStyle `000010000000` (band1Vert; col banding skips the first
   column when firstColumn=1).

---

### User Story 2 - The Table Style Options group (Priority: P1)

The Table Design tab gains Word's Table Style Options group: six labeled checkboxes —
Header Row, Total Row, Banded Rows, First Column, Last Column, Banded Columns — whose
checked state reflects the table's current tblLook and whose toggling updates the file
markers AND the visible painting of the styled table.

**Why this priority**: STRUCTURE lists all six as missing idMso
(TableStyleHeaderRowWord…); the checkboxes are the ONLY UI route to the §2 file semantics.

**Independent Test**: Caret in a styled table → Design tab shows the 6 checkboxes with
correct initial states (Header Row ✓, First Column ✓, Banded Rows ✓ per Word defaults);
toggling each updates the export accordingly.

**Acceptance Scenarios**:

1. **Given** the caret in a styled table, **When** Table Design renders, **Then** the six
   checkboxes appear with states derived from tblLook (defaults: firstRow ✓, firstColumn ✓,
   banded rows ✓ i.e. noHBand=0, others off).
2. **Given** any checkbox toggled, **When** exported, **Then** the tblLook val+flags and
   the cnfStyle stamps match the corresponding rw fixture pattern (scenarios above).
3. **Given** a toggle, **Then** one undo step reverts BOTH the look flags and the stamps.

---

### User Story 3 - Stamps survive structural edits (Priority: P2)

Inserting or deleting rows/columns in a styled table keeps the markers consistent
(banding renumbered, first/last roles re-assigned) — the file never carries stale stamps.

**Why this priority**: P2 — the OOXML tasks measure apply/toggle, but stale stamps after
an edit would be a false-fidelity regression the pipeline's insert tasks would flag on
styled tables later.

**Independent Test**: GT4A1 3×3 → insert a row above row1 → export → stamps re-derived
(band pattern shifted correctly, single firstRow marker).

**Acceptance Scenarios**:

1. **Given** a styled table, **When** a row/column is inserted or deleted via the Layout
   verbs, **Then** the exported stamps equal a fresh stamping of the resulting geometry.
2. **Given** an UNstyled table (Table Grid), **Then** no cnfStyle is ever stamped
   (matches Word — plain tables carry no markers).

### Edge Cases

- 1×1 table with firstRow+lastRow+firstColumn+lastColumn all on: row0 gets firstRow AND
  lastRow bits? (Resolve from a targeted rw capture if the differ flags it — do not guess;
  the 3×3 tasks don't exercise it. Marked as a follow-up oracle experiment.)
- Toggling options on a TableGrid (no tblStylePr) table: Word still writes tblLook and
  stamps? (rw-tb-styleopt-* fixtures apply GT4A1 first — v1 scope: stamps only when a
  catalog/tblStylePr style is active; look flags always written.)
- Merged cells: banding counts GRID columns, not cells (gridSpan) — stamp the first cell
  of each band run; targeted combo task exists (tb-combo-diag-merged) for the diff to
  arbitrate.
- Clear style: stamps removed together with w:tblStyle (Clear already resets attrs via
  setTableStyle('') — the writer must strip cnfStyle too).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The export MUST write `w:tblLook` with the six flag attributes AND the
  `w:val` bitmask computed as OR of firstRow 0x20 / lastRow 0x40 / firstColumn 0x80 /
  lastColumn 0x100 / noHBand 0x200 / noVBand 0x400 (verified against 4 rw fixtures).
- **FR-002**: A single writer MUST stamp trPr/tcPr `w:cnfStyle` per the recorded rules:
  row-level firstRow/lastRow/band1Horz (banding indexed from the first non-header row,
  odd bands stamped, even bands unstamped; header/total rows excluded from banding);
  cell-level firstColumn/lastColumn/band1Vert (column banding indexed after the first
  column when firstColumn is on); 12-bit val string + the individual flag attributes
  exactly as Word emits them.
- **FR-003**: Stamps apply ONLY to tables whose active style has conditional formats
  (tblStylePr); plain tables carry none.
- **FR-004**: The six checkboxes MUST render in a Table Style Options group on Table
  Design, states derived from tblLook, Word's labels (per the idMso inventory), and each
  toggle = one undoable step updating look+stamps+paint.
- **FR-005**: Style apply (tableSetStyle) and structural verbs (add/delete row/column,
  merge/split) MUST re-derive the stamps for styled tables.
- **FR-006**: Import round-trip MUST preserve document-authored cnfStyle byte-for-byte
  when the geometry is untouched (no gratuitous re-stamping on open/save).

### Key Entities

- **tblLook state**: {firstRow, lastRow, firstColumn, lastColumn, noHBand, noVBand} —
  single source of truth on the table's properties; val derived.
- **cnfStyle stamp**: 12-bit role mask per row (trPr) / cell (tcPr); positions:
  firstRow, lastRow, firstColumn, lastColumn, band1Vert, band2Vert, band1Horz, band2Horz,
  neCell, nwCell, seCell, swCell.

## Success Criteria *(mandatory)*

- **SC-001**: `run.py --only tb-style-grid4a1` → semantic-pass except the F-class
  insert-default rows (gridCol/tblW/tcW/pPr-trPr — FIX 5 scope); all cnfStyle + tblLook
  nodes present. Same for `tb-style-listtable3`.
- **SC-002**: All six `tb-styleopt-*` tasks reach the same bar (cnfStyle/tblLook clean).
- **SC-003**: STRUCTURE: the six TableStyle*Word checkboxes move missing→matched on
  table-design.
- **SC-004**: BEHAVIOR: a new signed-card-exempt generated twin per toggle (docChanged +
  paint) passes; no existing card regresses.
- **SC-005**: Import legs on the 7 style tasks stay semantic-pass (FR-006).
- **SC-006**: The 3 standing gates + bundle stay green.

## Assumptions

- The corner-cell bits (nw/ne/sw/se) and band2 bits are NOT stamped by Word in the
  measured patterns — the writer emits them only as zero-bits inside the 12-char val
  (matching the fixtures); if a future task surfaces them, the writer extends.
- STATE-axis checkbox enable/disable matrix is FIX 4+ scope (contextual states).
- In-app banding PAINT beyond what the PE already renders is out of scope (paint parity
  is judged by VISUAL; this feature's paint duty = checkbox toggles visibly change the
  styled table where the PE already supports it).
