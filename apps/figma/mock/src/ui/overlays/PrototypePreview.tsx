// Draggable prototype preview window — floating over the canvas.

import { useEffect, useRef, useCallback, useState } from "react";
import { useStore } from "@/engine/store";
import { getActivePage } from "@/engine/selectors";
import { NodeRenderer } from "@/ui/canvas/NodeRenderer";
import { findDevice } from "@/util/prototypeDevices";
import { emitSemantic } from "@/logger/semantic";
import { X, ChevronLeft, ChevronRight, RotateCcw } from "lucide-react";
import type { Frame, PrototypeAction, PrototypeConnection, PrototypeTrigger } from "@/types/scene";

const TOOLBAR_H = 40;
const CONTENT_W = 360;
const CONTENT_H = 480;

export function PrototypePreview() {
  const preview = useStore((s) => s.prototypePreview);
  const page = useStore((s) => getActivePage(s));
  // overrideFrameId is set when a connection-based navigation fires in the preview
  const [overrideFrameId, setOverrideFrameId] = useState<string | null>(null);
  const [frameHistory, setFrameHistory] = useState<string[]>([]);

  const topFrames = sortPreviewFrames((page?.children.filter((c) => c.type === "frame") as Frame[] | undefined) ?? []);
  const connections = page?.prototypeConnections ?? [];

  const count = topFrames.length;
  const flowIndex = Math.max(0, Math.min(preview?.flowIndex ?? 0, Math.max(0, count - 1)));

  const indexedFrame: Frame | undefined = topFrames[flowIndex];

  // Connection navigation overrides the index-based frame
  const frame: Frame | undefined = overrideFrameId
    ? (page?.children.find((c) => c.id === overrideFrameId) as Frame | undefined) ?? indexedFrame
    : indexedFrame;

  const settings = page?.prototypeSettings ?? { device: null, backgroundColor: { r: 0.055, g: 0.051, b: 0.051, a: 1 } };
  const device = findDevice(settings.device);

  function close() {
    useStore.setState((s) => { s.prototypePreview = null; });
    emitSemantic({ name: "close_prototype_preview", trigger: "close_button" });
  }
  function prev() {
    setOverrideFrameId(null);
    setFrameHistory([]);
    const to = Math.max(0, flowIndex - 1);
    useStore.setState((s) => { if (s.prototypePreview) s.prototypePreview.flowIndex = to; });
    emitSemantic({ name: "navigate_prototype_preview", direction: "prev", fromIndex: flowIndex, toIndex: to });
  }
  function next() {
    setOverrideFrameId(null);
    setFrameHistory([]);
    const to = Math.min(count - 1, flowIndex + 1);
    useStore.setState((s) => { if (s.prototypePreview) s.prototypePreview.flowIndex = to; });
    emitSemantic({ name: "navigate_prototype_preview", direction: "next", fromIndex: flowIndex, toIndex: to });
  }
  function restart() {
    setOverrideFrameId(null);
    setFrameHistory([]);
    useStore.setState((s) => { if (s.prototypePreview) s.prototypePreview.flowIndex = 0; });
  }

  function activateConnection(layerId: string, trigger: PrototypeTrigger) {
    const conn = connections.find((c) => c.sourceLayerId === layerId && c.trigger === trigger && isRuntimeAction(c.action));
    if (!conn) return;
    if (conn.action === "back" || conn.action === "close_overlay") {
      const previous = frameHistory[frameHistory.length - 1];
      if (!previous) return;
      setFrameHistory((history) => history.slice(0, -1));
      setOverrideFrameId(previous);
      emitSemantic({ name: "navigate_prototype_connection", connectionId: conn.id, sourceLayerId: layerId, destinationFrameId: previous });
      return;
    }
    if (!conn.destinationFrameId) return;
    const currentFrameId = frame?.id;
    if (currentFrameId) setFrameHistory((history) => [...history, currentFrameId]);
    setOverrideFrameId(conn.destinationFrameId);
    emitSemantic({ name: "navigate_prototype_connection", connectionId: conn.id, sourceLayerId: layerId, destinationFrameId: conn.destinationFrameId });
  }

  useEffect(() => {
    if (!frame) return;
    const delayed = connections.find((c) => c.sourceLayerId === frame.id && c.trigger === "after_delay" && isRuntimeAction(c.action));
    if (!delayed) return;
    const timer = window.setTimeout(() => activateConnection(frame.id, "after_delay"), delayed.delayMs ?? 800);
    return () => window.clearTimeout(timer);
  }, [frame?.id, connections]);

  useEffect(() => {
    if (!frame) return;
    const currentFrame = frame;
    function onKeyDown() {
      activateConnection(currentFrame.id, "key_gamepad");
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [frame?.id, connections, frameHistory]);

  if (!preview || !page) return null;

  return (
    <Draggable initialPos={preview.pos}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          background: "transparent",
          userSelect: "none",
          filter: "drop-shadow(0 8px 32px rgba(0,0,0,0.6))",
        }}
      >
        {/* Toolbar */}
        <div
          data-drag-handle
          style={{
            height: TOOLBAR_H,
            background: "#2C2C2C",
            borderRadius: "10px 10px 0 0",
            display: "flex",
            alignItems: "center",
            padding: "0 10px",
            gap: 4,
            cursor: "grab",
          }}
        >
          <ToolBtn disabled={flowIndex === 0 && !overrideFrameId} onClick={prev}><ChevronLeft size={16} /></ToolBtn>
          <ToolBtn disabled={flowIndex === count - 1 && !overrideFrameId} onClick={next}><ChevronRight size={16} /></ToolBtn>
          <ToolBtn onClick={restart}><RotateCcw size={14} /></ToolBtn>
          <span style={{ flex: 1 }} />
          <ToolBtn onClick={close}><X size={14} /></ToolBtn>
        </div>

        {/* Content */}
        <div
          style={{
            width: CONTENT_W,
            height: CONTENT_H,
            background: bgColor(settings.backgroundColor),
            borderRadius: "0 0 10px 10px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            overflow: "hidden",
            position: "relative",
          }}
        >
          {frame ? (
            device ? (
              <DeviceFrame device={device} frame={frame} connections={connections} onConnection={activateConnection} />
            ) : (
              <NoDeviceFrame frame={frame} connections={connections} onConnection={activateConnection} />
            )
          ) : (
            <span style={{ color: "rgba(255,255,255,0.3)", fontSize: 13 }}>
              {topFrames.length === 0 ? "Add a frame to preview" : "No frame"}
            </span>
          )}
        </div>
      </div>
    </Draggable>
  );
}

// ─── frame renderers ──────────────────────────────────────────────────────────

type FrameRendererProps = {
  frame: Frame;
  connections: PrototypeConnection[];
  onConnection: (layerId: string, trigger: PrototypeTrigger) => void;
};

function NoDeviceFrame({ frame, connections, onConnection }: FrameRendererProps) {
  const maxW = CONTENT_W - 32;
  const maxH = CONTENT_H - 32;
  const visual = prototypeFrameVisualBounds(frame);
  const scale = Math.min(maxW / visual.w, maxH / visual.h, 1);
  const displayW = visual.w * scale;
  const displayH = visual.h * scale;

  return (
    <svg width={displayW} height={displayH} viewBox={`${visual.x} ${visual.y} ${visual.w} ${visual.h}`} style={{ display: "block" }}>
      <g transform={prototypeFrameTransform(frame)}>
        <FrameContent frame={frame} connections={connections} onConnection={onConnection} />
      </g>
    </svg>
  );
}

function DeviceFrame({ device, frame, connections, onConnection }: { device: ReturnType<typeof findDevice> } & FrameRendererProps) {
  if (!device) return null;

  const maxW = CONTENT_W - 24;
  const maxH = CONTENT_H - 24;
  const deviceScale = Math.min(maxW / device.w, maxH / device.h);
  const deviceW = device.w * deviceScale;
  const deviceH = device.h * deviceScale;

  if (device.kind === "phone") return <IPhoneFrame deviceW={deviceW} deviceH={deviceH} frame={frame} connections={connections} onConnection={onConnection} />;
  if (device.kind === "tablet") return <IPadFrame deviceW={deviceW} deviceH={deviceH} frame={frame} connections={connections} onConnection={onConnection} />;
  return <DesktopFrame deviceW={deviceW} deviceH={deviceH} frame={frame} connections={connections} onConnection={onConnection} />;
}

function IPhoneFrame({ deviceW, deviceH, frame, connections, onConnection }: { deviceW: number; deviceH: number } & FrameRendererProps) {
  // iPhone 17-style: edge-to-edge screen, thin bezels, dynamic island on screen
  const shellRadius = deviceW * 0.145;
  const bezelX = deviceW * 0.034;
  const bezelY = deviceW * 0.034;
  const screenW = deviceW - bezelX * 2;
  const screenH = deviceH - bezelY * 2;
  const screenRadius = shellRadius - bezelX;

  // Dynamic island — sits inside the screen at top center
  const islandW = screenW * 0.27;
  const islandH = screenH * 0.033;
  const islandTop = screenH * 0.018;

  // Button dimensions
  const btnW = deviceW * 0.018;
  const btnRadius = btnW / 2;

  const visual = prototypeFrameVisualBounds(frame);
  const frameScale = Math.min(screenW / visual.w, screenH / visual.h);
  const frameDisplayW = visual.w * frameScale;
  const frameDisplayH = visual.h * frameScale;

  return (
    <div style={{ position: "relative", width: deviceW, height: deviceH, flexShrink: 0 }}>
      {/* Shell */}
      <div style={{
        position: "absolute", inset: 0,
        background: "linear-gradient(160deg, #2d2d2d 0%, #111 60%, #0a0a0a 100%)",
        borderRadius: shellRadius,
        boxShadow: "inset 0 0 0 0.5px rgba(255,255,255,0.18), 0 0 0 0.5px rgba(0,0,0,0.9), 0 24px 48px rgba(0,0,0,0.7)",
      }} />

      {/* Right side — power button */}
      <div style={{ position: "absolute", top: deviceH * 0.28, right: -btnW + 1, width: btnW, height: deviceH * 0.13, background: "linear-gradient(90deg,#1a1a1a,#2a2a2a)", borderRadius: `0 ${btnRadius}px ${btnRadius}px 0`, boxShadow: "1px 0 0 rgba(255,255,255,0.1)" }} />

      {/* Left side — mute toggle */}
      <div style={{ position: "absolute", top: deviceH * 0.16, left: -btnW + 1, width: btnW, height: deviceH * 0.045, background: "linear-gradient(270deg,#1a1a1a,#2a2a2a)", borderRadius: `${btnRadius}px 0 0 ${btnRadius}px`, boxShadow: "-1px 0 0 rgba(255,255,255,0.1)" }} />
      {/* Left side — volume up */}
      <div style={{ position: "absolute", top: deviceH * 0.23, left: -btnW + 1, width: btnW, height: deviceH * 0.1, background: "linear-gradient(270deg,#1a1a1a,#2a2a2a)", borderRadius: `${btnRadius}px 0 0 ${btnRadius}px`, boxShadow: "-1px 0 0 rgba(255,255,255,0.1)" }} />
      {/* Left side — volume down */}
      <div style={{ position: "absolute", top: deviceH * 0.35, left: -btnW + 1, width: btnW, height: deviceH * 0.1, background: "linear-gradient(270deg,#1a1a1a,#2a2a2a)", borderRadius: `${btnRadius}px 0 0 ${btnRadius}px`, boxShadow: "-1px 0 0 rgba(255,255,255,0.1)" }} />

      {/* Screen */}
      <div style={{
        position: "absolute",
        top: bezelY, left: bezelX,
        width: screenW, height: screenH,
        borderRadius: screenRadius,
        overflow: "hidden",
        background: "#000",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <svg width={frameDisplayW} height={frameDisplayH} viewBox={`${visual.x} ${visual.y} ${visual.w} ${visual.h}`} style={{ display: "block" }}>
          <g transform={prototypeFrameTransform(frame)}><FrameContent frame={frame} connections={connections} onConnection={onConnection} /></g>
        </svg>

        {/* Dynamic island — floats above content */}
        <div style={{
          position: "absolute",
          top: islandTop, left: "50%",
          transform: "translateX(-50%)",
          width: islandW, height: islandH,
          background: "#000",
          borderRadius: islandH / 2,
          zIndex: 10,
          boxShadow: "0 0 0 1px rgba(255,255,255,0.06)",
        }} />
      </div>

      {/* Bottom speaker dots */}
      <SpeakerDots cx={deviceW / 2} cy={deviceH - bezelY * 0.55} count={6} spacing={deviceW * 0.028} r={deviceW * 0.008} />
    </div>
  );
}

function IPadFrame({ deviceW, deviceH, frame, connections, onConnection }: { deviceW: number; deviceH: number } & FrameRendererProps) {
  const shellRadius = deviceW * 0.06;
  const bezelX = deviceW * 0.05;
  const bezelY = deviceH * 0.04;
  const screenW = deviceW - bezelX * 2;
  const screenH = deviceH - bezelY * 2;
  const screenRadius = shellRadius * 0.6;

  // Face ID bar at top center
  const faceIdW = screenW * 0.12;
  const faceIdH = screenH * 0.016;

  const visual = prototypeFrameVisualBounds(frame);
  const frameScale = Math.min(screenW / visual.w, screenH / visual.h);
  const frameDisplayW = visual.w * frameScale;
  const frameDisplayH = visual.h * frameScale;

  return (
    <div style={{ position: "relative", width: deviceW, height: deviceH, flexShrink: 0 }}>
      <div style={{
        position: "absolute", inset: 0,
        background: "linear-gradient(160deg, #2a2a2a 0%, #0f0f0f 100%)",
        borderRadius: shellRadius,
        boxShadow: "inset 0 0 0 0.5px rgba(255,255,255,0.15), 0 20px 40px rgba(0,0,0,0.6)",
      }} />
      <div style={{
        position: "absolute",
        top: bezelY, left: bezelX,
        width: screenW, height: screenH,
        borderRadius: screenRadius,
        overflow: "hidden",
        background: "#000",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <svg width={frameDisplayW} height={frameDisplayH} viewBox={`${visual.x} ${visual.y} ${visual.w} ${visual.h}`} style={{ display: "block" }}>
          <g transform={prototypeFrameTransform(frame)}><FrameContent frame={frame} connections={connections} onConnection={onConnection} /></g>
        </svg>
        {/* Face ID capsule */}
        <div style={{
          position: "absolute", top: screenH * 0.014, left: "50%",
          transform: "translateX(-50%)",
          width: faceIdW, height: faceIdH,
          background: "#111", borderRadius: faceIdH / 2, zIndex: 10,
        }} />
      </div>
    </div>
  );
}

function DesktopFrame({ deviceW, deviceH, frame, connections, onConnection }: { deviceW: number; deviceH: number } & FrameRendererProps) {
  const shellRadius = deviceW * 0.015;
  const bezelX = deviceW * 0.025;
  const bezelY = deviceH * 0.025;
  const screenW = deviceW - bezelX * 2;
  const screenH = deviceH - bezelY * 2;
  const dockH = deviceH * 0.08;

  const visual = prototypeFrameVisualBounds(frame);
  const frameScale = Math.min(screenW / visual.w, (screenH - dockH) / visual.h);
  const frameDisplayW = visual.w * frameScale;
  const frameDisplayH = visual.h * frameScale;

  return (
    <div style={{ position: "relative", width: deviceW, height: deviceH, flexShrink: 0 }}>
      <div style={{
        position: "absolute", inset: 0,
        background: "linear-gradient(160deg, #252525 0%, #0f0f0f 100%)",
        borderRadius: shellRadius,
        boxShadow: "inset 0 0 0 0.5px rgba(255,255,255,0.1), 0 20px 40px rgba(0,0,0,0.6)",
      }} />
      {/* Keyboard dock */}
      <div style={{
        position: "absolute", bottom: 0, left: 0, right: 0,
        height: dockH,
        background: "#181818",
        borderRadius: `0 0 ${shellRadius}px ${shellRadius}px`,
        borderTop: "1px solid rgba(255,255,255,0.06)",
      }} />
      <div style={{
        position: "absolute",
        top: bezelY, left: bezelX,
        width: screenW, height: screenH - dockH,
        borderRadius: shellRadius * 0.4,
        overflow: "hidden",
        background: "#000",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <svg width={frameDisplayW} height={frameDisplayH} viewBox={`${visual.x} ${visual.y} ${visual.w} ${visual.h}`} style={{ display: "block" }}>
          <g transform={prototypeFrameTransform(frame)}><FrameContent frame={frame} connections={connections} onConnection={onConnection} /></g>
        </svg>
      </div>
    </div>
  );
}

function SpeakerDots({ cx, cy, count, spacing, r }: { cx: number; cy: number; count: number; spacing: number; r: number }) {
  const totalW = (count - 1) * spacing;
  return (
    <div style={{ position: "absolute", left: cx - totalW / 2, top: cy - r, display: "flex", gap: spacing - r * 2, pointerEvents: "none" }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} style={{ width: r * 2, height: r * 2, borderRadius: "50%", background: "rgba(255,255,255,0.15)" }} />
      ))}
    </div>
  );
}

function FrameContent({ frame, connections, onConnection }: FrameRendererProps) {
  const interactiveIds = new Set(
    connections.filter((c) => isRuntimeTrigger(c.trigger) && isRuntimeAction(c.action)).map((c) => c.sourceLayerId),
  );

  return (
    <g>
      {/* Frame background */}
      <rect
        x={0}
        y={0}
        width={frame.w}
        height={frame.h}
        fill={frameFill(frame)}
        rx={typeof frame.cornerRadius === "number" ? frame.cornerRadius : 0}
      />
      {/* Children */}
      {frame.children.map((child) => (
        <g key={child.id} transform={`translate(${child.x} ${child.y})`}>
          <NodeRenderer layer={{ ...child, x: 0, y: 0 }} />
          {interactiveIds.has(child.id) && (
            <rect
              x={0} y={0} width={child.w} height={child.h}
              fill="transparent"
              style={{ cursor: "pointer" }}
              {...connectionHandlers(child.id, onConnection)}
            />
          )}
        </g>
      ))}
      {/* Frame itself may have a tap connection */}
      {interactiveIds.has(frame.id) && (
        <rect
          x={0} y={0} width={frame.w} height={frame.h}
          fill="transparent"
          style={{ cursor: "pointer" }}
          {...connectionHandlers(frame.id, onConnection)}
        />
      )}
    </g>
  );
}

// ─── draggable wrapper ────────────────────────────────────────────────────────

function Draggable({ initialPos, children }: { initialPos: { x: number; y: number }; children: React.ReactNode }) {
  const posRef = useRef(initialPos);
  const divRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);
  const startPointer = useRef({ x: 0, y: 0 });
  const startPos = useRef({ x: 0, y: 0 });

  const onPointerDown = useCallback((e: React.PointerEvent) => {
    const target = e.target as HTMLElement;
    // Don't start drag when clicking a button inside the toolbar
    if (target.closest("button")) return;
    const handle = target.closest("[data-drag-handle]");
    if (!handle) return;
    dragging.current = true;
    startPointer.current = { x: e.clientX, y: e.clientY };
    startPos.current = { ...posRef.current };
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    e.preventDefault();
  }, []);

  const onPointerMove = useCallback((e: React.PointerEvent) => {
    if (!dragging.current || !divRef.current) return;
    const dx = e.clientX - startPointer.current.x;
    const dy = e.clientY - startPointer.current.y;
    posRef.current = { x: startPos.current.x + dx, y: startPos.current.y + dy };
    divRef.current.style.left = posRef.current.x + "px";
    divRef.current.style.top = posRef.current.y + "px";
  }, []);

  const onPointerUp = useCallback((e: React.PointerEvent) => {
    dragging.current = false;
    useStore.setState((s) => { if (s.prototypePreview) s.prototypePreview.pos = { ...posRef.current }; });
    (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
  }, []);

  return (
    <div
      ref={divRef}
      style={{
        position: "fixed",
        left: initialPos.x,
        top: initialPos.y,
        zIndex: 500,
        borderRadius: 10,
      }}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
    >
      {children}
    </div>
  );
}

// ─── helpers ──────────────────────────────────────────────────────────────────

function bgColor(c: { r: number; g: number; b: number; a: number }): string {
  return `rgba(${Math.round(c.r * 255)},${Math.round(c.g * 255)},${Math.round(c.b * 255)},${c.a})`;
}

function frameFill(frame: Frame): string {
  for (const p of frame.fills) {
    if (!p.visible) continue;
    if (p.kind === "solid") {
      return `rgba(${Math.round(p.color.r * 255)},${Math.round(p.color.g * 255)},${Math.round(p.color.b * 255)},${p.color.a})`;
    }
  }
  return "white";
}

function prototypeFrameTransform(frame: Frame): string {
  const cx = frame.w / 2;
  const cy = frame.h / 2;
  const parts: string[] = [];
  if (frame.rotation !== 0) parts.push(`rotate(${frame.rotation} ${cx} ${cy})`);
  if (frame.scaleX !== 1 || frame.scaleY !== 1) {
    parts.push(`translate(${cx} ${cy}) scale(${frame.scaleX} ${frame.scaleY}) translate(${-cx} ${-cy})`);
  }
  return parts.join(" ");
}

function prototypeFrameVisualBounds(frame: Frame): { x: number; y: number; w: number; h: number } {
  const cx = frame.w / 2;
  const cy = frame.h / 2;
  const rad = (frame.rotation * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const corners = [
    { x: 0, y: 0 },
    { x: frame.w, y: 0 },
    { x: frame.w, y: frame.h },
    { x: 0, y: frame.h },
  ].map((p) => {
    let x = cx + (p.x - cx) * frame.scaleX;
    let y = cy + (p.y - cy) * frame.scaleY;
    const dx = x - cx;
    const dy = y - cy;
    x = cx + dx * cos - dy * sin;
    y = cy + dx * sin + dy * cos;
    return { x, y };
  });
  const xs = corners.map((p) => p.x);
  const ys = corners.map((p) => p.y);
  const minX = Math.min(...xs);
  const minY = Math.min(...ys);
  const maxX = Math.max(...xs);
  const maxY = Math.max(...ys);
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

function sortPreviewFrames(frames: Frame[]): Frame[] {
  return [...frames].sort((a, b) => {
    const aNameNumber = frameNameNumber(a.name);
    const bNameNumber = frameNameNumber(b.name);
    if (aNameNumber !== bNameNumber) return aNameNumber - bNameNumber;
    if (a.y !== b.y) return a.y - b.y;
    if (a.x !== b.x) return a.x - b.x;
    return a.name.localeCompare(b.name);
  });
}

function frameNameNumber(name: string): number {
  const match = name.match(/\bframe\s+(\d+)\b/i);
  return match ? Number(match[1]) : Number.POSITIVE_INFINITY;
}

function isRuntimeTrigger(trigger: PrototypeTrigger): boolean {
  return trigger !== "none" && trigger !== "key_gamepad" && trigger !== "after_delay";
}

function isRuntimeAction(action: PrototypeAction): boolean {
  return action === "navigate_to" || action === "change_to" || action === "back" || action === "open_overlay" || action === "swap_overlay" || action === "close_overlay";
}

function connectionHandlers(layerId: string, onConnection: (layerId: string, trigger: PrototypeTrigger) => void) {
  return {
    onClick: () => onConnection(layerId, "on_tap"),
    onMouseEnter: () => {
      onConnection(layerId, "mouse_enter");
      onConnection(layerId, "while_hovering");
    },
    onMouseLeave: () => onConnection(layerId, "mouse_leave"),
    onPointerDown: () => {
      onConnection(layerId, "touch_down");
      onConnection(layerId, "while_pressing");
      onConnection(layerId, "on_drag");
    },
    onPointerUp: () => onConnection(layerId, "touch_up"),
  };
}

function ToolBtn({ children, onClick, disabled }: { children: React.ReactNode; onClick: () => void; disabled?: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        width: 28,
        height: 28,
        borderRadius: 6,
        display: "grid",
        placeItems: "center",
        color: disabled ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.7)",
        background: "transparent",
        cursor: disabled ? "default" : "pointer",
      }}
      onMouseEnter={(e) => { if (!disabled) e.currentTarget.style.background = "rgba(255,255,255,0.1)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}
    >
      {children}
    </button>
  );
}
