import { useState, useRef, useEffect } from "react";
import { useStore } from "@/engine/store";
import { getActivePage, getSelectedLayers } from "@/engine/selectors";
import { uid } from "@/util/id";
import { findDevice } from "@/util/prototypeDevices";
import { getDeviceCategories } from "@/util/framePresets";
import type { Frame, PrototypeFlow, PrototypeConnection, PrototypeTrigger, ScrollBehavior, ScrollPosition } from "@/types/scene";
import { ChevronDown, Plus, Minus } from "lucide-react";
import { InteractionModal } from "@/ui/overlays/InteractionModal";
import {
  setPrototypeDevice,
  addPrototypeFlow,
  removePrototypeFlow,
  renamePrototypeFlow,
  deletePrototypeConnection,
  setLayerOverflowScrolling,
  setLayerScrollPosition,
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

  const allFlows = page.prototypeFlows ?? [];
  const frameIds = new Set(page.children.map((c) => c.id));

  // Filter out flows for deleted frames at render time. We deliberately do NOT
  // mutate the document here — if the parent delete is undone, the original
  // flow is restored automatically because it was never removed from the
  // document. (Prior implementations pruned during render via setState; that
  // either broke React's render contract or destroyed flows undo-irreversibly.)
  const flows = allFlows.filter((f) => frameIds.has(f.frameId));
  const settings = page.prototypeSettings ?? { device: null, backgroundColor: { r: 0.055, g: 0.051, b: 0.051, a: 1 } };
  const allConnections = page.prototypeConnections ?? [];
  const topFrames = page.children.filter((c) => c.type === "frame") as Frame[];

  if (selection.length === 0) {
    return <NoSelectionPanel flows={flows} settings={settings} pageId={page.id} />;
  }

  const layer = selection[0];
  const isTopLevelFrame = layer.type === "frame" && layer.parentId === page.id;

  if (isTopLevelFrame) {
    return <FramePanel frame={layer as Frame} flows={flows} connections={allConnections} topFrames={topFrames} pageId={page.id} />;
  }

  return <ItemPanel layer={layer} connections={allConnections} topFrames={topFrames} pageId={page.id} />;
}

// ─── no-selection: prototype settings ─────────────────────────────────────────

function NoSelectionPanel({
  flows,
  settings,
  pageId,
}: {
  flows: PrototypeFlow[];
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

      {/* Flows list */}
      {flows.length > 0 && (
        <div style={{ marginTop: 4 }}>
          <div style={{ fontSize: "var(--fs-sm)", fontWeight: 600, color: "var(--color-text-primary)", marginBottom: 6 }}>
            Flows
          </div>
          {flows.map((f) => (
            <FlowListItem key={f.id} flow={f} pageId={pageId} />
          ))}
        </div>
      )}
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

function FlowListItem({ flow, pageId }: { flow: PrototypeFlow; pageId: string }) {
  const page = useStore((s) => s.document.pages.find((p) => p.id === pageId));
  const frameName = page
    ? (() => {
        const node = page.children.find((c) => c.id === flow.frameId);
        return node?.name ?? flow.frameId;
      })()
    : flow.frameId;

  return (
    <button
      style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        height: 28,
        padding: "0 4px",
        borderRadius: 4,
        color: "var(--color-text-secondary)",
        fontSize: "var(--fs-sm)",
        textAlign: "left",
        gap: 6,
      }}
      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
      onClick={() => {
        const flows = useStore.getState().document.pages.find((p) => p.id === pageId)?.prototypeFlows ?? [];
        const idx = flows.findIndex((f) => f.id === flow.id);
        if (idx !== -1) {
          useStore.setState((s) => { s.prototypePreview = { pos: { x: 100, y: 100 }, flowIndex: idx }; });
        }
      }}
    >
      <span style={{ color: "var(--color-text-primary)" }}>{flow.name}</span>
      <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{frameName}</span>
    </button>
  );
}

// ─── frame selected ───────────────────────────────────────────────────────────

function FramePanel({
  frame,
  flows,
  connections,
  topFrames,
  pageId,
}: {
  frame: Frame;
  flows: PrototypeFlow[];
  connections: PrototypeConnection[];
  topFrames: Frame[];
  pageId: string;
}) {
  const [modalConn, setModalConn] = useState<PrototypeConnection | "new" | null>(null);
  const frameFlow = flows.find((f) => f.frameId === frame.id);
  const layerConns = connections.filter((c) => c.sourceLayerId === frame.id);

  function addFlow() {
    const p = useStore.getState().document.pages.find((pg) => pg.id === pageId);
    const existing = p?.prototypeFlows ?? [];
    const validFrameIds = new Set((p?.children ?? []).map((c) => c.id));
    const validCount = existing.filter((f) => validFrameIds.has(f.frameId)).length;
    const newFlow: PrototypeFlow = { id: uid("flow"), name: `Flow ${validCount + 1}`, frameId: frame.id };
    addPrototypeFlow(pageId, newFlow);
  }

  function removeFlow() {
    if (!frameFlow) return;
    removePrototypeFlow(pageId, frameFlow.id);
  }

  function renameFlow(newName: string) {
    if (!frameFlow) return;
    renamePrototypeFlow(pageId, frameFlow.id, newName);
  }

  function deleteConnection(id: string) {
    deletePrototypeConnection(pageId, id);
  }

  const overflow: ScrollBehavior = frame.overflowScrolling ?? "none";

  function setOverflow(v: ScrollBehavior) {
    setLayerOverflowScrolling(pageId, frame.id, v);
  }

  return (
    <>
      <div style={{ display: "flex", flexDirection: "column" }}>
        {/* Flow starting point */}
        <Section
          label="Flow starting point"
          action={
            frameFlow ? (
              <button onClick={removeFlow} style={iconBtnStyle}>
                <Minus size={12} />
              </button>
            ) : (
              <button onClick={addFlow} style={iconBtnStyle}>
                <Plus size={12} />
              </button>
            )
          }
        >
          {frameFlow && (
            <FlowRow
              flow={frameFlow}
              frameName={frame.name}
              allFrames={[frame]}
              onRename={renameFlow}
            />
          )}
        </Section>

        {/* Interactions */}
        <Section
          label="Interactions"
          action={
            <button onClick={() => setModalConn("new")} style={iconBtnStyle}><Plus size={12} /></button>
          }
        >
          {layerConns.map((conn) => (
            <InteractionRow
              key={conn.id}
              connection={conn}
              topFrames={topFrames}
              onEdit={() => setModalConn(conn)}
              onDelete={() => deleteConnection(conn.id)}
            />
          ))}
        </Section>

        {/* Scroll behavior */}
        <div style={{ padding: "10px 16px", borderBottom: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: "var(--fs-sm)", fontWeight: 600, color: "var(--color-text-primary)", marginBottom: 8 }}>
            Scroll behavior
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: "var(--fs-sm)", color: "var(--color-text-secondary)", flex: 1 }}>Overflow</span>
            <SelectDropdown
              value={overflow}
              options={[
                { value: "none", label: "No scrolling" },
                { value: "horizontal", label: "Horizontal scrolling" },
                { value: "vertical", label: "Vertical scrolling" },
                { value: "both", label: "Horizontal and vertical" },
              ]}
              onChange={(v) => setOverflow(v as ScrollBehavior)}
            />
          </div>
        </div>

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

      {/* Interaction modal */}
      {modalConn !== null && (
        <InteractionModal
          connection={modalConn === "new" ? null : modalConn}
          sourceLayerId={frame.id}
          pageId={pageId}
          frames={topFrames}
          onClose={() => setModalConn(null)}
          onDelete={deleteConnection}
        />
      )}
    </>
  );
}

function FlowRow({
  flow,
  frameName,
  onRename,
}: {
  flow: PrototypeFlow;
  frameName: string;
  allFrames: Frame[];
  onRename: (name: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(flow.name);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6 }}>
      {editing ? (
        <input
          autoFocus
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={() => { onRename(draft); setEditing(false); }}
          onKeyDown={(e) => {
            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
            if (e.key === "Escape") { setDraft(flow.name); setEditing(false); }
          }}
          style={{
            flex: 1,
            height: 24,
            background: "var(--color-bg-input)",
            border: "1px solid var(--color-selection-blue)",
            borderRadius: 4,
            color: "var(--color-text-primary)",
            fontSize: "var(--fs-sm)",
            padding: "0 6px",
            outline: "none",
          }}
        />
      ) : (
        <button
          onDoubleClick={() => { setDraft(flow.name); setEditing(true); }}
          style={{
            flex: 1,
            height: 24,
            background: "var(--color-bg-input)",
            border: "1px solid var(--color-border)",
            borderRadius: 4,
            color: "var(--color-text-primary)",
            fontSize: "var(--fs-sm)",
            padding: "0 6px",
            textAlign: "left",
          }}
        >
          {flow.name}
        </button>
      )}
      <div
        style={{
          height: 24,
          padding: "0 6px",
          background: "var(--color-bg-input)",
          border: "1px solid var(--color-border)",
          borderRadius: 4,
          display: "flex",
          alignItems: "center",
          gap: 4,
          fontSize: "var(--fs-sm)",
          color: "var(--color-text-primary)",
        }}
      >
        <span>{frameName}</span>
        <ChevronDown size={10} style={{ color: "var(--color-text-secondary)" }} />
      </div>
    </div>
  );
}

// ─── item inside frame selected ───────────────────────────────────────────────

function ItemPanel({ layer, connections, topFrames, pageId }: {
  layer: import("@/types/scene").Layer;
  connections: PrototypeConnection[];
  topFrames: Frame[];
  pageId: string;
}) {
  const [modalConn, setModalConn] = useState<PrototypeConnection | "new" | null>(null);
  const pos: ScrollPosition = layer.scrollPosition ?? "scroll_with_parent";
  const layerConns = connections.filter((c) => c.sourceLayerId === layer.id);

  function setPos(v: ScrollPosition) {
    setLayerScrollPosition(pageId, layer.id, v);
  }

  function deleteConnection(id: string) {
    deletePrototypeConnection(pageId, id);
  }

  return (
    <>
      <div style={{ display: "flex", flexDirection: "column" }}>
        {/* Interactions */}
        <Section
          label="Interactions"
          action={
            <button onClick={() => setModalConn("new")} style={iconBtnStyle}><Plus size={12} /></button>
          }
        >
          {layerConns.map((conn) => (
            <InteractionRow
              key={conn.id}
              connection={conn}
              topFrames={topFrames}
              onEdit={() => setModalConn(conn)}
              onDelete={() => deleteConnection(conn.id)}
            />
          ))}
        </Section>

        {/* Scroll behavior */}
        <div style={{ padding: "10px 16px", borderBottom: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: "var(--fs-sm)", fontWeight: 600, color: "var(--color-text-primary)", marginBottom: 8 }}>
            Scroll behavior
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: "var(--fs-sm)", color: "var(--color-text-secondary)", flex: 1 }}>Position</span>
            <SelectDropdown
              value={pos}
              options={[
                { value: "scroll_with_parent", label: "Scroll with parent" },
                { value: "fixed", label: "Fixed (stay in place)" },
                { value: "sticky", label: "Sticky (stop at top edge)" },
              ]}
              onChange={(v) => setPos(v as ScrollPosition)}
            />
          </div>
        </div>

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

      {modalConn !== null && (
        <InteractionModal
          connection={modalConn === "new" ? null : modalConn}
          sourceLayerId={layer.id}
          pageId={pageId}
          frames={topFrames}
          onClose={() => setModalConn(null)}
          onDelete={deleteConnection}
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
    <button
      onClick={onEdit}
      style={{
        width: "100%",
        height: 32,
        background: "var(--color-bg-input)",
        border: "1px solid var(--color-border)",
        borderRadius: 6,
        display: "grid",
        gridTemplateColumns: "1fr auto 1fr",
        alignItems: "center",
        padding: "0 10px",
        gap: 6,
        marginTop: 6,
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

function SelectDropdown({
  value,
  options,
  onChange,
}: {
  value: string;
  options: { value: string; label: string }[];
  onChange: (v: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const current = options.find((o) => o.value === value);

  useEffect(() => {
    if (!open) return;
    function onDoc(e: MouseEvent) {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [open]);

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button
        onClick={() => setOpen((v) => !v)}
        style={{
          height: 24,
          padding: "0 8px",
          background: "var(--color-bg-input)",
          border: "1px solid var(--color-border)",
          borderRadius: 4,
          fontSize: "var(--fs-sm)",
          color: "var(--color-text-primary)",
          display: "flex",
          alignItems: "center",
          gap: 4,
          maxWidth: 160,
        }}
      >
        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {current?.label ?? value}
        </span>
        <ChevronDown size={10} style={{ flexShrink: 0, color: "var(--color-text-secondary)" }} />
      </button>
      {open && (
        <div
          style={{
            position: "absolute",
            top: 28,
            right: 0,
            minWidth: 180,
            background: "var(--color-bg-panel-elevated)",
            border: "1px solid var(--color-border-strong)",
            borderRadius: 6,
            boxShadow: "0 8px 24px rgba(0,0,0,0.5)",
            zIndex: 200,
            padding: 4,
          }}
        >
          {options.map((o) => (
            <button
              key={o.value}
              onClick={() => { onChange(o.value); setOpen(false); }}
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                height: 26,
                padding: "0 8px",
                borderRadius: 4,
                background: o.value === value ? "var(--color-selection-blue)" : "transparent",
                color: o.value === value ? "var(--color-text-on-accent)" : "var(--color-text-primary)",
                fontSize: "var(--fs-sm)",
                textAlign: "left",
              }}
              onMouseEnter={(e) => { if (o.value !== value) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
              onMouseLeave={(e) => { if (o.value !== value) e.currentTarget.style.background = "transparent"; }}
            >
              {o.label}
            </button>
          ))}
        </div>
      )}
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
