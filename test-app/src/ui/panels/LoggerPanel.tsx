// Dev panel: live event stream + Export JSON. Toggled with backtick (`).

import { useEffect, useState } from "react";
import { logger } from "@/logger/buffer";
import { downloadLogAsJson } from "@/logger/export";
import { Download, X } from "lucide-react";
import { useStore } from "@/engine/store";

export function LoggerPanel() {
  const [tick, setTick] = useState(0);
  useEffect(() => logger.subscribe(() => setTick((n) => n + 1)), []);

  // Use tick to force re-render on each new event.
  void tick;
  const semantic = logger.semanticEvents.slice(-200).reverse();
  const rawCount = logger.rawEvents.length;

  return (
    <aside
      className="no-select"
      style={{
        position: "fixed",
        right: 12,
        bottom: 64,
        width: 380,
        maxHeight: "70vh",
        background: "var(--color-bg-panel-elevated)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: 8,
        boxShadow: "0 12px 28px rgba(0,0,0,0.5)",
        display: "flex",
        flexDirection: "column",
        zIndex: 400,
      }}
    >
      <header
        style={{
          height: 36,
          padding: "0 8px 0 12px",
          display: "flex",
          alignItems: "center",
          gap: 6,
          borderBottom: "1px solid var(--color-border)",
          fontSize: "var(--fs-sm)",
          color: "var(--color-text-primary)",
        }}
      >
        <strong>Logger</strong>
        <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>
          {logger.semanticEvents.length} semantic · {rawCount} raw
        </span>
        <span style={{ flex: 1 }} />
        <button
          onClick={() => downloadLogAsJson()}
          title="Export log as JSON"
          style={{
            height: 26,
            padding: "0 8px",
            borderRadius: 4,
            background: "var(--color-bg-input)",
            color: "var(--color-text-primary)",
            display: "flex",
            alignItems: "center",
            gap: 4,
            fontSize: "var(--fs-xs)",
          }}
        >
          <Download size={12} /> Export
        </button>
        <button
          onClick={() => useStore.setState({ showLogger: false })}
          title="Close (`)"
          style={{
            width: 24,
            height: 24,
            borderRadius: 4,
            color: "var(--color-text-secondary)",
            display: "grid",
            placeItems: "center",
          }}
        >
          <X size={12} />
        </button>
      </header>
      <div className="scroll-y" style={{ flex: 1, padding: "4px 0" }}>
        {semantic.map((e) => (
          <div
            key={e.eventId}
            style={{
              padding: "4px 12px",
              fontSize: "var(--fs-xs)",
              color: "var(--color-text-secondary)",
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
              borderBottom: "1px solid var(--color-divider)",
              wordBreak: "break-all",
            }}
          >
            <span style={{ color: "var(--color-selection-blue)" }}>{e.name}</span>
            <span style={{ marginLeft: 8 }}>{summarize(e)}</span>
          </div>
        ))}
        {semantic.length === 0 && (
          <div style={{ padding: 12, color: "var(--color-text-muted)" }}>No semantic events yet.</div>
        )}
      </div>
    </aside>
  );
}

function summarize(e: object): string {
  const skip = new Set(["name", "schemaVersion", "sessionId", "eventId", "timestamp", "pageId", "rawEventIdRange"]);
  const parts: string[] = [];
  for (const [k, v] of Object.entries(e)) {
    if (skip.has(k)) continue;
    parts.push(`${k}=${shortValue(v)}`);
  }
  return parts.join(" ");
}

function shortValue(v: unknown): string {
  if (v == null) return String(v);
  if (typeof v === "string") return v.length > 24 ? v.slice(0, 24) + "…" : v;
  if (typeof v === "number") return Number(v.toFixed(2)).toString();
  if (typeof v === "boolean") return String(v);
  if (Array.isArray(v)) return `[${v.length}]`;
  if (typeof v === "object") return JSON.stringify(v).slice(0, 40);
  return String(v);
}
