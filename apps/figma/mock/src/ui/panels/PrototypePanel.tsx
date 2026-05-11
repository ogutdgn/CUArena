import { useState, useRef, useEffect } from "react";
import { useStore } from "@/engine/store";
import { getActivePage, getSelectedLayers } from "@/engine/selectors";
import { uid } from "@/util/id";
import { findDevice } from "@/util/prototypeDevices";
import { getDeviceCategories } from "@/util/framePresets";
import type { Frame, PrototypeConnection, PrototypeTrigger } from "@/types/scene";
import { ChevronDown, Plus, Minus } from "lucide-react";
import { InteractionModal } from "@/ui/overlays/InteractionModal";
import {
  setPrototypeDevice,
  createPrototypeConnection,
  deletePrototypeConnection,
} from "@/engine/prototypeCommands";

// Short display labels for interaction rows (matches Figma's compact format)
const TRIGGER_SHORT: Record<PrototypeTrigger, string> = {
  none: "None",
  on_tap: "Tap",
  on_drag: "Drag",
  while_hovering: "Hover",
  while_pressing: "Press",
  key_gamepad: "Key",
  mouse_enter: "Enter",
  mouse_leave: "Leave",
  touch_down: "Touch ↓",
  touch_up: "Touch ↑",
  after_delay: "Delay",
};

// ─── main panel ───────────────────────────────────────────────────────────────

export function PrototypePanel() {
  const page = useStore((s) => getActivePage(s));
  const selection = useStore((s) => getSelectedLayers(s));

  if (!page) return null;

  const settings = page.prototypeSettings ?? { device: null, backgroundColor: { r: 0.055, g: 0.051, b: 0.051, a: 1 } };
  const allConnections = page.prototypeConnections ?? [];
  const topFrames = page.children.filter((c) => c.type === "frame") as Frame[];

  if (selection.length === 0) {
    return <NoSelectionPanel settings={settings} pageId={page.id} />;
  }

  const layer = selection[0];
  const isTopLevelFrame = layer.type === "frame" && layer.parentId === page.id;

  if (isTopLevelFrame) {
    return <FramePanel frame={layer as Frame} connections={allConnections} topFrames={topFrames} pageId={page.id} />;
  }

  return <ItemPanel layer={layer} connections={allConnections} topFrames={topFrames} pageId={page.id} />;
}

// ─── no-selection: prototype settings ─────────────────────────────────────────

function NoSelectionPanel({
  settings,
  pageId,
}: {
  settings: { device: string | null; backgroundColor: { r: number; g: number; b: number; a: number } };
  pageId: string;
}) {
  const [deviceOpen, setDeviceOpen] = useState(false);
  const deviceRef = useRef<HTMLDivElement>(null);
  const device = findDevice(settings.device);

  useEffect(() => {
    if (!deviceOpen) return;
    function onDoc(e: MouseEvent) {
      if (!deviceRef.current?.contains(e.target as Node)) setDeviceOpen(false);
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [deviceOpen]);

  function setDevice(id: string | null) {
    setDeviceOpen(false);
    setPrototypeDevice(pageId, id);
  }

  return (
    <div style={{ padding: "12px 16px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ fontSize: "var(--fs-sm)", fontWeight: 600, color: "var(--color-text-primary)" }}>
        Prototype settings
      </div>

      {/* Device dropdown */}
      <div ref={deviceRef} style={{ position: "relative" }}>
        <button
          onClick={() => setDeviceOpen((v) => !v)}
          style={{
            width: "100%",
            height: 28,
            background: "var(--color-bg-input)",
            border: "1px solid var(--color-border)",
            borderRadius: 6,
            display: "flex",
            alignItems: "center",
            padding: "0 8px",
            fontSize: "var(--fs-sm)",
            color: "var(--color-text-primary)",
            gap: 4,
          }}
        >
          <span style={{ flex: 1, textAlign: "left" }}>{device ? device.label : "No device"}</span>
          <ChevronDown size={11} style={{ color: "var(--color-text-secondary)" }} />
        </button>
        {deviceOpen && (
          <div
            style={{
              position: "absolute",
              top: 32,
              left: 0,
              right: 0,
              background: "var(--color-bg-panel-elevated)",
              border: "1px solid var(--color-border-strong)",
              borderRadius: 6,
              boxShadow: "0 12px 28px rgba(0,0,0,0.5)",
              zIndex: 200,
              maxHeight: 320,
              overflowY: "auto",
              padding: 4,
            }}
          >
            <DeviceOption label="No device" selected={!settings.device} onClick={() => setDevice(null)} />
            {getDeviceCategories().map((cat) => (
              <div key={cat.id}>
                <div style={{ height: 1, background: "var(--color-divider)", margin: "4px 0" }} />
                <div style={{ padding: "3px 8px 1px", fontSize: "var(--fs-xs)", color: "var(--color-text-disabled)", fontWeight: 600, letterSpacing: 0.3, textTransform: "uppercase" }}>
                  {cat.label}
                </div>
                {cat.presets.map((d) => (
                  <DeviceOption
                    key={d.id}
                    label={d.label}
                    size={`${d.w}×${d.h}`}
                    selected={settings.device === d.id}
                    onClick={() => setDevice(d.id)}
                  />
                ))}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Device preview — only shown when a device is selected */}
      {device && <DevicePreview device={device} />}
    </div>
  );
}

function DeviceOption({
  label,
  size,
  selected,
  onClick,
}: {
  label: string;
  size?: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        height: 26,
        padding: "0 8px",
        borderRadius: 4,
        background: selected ? "var(--color-selection-blue)" : "transparent",
        color: selected ? "var(--color-text-on-accent)" : "var(--color-text-primary)",
        fontSize: "var(--fs-sm)",
        textAlign: "left",
      }}
      onMouseEnter={(e) => { if (!selected) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
      onMouseLeave={(e) => { if (!selected) e.currentTarget.style.background = "transparent"; }}
    >
      <span style={{ flex: 1 }}>{label}</span>
      {size && <span style={{ color: selected ? "rgba(255,255,255,0.7)" : "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{size}</span>}
    </button>
  );
}

function DevicePreview({ device }: { device: NonNullable<ReturnType<typeof findDevice>> }) {
  const MAX_W = 176;
  const MAX_H = 164;
  const scale = Math.min(MAX_W / device.w, MAX_H / device.h);
  const pw = Math.round(device.w * scale);
  const ph = Math.round(device.h * scale);
  const radius = device.kind === "phone" ? Math.round(14 * scale) : device.kind === "tablet" ? Math.round(10 * scale) : 4;
  const screenInset = 3;
  const screenRadius = Math.max(2, radius - 2);
  const showIsland = device.kind === "phone" && ph > 60;

  return (
    <div style={{ width: "100%", display: "flex", justifyContent: "center", padding: "8px 0" }}>
      <div
        style={{
          width: pw,
          height: ph,
          borderRadius: radius,
          background: "linear-gradient(135deg, #2a2a2a 0%, #0e0e0e 100%)",
          border: "1.5px solid rgba(255,255,255,0.18)",
          position: "relative",
          flexShrink: 0,
          boxShadow: "0 8px 24px rgba(0,0,0,0.6)",
        }}
      >
        {/* Screen */}
        <div
          style={{
            position: "absolute",
            inset: screenInset,
            borderRadius: screenRadius,
            background: "#0d0d1a",
          }}
        />
        {/* Dynamic island for phones */}
        {showIsland && (
          <div
            style={{
              position: "absolute",
              top: screenInset + 4,
              left: "50%",
              transform: "translateX(-50%)",
              width: Math.round(pw * 0.35),
              height: Math.max(4, Math.round(ph * 0.015)),
              background: "#000",
              borderRadius: 99,
              zIndex: 1,
            }}
          />
        )}
        {/* Dimensions label */}
        <div
          style={{
            position: "absolute",
            bottom: screenInset + 4,
            left: 0,
            right: 0,
            textAlign: "center",
            fontSize: 9,
            color: "rgba(255,255,255,0.25)",
            pointerEvents: "none",
            lineHeight: 1,
          }}
        >
          {device.w}×{device.h}
        </div>
      </div>
    </div>
  );
}

// ─── frame selected ───────────────────────────────────────────────────────────

function FramePanel({
  frame,
  connections,
  topFrames,
  pageId,
}: {
  frame: Frame;
  connections: PrototypeConnection[];
  topFrames: Frame[];
  pageId: string;
}) {
  return (
    <InteractionsPanel
      sourceLayerId={frame.id}
      connections={connections}
      topFrames={topFrames}
      pageId={pageId}
    />
  );
}

// ─── item inside frame selected ───────────────────────────────────────────────

function ItemPanel({
  layer,
  connections,
  topFrames,
  pageId,
}: {
  layer: import("@/types/scene").Layer;
  connections: PrototypeConnection[];
  topFrames: Frame[];
  pageId: string;
}) {
  return (
    <InteractionsPanel
      sourceLayerId={layer.id}
      connections={connections}
      topFrames={topFrames}
      pageId={pageId}
    />
  );
}

// ─── shared interactions panel (frame & item selection share this) ────────────

function InteractionsPanel({
  sourceLayerId,
  connections,
  topFrames,
  pageId,
}: {
  sourceLayerId: string;
  connections: PrototypeConnection[];
  topFrames: Frame[];
  pageId: string;
}) {
  const [editingConnId, setEditingConnId] = useState<string | null>(null);
  const layerConns = connections.filter((c) => c.sourceLayerId === sourceLayerId);
  const editingConn = editingConnId ? layerConns.find((c) => c.id === editingConnId) ?? null : null;

  // Pre-create a default connection and open the modal for it. Auto-save model:
  // the row appears immediately and every modal change updates it in place.
  function addInteraction() {
    const id = uid("conn");
    const defaultDest = topFrames[0]?.id;
    const newConn: PrototypeConnection = {
      id,
      sourceLayerId,
      trigger: "on_tap",
      action: "navigate_to",
      destinationFrameId: defaultDest,
      animation: "instant",
    };
    createPrototypeConnection(pageId, newConn);
    setEditingConnId(id);
  }

  function deleteConnection(id: string) {
    deletePrototypeConnection(pageId, id);
    if (editingConnId === id) setEditingConnId(null);
  }

  return (
    <>
      <div style={{ display: "flex", flexDirection: "column" }}>
        {/* Interactions */}
        <Section
          label="Interactions"
          action={
            <button onClick={addInteraction} style={iconBtnStyle}><Plus size={12} /></button>
          }
        >
          {layerConns.map((conn) => (
            <InteractionRow
              key={conn.id}
              connection={conn}
              topFrames={topFrames}
              onEdit={() => setEditingConnId(conn.id)}
              onDelete={() => deleteConnection(conn.id)}
            />
          ))}
        </Section>

        {/* Show prototype settings */}
        <div style={{ padding: "10px 16px", borderBottom: "1px solid var(--color-border)" }}>
          <button
            onClick={() => useStore.setState((s) => { s.selectionByPage[s.activePageId] = []; })}
            style={fullBtnStyle}
          >
            Show prototype settings
          </button>
        </div>
      </div>

      {/* Interaction modal — auto-saves on every field change */}
      {editingConn && (
        <InteractionModal
          connection={editingConn}
          pageId={pageId}
          frames={topFrames}
          onClose={() => setEditingConnId(null)}
        />
      )}
    </>
  );
}

// ─── interaction row ──────────────────────────────────────────────────────────

function InteractionRow({
  connection,
  topFrames,
  onEdit,
  onDelete,
}: {
  connection: PrototypeConnection;
  topFrames: Frame[];
  onEdit: () => void;
  onDelete: () => void;
}) {
  const shortTrigger = TRIGGER_SHORT[connection.trigger] ?? connection.trigger;
  const hasDestination = !!connection.destinationFrameId && connection.action !== "none" && connection.action !== "back";
  const destName = connection.destinationFrameId
    ? (topFrames.find((f) => f.id === connection.destinationFrameId)?.name ?? "Frame")
    : null;

  const midIcon = hasDestination ? "→" : "⊘";
  const rightLabel = destName ?? "None";

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6 }}>
      <button
        onClick={onEdit}
        style={{
          flex: 1,
          height: 32,
          background: "var(--color-bg-input)",
          border: "1px solid var(--color-border)",
          borderRadius: 6,
          display: "grid",
          gridTemplateColumns: "1fr auto 1fr",
          alignItems: "center",
          padding: "0 10px",
          gap: 6,
          textAlign: "left",
          cursor: "pointer",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--color-border-strong)")}
        onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--color-border)")}
      >
        <span style={{ fontSize: "var(--fs-sm)", color: "var(--color-text-primary)", fontWeight: 500 }}>
          {shortTrigger}
        </span>
        <span style={{ fontSize: "var(--fs-sm)", color: "var(--color-text-muted)", userSelect: "none" }}>
          {midIcon}
        </span>
        <span style={{ fontSize: "var(--fs-sm)", color: "var(--color-text-secondary)", textAlign: "right", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {rightLabel}
        </span>
      </button>
      <button
        onClick={onDelete}
        title="Delete interaction"
        style={{
          width: 28,
          height: 32,
          display: "grid",
          placeItems: "center",
          borderRadius: 6,
          border: "1px solid var(--color-border)",
          background: "var(--color-bg-input)",
          color: "var(--color-text-secondary)",
          flexShrink: 0,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = "var(--color-border-strong)";
          e.currentTarget.style.color = "var(--color-text-primary)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = "var(--color-border)";
          e.currentTarget.style.color = "var(--color-text-secondary)";
        }}
      >
        <Minus size={12} />
      </button>
    </div>
  );
}

// ─── shared components ────────────────────────────────────────────────────────

function Section({
  label,
  action,
  children,
}: {
  label: string;
  action?: React.ReactNode;
  children?: React.ReactNode;
}) {
  return (
    <div style={{ padding: "10px 16px", borderBottom: "1px solid var(--color-border)" }}>
      <div style={{ display: "flex", alignItems: "center" }}>
        <span style={{ flex: 1, fontSize: "var(--fs-sm)", color: "var(--color-text-secondary)" }}>{label}</span>
        {action}
      </div>
      {children}
    </div>
  );
}

const iconBtnStyle: React.CSSProperties = {
  width: 20,
  height: 20,
  display: "grid",
  placeItems: "center",
  borderRadius: 4,
  color: "var(--color-text-secondary)",
  background: "transparent",
};

const fullBtnStyle: React.CSSProperties = {
  width: "100%",
  height: 28,
  borderRadius: 6,
  border: "1px solid var(--color-border)",
  background: "var(--color-bg-input)",
  color: "var(--color-text-primary)",
  fontSize: "var(--fs-sm)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};
