// Editable numeric input with commit on Enter / blur. Supports "Mixed" placeholder.

import { useEffect, useRef, useState } from "react";

export function NumericInput({
  value,
  onCommit,
  suffix,
  min,
  max,
  step = 1,
  width,
}: {
  value: number | "Mixed";
  onCommit: (n: number) => void;
  suffix?: string;
  min?: number;
  max?: number;
  step?: number;
  width?: number | string;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const ref = useRef<HTMLInputElement | null>(null);

  // Sync incoming value when not editing.
  useEffect(() => {
    if (!editing) {
      setDraft(formatValue(value));
    }
  }, [value, editing]);

  function commit() {
    const n = parseFloat(draft);
    if (Number.isFinite(n)) {
      let v = n;
      if (typeof min === "number") v = Math.max(min, v);
      if (typeof max === "number") v = Math.min(max, v);
      onCommit(v);
    }
    setEditing(false);
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
        background: "var(--color-bg-input)",
        borderRadius: 4,
        padding: "0 6px",
        width,
      }}
    >
      <input
        ref={ref}
        value={draft}
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
