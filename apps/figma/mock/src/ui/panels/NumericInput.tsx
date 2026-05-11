// Editable numeric input with commit on Enter / blur. Supports "Mixed" placeholder.
// Also supports Figma-style drag-scrub on the icon strip at the left edge: click
// and drag horizontally to change the value (1px → step; Shift → 10×step).

import { useEffect, useRef, useState } from "react";

export function NumericInput({
  value,
  onCommit,
  suffix,
  prefix,
  min,
  max,
  step = 1,
  width,
  noBg,
  integer,
  disabled,
  onScrubStart,
  onScrubEnd,
}: {
  value: number | "Mixed";
  onCommit: (n: number, context?: { transactionId?: string }) => void;
  suffix?: string;
  // Glyph rendered inside the box on the left. When provided, it doubles as
  // the drag-scrub handle — pointer-down on it starts a horizontal scrub. If
  // omitted, a thin invisible strip serves the same purpose so click-to-edit
  // on the input still works.
  prefix?: React.ReactNode;
  min?: number;
  max?: number;
  step?: number;
  noBg?: boolean;
  width?: number | string;
  // Snap commits and live-drag values to integers. Used for counts that can
  // never be fractional (polygon sides, star points).
  integer?: boolean;
  // Renders the field greyed out and ignores edits/scrubs. Used to keep the
  // Appearance panel layout stable across shape types when a property
  // doesn't apply (e.g. corner radius on a line).
  disabled?: boolean;
  onScrubStart?: () => string | undefined;
  onScrubEnd?: (transactionId: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const ref = useRef<HTMLInputElement | null>(null);
  const scrubStateRef = useRef<{ baseX: number; baseValue: number; lastV: number; transactionId?: string } | null>(null);

  // Sync incoming value when not editing.
  useEffect(() => {
    if (!editing) {
      setDraft(formatValue(value));
    }
  }, [value, editing]);

  function commit() {
    const n = parseFloat(draft);
    if (Number.isFinite(n)) {
      onCommit(clampValue(n));
    }
    setEditing(false);
  }

  function clampValue(v: number): number {
    if (integer) v = Math.round(v);
    if (typeof min === "number") v = Math.max(min, v);
    if (typeof max === "number") v = Math.min(max, v);
    return v;
  }

  function onScrubPointerDown(e: React.PointerEvent<HTMLDivElement>) {
    if (disabled) return;
    if (typeof value !== "number") return; // No scrubbing on Mixed.
    e.preventDefault();
    e.stopPropagation();
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    scrubStateRef.current = { baseX: e.clientX, baseValue: value, lastV: value, transactionId: onScrubStart?.() };
  }

  function onScrubPointerMove(e: React.PointerEvent<HTMLDivElement>) {
    const s = scrubStateRef.current;
    if (!s) return;
    const factor = e.shiftKey ? 10 : 1;
    const dx = e.clientX - s.baseX;
    const next = clampValue(s.baseValue + dx * step * factor);
    if (next === s.lastV) return;
    s.lastV = next;
    setDraft(formatValue(next));
    // Live update — fire onCommit on each tick so the canvas reflects the
    // drag in real time. Callers can pass a transaction id so the whole scrub
    // lands as a single undoable gesture.
    onCommit(next, { transactionId: s.transactionId });
  }

  function onScrubPointerUp(e: React.PointerEvent<HTMLDivElement>) {
    const s = scrubStateRef.current;
    if (!s) return;
    (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
    scrubStateRef.current = null;
    if (s.transactionId) onScrubEnd?.(s.transactionId);
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 4,
        flex: 1,
        minWidth: 0,
        height: 24,
        background: noBg ? "transparent" : "var(--color-bg-input)",
        borderRadius: noBg ? 0 : 4,
        padding: "0 6px",
        width,
        opacity: disabled ? 0.4 : 1,
        pointerEvents: disabled ? "none" : "auto",
      }}
    >
      {/* Drag-scrub handle. When `prefix` is set the glyph itself is the
          handle (X/Y label, blur dots, spread sun, etc); otherwise a thin
          invisible strip preserves click-to-edit on the input. */}
      <div
        onPointerDown={onScrubPointerDown}
        onPointerMove={onScrubPointerMove}
        onPointerUp={onScrubPointerUp}
        onPointerCancel={onScrubPointerUp}
        style={{
          minWidth: prefix ? 14 : 6,
          height: prefix ? 20 : 18,
          flexShrink: 0,
          display: "grid",
          placeItems: "center",
          cursor: "ew-resize",
          color: "var(--color-text-muted)",
          fontSize: "var(--fs-xs)",
          touchAction: "none",
          userSelect: "none",
        }}
        title="Drag to scrub"
      >
        {prefix}
      </div>
      <input
        ref={ref}
        value={draft}
        disabled={disabled}
        onChange={(e) => setDraft(e.target.value)}
        onFocus={(e) => {
          setEditing(true);
          if (value === "Mixed") setDraft("");
          requestAnimationFrame(() => e.target.select());
        }}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            (e.target as HTMLInputElement).blur();
          } else if (e.key === "Escape") {
            setDraft(formatValue(value));
            setEditing(false);
            (e.target as HTMLInputElement).blur();
          } else if (e.key === "ArrowUp" || e.key === "ArrowDown") {
            e.preventDefault();
            const cur = parseFloat(draft);
            if (Number.isFinite(cur)) {
              const inc = (e.shiftKey ? step * 10 : step) * (e.key === "ArrowUp" ? 1 : -1);
              setDraft(String(cur + inc));
            }
          }
        }}
        style={{
          flex: 1,
          minWidth: 0,
          background: "transparent",
          border: 0,
          outline: 0,
          color: "var(--color-text-primary)",
          fontSize: "var(--fs-sm)",
          width: "100%",
        }}
      />
      {suffix && (
        <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{suffix}</span>
      )}
    </div>
  );
}

function formatValue(v: number | "Mixed"): string {
  if (v === "Mixed") return "Mixed";
  if (Number.isInteger(v)) return String(v);
  return String(Number(v.toFixed(2)));
}
