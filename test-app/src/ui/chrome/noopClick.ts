// Helper used by every visual-only chrome element.

import { emitSemantic } from "@/logger/semantic";

export function noopClick(elementId: string, evt?: { clientX?: number; clientY?: number }) {
  emitSemantic({
    name: "noop_click",
    elementId,
    pointer: { x: evt?.clientX ?? 0, y: evt?.clientY ?? 0 },
  });
}
