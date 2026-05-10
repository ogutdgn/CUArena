import { useEffect, useMemo, useRef, useState } from "react";
import { X, ChevronDown } from "lucide-react";
import type { Color } from "@/types/scene";

type Format = "hex" | "rgb" | "css" | "hsl" | "hsb";

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
  onChangeStart?: () => void;
  onChangeEnd?: () => void;
  onClose: () => void;
  anchor: { right: number; top: number };
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const pickerHeight = 290; // conservative estimate — header+plane+sliders+format row
  const flipUp = anchor.top + pickerHeight > window.innerHeight;

  const [hsv, setHsv] = useState(() => rgbToHsv(value));
  const [alpha, setAlpha] = useState(value.a);
  const [format, setFormat] = useState<Format>("hex");
  const [formatOpen, setFormatOpen] = useState(false);
  const formatRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setHsv(rgbToHsv(value));
    setAlpha(value.a);
  }, [value.r, value.g, value.b, value.a]);

  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (!ref.current?.contains(e.target as Node)) onClose();
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

  useEffect(() => {
    if (!formatOpen) return;
    function onDoc(e: MouseEvent) {
      if (!formatRef.current?.contains(e.target as Node)) setFormatOpen(false);
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [formatOpen]);

  function commit(h: { h: number; s: number; v: number }, a: number) {
    const rgb = hsvToRgb(h);
    onChange({ r: rgb.r, g: rgb.g, b: rgb.b, a });
  }

  const svBg = useMemo(() => {
    const rgb = hsvToRgb({ h: hsv.h, s: 1, v: 1 });
    return `rgb(${Math.round(rgb.r * 255)}, ${Math.round(rgb.g * 255)}, ${Math.round(rgb.b * 255)})`;
  }, [hsv.h]);

  const currentRgb = hsvToRgb(hsv);

  return (
    <div
      ref={ref}
      role="dialog"
      style={{
        position: "fixed",
        right: anchor.right,
        ...(flipUp
          ? { bottom: window.innerHeight - anchor.top }
          : { top: anchor.top }),
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
      {/* Header */}
      <div style={{ height: 36, display: "flex", alignItems: "center", padding: "0 12px", borderBottom: "1px solid var(--color-border)" }}>
        <span style={{ flex: 1, fontSize: "var(--fs-sm)", fontWeight: 600, color: "var(--color-text-primary)" }}>Custom</span>
        <button
          onClick={onClose}
          style={{ width: 20, height: 20, borderRadius: 4, display: "grid", placeItems: "center", color: "var(--color-text-secondary)" }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          <X size={13} />
        </button>
      </div>

      {/* SV plane */}
      <SVPlane
        bg={svBg}
        hsv={hsv}
        onDragStart={onChangeStart}
        onDragEnd={onChangeEnd}
        onChange={(h) => { setHsv(h); commit(h, alpha); }}
      />

      {/* Sliders + current color swatch */}
      <div style={{ padding: "10px 10px 0", display: "flex", alignItems: "center", gap: 8 }}>
        {/* Current color preview */}
        <div style={{
          width: 28, height: 28, borderRadius: 6, flexShrink: 0,
          background: `rgba(${Math.round(currentRgb.r*255)},${Math.round(currentRgb.g*255)},${Math.round(currentRgb.b*255)},${alpha}), repeating-conic-gradient(#888 0% 25%, #555 0% 50%) 50% / 6px 6px`,
          border: "1px solid rgba(255,255,255,0.12)",
        }} />
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
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
          <AlphaSlider
            alpha={alpha}
            baseColor={currentRgb}
            onDragStart={onChangeStart}
            onDragEnd={onChangeEnd}
            onChange={(a) => { setAlpha(a); commit(hsv, a); }}
          />
        </div>
      </div>

      {/* Format row */}
      <div style={{ display: "flex", alignItems: "center", padding: "8px 10px 10px", gap: 5 }}>
        {/* Format dropdown */}
        <div ref={formatRef} style={{ position: "relative", flexShrink: 0 }}>
          <button
            onClick={() => setFormatOpen((o) => !o)}
            style={{
              height: 26, padding: "0 6px", borderRadius: 4,
              background: "var(--color-bg-input)",
              color: "var(--color-text-primary)",
              fontSize: "var(--fs-xs)", fontWeight: 500,
              display: "flex", alignItems: "center", gap: 3,
              border: formatOpen ? "1px solid var(--color-selection-blue)" : "1px solid transparent",
            }}
          >
            {format.toUpperCase()}
            <ChevronDown size={9} />
          </button>
          {formatOpen && (
            <div style={{
              position: "absolute", bottom: "100%", left: 0, marginBottom: 2,
              background: "var(--color-bg-panel-elevated)",
              border: "1px solid var(--color-border-strong)",
              borderRadius: 6, boxShadow: "0 8px 20px rgba(0,0,0,0.5)",
              padding: 4, zIndex: 300, minWidth: 70,
            }}>
              {(["hex", "rgb", "css", "hsl", "hsb"] as Format[]).map((f) => (
                <button
                  key={f}
                  onClick={() => { setFormat(f); setFormatOpen(false); }}
                  style={{
                    width: "100%", textAlign: "left", padding: "4px 8px",
                    borderRadius: 4, fontSize: "var(--fs-xs)",
                    color: format === f ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                    background: format === f ? "var(--color-bg-row-active)" : "transparent",
                    fontWeight: format === f ? 600 : 400,
                  }}
                  onMouseEnter={(e) => { if (format !== f) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
                  onMouseLeave={(e) => { if (format !== f) e.currentTarget.style.background = "transparent"; }}
                >
                  {f.toUpperCase()}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Format-specific inputs */}
        <FormatInputs
          key={format}
          format={format}
          hsv={hsv}
          alpha={alpha}
          onCommit={(newHsv, newAlpha) => {
            setHsv(newHsv);
            setAlpha(newAlpha);
            commit(newHsv, newAlpha);
          }}
        />
      </div>
    </div>
  );
}

// ─── Format inputs ─────────────────────────────────────────────────────────────

function FormatInputs({ format, hsv, alpha, onCommit }: {
  format: Format;
  hsv: { h: number; s: number; v: number };
  alpha: number;
  onCommit: (hsv: { h: number; s: number; v: number }, alpha: number) => void;
}) {
  const rgb = hsvToRgb(hsv);

  if (format === "hex") {
    return <HexInputs rgb={rgb} alpha={alpha} onCommit={onCommit} />;
  }
  if (format === "rgb") {
    return <RGBInputs rgb={rgb} alpha={alpha} onCommit={onCommit} />;
  }
  if (format === "css") {
    return <CSSInput rgb={rgb} alpha={alpha} onCommit={onCommit} />;
  }
  if (format === "hsl") {
    const hsl = rgbToHsl(rgb);
    return <HSLInputs hsl={hsl} alpha={alpha} onCommit={onCommit} />;
  }
  // hsb
  return <HSBInputs hsv={hsv} alpha={alpha} onCommit={onCommit} />;
}

function HexInputs({ rgb, alpha, onCommit }: {
  rgb: { r: number; g: number; b: number };
  alpha: number;
  onCommit: (hsv: { h: number; s: number; v: number }, alpha: number) => void;
}) {
  const [draft, setDraft] = useState(colorToHex(rgb));
  useEffect(() => setDraft(colorToHex(rgb)), [rgb.r, rgb.g, rgb.b]);

  function commit() {
    const c = parseHex(draft);
    if (c) onCommit(rgbToHsv(c), alpha);
    else setDraft(colorToHex(rgb));
  }

  return (
    <>
      <PickerInput
        value={draft}
        onChange={setDraft}
        onCommit={commit}
        style={{ flex: 1, fontFamily: "monospace" }}
      />
      <AlphaInput alpha={alpha} onCommit={(a) => onCommit(rgbToHsv(rgb), a)} />
    </>
  );
}

function RGBInputs({ rgb, alpha, onCommit }: {
  rgb: { r: number; g: number; b: number };
  alpha: number;
  onCommit: (hsv: { h: number; s: number; v: number }, alpha: number) => void;
}) {
  const [r, setR] = useState(String(Math.round(rgb.r * 255)));
  const [g, setG] = useState(String(Math.round(rgb.g * 255)));
  const [b, setB] = useState(String(Math.round(rgb.b * 255)));
  useEffect(() => {
    setR(String(Math.round(rgb.r * 255)));
    setG(String(Math.round(rgb.g * 255)));
    setB(String(Math.round(rgb.b * 255)));
  }, [rgb.r, rgb.g, rgb.b]);

  function commitRgb(rStr: string, gStr: string, bStr: string) {
    const rv = parseInt(rStr, 10), gv = parseInt(gStr, 10), bv = parseInt(bStr, 10);
    if ([rv, gv, bv].some((v) => !Number.isFinite(v) || v < 0 || v > 255)) return;
    onCommit(rgbToHsv({ r: rv / 255, g: gv / 255, b: bv / 255 }), alpha);
  }

  return (
    <>
      <PickerInput value={r} onChange={setR} onCommit={() => commitRgb(r, g, b)} style={{ width: 34 }} />
      <PickerInput value={g} onChange={setG} onCommit={() => commitRgb(r, g, b)} style={{ width: 34 }} />
      <PickerInput value={b} onChange={setB} onCommit={() => commitRgb(r, g, b)} style={{ width: 34 }} />
      <AlphaInput alpha={alpha} onCommit={(a) => onCommit(rgbToHsv(rgb), a)} />
    </>
  );
}

function CSSInput({ rgb, alpha, onCommit }: {
  rgb: { r: number; g: number; b: number };
  alpha: number;
  onCommit: (hsv: { h: number; s: number; v: number }, alpha: number) => void;
}) {
  const toCss = (c: typeof rgb, a: number) =>
    `rgba(${Math.round(c.r * 255)}, ${Math.round(c.g * 255)}, ${Math.round(c.b * 255)}, ${parseFloat(a.toFixed(2))})`;
  const [draft, setDraft] = useState(toCss(rgb, alpha));
  useEffect(() => setDraft(toCss(rgb, alpha)), [rgb.r, rgb.g, rgb.b, alpha]);

  function commit() {
    const m = draft.trim().match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)/);
    if (!m) { setDraft(toCss(rgb, alpha)); return; }
    const r = parseInt(m[1], 10) / 255;
    const g = parseInt(m[2], 10) / 255;
    const b = parseInt(m[3], 10) / 255;
    const a = m[4] !== undefined ? Math.max(0, Math.min(1, parseFloat(m[4]))) : alpha;
    onCommit(rgbToHsv({ r, g, b }), a);
  }

  return (
    <PickerInput value={draft} onChange={setDraft} onCommit={commit} style={{ flex: 1, fontFamily: "monospace", fontSize: 10 }} />
  );
}

function HSLInputs({ hsl, alpha, onCommit }: {
  hsl: { h: number; s: number; l: number };
  alpha: number;
  onCommit: (hsv: { h: number; s: number; v: number }, alpha: number) => void;
}) {
  const [h, setH] = useState(String(Math.round(hsl.h)));
  const [s, setS] = useState(String(Math.round(hsl.s * 100)));
  const [l, setL] = useState(String(Math.round(hsl.l * 100)));
  useEffect(() => {
    setH(String(Math.round(hsl.h)));
    setS(String(Math.round(hsl.s * 100)));
    setL(String(Math.round(hsl.l * 100)));
  }, [hsl.h, hsl.s, hsl.l]);

  function commitHsl() {
    const hv = parseFloat(h), sv = parseFloat(s), lv = parseFloat(l);
    if ([hv, sv, lv].some((v) => !Number.isFinite(v))) return;
    const rgb = hslToRgb({ h: ((hv % 360) + 360) % 360, s: Math.max(0, Math.min(100, sv)) / 100, l: Math.max(0, Math.min(100, lv)) / 100 });
    onCommit(rgbToHsv(rgb), alpha);
  }

  return (
    <>
      <PickerInput value={h} onChange={setH} onCommit={commitHsl} style={{ width: 34 }} />
      <PickerInput value={s} onChange={setS} onCommit={commitHsl} style={{ width: 34 }} />
      <PickerInput value={l} onChange={setL} onCommit={commitHsl} style={{ width: 34 }} />
      <AlphaInput alpha={alpha} onCommit={(a) => onCommit(rgbToHsv(hslToRgb({ h: hsl.h, s: hsl.s, l: hsl.l })), a)} />
    </>
  );
}

function HSBInputs({ hsv, alpha, onCommit }: {
  hsv: { h: number; s: number; v: number };
  alpha: number;
  onCommit: (hsv: { h: number; s: number; v: number }, alpha: number) => void;
}) {
  const [h, setH] = useState(String(Math.round(hsv.h)));
  const [s, setS] = useState(String(Math.round(hsv.s * 100)));
  const [b, setB] = useState(String(Math.round(hsv.v * 100)));
  useEffect(() => {
    setH(String(Math.round(hsv.h)));
    setS(String(Math.round(hsv.s * 100)));
    setB(String(Math.round(hsv.v * 100)));
  }, [hsv.h, hsv.s, hsv.v]);

  function commitHsb() {
    const hv = parseFloat(h), sv = parseFloat(s), bv = parseFloat(b);
    if ([hv, sv, bv].some((v) => !Number.isFinite(v))) return;
    onCommit(
      { h: ((hv % 360) + 360) % 360, s: Math.max(0, Math.min(100, sv)) / 100, v: Math.max(0, Math.min(100, bv)) / 100 },
      alpha,
    );
  }

  return (
    <>
      <PickerInput value={h} onChange={setH} onCommit={commitHsb} style={{ width: 34 }} />
      <PickerInput value={s} onChange={setS} onCommit={commitHsb} style={{ width: 34 }} />
      <PickerInput value={b} onChange={setB} onCommit={commitHsb} style={{ width: 34 }} />
      <AlphaInput alpha={alpha} onCommit={(a) => onCommit(hsv, a)} />
    </>
  );
}

function AlphaInput({ alpha, onCommit }: { alpha: number; onCommit: (a: number) => void }) {
  const [draft, setDraft] = useState(String(Math.round(alpha * 100)));
  useEffect(() => setDraft(String(Math.round(alpha * 100))), [alpha]);

  function commit() {
    const n = parseFloat(draft);
    if (Number.isFinite(n)) onCommit(Math.max(0, Math.min(100, n)) / 100);
    else setDraft(String(Math.round(alpha * 100)));
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 2, flexShrink: 0 }}>
      <PickerInput value={draft} onChange={setDraft} onCommit={commit} style={{ width: 30 }} />
      <span style={{ fontSize: "var(--fs-xs)", color: "var(--color-text-muted)" }}>%</span>
    </div>
  );
}

function PickerInput({ value, onChange, onCommit, style }: {
  value: string;
  onChange: (v: string) => void;
  onCommit: () => void;
  style?: React.CSSProperties;
}) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onBlur={onCommit}
      onKeyDown={(e) => { if (e.key === "Enter") (e.target as HTMLInputElement).blur(); }}
      style={{
        height: 26,
        background: "var(--color-bg-input)",
        border: 0,
        borderRadius: 4,
        color: "var(--color-text-primary)",
        padding: "0 5px",
        fontSize: "var(--fs-xs)",
        outline: 0,
        textAlign: "center",
        minWidth: 0,
        ...style,
      }}
    />
  );
}

// ─── Sliders + SV plane ────────────────────────────────────────────────────────

function SVPlane({ bg, hsv, onChange, onDragStart, onDragEnd }: {
  bg: string;
  hsv: { h: number; s: number; v: number };
  onChange: (h: { h: number; s: number; v: number }) => void;
  onDragStart?: () => void;
  onDragEnd?: () => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  function update(e: PointerEvent) {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
    const y = Math.max(0, Math.min(1, (e.clientY - r.top) / r.height));
    onChange({ h: hsv.h, s: x, v: 1 - y });
  }
  return (
    <div
      ref={ref}
      onPointerDown={(e) => { e.currentTarget.setPointerCapture(e.pointerId); onDragStart?.(); update(e.nativeEvent); }}
      onPointerMove={(e) => { if (e.buttons === 1) update(e.nativeEvent); }}
      onPointerUp={() => onDragEnd?.()}
      onPointerCancel={() => onDragEnd?.()}
      style={{
        position: "relative", height: 150,
        background: `linear-gradient(to top, #000, transparent), linear-gradient(to right, #fff, transparent), ${bg}`,
        cursor: "crosshair", touchAction: "none",
      }}
    >
      <div style={{
        position: "absolute",
        left: `${hsv.s * 100}%`, top: `${(1 - hsv.v) * 100}%`,
        width: 12, height: 12, borderRadius: "50%",
        border: "2px solid white", boxShadow: "0 0 0 1px rgba(0,0,0,0.4)",
        transform: "translate(-50%, -50%)", pointerEvents: "none",
      }} />
    </div>
  );
}

function HueSlider({ hue, onChange, onDragStart, onDragEnd }: {
  hue: number;
  onChange: (h: number) => void;
  onDragStart?: () => void;
  onDragEnd?: () => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  function update(e: PointerEvent) {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    onChange(Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * 360);
  }
  const thumbColor = (() => {
    const rgb = hsvToRgb({ h: hue, s: 1, v: 1 });
    return `rgb(${Math.round(rgb.r * 255)},${Math.round(rgb.g * 255)},${Math.round(rgb.b * 255)})`;
  })();
  return (
    <div
      ref={ref}
      onPointerDown={(e) => { e.currentTarget.setPointerCapture(e.pointerId); onDragStart?.(); update(e.nativeEvent); }}
      onPointerMove={(e) => { if (e.buttons === 1) update(e.nativeEvent); }}
      onPointerUp={() => onDragEnd?.()}
      onPointerCancel={() => onDragEnd?.()}
      style={{
        position: "relative", height: 12, borderRadius: 6,
        background: "linear-gradient(to right, #f00, #ff0, #0f0, #0ff, #00f, #f0f, #f00)",
        cursor: "ew-resize", touchAction: "none",
      }}
    >
      <div style={{
        position: "absolute",
        left: `${(hue / 360) * 100}%`, top: "50%",
        width: 14, height: 14, borderRadius: "50%",
        background: thumbColor,
        border: "2px solid white", boxShadow: "0 0 0 1px rgba(0,0,0,0.35)",
        transform: "translate(-50%, -50%)", pointerEvents: "none",
      }} />
    </div>
  );
}

function AlphaSlider({ alpha, baseColor, onChange, onDragStart, onDragEnd }: {
  alpha: number;
  baseColor: { r: number; g: number; b: number };
  onChange: (a: number) => void;
  onDragStart?: () => void;
  onDragEnd?: () => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const css = `rgb(${Math.round(baseColor.r * 255)},${Math.round(baseColor.g * 255)},${Math.round(baseColor.b * 255)})`;
  function update(e: PointerEvent) {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    onChange(Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)));
  }
  return (
    <div
      ref={ref}
      onPointerDown={(e) => { e.currentTarget.setPointerCapture(e.pointerId); onDragStart?.(); update(e.nativeEvent); }}
      onPointerMove={(e) => { if (e.buttons === 1) update(e.nativeEvent); }}
      onPointerUp={() => onDragEnd?.()}
      onPointerCancel={() => onDragEnd?.()}
      style={{
        position: "relative", height: 12, borderRadius: 6,
        background: `linear-gradient(to right, transparent, ${css}), repeating-conic-gradient(#666 0% 25%, #999 0% 50%) 50% / 8px 8px`,
        cursor: "ew-resize", touchAction: "none",
      }}
    >
      <div style={{
        position: "absolute",
        left: `${alpha * 100}%`, top: "50%",
        width: 14, height: 14, borderRadius: "50%",
        background: `rgba(${Math.round(baseColor.r * 255)},${Math.round(baseColor.g * 255)},${Math.round(baseColor.b * 255)},${alpha})`,
        border: "2px solid white", boxShadow: "0 0 0 1px rgba(0,0,0,0.35)",
        transform: "translate(-50%, -50%)", pointerEvents: "none",
      }} />
    </div>
  );
}

// ─── Color math ────────────────────────────────────────────────────────────────

function rgbToHsv(c: { r: number; g: number; b: number }): { h: number; s: number; v: number } {
  const max = Math.max(c.r, c.g, c.b), min = Math.min(c.r, c.g, c.b), d = max - min;
  let h = 0;
  if (d !== 0) {
    if (max === c.r) h = 60 * (((c.g - c.b) / d) % 6);
    else if (max === c.g) h = 60 * ((c.b - c.r) / d + 2);
    else h = 60 * ((c.r - c.g) / d + 4);
  }
  if (h < 0) h += 360;
  return { h, s: max === 0 ? 0 : d / max, v: max };
}

export function hsvToRgb({ h, s, v }: { h: number; s: number; v: number }): { r: number; g: number; b: number } {
  const c = v * s, hh = (h / 60) % 6, x = c * (1 - Math.abs((hh % 2) - 1));
  let r = 0, g = 0, b = 0;
  if (hh < 1) { r = c; g = x; } else if (hh < 2) { r = x; g = c; }
  else if (hh < 3) { g = c; b = x; } else if (hh < 4) { g = x; b = c; }
  else if (hh < 5) { r = x; b = c; } else { r = c; b = x; }
  const m = v - c;
  return { r: r + m, g: g + m, b: b + m };
}

function rgbToHsl({ r, g, b }: { r: number; g: number; b: number }): { h: number; s: number; l: number } {
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  const l = (max + min) / 2;
  if (max === min) return { h: 0, s: 0, l };
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h;
  if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
  else if (max === g) h = ((b - r) / d + 2) / 6;
  else h = ((r - g) / d + 4) / 6;
  return { h: h * 360, s, l };
}

function hslToRgb({ h, s, l }: { h: number; s: number; l: number }): { r: number; g: number; b: number } {
  if (s === 0) return { r: l, g: l, b: l };
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;
  const hue2rgb = (t: number) => {
    if (t < 0) t += 1; if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
  };
  const hh = h / 360;
  return { r: hue2rgb(hh + 1 / 3), g: hue2rgb(hh), b: hue2rgb(hh - 1 / 3) };
}

export function colorToHex(c: { r: number; g: number; b: number }): string {
  const to = (v: number) => Math.round(v * 255).toString(16).padStart(2, "0").toUpperCase();
  return `${to(c.r)}${to(c.g)}${to(c.b)}`;
}

// Split swatch background — left half shows the solid (fully opaque) color,
// right half shows the color at its actual alpha over a checker pattern. Lets
// the user see both the chosen hue and what its current opacity will look like
// against an unknown background. At a=1 both halves match.
export function swatchBackground(color: { r: number; g: number; b: number; a: number }): string {
  const R = Math.round(color.r * 255), G = Math.round(color.g * 255), B = Math.round(color.b * 255);
  const opaque = `rgba(${R}, ${G}, ${B}, 1)`;
  const alpha = `rgba(${R}, ${G}, ${B}, ${color.a})`;
  return [
    `linear-gradient(to right, ${opaque} 50%, transparent 50%)`,
    `linear-gradient(to right, transparent 50%, ${alpha} 50%)`,
    `repeating-conic-gradient(#666 0% 25%, #999 0% 50%) 50% / 4px 4px`,
  ].join(", ");
}

export function parseHex(input: string): Color | null {
  let s = input.trim().replace(/^#/, "");
  if (s.length === 3) s = s.split("").map((c) => c + c).join("");
  if (s.length === 6) s = s + "FF";
  if (s.length !== 8) return null;
  const r = parseInt(s.slice(0, 2), 16), g = parseInt(s.slice(2, 4), 16);
  const b = parseInt(s.slice(4, 6), 16), a = parseInt(s.slice(6, 8), 16);
  if ([r, g, b, a].some((v) => Number.isNaN(v))) return null;
  return { r: r / 255, g: g / 255, b: b / 255, a: a / 255 };
}
