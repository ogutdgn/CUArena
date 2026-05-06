// Shared section shell for the right-panel.

import type { ReactNode } from "react";
import { ChevronDown, Plus } from "lucide-react";
import { noopClick } from "@/ui/chrome/noopClick";

export function Section({
  title,
  children,
  addId,
  collapsibleId,
}: {
  title: string;
  children: ReactNode;
  addId?: string;
  collapsibleId?: string;
}) {
  return (
    <section
      style={{
        borderBottom: "1px solid var(--color-divider)",
        padding: "8px 12px 12px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          height: 24,
          color: "var(--color-text-secondary)",
          fontSize: "var(--fs-xs)",
          fontWeight: 600,
          letterSpacing: 0.4,
          textTransform: "uppercase",
        }}
      >
        <span style={{ flex: 1 }}>{title}</span>
        {addId && (
          <button
            data-id={addId}
            onClick={(e) => noopClick(addId, e)}
            title={`${title} — add — not implemented in this mock`}
            style={{
              width: 18,
              height: 18,
              borderRadius: 3,
              display: "grid",
              placeItems: "center",
              color: "var(--color-text-secondary)",
            }}
          >
            <Plus size={11} />
          </button>
        )}
        {collapsibleId && (
          <button
            data-id={collapsibleId}
            onClick={(e) => noopClick(collapsibleId, e)}
            title="Collapse — not implemented"
            style={{
              width: 18,
              height: 18,
              borderRadius: 3,
              display: "grid",
              placeItems: "center",
              color: "var(--color-text-secondary)",
            }}
          >
            <ChevronDown size={11} />
          </button>
        )}
      </div>
      <div style={{ marginTop: 6, display: "grid", gap: 6 }}>{children}</div>
    </section>
  );
}

export function NumericRow({ label, value, suffix }: { label: string; value: number | string; suffix?: string }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        height: 28,
      }}
    >
      <span
        style={{
          width: 18,
          color: "var(--color-text-muted)",
          fontSize: "var(--fs-xs)",
        }}
      >
        {label}
      </span>
      <input
        readOnly
        value={typeof value === "number" ? Number(value.toFixed(2)).toString() : value}
        style={{
          flex: 1,
          background: "var(--color-bg-input)",
          border: "1px solid transparent",
          color: "var(--color-text-primary)",
          height: 24,
          padding: "0 6px",
          borderRadius: 4,
          fontSize: "var(--fs-sm)",
          minWidth: 0,
          width: "100%",
        }}
      />
      {suffix && (
        <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{suffix}</span>
      )}
    </div>
  );
}
