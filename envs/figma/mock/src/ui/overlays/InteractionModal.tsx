// Floating interaction editor popup — trigger + action pickers.
//
// Always edits an existing connection. The connection is created up-front in
// the panel when the user clicks "+", so this modal is pure auto-save: every
// field change immediately dispatches updatePrototypeConnection.

import { useEffect, useRef, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import { ArrowRight, Clock3, MousePointerClick, X, ChevronDown } from "lucide-react";
import type { PrototypeConnection, PrototypeTrigger, PrototypeAction, PrototypeAnimation, Frame } from "@/types/scene";
import { updatePrototypeConnection } from "@/engine/prototypeCommands";

export const TRIGGER_LABELS: Record<PrototypeTrigger, string> = {
  none: "None",
  on_tap: "On click",
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

export const ANIMATION_LABELS: Record<PrototypeAnimation, string> = {
  instant: "Instant",
  dissolve: "Dissolve",
  smart_animate: "Smart animate",
  move_in: "Move in",
  move_out: "Move out",
  push: "Push",
  slide_in: "Slide in",
  slide_out: "Slide out",
};

const ANIMATIONS = Object.keys(ANIMATION_LABELS) as PrototypeAnimation[];

interface Props {
  connection: PrototypeConnection;
  pageId: string;
  frames: Frame[];
  onClose: () => void;
}

export function InteractionModal({ connection, pageId, frames, onClose }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [openMenu, setOpenMenu] = useState<"trigger" | "action" | "destination" | "animation" | null>(null);

  const trigger = connection.trigger;
  const action = connection.action;
  const animation = connection.animation ?? "instant";
  const delayMs = connection.delayMs ?? 800;
  const destFrameId = connection.destinationFrameId ?? "";

  // Close on outside click
  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (!ref.current?.contains(e.target as Node)) onClose();
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [onClose]);

  function setTrigger(value: PrototypeTrigger) {
    const patch: Partial<Omit<PrototypeConnection, "id" | "sourceLayerId">> = { trigger: value };
    // Trigger changed AWAY from after_delay — clear the now-irrelevant delay.
    if (value !== "after_delay" && trigger === "after_delay") patch.delayMs = undefined;
    updatePrototypeConnection(pageId, connection.id, patch);
  }

  function setAction(value: PrototypeAction) {
    const patch: Partial<Omit<PrototypeConnection, "id" | "sourceLayerId">> = { action: value };
    if (!needsDest(value) && connection.destinationFrameId !== undefined) {
      patch.destinationFrameId = undefined;
    } else if (needsDest(value) && !connection.destinationFrameId && frames[0]) {
      patch.destinationFrameId = frames[0].id;
    }
    updatePrototypeConnection(pageId, connection.id, patch);
  }

  function setAnimation(value: PrototypeAnimation) {
    updatePrototypeConnection(pageId, connection.id, { animation: value });
  }

  function setDestFrameId(value: string) {
    updatePrototypeConnection(pageId, connection.id, { destinationFrameId: value });
  }

  function setDelayMs(value: number) {
    updatePrototypeConnection(pageId, connection.id, { delayMs: Math.max(0, Math.min(60000, value)) });
  }

  const destFrame = frames.find((f) => f.id === destFrameId);

  return (
    <div
      ref={ref}
      onPointerDown={(e) => e.stopPropagation()}
      onPointerMove={(e) => e.stopPropagation()}
      onPointerUp={(e) => e.stopPropagation()}
      onClick={(e) => e.stopPropagation()}
      onWheel={(e) => e.stopPropagation()}
      onContextMenu={(e) => e.stopPropagation()}
      style={{
        position: "fixed",
        right: 248,
        top: 120,
        width: 268,
        background: "var(--color-bg-panel-elevated)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: 8,
        boxShadow: "0 16px 40px rgba(0,0,0,0.6)",
        zIndex: 600,
        fontSize: "var(--fs-sm)",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", padding: "8px 12px", borderBottom: "1px solid var(--color-border)" }}>
        <span style={{ flex: 1, fontWeight: 600, color: "var(--color-text-primary)" }}>Interaction</span>
        <button onClick={onClose} style={{ color: "var(--color-text-secondary)", display: "grid", placeItems: "center", width: 20, height: 20 }}>
          <X size={13} />
        </button>
      </div>

      <div style={{ padding: "10px 14px", display: "flex", flexDirection: "column", gap: 10 }}>
        <SelectRow
          label="Trigger"
          value={trigger}
          display={TRIGGER_LABELS[trigger]}
          icon={trigger === "after_delay" ? <Clock3 size={13} /> : <MousePointerClick size={13} />}
          options={TRIGGERS.map((value) => ({ value, label: TRIGGER_LABELS[value] }))}
          open={openMenu === "trigger"}
          onToggle={() => setOpenMenu(openMenu === "trigger" ? null : "trigger")}
          onSelect={(value) => { setTrigger(value as PrototypeTrigger); setOpenMenu(null); }}
        />
        {trigger === "after_delay" && (
          <FieldRow label="Delay">
            <div style={selectButtonStyle}>
              <Clock3 size={13} style={{ color: "var(--color-text-secondary)" }} />
              <input
                value={`${delayMs}ms`}
                onChange={(e) => {
                  const n = Number(e.target.value.replace(/[^0-9]/g, ""));
                  if (!Number.isNaN(n)) setDelayMs(n);
                }}
                style={{
                  width: "100%",
                  background: "transparent",
                  border: 0,
                  outline: "none",
                  color: "var(--color-text-primary)",
                  fontSize: "var(--fs-sm)",
                  fontWeight: 600,
                }}
              />
            </div>
          </FieldRow>
        )}
      </div>

      <div style={{ padding: "10px 14px", borderTop: "1px solid var(--color-border)", display: "flex", flexDirection: "column", gap: 10 }}>
        <SelectRow
          label="Action"
          value={action}
          display={ACTION_LABELS[action]}
          icon={<ArrowRight size={13} />}
          options={ACTIONS.map((value) => ({ value, label: ACTION_LABELS[value] }))}
          open={openMenu === "action"}
          onToggle={() => setOpenMenu(openMenu === "action" ? null : "action")}
          onSelect={(value) => { setAction(value as PrototypeAction); setOpenMenu(null); }}
        />
        {needsDest(action) && frames.length > 0 && (
          <SelectRow
            label="Destination"
            value={destFrameId}
            display={destFrame?.name ?? "Select frame"}
            options={frames.map((frame) => ({ value: frame.id, label: frame.name }))}
            open={openMenu === "destination"}
            onToggle={() => setOpenMenu(openMenu === "destination" ? null : "destination")}
            onSelect={(value) => { setDestFrameId(value); setOpenMenu(null); }}
          />
        )}
      </div>

      <div style={{ padding: "10px 14px", borderTop: "1px solid var(--color-border)" }}>
        <SelectRow
          label="Animation"
          value={animation}
          display={ANIMATION_LABELS[animation]}
          options={ANIMATIONS.map((value) => ({ value, label: ANIMATION_LABELS[value] }))}
          open={openMenu === "animation"}
          onToggle={() => setOpenMenu(openMenu === "animation" ? null : "animation")}
          onSelect={(value) => { setAnimation(value as PrototypeAnimation); setOpenMenu(null); }}
        />
      </div>
    </div>
  );
}

const selectButtonStyle: CSSProperties = {
  width: "100%",
  height: 26,
  background: "var(--color-bg-input)",
  border: "1px solid var(--color-border)",
  borderRadius: 5,
  display: "flex",
  alignItems: "center",
  padding: "0 8px",
  gap: 6,
  color: "var(--color-text-primary)",
  fontSize: "var(--fs-sm)",
};

function FieldRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "72px 1fr", alignItems: "center", gap: 8 }}>
      <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--fs-sm)", fontWeight: 600 }}>{label}</div>
      {children}
    </div>
  );
}

function SelectRow({
  label,
  value,
  display,
  options,
  open,
  icon,
  onToggle,
  onSelect,
}: {
  label: string;
  value: string;
  display: string;
  options: Array<{ value: string; label: string }>;
  open: boolean;
  icon?: ReactNode;
  onToggle: () => void;
  onSelect: (value: string) => void;
}) {
  return (
    <FieldRow label={label}>
      <div style={{ position: "relative" }}>
        <button onClick={onToggle} style={selectButtonStyle}>
          <span style={{ display: "grid", placeItems: "center", color: "var(--color-text-secondary)", width: 13, height: 13, flexShrink: 0 }}>
            {icon}
          </span>
          <span style={{ flex: 1, textAlign: "left", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontWeight: 600 }}>
            {display}
          </span>
          <ChevronDown size={10} style={{ color: "var(--color-text-secondary)", flexShrink: 0 }} />
        </button>
        {open && (
          <div
            style={{
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
              maxHeight: 190,
              overflowY: "auto",
            }}
          >
            {options.map((option) => (
              <button
                key={option.value}
                onClick={() => onSelect(option.value)}
                style={{
                  width: "100%",
                  height: 26,
                  padding: "0 8px",
                  borderRadius: 4,
                  background: option.value === value ? "var(--color-selection-blue)" : "transparent",
                  color: option.value === value ? "var(--color-text-on-accent)" : "var(--color-text-primary)",
                  fontSize: "var(--fs-sm)",
                  textAlign: "left",
                  display: "flex",
                  alignItems: "center",
                }}
                onMouseEnter={(e) => { if (option.value !== value) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
                onMouseLeave={(e) => { if (option.value !== value) e.currentTarget.style.background = "transparent"; }}
              >
                {option.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </FieldRow>
  );
}

function needsDest(action: PrototypeAction): boolean {
  return action === "navigate_to" || action === "change_to" || action === "open_overlay" || action === "swap_overlay";
}
