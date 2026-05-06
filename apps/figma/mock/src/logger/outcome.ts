// Outcome snapshot: a complete picture of the current scene, written on the
// same flush cadence as raw + semantic. Evaluators read this offline to score
// rubrics that depend on the final document state (e.g. shape counts,
// alignment, geometry). History is not preserved — each flush overwrites.

import type { DocumentNode, Layer, NodeType } from "@/types/scene";
import { isContainer } from "@/types/scene";
import { useStore } from "@/engine/store";
import { logger } from "./buffer";

export interface OutcomeSummary {
  // Total `pushSemantic` calls observed this session — efficiency rubrics
  // compare this against a per-task target turn count.
  semanticEventCount: number;
  // Counts every layer in every page by `type`, including containers
  // (frame/section/group). Evaluators filter to the types they care about.
  shapeCounts: Partial<Record<NodeType, number>>;
}

export interface OutcomeSnapshot {
  schemaVersion: number;
  sessionId: string;
  capturedAt: number;
  activePageId: string;
  summary: OutcomeSummary;
  document: DocumentNode;
}

function countLayers(layers: Layer[], counts: Partial<Record<NodeType, number>>): void {
  for (const l of layers) {
    counts[l.type] = (counts[l.type] ?? 0) + 1;
    if (isContainer(l)) countLayers(l.children, counts);
  }
}

function buildSummary(doc: DocumentNode): OutcomeSummary {
  const shapeCounts: Partial<Record<NodeType, number>> = {};
  for (const page of doc.pages) countLayers(page.children, shapeCounts);
  return {
    semanticEventCount: logger.semanticEvents.length,
    shapeCounts,
  };
}

export function buildOutcomeSnapshot(): OutcomeSnapshot {
  const state = useStore.getState();
  return {
    schemaVersion: 1,
    sessionId: state.sessionId,
    capturedAt: Date.now(),
    activePageId: state.activePageId,
    summary: buildSummary(state.document),
    document: state.document,
  };
}
