import { useState } from "react";
import { Section } from "./sectionShell";
import { useStore } from "@/engine/store";
import { ColorPicker, colorToHex } from "@/ui/overlays/ColorPicker";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { emitSemantic } from "@/logger/semantic";
import { noopClick } from "@/ui/chrome/noopClick";
import type { Color } from "@/types/scene";

export function PageSection() {
  const page = useStore((s) => s.document.pages.find((p) => p.id === s.activePageId));
  const [pickerAnchor, setPickerAnchor] = useState<{ right: number; top: number } | null>(null);
  if (!page) return null;
  const c = page.backgroundColor;
  const hex = colorToHex(c);
  const swatch = `rgba(${Math.round(c.r * 255)}, ${Math.round(c.g * 255)}, ${Math.round(c.b * 255)}, ${c.a})`;

  function setBg(color: Color) {
    if (!page) return;
    const before = page.backgroundColor;
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
    });
  }

  return (
    <>
      <Section title="Page">
        <button
          data-id="page.bg.open-color-picker"
          onClick={(e) => {
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
            setPickerAnchor({ right: window.innerWidth - rect.left + 8, top: rect.top });
          }}
          title="Page background"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            height: 28,
            padding: "0 6px",
            background: "var(--color-bg-input)",
            borderRadius: 4,
            color: "var(--color-text-primary)",
            fontSize: "var(--fs-sm)",
            textAlign: "left",
          }}
        >
          <span
            aria-hidden
            style={{
              width: 14,
              height: 14,
              borderRadius: 3,
              background: swatch,
              border: "1px solid var(--color-border)",
            }}
          />
          {hex}
        </button>
        {pickerAnchor && (
          <ColorPicker
            value={c}
            onChange={setBg}
            onClose={() => setPickerAnchor(null)}
            anchor={pickerAnchor}
          />
        )}
      </Section>
      <Section title="Local styles and variables" addId="local-styles.create-text">
        <Empty />
      </Section>
      <Section title="Export" addId="export-page.add">
        <Empty />
      </Section>
    </>
  );
}

function Empty() {
  // eslint-disable-next-line @typescript-eslint/no-unused-expressions
  void noopClick;
  return (
    <div
      style={{
        color: "var(--color-text-muted)",
        fontSize: "var(--fs-xs)",
        padding: "4px 0",
      }}
    >
      Visual-only in this mock.
    </div>
  );
}
