# Cross-Environment Log Contract

> **Status: PARTIAL — two implementations, one design.**
> [`envs/figma`](../envs/figma/) emits this contract from a TypeScript mock and is the
> reference implementation. [`envs/ms-word-native`](../envs/ms-word-native/rllogger/) emitted it
> from C++ inside a rented LibreOffice engine; that line is superseded, but its logger is kept
> because writing it is what proved the contract needs a dispatch point you own
> ([engine-rent-vs-own](decisions/engine-rent-vs-own.md)).
> [`envs/ms-word`](../envs/ms-word/) (Electron + ProseMirror) has the contract **designed** —
> `dispatchTransaction` is the semantic tap, `state.doc.toJSON()` the outcome snapshot
> ([ADR-0002](../envs/ms-word/docs/decisions/0002-prosemirror-document-model.md)) — but not
> yet built.
>
> This document is promoted from "two implementations" to canonical once the Word env ships its logger.

---

## Environments producing logs today

**figma** — TypeScript mock. Schema fully specified at [envs/figma/app-docs/mock-doc/logging-documentation.md](../envs/figma/app-docs/mock-doc/logging-documentation.md). Defines:
- Three streams (`raw`, `semantic`, `outcome`) and their storage layout
- Per-event schemas for figma semantic events
- The full `OutcomeSnapshot` shape for figma's scene graph

**ms-word-native** (superseded) — real Linux binary, LibreOffice fork. Schema specified at [envs/ms-word-native/rllogger/](../envs/ms-word-native/rllogger/) and [envs/ms-word-native/AGENTS.md §4.3](../envs/ms-word-native/AGENTS.md). Defines:
- `raw.jsonl` — VCL key/mouse/focus/command/gesture events
- `semantic.jsonl` — `.uno:*` dispatches mapped to RL-friendly names with `args`, `trigger`, `rawEventIdRange`
- `outcome.jsonl` — document URL, modified flag, counts, cursor, selection, format-at-cursor; rewritten every 250 ms
- Default base directory: `~/.lo-rl-logs/<sessionId>/` (Linux/macOS) or `%LOCALAPPDATA%\lo-rl-logs\<sessionId>\` (Windows). Override via `LO_RL_LOG_DIR=<path>`. Opt-out via `LO_RL_LOG_DISABLE=1`. A `rllogger-export.py` consolidator merges a session into the single-file `exportLog()` shape that matches figma's JSON.

Both follow the same three-stream split, so a verifier built against the contract works against either log set with at most an app-specific CommandMap (figma's `create_rectangle` vs libreoffice's `.uno:InsertTable`, etc.).

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

If you're building a feature that touches the log shape, edit only the figma-specific doc and add a note here that a cross-environment rule may be needed. Promotion from per-app to cross-environment happens deliberately, not implicitly.
