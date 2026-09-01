# Cross-App Log Contract

> **Status: PARTIAL.** Two apps emit logs against this contract: figma (TS mock) and libreoffice (real binary via the [rllogger](../apps/ms-word/libreoffice-codebase/rllogger/) module). Sheets and Docs are still placeholders. The contract section below will be promoted from "two implementations" to "canonical source of truth" once one more app ships.

---

## Apps producing logs today

**figma** — TypeScript mock. Schema fully specified at [apps/figma/app-docs/logging-documentation.md](../apps/figma/app-docs/logging-documentation.md). Defines:
- Three streams (`raw`, `semantic`, `outcome`) and their storage layout
- Per-event schemas for figma semantic events
- The full `OutcomeSnapshot` shape for figma's scene graph

**libreoffice** — real Linux binary (stripped LibreOffice fork). Schema specified at [apps/ms-word/docs/architecture/PHASE3_LOGGER_DESIGN.md](../apps/ms-word/docs/architecture/PHASE3_LOGGER_DESIGN.md) and [apps/ms-word/AGENTS.md §4.3](../apps/ms-word/AGENTS.md). Defines:
- `raw.jsonl` — VCL key/mouse/focus/command/gesture events
- `semantic.jsonl` — `.uno:*` dispatches mapped to RL-friendly names with `args`, `trigger`, `rawEventIdRange`
- `outcome.jsonl` — document URL, modified flag, counts, cursor, selection, format-at-cursor; rewritten every 250 ms
- Default base directory: `~/.lo-rl-logs/<sessionId>/` (Linux/macOS) or `%LOCALAPPDATA%\lo-rl-logs\<sessionId>\` (Windows). Override via `LO_RL_LOG_DIR=<path>`. Opt-out via `LO_RL_LOG_DISABLE=1`. A `rllogger-export.py` consolidator merges a session into the single-file `exportLog()` shape that matches figma's JSON.

Both apps follow the same three-stream split, so a verifier built against the contract works against either log set with at most an app-specific CommandMap (figma's `create_rectangle` vs libreoffice's `.uno:InsertTable`, etc.).

---

## What the contract is expected to fix (when written)

The shared parts that every app's logger must implement identically:

- File naming: `<app>-mock-log-<sessionId>.json`
- Top-level shape: `{ schemaVersion, sessionId, exportedAt, raw[], semantic[], outcome{} }`
- `raw` event base fields (`eventId`, `type`, `timestamp`, `sessionTime`, `targetId`, `modifiers`, `fields`)
- `semantic` event base fields (`schemaVersion`, `sessionId`, `eventId`, `timestamp`, `pageId`/`sheetId`/`docId`, `rawEventIdRange`, `name`)
- `outcome` top-level (`schemaVersion`, `sessionId`, `capturedAt`, `summary`, `document` — where `document` is per-app)
- `summary.semanticEventCount` (drives efficiency rubric)
- Coordinate / color conventions (0..1 ranges, scene-relative coords for figma, cell-address coords for sheets, etc.)

---

## What stays per-app

Each app extends the contract with its own:

- `semantic[i].name` registry (figma has `create_rectangle`, sheets will have `set_cell` etc.)
- `outcome.summary.<...>` aggregates (figma has `shapeCounts`; sheets will have `cellCount`, `formulaCount`; docs will have `paragraphCount`, `runCount`)
- `outcome.document` shape

---

## Rule for now

If you're building a feature that touches the log shape, edit only the figma-specific doc and add a note here that a cross-app rule may be needed. Promotion from per-app to cross-app happens deliberately, not implicitly.
