// Semantic event emission. Wraps each event with the common fields.
// Source: .analysis/engine-report.md §5.

import type { SemanticEvent, SemanticEventInput } from "@/types/events";
import { SCHEMA_VERSION } from "@/types/events";
import { uid } from "@/util/id";
import { logger } from "./buffer";
import { useStore } from "@/engine/store";
import { getMostRecentRawId } from "./raw";

// `lastEmittedRawId` is the most-recent raw id captured at the previous emit.
// `prevGestureBoundary` is the raw id where the previous *gesture* ended; the
// current semantic event's range starts at the first raw strictly after this
// boundary. The boundary only advances when a new raw event has arrived since
// the previous emit — that way multiple semantic events triggered by the same
// user gesture (e.g. updatePrototypeConnection emitting one event per changed
// field after a single Save click) all share the same raw-event range.
let lastEmittedRawId: string | null = null;
let prevGestureBoundary: string | null = null;

function rangeStartAfter(boundary: string | null): string | null {
  const arr = logger.rawEvents.toArray();
  if (arr.length === 0) return null;
  if (boundary == null) return arr[0].eventId;
  const idx = arr.findIndex((e) => e.eventId === boundary);
  if (idx < 0) return arr[0].eventId; // boundary fell off the ring buffer (truncated)
  if (idx + 1 >= arr.length) return null; // boundary IS the most recent raw — no events after
  return arr[idx + 1].eventId;
}

export function emitSemantic(payload: SemanticEventInput): void {
  const state = useStore.getState();
  const rawId = getMostRecentRawId();

  // A new gesture has started iff a new raw event arrived since the previous
  // emit. Promote the previous lastEmittedRawId to the gesture boundary; until
  // the next raw arrives, all emits share the same range (same gesture batch).
  if (rawId != null && rawId !== lastEmittedRawId) {
    prevGestureBoundary = lastEmittedRawId;
  }

  const range: [string, string] | null = (() => {
    if (rawId == null) return null;
    const start = rangeStartAfter(prevGestureBoundary);
    // No raw event after the boundary (e.g. boundary IS the most-recent raw —
    // happens for same-gesture batched emits when no new raw arrived); fall
    // back to a single-event range pointing at the most recent raw.
    return start == null ? [rawId, rawId] : [start, rawId];
  })();
  lastEmittedRawId = rawId;

  const event = {
    schemaVersion: SCHEMA_VERSION,
    sessionId: state.sessionId,
    eventId: uid("sem"),
    timestamp: performance.now(),
    pageId: state.activePageId,
    rawEventIdRange: range,
    ...payload,
  } as SemanticEvent;

  logger.pushSemantic(event);
}

// Reset module state — invoked by logger.clear() / session start so stale
// boundaries from a previous session do not leak into the new one.
export function resetSemanticEmissionState(): void {
  lastEmittedRawId = null;
  prevGestureBoundary = null;
}

logger.onClear(resetSemanticEmissionState);
