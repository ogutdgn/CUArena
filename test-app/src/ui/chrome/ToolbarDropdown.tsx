// Generic dropdown popover for toolbar buttons. Opens above the toolbar.

import { useEffect, useRef } from "react";
import type { ReactNode } from "react";

export interface DropdownItem {
  id: string;
  label: string;
  icon?: ReactNode;
  shortcut?: string;
  onClick: () => void;
  disabled?: boolean;
}

export function ToolbarDropdown({
  items,
  onClose,
  anchor,
}: {
  items: DropdownItem[];
  onClose: () => void;
  anchor: { left: number; bottom: number };
}) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (!ref.current) return;
      if (!ref.current.contains(e.target as Node)) onClose();
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("mousedown", onDoc, true);
    document.addEventListener("keydown", onKey, true);
    return () => {
      document.removeEventListener("mousedown", onDoc, true);
      document.removeEventListener("keydown", onKey, true);
    };
  }, [onClose]);

  return (
    <div
      ref={ref}
      role="menu"
      style={{
        position: "fixed",
        left: anchor.left,
        bottom: anchor.bottom,
        minWidth: 200,
        background: "var(--color-bg-panel-elevated)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: 8,
        boxShadow: "0 12px 28px rgba(0,0,0,0.5)",
        padding: 4,
        zIndex: 100,
      }}
    >
      {items.map((it) => (
        <button
          key={it.id}
          data-id={it.id}
          onClick={() => {
            if (!it.disabled) {
              it.onClick();
              onClose();
            }
          }}
          disabled={it.disabled}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "6px 10px",
            borderRadius: 4,
            color: it.disabled ? "var(--color-text-disabled)" : "var(--color-text-primary)",
            fontSize: "var(--fs-sm)",
            background: "transparent",
            textAlign: "left",
            cursor: it.disabled ? "default" : "pointer",
          }}
          onMouseEnter={(e) => {
            if (!it.disabled) e.currentTarget.style.background = "var(--color-bg-row-hover)";
          }}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          <span style={{ width: 16, display: "grid", placeItems: "center", color: "var(--color-text-secondary)" }}>
            {it.icon}
          </span>
          <span style={{ flex: 1 }}>{it.label}</span>
          {it.shortcut && (
            <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{it.shortcut}</span>
          )}
        </button>
      ))}
    </div>
  );
}
