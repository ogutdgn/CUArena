// Floating interaction editor popup — trigger + action pickers.

import { useEffect, useRef } from "react";
import { useStore } from "@/engine/store";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import { X, ChevronDown } from "lucide-react";
import type { PrototypeConnection, PrototypeTrigger, PrototypeAction, Frame } from "@/types/scene";
import { useState } from "react";

export const TRIGGER_LABELS: Record<PrototypeTrigger, string> = {
  none: "None",
  on_tap: "On tap",
  on_drag: "On drag",
  while_hovering: "While hovering",
  while_pressing: "While pressing",
  key_gamepad: "Key / Gamepad",
  mouse_enter: "Mouse enter",
  mouse_leave: "Mouse leave",
  touch_down: "Touch down",
  touch_up: "Touch up",
  after_delay: "After delay",
};

export const ACTION_LABELS: Record<PrototypeAction, string> = {
  none: "None",
  navigate_to: "Navigate to",
  change_to: "Change to",
  back: "Back",
  scroll_to: "Scroll to",
  open_link: "Open link",
  set_variable: "Set variable",
  set_variable_mode: "Set variable mode",
  conditional: "Conditional",
  open_overlay: "Open overlay",
  swap_overlay: "Swap overlay",
  close_overlay: "Close overlay",
};

const TRIGGERS = Object.keys(TRIGGER_LABELS) as PrototypeTrigger[];
const ACTIONS = Object.keys(ACTION_LABELS) as PrototypeAction[];

interface Props {
  connection: PrototypeConnection | null; // null → new
  sourceLayerId: string;
  pageId: string;
  frames: Frame[];
  onClose: () => void;
  onDelete?: (id: string) => void;
}

export function InteractionModal({ connection, sourceLayerId, pageId, frames, onClose, onDelete }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [trigger, setTrigger] = useState<PrototypeTrigger>(connection?.trigger ?? "on_tap");
  const [action, setAction] = useState<PrototypeAction>(connection?.action ?? "navigate_to");
  const [destFrameId, setDestFrameId] = useState<string>(connection?.destinationFrameId ?? (frames[0]?.id ?? ""));
  const [destOpen, setDestOpen] = useState(false);
  const destRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (!ref.current?.contains(e.target as Node)) onClose();
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [onClose]);

  // Close dest dropdown on outside click
  useEffect(() => {
    if (!destOpen) return;
    function onDoc(e: MouseEvent) {
      if (!destRef.current?.contains(e.target as Node)) setDestOpen(false);
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [destOpen]);

  function save() {
    if (connection) {
      // Update existing
      const prev = connection;
      useStore.setState((s) => {
        const p = s.document.pages.find((pg) => pg.id === pageId);
        if (!p?.prototypeConnections) return;
        const c = p.prototypeConnections.find((c) => c.id === connection.id);
        if (!c) return;
        c.trigger = trigger;
        c.action = action;
        c.destinationFrameId = needsDest(action) ? destFrameId : undefined;
      });
      if (prev.trigger !== trigger) {
        emitSemantic({ name: "update_prototype_connection", connectionId: connection.id, field: "trigger", before: prev.trigger, after: trigger });
      }
      if (prev.action !== action) {
        emitSemantic({ name: "update_prototype_connection", connectionId: connection.id, field: "action", before: prev.action, after: action });
      }
      if (needsDest(action) && prev.destinationFrameId !== destFrameId) {
        emitSemantic({ name: "update_prototype_connection", connectionId: connection.id, field: "destinationFrameId", before: prev.destinationFrameId ?? null, after: destFrameId });
      }
    } else {
      // Create new
      const id = uid("conn");
      const newConn: PrototypeConnection = {
        id,
        sourceLayerId,
        trigger,
        action,
        destinationFrameId: needsDest(action) ? destFrameId : undefined,
        animation: "instant",
      };
      useStore.setState((s) => {
        const p = s.document.pages.find((pg) => pg.id === pageId);
        if (!p) return;
        if (!p.prototypeConnections) p.prototypeConnections = [];
        p.prototypeConnections.push(newConn);
      });
      emitSemantic({ name: "create_prototype_connection", connectionId: id, sourceLayerId, trigger, action });
    }
    onClose();
  }

  const destFrame = frames.find((f) => f.id === destFrameId);

  return (
    <div
      ref={ref}
      style={{
        position: "fixed",
        right: 248,
        top: 120,
        width: 220,
        background: "var(--color-bg-panel-elevated)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: 8,
        boxShadow: "0 16px 40px rgba(0,0,0,0.6)",
        zIndex: 600,
        fontSize: "var(--fs-sm)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", padding: "8px 12px", borderBottom: "1px solid var(--color-border)" }}>
        <span style={{ flex: 1, fontWeight: 600, color: "var(--color-text-primary)" }}>Interaction</span>
        <button onClick={onClose} style={{ color: "var(--color-text-secondary)", display: "grid", placeItems: "center", width: 20, height: 20 }}>
          <X size={13} />
        </button>
      </div>

      {/* Trigger section */}
      <div style={{ padding: "8px 0" }}>
        <div style={{ padding: "0 12px 4px", fontSize: "var(--fs-xs)", color: "var(--color-text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Trigger
        </div>
        {TRIGGERS.map((t) => (
          <OptionRow key={t} label={TRIGGER_LABELS[t]} selected={trigger === t} onClick={() => setTrigger(t)} />
        ))}
      </div>

      {/* Action section */}
      <div style={{ padding: "8px 0", borderTop: "1px solid var(--color-border)" }}>
        <div style={{ padding: "0 12px 4px", fontSize: "var(--fs-xs)", color: "var(--color-text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Action
        </div>
        {ACTIONS.map((a) => (
          <OptionRow key={a} label={ACTION_LABELS[a]} selected={action === a} onClick={() => setAction(a)} />
        ))}
      </div>

      {/* Destination frame picker (for navigate_to / open_overlay / swap_overlay) */}
      {needsDest(action) && frames.length > 0 && (
        <div style={{ padding: "8px 12px", borderTop: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: "var(--fs-xs)", color: "var(--color-text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 6 }}>
            Destination
          </div>
          <div ref={destRef} style={{ position: "relative" }}>
            <button
              onClick={() => setDestOpen((v) => !v)}
              style={{
                width: "100%",
                height: 26,
                background: "var(--color-bg-input)",
                border: "1px solid var(--color-border)",
                borderRadius: 4,
                display: "flex",
                alignItems: "center",
                padding: "0 8px",
                gap: 4,
                color: "var(--color-text-primary)",
                fontSize: "var(--fs-sm)",
              }}
            >
              <span style={{ flex: 1, textAlign: "left", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {destFrame?.name ?? "Select frame"}
              </span>
              <ChevronDown size={10} />
            </button>
            {destOpen && (
              <div style={{
                position: "absolute",
                top: 30,
                left: 0,
                right: 0,
                background: "var(--color-bg-panel-elevated)",
                border: "1px solid var(--color-border-strong)",
                borderRadius: 6,
                boxShadow: "0 8px 24px rgba(0,0,0,0.5)",
                zIndex: 700,
                padding: 4,
                maxHeight: 180,
                overflowY: "auto",
              }}>
                {frames.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => { setDestFrameId(f.id); setDestOpen(false); }}
                    style={{
                      width: "100%",
                      height: 26,
                      padding: "0 8px",
                      borderRadius: 4,
                      background: f.id === destFrameId ? "var(--color-selection-blue)" : "transparent",
                      color: f.id === destFrameId ? "var(--color-text-on-accent)" : "var(--color-text-primary)",
                      fontSize: "var(--fs-sm)",
                      textAlign: "left",
                      display: "flex",
                      alignItems: "center",
                    }}
                    onMouseEnter={(e) => { if (f.id !== destFrameId) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
                    onMouseLeave={(e) => { if (f.id !== destFrameId) e.currentTarget.style.background = "transparent"; }}
                  >
                    {f.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{ padding: "8px 12px", borderTop: "1px solid var(--color-border)", display: "flex", gap: 6 }}>
        {connection && onDelete && (
          <button
            onClick={() => { onDelete(connection.id); onClose(); }}
            style={{
              height: 28,
              padding: "0 10px",
              borderRadius: 6,
              border: "1px solid var(--color-border)",
              background: "transparent",
              color: "var(--color-text-muted)",
              fontSize: "var(--fs-sm)",
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = "var(--color-text-primary)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = "var(--color-text-muted)"; }}
          >
            Delete
          </button>
        )}
        <button
          onClick={save}
          style={{
            flex: 1,
            height: 28,
            borderRadius: 6,
            background: "var(--color-selection-blue)",
            color: "var(--color-text-on-accent)",
            fontSize: "var(--fs-sm)",
            fontWeight: 600,
          }}
        >
          {connection ? "Update" : "Add"}
        </button>
      </div>
    </div>
  );
}

function OptionRow({ label, selected, onClick }: { label: string; selected: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        width: "100%",
        height: 24,
        padding: "0 12px",
        display: "flex",
        alignItems: "center",
        gap: 8,
        background: selected ? "var(--color-selection-blue)" : "transparent",
        color: selected ? "var(--color-text-on-accent)" : "var(--color-text-primary)",
        fontSize: "var(--fs-sm)",
        textAlign: "left",
      }}
      onMouseEnter={(e) => { if (!selected) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
      onMouseLeave={(e) => { if (!selected) e.currentTarget.style.background = "transparent"; }}
    >
      {label}
    </button>
  );
}

function needsDest(action: PrototypeAction): boolean {
  return action === "navigate_to" || action === "change_to" || action === "open_overlay" || action === "swap_overlay";
}
