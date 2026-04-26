// Semantic event emission. Wraps each event with the common fields.
// Source: .analysis/engine-report.md §5.

import type { SemanticEvent, SemanticEventInput } from "@/types/events";
import { SCHEMA_VERSION } from "@/types/events";
import { uid } from "@/util/id";
import { logger } from "./buffer";
import { useStore } from "@/engine/store";
import { getMostRecentRawId } from "./raw";

let lastEmittedRawId: string | null = null;

export function emitSemantic(payload: SemanticEventInput): void {
  const state = useStore.getState();
  const rawId = getMostRecentRawId();
  const range: [string, string] | null =
    rawId == null
      ? null
      : lastEmittedRawId == null
      ? [rawId, rawId]
      : [lastEmittedRawId, rawId];
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
