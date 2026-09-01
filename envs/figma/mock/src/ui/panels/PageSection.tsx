import { useRef, useState } from "react";
import { Section } from "./sectionShell";
import { useStore } from "@/engine/store";
import { ColorPicker, colorToHex, parseHex, swatchBackground } from "@/ui/overlays/ColorPicker";
import { dispatch, makeOpId, openTransaction, commitTransaction } from "@/engine/dispatch";
import { emitSemantic } from "@/logger/semantic";
import { Eye, EyeClosed } from "lucide-react";
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
  // Color-picker drag transaction. Each pointerdown on a slider opens one,
  // pointerup commits it. All onChange ticks in between dispatch with the
  // same transactionId so the entire drag becomes a single undo entry. Avoids
  // the per-tick flooding hypothesis from item #15.
  const pickerTxRef = useRef<string | null>(null);
  if (!page) return null;
  const c = page.backgroundColor;
  const opacityPct = Math.round(c.a * 100);

  function commitBg(color: Color, trigger: "color_picker" | "hex_input") {
    if (!page) return;
    const before = page.backgroundColor;
    if (before.r === color.r && before.g === color.g && before.b === color.b && before.a === color.a) return;
    const txId = pickerTxRef.current;
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_property",
        pageId: page.id,
        ids: [page.id],
        path: "backgroundColor",
        before: { [page.id]: { ...before } },
        after: { [page.id]: { ...color } },
      },
      txId ? { transactionId: txId } : undefined,
    );
    emitSemantic({
      name: "set_page_background",
      targetPageId: page.id,
      before,
      after: color,
      trigger,
    });
  }

  function pickerDragStart() {
    if (pickerTxRef.current != null) return;
    pickerTxRef.current = openTransaction();
  }

  function pickerDragEnd() {
    const id = pickerTxRef.current;
    if (id == null) return;
    pickerTxRef.current = null;
    commitTransaction(id);
  }

  function commitOpacity(pct: number, txId?: string | null) {
    if (!page) return;
    const beforePct = Math.round(page.backgroundColor.a * 100);
    const target = Math.max(0, Math.min(100, Math.round(pct)));
    if (beforePct === target) return;
    const v = target / 100;
    const before = page.backgroundColor.a;
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_property",
        pageId: page.id,
        ids: [page.id],
        path: "backgroundColor/a",
        before: { [page.id]: before },
        after: { [page.id]: v },
      },
      txId ? { transactionId: txId } : undefined,
    );
    emitSemantic({
      name: "set_page_background_opacity",
      targetPageId: page.id,
      before,
      after: v,
      trigger: "panel_input",
    });
  }

  function syncHiddenToOpacity(targetPct: number) {
    if (!page) return;
    if (targetPct === 0 && !page.backgroundHidden) toggleHidden();
    else if (targetPct > 0 && page.backgroundHidden) toggleHidden();
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

  // Scrub state for % drag
  const scrubRef = useRef<{ baseX: number; baseValue: number } | null>(null);
  const scrubTxRef = useRef<string | null>(null);
  const [opacityDraft, setOpacityDraft] = useState<string | null>(null);
  const [scrubbing, setScrubbing] = useState(false);
  const opacityDisplay = opacityDraft ?? String(opacityPct);

  return (
    <Section title="Page">
      <div style={{ display: "flex", alignItems: "center", gap: 6, height: 28, minWidth: 0, overflow: "hidden" }}>
        <button
          data-id="page.bg.open-color-picker"
          onClick={(e) => {
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
            setPickerAnchor({ right: window.innerWidth - rect.left + 8, top: rect.top });
          }}
          title="Page background color"
          style={{
            width: 22, height: 22, borderRadius: 3, flexShrink: 0,
            background: swatchBackground(c),
            border: "1px solid var(--color-border)",
          }}
        />
        <input
          data-id="page.bg.hex-input"
          value={hexValue}
          onChange={(e) => setHexDraft(e.target.value)}
          onFocus={(e) => requestAnimationFrame(() => e.target.select())}
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
            flex: 1, minWidth: 0, height: 22,
            background: "var(--color-bg-input)",
            color: "var(--color-text-primary)",
            border: 0, borderRadius: 3, padding: "0 6px",
            fontSize: "var(--fs-sm)", fontFamily: "var(--font-family)", outline: 0,
          }}
        />
        {/* Opacity: editable number + draggable % */}
        <div
          style={{
            display: "flex", alignItems: "center",
            height: 22, background: "var(--color-bg-input)", borderRadius: 3,
            flexShrink: 0,
            opacity: page.backgroundHidden ? 0.35 : 1,
            pointerEvents: page.backgroundHidden ? "none" : "auto",
          }}
        >
          <input
            data-id="page.bg.opacity-input"
            value={opacityDisplay}
            onChange={(e) => setOpacityDraft(e.target.value)}
            onFocus={(e) => { setOpacityDraft(String(opacityPct)); requestAnimationFrame(() => e.target.select()); }}
            onBlur={() => {
              const n = parseFloat(opacityDisplay);
              if (Number.isFinite(n)) {
                commitOpacity(n);
                syncHiddenToOpacity(Math.max(0, Math.min(100, Math.round(n))));
              }
              setOpacityDraft(null);
            }}
            onKeyDown={(e) => { if (e.key === "Enter") (e.target as HTMLInputElement).blur(); }}
            style={{
              width: 28, background: "transparent", border: 0,
              color: "var(--color-text-primary)", fontSize: "var(--fs-sm)",
              outline: 0, textAlign: "right", padding: "0 2px",
            }}
          />
          <span
            data-id="page.bg.opacity-scrub"
            onPointerDown={(e) => {
              (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
              scrubRef.current = { baseX: e.clientX, baseValue: opacityPct };
              scrubTxRef.current = openTransaction();
              setScrubbing(true);
            }}
            onPointerMove={(e) => {
              if (!scrubRef.current) return;
              const dx = e.clientX - scrubRef.current.baseX;
              const next = Math.max(0, Math.min(100, Math.round(scrubRef.current.baseValue + dx)));
              setOpacityDraft(String(next));
              commitOpacity(next, scrubTxRef.current);
            }}
            onPointerUp={(e) => {
              if (!scrubRef.current) return;
              const dx = e.clientX - scrubRef.current.baseX;
              const next = Math.max(0, Math.min(100, Math.round(scrubRef.current.baseValue + dx)));
              commitOpacity(next, scrubTxRef.current);
              if (scrubTxRef.current) {
                commitTransaction(scrubTxRef.current);
                scrubTxRef.current = null;
              }
              syncHiddenToOpacity(next);
              setOpacityDraft(null);
              scrubRef.current = null;
              setScrubbing(false);
            }}
            style={{
              fontSize: "var(--fs-xs)", color: "var(--color-text-muted)",
              paddingRight: 6, paddingLeft: 1,
              cursor: scrubbing ? "ew-resize" : "ew-resize",
              userSelect: "none", touchAction: "none",
            }}
          >
            %
          </span>
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
          {page.backgroundHidden ? <EyeClosed size={14} /> : <Eye size={14} />}
        </button>
      </div>
      {pickerAnchor && (
        <ColorPicker
          value={c}
          onChange={(color) => commitBg(color, "color_picker")}
          onChangeStart={pickerDragStart}
          onChangeEnd={pickerDragEnd}
          onClose={() => {
            // If a drag was still open when the picker closes (rare — e.g.
            // user clicks outside while holding), force-commit the txn.
            pickerDragEnd();
            setPickerAnchor(null);
          }}
          anchor={pickerAnchor}
        />
      )}
    </Section>
  );
}
