# Cross-App Log Contract

> **Status: PLACEHOLDER.** This document specifies the log shape that every mock in `cua-bench` must emit, as a cross-app contract. It will be promoted from "describes figma" to "describes all three apps" once we have at least two apps emitting logs.

---

## Current state of the contract

Today, only the figma app produces logs. Its schema is fully specified at:
[apps/figma/app-docs/logging-documentation.md](../apps/figma/app-docs/logging-documentation.md).

That document defines:
- The three streams (`raw`, `semantic`, `outcome`) and their storage layout.
- Per-event schemas for the figma app's semantic events.
- The full `OutcomeSnapshot` shape for figma's scene graph.

When Sheets is implemented, this `log-contract.md` will be promoted to **the cross-app source of truth** for the parts of the schema that all mocks share. Per-app extensions (figma's scene-graph, sheets' grid model, docs' text model) will live in each app's `app-docs/logging-documentation.md`.

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
