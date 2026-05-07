// Compact solid-color picker overlay. Slice 2 supports solid color only.
// Gradient/pattern/video tabs render but emit noop_click.

import { useEffect, useMemo, useRef, useState } from "react";
import type { Color } from "@/types/scene";
import { noopClick } from "@/ui/chrome/noopClick";

export function ColorPicker({
  value,
  onChange,
  onChangeStart,
  onChangeEnd,
  onClose,
  anchor,
}: {
  value: Color;
  onChange: (c: Color) => void;
  // Drag-lifecycle hooks for callers that want to wrap continuous slider
  // drags in a single undo transaction (item #15). Fires once per drag of any
  // of the three sliders (SV plane, hue, alpha). Optional — callers without
  // transactions can ignore them and keep the existing per-tick semantics.
  onChangeStart?: () => void;
  onChangeEnd?: () => void;
  onClose: () => void;
  anchor: { right: number; top: number };
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [hsv, setHsv] = useState(() => rgbToHsv(value));
  const [alpha, setAlpha] = useState(value.a);
  const [hexDraft, setHexDraft] = useState(() => colorToHex(value));

  // Sync incoming value if it changes from outside
  useEffect(() => {
    setHsv(rgbToHsv(value));
    setAlpha(value.a);
    setHexDraft(colorToHex(value));
  }, [value.r, value.g, value.b, value.a]);

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

  function commit(h: { h: number; s: number; v: number }, a: number) {
    const rgb = hsvToRgb(h);
    const c: Color = { r: rgb.r, g: rgb.g, b: rgb.b, a };
    setHexDraft(colorToHex(c));
    onChange(c);
  }

  const svBgFromHue = useMemo(() => {
    const rgb = hsvToRgb({ h: hsv.h, s: 1, v: 1 });
    return `rgb(${Math.round(rgb.r * 255)}, ${Math.round(rgb.g * 255)}, ${Math.round(rgb.b * 255)})`;
  }, [hsv.h]);

  return (
    <div
      ref={ref}
      role="dialog"
      style={{
        position: "fixed",
        right: anchor.right,
        top: anchor.top,
        width: 240,
        background: "var(--color-bg-panel-elevated)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: 8,
        boxShadow: "0 14px 32px rgba(0,0,0,0.55)",
        zIndex: 200,
        overflow: "hidden",
      }}
      onMouseDown={(e) => e.stopPropagation()}
    >
      {/* Tabs */}
      <div
        style={{
          height: 32,
          display: "flex",
          alignItems: "center",
          borderBottom: "1px solid var(--color-border)",
          padding: "0 4px",
        }}
      >
        <PickerTab id="color-picker.tab.solid" label="Solid" active />
        <PickerTab id="color-picker.tab.linear" label="Linear" />
        <PickerTab id="color-picker.tab.radial" label="Radial" />
        <PickerTab id="color-picker.tab.angular" label="Angular" />
        <PickerTab id="color-picker.tab.diamond" label="Diamond" />
        <PickerTab id="color-picker.tab.image" label="Image" />
      </div>

      {/* SV plane */}
      <SVPlane
        bg={svBgFromHue}
        hsv={hsv}
        onDragStart={onChangeStart}
        onDragEnd={onChangeEnd}
        onChange={(h) => { setHsv(h); commit(h, alpha); }}
      />

      {/* Hue slider */}
      <HueSlider
        hue={hsv.h}
        onDragStart={onChangeStart}
        onDragEnd={onChangeEnd}
        onChange={(h) => {
          const next = { ...hsv, h };
          setHsv(next);
          commit(next, alpha);
        }}
      />

      {/* Alpha slider */}
      <AlphaSlider
        alpha={alpha}
        baseColor={hsvToRgb(hsv)}
        onDragStart={onChangeStart}
        onDragEnd={onChangeEnd}
        onChange={(a) => {
          setAlpha(a);
          commit(hsv, a);
        }}
      />

      {/* Hex + alpha % row */}
      <div style={{ display: "flex", padding: "8px 10px 10px", gap: 6 }}>
        <input
          value={hexDraft}
          onChange={(e) => setHexDraft(e.target.value)}
          onBlur={() => {
            const c = parseHex(hexDraft);
            if (c) {
              setHsv(rgbToHsv({ ...c, a: alpha }));
              setAlpha(c.a);
              setHexDraft(colorToHex({ ...c, a: alpha }));
              onChange({ ...c, a: alpha });
            } else {
              setHexDraft(colorToHex({ ...hsvToRgb(hsv), a: alpha }));
            }
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
          }}
          style={{
            flex: 1,
            height: 26,
            background: "var(--color-bg-input)",
            border: 0,
            borderRadius: 4,
            color: "var(--color-text-primary)",
            padding: "0 6px",
            fontSize: "var(--fs-sm)",
            outline: 0,
            minWidth: 0,
          }}
        />
        <input
          value={`${Math.round(alpha * 100)}`}
          onChange={(e) => {
            const n = parseInt(e.target.value, 10);
            if (Number.isFinite(n)) {
              const a = Math.max(0, Math.min(100, n)) / 100;
              setAlpha(a);
              commit(hsv, a);
            }
          }}
          style={{
            width: 50,
            height: 26,
            background: "var(--color-bg-input)",
            border: 0,
            borderRadius: 4,
            color: "var(--color-text-primary)",
            padding: "0 6px",
            fontSize: "var(--fs-sm)",
            outline: 0,
          }}
        />
      </div>
    </div>
  );
}

function PickerTab({ id, label, active }: { id: string; label: string; active?: boolean }) {
  return (
    <button
      data-id={id}
      onClick={(e) => !active && noopClick(id, e)}
      style={{
        flex: 1,
        height: 24,
        borderRadius: 4,
        color: active ? "var(--color-text-primary)" : "var(--color-text-muted)",
        fontSize: "var(--fs-xs)",
        fontWeight: active ? 600 : 500,
        background: active ? "var(--color-bg-row-active)" : "transparent",
      }}
      title={active ? label : `${label} — not implemented in this mock`}
    >
      {label}
    </button>
  );
}

function SVPlane({
  bg,
  hsv,
  onChange,
  onDragStart,
  onDragEnd,
}: {
  bg: string;
  hsv: { h: number; s: number; v: number };
  onChange: (h: { h: number; s: number; v: number }) => void;
  onDragStart?: () => void;
  onDragEnd?: () => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  function update(e: React.PointerEvent | PointerEvent) {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, ((e as PointerEvent).clientX - r.left) / r.width));
    const y = Math.max(0, Math.min(1, ((e as PointerEvent).clientY - r.top) / r.height));
    onChange({ h: hsv.h, s: x, v: 1 - y });
  }
  return (
    <div
      ref={ref}
      onPointerDown={(e) => {
        e.currentTarget.setPointerCapture(e.pointerId);
        onDragStart?.();
        update(e.nativeEvent);
      }}
      onPointerMove={(e) => {
        if (e.buttons === 1) update(e.nativeEvent);
      }}
      onPointerUp={() => onDragEnd?.()}
      onPointerCancel={() => onDragEnd?.()}
      style={{
        position: "relative",
        height: 130,
        background: `linear-gradient(to top, #000, transparent), linear-gradient(to right, #fff, transparent), ${bg}`,
        cursor: "crosshair",
        touchAction: "none",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: `${hsv.s * 100}%`,
          top: `${(1 - hsv.v) * 100}%`,
          width: 12,
          height: 12,
          borderRadius: "50%",
          border: "2px solid white",
          boxShadow: "0 0 0 1px rgba(0,0,0,0.4)",
          transform: "translate(-50%, -50%)",
          pointerEvents: "none",
        }}
      />
    </div>
  );
}

function HueSlider({
  hue,
  onChange,
  onDragStart,
  onDragEnd,
}: {
  hue: number;
  onChange: (h: number) => void;
  onDragStart?: () => void;
  onDragEnd?: () => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  function update(e: PointerEvent) {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
    onChange(x * 360);
  }
  return (
    <div
      ref={ref}
      onPointerDown={(e) => {
        e.currentTarget.setPointerCapture(e.pointerId);
        onDragStart?.();
        update(e.nativeEvent);
      }}
      onPointerMove={(e) => {
        if (e.buttons === 1) update(e.nativeEvent);
      }}
      onPointerUp={() => onDragEnd?.()}
      onPointerCancel={() => onDragEnd?.()}
      style={{
        position: "relative",
        height: 14,
        margin: "10px 10px 0",
        borderRadius: 7,
        background: "linear-gradient(to right, #f00, #ff0, #0f0, #0ff, #00f, #f0f, #f00)",
        cursor: "ew-resize",
        touchAction: "none",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: `${(hue / 360) * 100}%`,
          top: -3,
          width: 4,
          height: 20,
          borderRadius: 2,
          background: "white",
          boxShadow: "0 0 0 1px rgba(0,0,0,0.4)",
          transform: "translateX(-50%)",
          pointerEvents: "none",
        }}
      />
    </div>
  );
}

function AlphaSlider({
  alpha,
  baseColor,
  onChange,
  onDragStart,
  onDragEnd,
}: {
  alpha: number;
  baseColor: { r: number; g: number; b: number };
  onChange: (a: number) => void;
  onDragStart?: () => void;
  onDragEnd?: () => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const css = `rgb(${Math.round(baseColor.r * 255)}, ${Math.round(baseColor.g * 255)}, ${Math.round(baseColor.b * 255)})`;
  function update(e: PointerEvent) {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
    onChange(x);
  }
  return (
    <div
      ref={ref}
      onPointerDown={(e) => {
        e.currentTarget.setPointerCapture(e.pointerId);
        onDragStart?.();
        update(e.nativeEvent);
      }}
      onPointerMove={(e) => {
        if (e.buttons === 1) update(e.nativeEvent);
      }}
      onPointerUp={() => onDragEnd?.()}
      onPointerCancel={() => onDragEnd?.()}
      style={{
        position: "relative",
        height: 14,
        margin: "8px 10px 0",
        borderRadius: 7,
        background: `linear-gradient(to right, transparent, ${css}), repeating-conic-gradient(#666 0% 25%, #999 0% 50%) 50% / 8px 8px`,
        cursor: "ew-resize",
        touchAction: "none",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: `${alpha * 100}%`,
          top: -3,
          width: 4,
          height: 20,
          borderRadius: 2,
          background: "white",
          boxShadow: "0 0 0 1px rgba(0,0,0,0.4)",
          transform: "translateX(-50%)",
          pointerEvents: "none",
        }}
      />
    </div>
  );
}

// ---- color helpers ----

function rgbToHsv(c: { r: number; g: number; b: number; a?: number }): { h: number; s: number; v: number } {
  const max = Math.max(c.r, c.g, c.b);
  const min = Math.min(c.r, c.g, c.b);
  const d = max - min;
  let h = 0;
  if (d === 0) h = 0;
  else if (max === c.r) h = 60 * (((c.g - c.b) / d) % 6);
  else if (max === c.g) h = 60 * ((c.b - c.r) / d + 2);
  else h = 60 * ((c.r - c.g) / d + 4);
  if (h < 0) h += 360;
  const s = max === 0 ? 0 : d / max;
  return { h, s, v: max };
}

export function hsvToRgb({ h, s, v }: { h: number; s: number; v: number }): { r: number; g: number; b: number } {
  const c = v * s;
  const hh = (h / 60) % 6;
  const x = c * (1 - Math.abs((hh % 2) - 1));
  let r = 0, g = 0, b = 0;
  if (hh < 1) { r = c; g = x; }
  else if (hh < 2) { r = x; g = c; }
  else if (hh < 3) { g = c; b = x; }
  else if (hh < 4) { g = x; b = c; }
  else if (hh < 5) { r = x; b = c; }
  else { r = c; b = x; }
  const m = v - c;
  return { r: r + m, g: g + m, b: b + m };
}

export function colorToHex(c: { r: number; g: number; b: number; a?: number }): string {
  const to = (v: number) => Math.round(v * 255).toString(16).padStart(2, "0").toUpperCase();
  return `${to(c.r)}${to(c.g)}${to(c.b)}`;
}

export function parseHex(input: string): Color | null {
  let s = input.trim().replace(/^#/, "");
  if (s.length === 3) s = s.split("").map((c) => c + c).join("");
  if (s.length === 6) s = s + "FF";
  if (s.length !== 8) return null;
  const r = parseInt(s.slice(0, 2), 16);
  const g = parseInt(s.slice(2, 4), 16);
  const b = parseInt(s.slice(4, 6), 16);
  const a = parseInt(s.slice(6, 8), 16);
  if ([r, g, b, a].some((v) => Number.isNaN(v))) return null;
  return { r: r / 255, g: g / 255, b: b / 255, a: a / 255 };
}
