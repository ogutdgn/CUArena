import { useState, useRef, useEffect } from "react";
import { useStore } from "@/engine/store";
import { getActivePage, getSelectedLayers } from "@/engine/selectors";
import { uid } from "@/util/id";
import { PROTOTYPE_DEVICES, findDevice } from "@/util/prototypeDevices";
import { noopClick } from "@/ui/chrome/noopClick";
import type { Frame, PrototypeFlow, ScrollBehavior, ScrollPosition } from "@/types/scene";
import { ChevronDown, Plus, Minus, Monitor } from "lucide-react";
import { emitSemantic } from "@/logger/semantic";

// ─── helpers ──────────────────────────────────────────────────────────────────

function colorToHex(c: { r: number; g: number; b: number }): string {
  const hex = (v: number) => Math.round(v * 255).toString(16).padStart(2, "0");
  return (hex(c.r) + hex(c.g) + hex(c.b)).toUpperCase();
}

// ─── main panel ───────────────────────────────────────────────────────────────

export function PrototypePanel() {
  const page = useStore((s) => getActivePage(s));
  const selection = useStore((s) => getSelectedLayers(s));

  if (!page) return null;

  const allFlows = page.prototypeFlows ?? [];
  const frameIds = new Set(page.children.map((c) => c.id));

  // Remove flows whose frame was deleted — do it as a side effect after render
  const orphanIds = allFlows.filter((f) => !frameIds.has(f.frameId)).map((f) => f.id);
  if (orphanIds.length > 0) {
    // Queue cleanup after current render cycle
    Promise.resolve().then(() => {
      useStore.setState((s) => {
        const p = s.document.pages.find((pg) => pg.id === page.id);
        if (p?.prototypeFlows) {
          p.prototypeFlows = p.prototypeFlows.filter((f) => !orphanIds.includes(f.id));
        }
      });
    });
  }

  const flows = allFlows.filter((f) => frameIds.has(f.frameId));
  const settings = page.prototypeSettings ?? { device: null, backgroundColor: { r: 0.055, g: 0.051, b: 0.051, a: 1 } };

  if (selection.length === 0) {
    return <NoSelectionPanel flows={flows} settings={settings} pageId={page.id} />;
  }

  const layer = selection[0];
  const isTopLevelFrame = layer.type === "frame" && layer.parentId === page.id;

  if (isTopLevelFrame) {
    return <FramePanel frame={layer as Frame} flows={flows} pageId={page.id} />;
  }

  return <ItemPanel layer={layer} />;
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
    const before = settings.device;
    useStore.setState((s) => {
      const p = s.document.pages.find((pg) => pg.id === pageId);
      if (!p) return;
      if (!p.prototypeSettings) p.prototypeSettings = { device: null, backgroundColor: { r: 0.055, g: 0.051, b: 0.051, a: 1 } };
      p.prototypeSettings.device = id;
    });
    emitSemantic({ name: "set_prototype_device", before, after: id });
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
            <div style={{ height: 1, background: "var(--color-divider)", margin: "4px 0" }} />
            {PROTOTYPE_DEVICES.map((d) => (
              <DeviceOption
                key={d.id}
                label={d.label}
                size={`${d.w}×${d.h}`}
                selected={settings.device === d.id}
                onClick={() => setDevice(d.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Background color */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          background: "var(--color-bg-input)",
          border: "1px solid var(--color-border)",
          borderRadius: 6,
          padding: "4px 8px",
          height: 28,
        }}
      >
        <div
          style={{
            width: 14,
            height: 14,
            borderRadius: 2,
            background: `rgb(${Math.round(settings.backgroundColor.r * 255)},${Math.round(settings.backgroundColor.g * 255)},${Math.round(settings.backgroundColor.b * 255)})`,
            border: "1px solid rgba(255,255,255,0.15)",
            flexShrink: 0,
          }}
        />
        <span style={{ fontSize: "var(--fs-sm)", color: "var(--color-text-primary)", fontFamily: "monospace" }}>
          {colorToHex(settings.backgroundColor)}
        </span>
      </div>

      {/* Device preview */}
      <DevicePreview deviceId={settings.device} bgColor={settings.backgroundColor} />

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

function DevicePreview({
  deviceId,
  bgColor,
}: {
  deviceId: string | null;
  bgColor: { r: number; g: number; b: number; a: number };
}) {
  const bg = `rgb(${Math.round(bgColor.r * 255)},${Math.round(bgColor.g * 255)},${Math.round(bgColor.b * 255)})`;
  return (
    <div
      style={{
        width: "100%",
        height: 120,
        background: bg,
        borderRadius: 6,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      {deviceId ? (
        <PhoneSilhouette />
      ) : (
        <Monitor size={32} style={{ color: "rgba(255,255,255,0.2)" }} />
      )}
    </div>
  );
}

function PhoneSilhouette() {
  return (
    <svg width="54" height="100" viewBox="0 0 54 100" fill="none">
      {/* Shell */}
      <rect x="1" y="1" width="52" height="98" rx="12" fill="url(#phoneGrad)" stroke="rgba(255,255,255,0.18)" strokeWidth="1" />
      <defs>
        <linearGradient id="phoneGrad" x1="0" y1="0" x2="54" y2="100" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#2d2d2d" />
          <stop offset="100%" stopColor="#0a0a0a" />
        </linearGradient>
      </defs>
      {/* Screen */}
      <rect x="3.5" y="3.5" width="47" height="93" rx="9.5" fill="#0d0d1a" />
      {/* Dynamic island */}
      <rect x="17" y="7" width="20" height="5.5" rx="2.75" fill="#000" />
      {/* Right power button */}
      <rect x="53" y="27" width="3" height="13" rx="1.5" fill="#222" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
      {/* Left mute */}
      <rect x="-2" y="18" width="3" height="5" rx="1.5" fill="#222" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
      {/* Left volume up */}
      <rect x="-2" y="27" width="3" height="9" rx="1.5" fill="#222" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
      {/* Left volume down */}
      <rect x="-2" y="39" width="3" height="9" rx="1.5" fill="#222" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
      {/* Speaker dots */}
      {[0,1,2,3,4,5].map(i => (
        <circle key={i} cx={21 + i * 2.4} cy={95} r={0.8} fill="rgba(255,255,255,0.18)" />
      ))}
    </svg>
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
  pageId,
}: {
  frame: Frame;
  flows: PrototypeFlow[];
  pageId: string;
}) {
  const frameFlow = flows.find((f) => f.frameId === frame.id);

  function addFlow() {
    const p = useStore.getState().document.pages.find((pg) => pg.id === pageId);
    const existing = p?.prototypeFlows ?? [];
    const validFrameIds = new Set((p?.children ?? []).map((c) => c.id));
    const validCount = existing.filter((f) => validFrameIds.has(f.frameId)).length;
    const newFlow: PrototypeFlow = { id: uid("flow"), name: `Flow ${validCount + 1}`, frameId: frame.id };
    useStore.setState((s) => {
      const pg = s.document.pages.find((pg) => pg.id === pageId);
      if (!pg) return;
      if (!pg.prototypeFlows) pg.prototypeFlows = [];
      pg.prototypeFlows.push(newFlow);
    });
    emitSemantic({ name: "add_prototype_flow", flowId: newFlow.id, flowName: newFlow.name, frameId: frame.id });
  }

  function removeFlow() {
    if (!frameFlow) return;
    useStore.setState((s) => {
      const p = s.document.pages.find((pg) => pg.id === pageId);
      if (!p?.prototypeFlows) return;
      p.prototypeFlows = p.prototypeFlows.filter((f) => f.id !== frameFlow.id);
    });
    emitSemantic({ name: "remove_prototype_flow", flowId: frameFlow.id, frameId: frame.id });
  }

  function renameFlow(newName: string) {
    if (!frameFlow) return;
    const before = frameFlow.name;
    useStore.setState((s) => {
      const p = s.document.pages.find((pg) => pg.id === pageId);
      const f = p?.prototypeFlows?.find((fl) => fl.id === frameFlow.id);
      if (f) f.name = newName;
    });
    emitSemantic({ name: "rename_prototype_flow", flowId: frameFlow.id, before, after: newName });
  }

  const overflow: ScrollBehavior = frame.overflowScrolling ?? "none";

  function setOverflow(v: ScrollBehavior) {
    const before = frame.overflowScrolling ?? "none";
    useStore.setState((s) => {
      const node = s.nodesById[frame.id];
      if (node && node.type === "frame") (node as Frame).overflowScrolling = v;
    });
    emitSemantic({ name: "set_overflow_scrolling", layerId: frame.id, before, after: v });
  }

  return (
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
          <button onClick={(e) => noopClick("prototype.interactions.add", e)} style={iconBtnStyle}>
            <Plus size={12} />
          </button>
        }
      />

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

function ItemPanel({ layer }: { layer: import("@/types/scene").Layer }) {
  const pos: ScrollPosition = layer.scrollPosition ?? "scroll_with_parent";

  function setPos(v: ScrollPosition) {
    const before = layer.scrollPosition ?? "scroll_with_parent";
    useStore.setState((s) => {
      const node = s.nodesById[layer.id];
      if (node && (node as import("@/types/scene").Page).type !== "page") {
        (node as import("@/types/scene").Layer).scrollPosition = v;
      }
    });
    emitSemantic({ name: "set_scroll_position", layerId: layer.id, before, after: v });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      {/* Interactions */}
      <Section
        label="Interactions"
        action={
          <button onClick={(e) => noopClick("prototype.interactions.add", e)} style={iconBtnStyle}>
            <Plus size={12} />
          </button>
        }
      />

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
