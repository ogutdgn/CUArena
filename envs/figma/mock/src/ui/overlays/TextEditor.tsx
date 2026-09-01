// In-place text editor overlay. Positioned over the text layer in screen coords.

import { useEffect, useRef } from "react";
import { useStore, selectActiveViewport } from "@/engine/store";
import { commitText, snapshotText } from "@/engine/textCommands";
import { emitSemantic } from "@/logger/semantic";
import type { Text as TextLayer } from "@/types/scene";
import { textEditorCssMatrix } from "./textEditorGeometry";

export function TextEditor() {
  const editMode = useStore((s) => s.editMode);
  const cssMatrix = useStore((s) => {
    if (s.editMode.kind !== "text" || !s.editMode.layerId) return null;
    const n = s.nodesById[s.editMode.layerId];
    if (!n || (n as TextLayer).type !== "text") return null;
    const svgEl = document.querySelector(".canvas-svg") as SVGSVGElement | null;
    const rect = svgEl?.getBoundingClientRect();
    if (!rect) return null;
    return textEditorCssMatrix(s, n as TextLayer, selectActiveViewport(s), rect);
  });
  const layer = useStore((s) => {
    if (s.editMode.kind !== "text" || !s.editMode.layerId) return null;
    const n = s.nodesById[s.editMode.layerId];
    return (n && (n as TextLayer).type === "text" ? (n as TextLayer) : null);
  });

  const ref = useRef<HTMLDivElement | null>(null);
  const snapshotRef = useRef<{
    content: string;
    runs: unknown[];
    fontFamily: string;
    fontWeight: number;
    fontSize: number;
  } | null>(null);
  const draftRef = useRef("");

  useEffect(() => {
    if (editMode.kind !== "text" || !editMode.layerId) return;
    const snap = snapshotText(editMode.layerId);
    if (snap) {
      snapshotRef.current = snap;
      draftRef.current = snap.content;
    }
    requestAnimationFrame(() => {
      if (ref.current) {
        ref.current.textContent = draftRef.current;
      }
      ref.current?.focus();
      // Move caret to end
      const el = ref.current;
      if (el) {
        const range = document.createRange();
        range.selectNodeContents(el);
        range.collapse(false);
        const sel = window.getSelection();
        sel?.removeAllRanges();
        sel?.addRange(range);
      }
    });
  }, [editMode.kind, editMode.layerId]);

  if (editMode.kind !== "text" || !layer) return null;

  // Compute screen transform from the full layer-to-world matrix. Text layers
  // inside frames store x/y in parent-local coordinates; using those directly
  // as world coordinates makes the editor appear near the page origin until
  // commit. The matrix path matches SVG rendering, including rotated/flipped
  // parents.
  const svgEl = document.querySelector(".canvas-svg") as SVGSVGElement | null;
  const r = svgEl?.getBoundingClientRect();
  if (!r || !cssMatrix) return null;

  function commit() {
    const layerId = (editMode as { layerId?: string }).layerId;
    if (!layerId || !snapshotRef.current || !layer) return;
    const after = {
      content: draftRef.current,
      runs: layer.runs,
      fontFamily: layer.fontFamily,
      fontWeight: layer.fontWeight,
      fontSize: layer.fontSize,
    };
    commitText(layerId, snapshotRef.current, after);
  }

  return (
    <div
      ref={ref}
      contentEditable
      suppressContentEditableWarning
      onInput={(e) => {
        const text = (e.currentTarget as HTMLDivElement).innerText;
        draftRef.current = text;
        emitSemantic({
          name: "type_characters",
          layerId: editMode.layerId ?? "",
          length: text.length,
        } as never);
      }}
      onBlur={commit}
      onKeyDown={(e) => {
        if (e.key === "Escape") {
          e.preventDefault();
          ref.current?.blur();
        }
      }}
      style={{
        position: "fixed",
        left: 0,
        top: 0,
        transform: cssMatrix,
        transformOrigin: "0 0",
        minWidth: layer.resizingMode === "fixed" ? layer.w : undefined,
        width: layer.resizingMode === "fixed" ? layer.w : "auto",
        height: layer.resizingMode === "fixed" ? layer.h : undefined,
        minHeight: 16,
        fontFamily: layer.fontFamily,
        fontSize: layer.fontSize,
        fontWeight: layer.fontWeight,
        lineHeight: layer.lineHeight.type === "auto" ? "normal" : `${layer.lineHeight.value}${layer.lineHeight.type === "px" ? "px" : "%"}`,
        textAlign: layer.hAlign,
        color: paintHex(layer.fills[0]) ?? "white",
        background: "transparent",
        border: "1.5px solid var(--color-selection-blue)",
        outline: "none",
        padding: 0,
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
        zIndex: 90,
        cursor: "text",
        boxSizing: "content-box",
      }}
    />
  );
}

function paintHex(p: TextLayer["fills"][number] | undefined): string | undefined {
  if (!p || p.kind !== "solid") return undefined;
  const c = p.color;
  return `rgba(${Math.round(c.r * 255)}, ${Math.round(c.g * 255)}, ${Math.round(c.b * 255)}, ${c.a})`;
}
