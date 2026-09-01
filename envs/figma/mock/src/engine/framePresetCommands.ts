import { useStore } from "@/engine/store";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { setSelection } from "@/engine/commands";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import { findFramePreset } from "@/util/framePresets";
import type { Frame, Layer } from "@/types/scene";

export function createFrameFromPreset(presetId: string): void {
  const preset = findFramePreset(presetId);
  if (!preset) return;

  const state = useStore.getState();
  const pageId = state.activePageId;
  const page = state.document.pages.find((p) => p.id === pageId);
  if (!page) return;

  // Smart placement: if no top-level frames exist, center at world origin.
  // Otherwise place to the right of the rightmost frame with a 100px gap.
  const topFrames = page.children.filter(
    (c) => c.type === "frame" || c.type === "section",
  );

  let x: number;
  let y: number;
  if (topFrames.length === 0) {
    x = -Math.round(preset.w / 2);
    y = -Math.round(preset.h / 2);
  } else {
    const rightEdge = Math.max(...topFrames.map((f) => f.x + f.w));
    const topY = Math.min(...topFrames.map((f) => f.y));
    x = rightEdge + 100;
    y = topY;
  }

  // Name: count existing frames whose names start with this preset's label.
  // First: "iPhone 17", second: "iPhone 17 - 2", etc.
  const base = preset.label;
  let count = 0;
  function countNamed(layers: Layer[]) {
    for (const l of layers) {
      if (l.name === base || l.name.startsWith(base + " - ")) count++;
      if ("children" in l && Array.isArray(l.children)) countNamed(l.children);
    }
  }
  countNamed(page.children);
  const name = count === 0 ? base : `${base} - ${count + 1}`;

  const node: Frame = {
    id: uid("frame"),
    parentId: pageId,
    type: "frame",
    name,
    x,
    y,
    w: preset.w,
    h: preset.h,
    rotation: 0,
    scaleX: 1,
    scaleY: 1,
    visible: true,
    locked: false,
    opacity: 1,
    constraints: { horizontal: "left", vertical: "top" },
    fills: [{ kind: "solid", color: { r: 0.92, g: 0.92, b: 0.92, a: 1 }, opacity: 1, visible: true }],
    strokes: [],
    effects: [],
    cornerRadius: 0,
    clipsContent: true,
    children: [],
  };

  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "create_node",
    pageId,
    parentId: pageId,
    indexInParent: page.children.length,
    node,
  });

  emitSemantic({
    name: "create_frame",
    layerId: node.id,
    x,
    y,
    w: preset.w,
    h: preset.h,
    parentId: pageId,
    mode: "preset",
    trigger: "preset",
  });

  setSelection([node.id], "implicit_after_create");

  // Revert tool to move
  const before = useStore.getState().activeTool;
  if (before !== "move") {
    dispatch({ id: makeOpId(), timestamp: performance.now(), kind: "set_tool", before, after: "move" });
    emitSemantic({ name: "tool_change", before, after: "move", trigger: "auto_revert_after_create" });
  }
}
