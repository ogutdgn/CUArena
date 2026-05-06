// Toast notifications — bottom-center stack, auto-dismiss.

import { useEffect } from "react";
import { useStore } from "@/engine/store";
import { uid } from "@/util/id";
import { X } from "lucide-react";

export function pushToast(text: string, durationMs = 3000): void {
  const id = uid("toast");
  const expiresAt = performance.now() + durationMs;
  useStore.setState((s) => {
    s.toasts.push({ id, text, expiresAt });
    if (s.toasts.length > 4) s.toasts.shift();
  });
}

function dismissToast(id: string) {
  useStore.setState((s) => {
    s.toasts = s.toasts.filter((t) => t.id !== id);
  });
}

export function Toasts() {
  const toasts = useStore((s) => s.toasts);

  useEffect(() => {
    if (toasts.length === 0) return;
    const tick = () => {
      const now = performance.now();
      const stale = toasts.filter((t) => t.expiresAt <= now);
      if (stale.length > 0) {
        useStore.setState((s) => {
          s.toasts = s.toasts.filter((t) => t.expiresAt > now);
        });
      }
    };
    const id = setInterval(tick, 250);
    return () => clearInterval(id);
  }, [toasts]);

  if (toasts.length === 0) return null;

  return (
    <div
      className="no-select"
      style={{
        position: "fixed",
        bottom: 72,
        left: "50%",
        transform: "translateX(-50%)",
        display: "flex",
        flexDirection: "column-reverse",
        gap: 8,
        zIndex: 300,
        pointerEvents: "none",
      }}
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "var(--color-bg-panel-elevated)",
            color: "var(--color-text-primary)",
            border: "1px solid var(--color-border-strong)",
            borderRadius: 6,
            padding: "8px 12px",
            boxShadow: "0 8px 22px rgba(0,0,0,0.55)",
            fontSize: "var(--fs-sm)",
            pointerEvents: "auto",
          }}
        >
          <span>{t.text}</span>
          <button
            onClick={() => dismissToast(t.id)}
            style={{
              width: 18,
              height: 18,
              borderRadius: 3,
              color: "var(--color-text-secondary)",
              display: "grid",
              placeItems: "center",
            }}
          >
            <X size={11} />
          </button>
        </div>
      ))}
    </div>
  );
}
