// JSON export of the current logger state.

import { logger } from "./buffer";
import { useStore } from "@/engine/store";

export interface LogExport {
  schemaVersion: number;
  sessionId: string;
  exportedAt: number;
  raw: ReturnType<typeof logger.rawEvents.toArray>;
  semantic: ReturnType<typeof logger.semanticEvents.toArray>;
}

export function exportLog(): LogExport {
  const state = useStore.getState();
  return {
    schemaVersion: 1,
    sessionId: state.sessionId,
    exportedAt: Date.now(),
    raw: logger.rawEvents.toArray(),
    semantic: logger.semanticEvents.toArray(),
  };
}

export function downloadLogAsJson(): void {
  const data = exportLog();
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `figma-mock-log-${data.sessionId}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
