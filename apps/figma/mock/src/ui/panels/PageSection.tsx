import { useRef, useState } from "react";
import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { ColorPicker, colorToHex, parseHex } from "@/ui/overlays/ColorPicker";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { emitSemantic } from "@/logger/semantic";
import { Eye, EyeOff } from "lucide-react";
import type { Color } from "@/types/scene";

// No-selection right-panel section. Renders only the Page block — Local styles
// and Export are intentionally omitted in this mock pass (user choice). Page
// shows: color swatch (opens picker) + hex input (typing commits) + opacity %
// + hide-background toggle. Color and opacity are separate undo entries so
// toggling visibility doesn't destroy the alpha value.
export function PageSection() {
  const page = useStore((s) => s.document.pages.find((p) => p.id === s.activePageId));
  const [pickerAnchor, setPickerAnchor] = useState<{ right: number; top: number } | null>(null);
  const [hexDraft, setHexDraft] = useState<string | null>(null);
  // Escape on the hex input cancels the draft. We blur after clearing the
  // draft, which fires onBlur — set this flag so blur skips the commit. Using
  // a ref (not state) so it's read synchronously inside the same blur tick.
  const cancelHexRef = useRef(false);
  if (!page) return null;
  const c = page.backgroundColor;
  const swatchBg = `rgba(${Math.round(c.r * 255)}, ${Math.round(c.g * 255)}, ${Math.round(c.b * 255)}, ${c.a})`;
  const opacityPct = Math.round(c.a * 100);

  function commitBg(color: Color, trigger: "color_picker" | "hex_input") {
    if (!page) return;
    const before = page.backgroundColor;
    if (before.r === color.r && before.g === color.g && before.b === color.b && before.a === color.a) return;
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_property",
      pageId: page.id,
      ids: [page.id],
      path: "backgroundColor",
      before: { [page.id]: { ...before } },
      after: { [page.id]: { ...color } },
    });
    emitSemantic({
      name: "set_page_background",
      targetPageId: page.id,
      before,
      after: color,
      trigger,
    });
  }

  function commitOpacity(pct: number) {
    if (!page) return;
    // Compare in the integer-percent space the UI displays. Without this, a
    // non-integer stored alpha (e.g. 0.255) round-trips through the input as
    // 26%, and a focus+blur without editing would dispatch a tiny opacity
    // change (0.255 → 0.26) and burn an undo entry.
    const beforePct = Math.round(page.backgroundColor.a * 100);
    const target = Math.max(0, Math.min(100, Math.round(pct)));
    if (beforePct === target) return;
    const v = target / 100;
    const before = page.backgroundColor.a;
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_property",
      pageId: page.id,
      ids: [page.id],
      path: "backgroundColor/a",
      before: { [page.id]: before },
      after: { [page.id]: v },
    });
    emitSemantic({
      name: "set_page_background_opacity",
      targetPageId: page.id,
      before,
      after: v,
      trigger: "panel_input",
    });
  }

  function toggleHidden() {
    if (!page) return;
    const before = page.backgroundHidden;
    const next = !before;
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_property",
      pageId: page.id,
      ids: [page.id],
      path: "backgroundHidden",
      before: { [page.id]: before },
      after: { [page.id]: next },
    });
    emitSemantic({
      name: "toggle_page_background_hidden",
      targetPageId: page.id,
      before,
      after: next,
      trigger: "panel_button",
    });
  }

  function commitHex(draft: string) {
    setHexDraft(null);
    const parsed = parseHex(draft);
    if (!parsed) return;
    // Preserve current alpha — hex input edits color only; opacity is a separate field.
    commitBg({ r: parsed.r, g: parsed.g, b: parsed.b, a: c.a }, "hex_input");
  }

  const hexValue = hexDraft ?? colorToHex(c);

  return (
    <Section title="Page">
      <div style={{ display: "flex", alignItems: "center", gap: 6, height: 28 }}>
        <button
          data-id="page.bg.open-color-picker"
          onClick={(e) => {
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
            setPickerAnchor({ right: window.innerWidth - rect.left + 8, top: rect.top });
          }}
          title="Page background"
          style={{
            width: 22,
            height: 22,
            borderRadius: 3,
            background: swatchBg,
            border: "1px solid var(--color-border)",
            flexShrink: 0,
          }}
        />
        <input
          data-id="page.bg.hex-input"
          value={hexValue}
          onChange={(e) => setHexDraft(e.target.value)}
          onBlur={(e) => {
            if (cancelHexRef.current) {
              cancelHexRef.current = false;
              return;
            }
            commitHex(e.currentTarget.value);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
            else if (e.key === "Escape") {
              cancelHexRef.current = true;
              setHexDraft(null);
              (e.target as HTMLInputElement).blur();
            }
          }}
          spellCheck={false}
          style={{
            flex: 1,
            minWidth: 0,
            height: 22,
            background: "var(--color-bg-input)",
            color: "var(--color-text-primary)",
            border: 0,
            borderRadius: 3,
            padding: "0 6px",
            fontSize: "var(--fs-sm)",
            fontFamily: "var(--font-family)",
            outline: 0,
          }}
        />
        <div style={{ width: 56, flexShrink: 0 }}>
          <NumericInput value={opacityPct} onCommit={commitOpacity} min={0} max={100} suffix="%" />
        </div>
        <button
          data-id="page.bg.toggle-hidden"
          onClick={toggleHidden}
          title={page.backgroundHidden ? "Show background" : "Hide background"}
          aria-pressed={page.backgroundHidden}
          style={{
            width: 22,
            height: 22,
            borderRadius: 3,
            color: page.backgroundHidden ? "var(--color-text-muted)" : "var(--color-text-secondary)",
            display: "grid",
            placeItems: "center",
            flexShrink: 0,
          }}
        >
          {page.backgroundHidden ? <EyeOff size={14} /> : <Eye size={14} />}
        </button>
      </div>
      {pickerAnchor && (
        <ColorPicker
          value={c}
          onChange={(color) => commitBg(color, "color_picker")}
          onClose={() => setPickerAnchor(null)}
          anchor={pickerAnchor}
        />
      )}
    </Section>
  );
}
