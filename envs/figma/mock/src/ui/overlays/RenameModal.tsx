// Cmd+R rename modal. Slice 11 simplification: single text input.

import { useEffect, useRef, useState } from "react";
import { useStore } from "@/engine/store";
import { renameLayer } from "@/engine/hierarchyCommands";
import { getSelectedLayers } from "@/engine/selectors";

export function RenameModal() {
  const open = useStore((s) => s.openModal === "rename");
  const layers = useStore((s) => getSelectedLayers(s));
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [draft, setDraft] = useState("");
  const allSame = layers.length > 0 && layers.every((l) => l.name === layers[0].name);

  useEffect(() => {
    if (open) {
      setDraft(layers.length === 1 ? layers[0].name : allSame ? layers[0].name : "");
      requestAnimationFrame(() => {
        inputRef.current?.focus();
        inputRef.current?.select();
      });
    }
  }, [open, layers.length, layers[0]?.name, allSame]);

  if (!open) return null;

  function commit() {
    const v = draft.trim();
    if (v) {
      for (const l of layers) {
        renameLayer(l.id, v, "rename_modal");
      }
    }
    useStore.setState((s) => { s.openModal = null; });
  }

  function cancel() {
    useStore.setState((s) => { s.openModal = null; });
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "var(--color-bg-scrim)",
        display: "grid",
        placeItems: "center",
        zIndex: 200,
      }}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) cancel();
      }}
    >
      <div
        style={{
          width: 360,
          background: "var(--color-bg-panel-elevated)",
          border: "1px solid var(--color-border-strong)",
          borderRadius: 8,
          boxShadow: "0 14px 32px rgba(0,0,0,0.55)",
          padding: 16,
        }}
      >
        <div style={{ marginBottom: 8, fontSize: "var(--fs-md)", fontWeight: 600 }}>Rename</div>
        <div style={{ marginBottom: 12, fontSize: "var(--fs-xs)", color: "var(--color-text-muted)" }}>
          {layers.length === 1
            ? `Rename "${layers[0].name}"`
            : `Rename ${layers.length} layers (use # for current name, %n for index)`}
        </div>
        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={allSame ? "" : "Mixed"}
          onKeyDown={(e) => {
            if (e.key === "Enter") commit();
            if (e.key === "Escape") cancel();
          }}
          style={{
            width: "100%",
            height: 32,
            background: "var(--color-bg-input)",
            color: "var(--color-text-primary)",
            border: "1px solid var(--color-border)",
            borderRadius: 4,
            padding: "0 8px",
            fontSize: "var(--fs-base)",
            outline: 0,
          }}
        />
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12 }}>
          <button
            onClick={cancel}
            style={{
              height: 28,
              padding: "0 12px",
              borderRadius: 4,
              background: "transparent",
              color: "var(--color-text-secondary)",
              fontSize: "var(--fs-sm)",
            }}
          >
            Cancel
          </button>
          <button
            onClick={commit}
            style={{
              height: 28,
              padding: "0 12px",
              borderRadius: 4,
              background: "var(--color-selection-blue)",
              color: "var(--color-text-on-accent)",
              fontSize: "var(--fs-sm)",
              fontWeight: 600,
            }}
          >
            Rename
          </button>
        </div>
      </div>
    </div>
  );
}
