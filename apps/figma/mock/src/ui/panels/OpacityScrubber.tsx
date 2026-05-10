// Opacity input + draggable % suffix. Used inside Fill/Stroke/Effect color
// rows so the user can edit by typing (input) or by dragging horizontally on
// the % glyph (Figma-style scrub). Commits clamp to [0, 100] integer percent.

import { useRef, useState } from "react";

export function OpacityScrubber({
  value,
  onCommit,
  testId,
}: {
  value: number;
  onCommit: (pct: number) => void;
  testId?: string;
}) {
  const [draft, setDraft] = useState<string | null>(null);
  const scrubRef = useRef<{ baseX: number; baseValue: number } | null>(null);
  const display = draft ?? String(value);

  function commit(n: number) {
    if (!Number.isFinite(n)) return;
    onCommit(Math.max(0, Math.min(100, Math.round(n))));
  }

  return (
    <>
      <input
        data-id={testId}
        value={display}
        onChange={(e) => setDraft(e.target.value)}
        onFocus={(e) => { setDraft(String(value)); requestAnimationFrame(() => e.target.select()); }}
        onBlur={() => {
          const n = parseFloat(display);
          if (Number.isFinite(n)) commit(n);
          setDraft(null);
        }}
        onKeyDown={(e) => { if (e.key === "Enter") (e.target as HTMLInputElement).blur(); }}
        style={{
          width: 28, background: "transparent", border: 0,
          color: "var(--color-text-primary)", fontSize: "var(--fs-sm)",
          outline: 0, textAlign: "right", padding: 0,
        }}
      />
      <span
        onPointerDown={(e) => {
          (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
          scrubRef.current = { baseX: e.clientX, baseValue: value };
        }}
        onPointerMove={(e) => {
          if (!scrubRef.current) return;
          const dx = e.clientX - scrubRef.current.baseX;
          const next = Math.max(0, Math.min(100, Math.round(scrubRef.current.baseValue + dx)));
          setDraft(String(next));
          commit(next);
        }}
        onPointerUp={(e) => {
          if (!scrubRef.current) return;
          const dx = e.clientX - scrubRef.current.baseX;
          const next = Math.max(0, Math.min(100, Math.round(scrubRef.current.baseValue + dx)));
          commit(next);
          setDraft(null);
          scrubRef.current = null;
          (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
        }}
        style={{
          fontSize: "var(--fs-xs)", color: "var(--color-text-muted)",
          flexShrink: 0, cursor: "ew-resize",
          userSelect: "none", touchAction: "none",
          paddingLeft: 2, paddingRight: 2,
        }}
      >
        %
      </span>
    </>
  );
}
