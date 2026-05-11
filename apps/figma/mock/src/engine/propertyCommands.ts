// High-level commands for editing a layer's properties (fired from panel inputs).
// Each command captures snapshot before/after and dispatches the appropriate op
// + a semantic event.

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { getSelectedLayers } from "./selectors";
import type { Layer, Page } from "@/types/scene";
import type { TransformMap } from "@/types/ops";
import type { Color } from "@/types/scene";
import { getLayerPositionValue, transformForLayerPositionValue } from "./positionCoordinates";
import { getFrameContainmentMoves } from "./frameContainment";

function txtuple(l: Layer) {
  return { x: l.x, y: l.y, w: l.w, h: l.h, rotation: l.rotation, scaleX: l.scaleX, scaleY: l.scaleY } as const;
}

// Generic helper: dispatch a set_property op AND emit a `set_property` semantic
// event so the action stream stays consistent with the document mutation.
// Used by stroke/effect/lock commands that don't have a domain-specific
// semantic event in the schema. Skips emission when no layer was actually
// changed (Object.keys(after).length === 0).
function dispatchPropertyWithSemantic(
  pageId: string,
  ids: string[],
  path: string,
  before: Record<string, unknown>,
  after: Record<string, unknown>,
  trigger: "panel_input" | "color_picker" | "context_menu" | "shortcut" = "panel_input",
): void {
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId,
    ids,
    path,
    before,
    after,
  });
  const changedIds = Object.keys(after);
  if (changedIds.length === 0) return;
  emitSemantic({
    name: "set_property",
    layerIds: changedIds,
    path,
    before,
    after,
    trigger,
  });
}

export function setTransformField(
  field: "x" | "y" | "w" | "h" | "rotation",
  value: number,
  options: { transactionId?: string; deferFrameContainment?: boolean } = {},
) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return;
  // Normalize rotation to [0, 360). Lets users type magnitudes like -1060 and
  // see the input snap to the equivalent canonical angle (per user spec, item 20).
  let v = value;
  if (field === "rotation") v = ((value % 360) + 360) % 360;
  const before: TransformMap = {};
  const after: TransformMap = {};
  for (const l of layers) {
    const t = txtuple(l);
    before[l.id] = { ...t };
    if (field === "x" || field === "y") {
      const pos = getLayerPositionValue(s, l);
      after[l.id] = transformForLayerPositionValue(s, l, { ...pos, [field]: v });
    } else if (field === "w" || field === "h") {
      const pos = getLayerPositionValue(s, l);
      after[l.id] = transformForLayerPositionValue(s, l, pos, { [field]: Math.max(1, v) });
    } else {
      after[l.id] = { ...t, [field]: v };
    }
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_transform",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    before,
    after,
  }, {
    transactionId: options.transactionId,
  });
  if (!options.deferFrameContainment && (field === "x" || field === "y" || field === "w" || field === "h")) {
    dispatchPanelFrameContainment(layers.map((l) => l.id), options.transactionId);
  }
  if (field === "rotation") {
    const beforeR: Record<string, number> = {};
    const afterR: Record<string, number> = {};
    for (const l of layers) {
      beforeR[l.id] = l.rotation;
      afterR[l.id] = v;
    }
    emitSemantic({ name: "rotate_layer", layerIds: layers.map((l) => l.id), before: beforeR, after: afterR, trigger: "panel_input" });
  } else if (field === "w" || field === "h") {
    const beforeR: Record<string, { x: number; y: number; w: number; h: number }> = {};
    const afterR: Record<string, { x: number; y: number; w: number; h: number }> = {};
    for (const l of layers) {
      beforeR[l.id] = { x: l.x, y: l.y, w: l.w, h: l.h };
      afterR[l.id] = { x: l.x, y: l.y, w: field === "w" ? Math.max(1, value) : l.w, h: field === "h" ? Math.max(1, value) : l.h };
    }
    emitSemantic({
      name: "resize_layer",
      layerIds: layers.map((l) => l.id),
      before: beforeR,
      after: afterR,
      handle: field === "w" ? "e" : "s",
      trigger: "panel_input",
      modifiers: { shift: false, alt: false },
    });
  } else {
    const beforeR: Record<string, { x: number; y: number }> = {};
    const afterR: Record<string, { x: number; y: number }> = {};
    for (const l of layers) {
      const pos = getLayerPositionValue(s, l);
      beforeR[l.id] = pos;
      afterR[l.id] = { ...pos, [field]: value };
    }
    emitSemantic({
      name: "move_layer",
      layerIds: layers.map((l) => l.id),
      before: beforeR,
      after: afterR,
      trigger: "panel_input",
      modifiers: { shift: false, alt: false, ctrl: false },
    });
  }
}

export function applyPanelFrameContainmentForSelection(transactionId?: string): void {
  const layers = getSelectedLayers(useStore.getState());
  if (layers.length === 0) return;
  dispatchPanelFrameContainment(layers.map((l) => l.id), transactionId);
}

function dispatchPanelFrameContainment(layerIds: string[], transactionId?: string): void {
  const moves = getFrameContainmentMoves(useStore.getState(), layerIds, { exitRatio: 0.6 });
  for (const move of moves) {
    const now = useStore.getState();
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "reparent",
        pageId: now.activePageId,
        moves: [move],
      },
      { transactionId },
    );
    const afterState = useStore.getState();
    const afterLayer = afterState.nodesById[move.id] as Layer | undefined;
    const afterArr = afterLayer ? childrenOf(afterState, afterLayer.parentId) : null;
    const afterIndex = afterArr && afterLayer ? afterArr.findIndex((c) => c.id === move.id) : move.toIndex;
    emitSemantic({
      name: "reorder_layer",
      layerIds: [move.id],
      before: [{ parentId: move.fromParentId, index: move.fromIndex }],
      after: [{ parentId: afterLayer?.parentId ?? move.toParentId, index: afterIndex >= 0 ? afterIndex : move.toIndex }],
      trigger: "panel_drag",
    });
  }
}

function childrenOf(state: ReturnType<typeof useStore.getState>, parentId: string): Layer[] | null {
  const p = state.nodesById[parentId] as Layer | Page | undefined;
  if (!p) return null;
  if ((p as Page).type === "page") return (p as Page).children;
  if ("children" in (p as object)) return ((p as Layer & { children?: Layer[] }).children ?? null);
  return null;
}

export function setOpacity(value: number) {
  const v = Math.max(0, Math.min(1, value / 100));
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  const beforePct: Record<string, number> = {};
  const afterPct: Record<string, number> = {};
  for (const l of layers) {
    before[l.id] = l.opacity;
    after[l.id] = v;
    beforePct[l.id] = l.opacity;
    afterPct[l.id] = v;
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    path: "opacity",
    before,
    after,
  });
  emitSemantic({
    name: "set_layer_opacity",
    layerIds: layers.map((l) => l.id),
    before: beforePct,
    after: afterPct,
    trigger: "panel_input",
  });
}

export function setVisibility(visible: boolean) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    before[l.id] = l.visible;
    after[l.id] = visible;
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    path: "visible",
    before,
    after,
  });
  emitSemantic({
    name: "toggle_layer_visibility",
    layerIds: layers.map((l) => l.id),
    after: visible,
  });
}

export function setLocked(locked: boolean) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    before[l.id] = l.locked;
    after[l.id] = locked;
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    "locked",
    before,
    after,
  );
}

// Sets corner radius. Single number → uniform; 4-tuple → per-corner
// [topLeft, topRight, bottomRight, bottomLeft]. Frames are excluded —
// frames always render as plain rectangles regardless of model state.
export function setCornerRadius(value: number | [number, number, number, number]) {
  const clamp = (n: number) => Math.max(0, n);
  const v: number | [number, number, number, number] = Array.isArray(value)
    ? [clamp(value[0]), clamp(value[1]), clamp(value[2]), clamp(value[3])]
    : clamp(value);
  const s = useStore.getState();
  // Frames intentionally excluded — they always render flat. Polygons and
  // stars accept only a uniform number (no per-corner editing for them).
  const layers = getSelectedLayers(s).filter((l) =>
    l.type === "rectangle" || l.type === "image" || l.type === "polygon" || l.type === "star",
  );
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  const beforeS: Record<string, number | [number, number, number, number]> = {};
  const afterS: Record<string, number | [number, number, number, number]> = {};
  for (const l of layers) {
    const cr = (l as { cornerRadius?: number | [number, number, number, number] }).cornerRadius ?? 0;
    // Polygon/star only accept uniform — collapse a tuple to its first value.
    const layerVal: number | [number, number, number, number] =
      (l.type === "polygon" || l.type === "star") && Array.isArray(v) ? v[0] : v;
    before[l.id] = cr;
    after[l.id] = layerVal;
    beforeS[l.id] = cr;
    afterS[l.id] = layerVal;
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    path: "cornerRadius",
    before,
    after,
  });
  emitSemantic({
    name: "set_corner_radius",
    layerIds: layers.map((l) => l.id),
    before: beforeS,
    after: afterS,
    trigger: "panel_input",
  });
}

export function setFillColor(fillIndex: number, color: Color) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "fills" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  const beforeC: Record<string, Color> = {};
  for (const l of layers) {
    const fills = (l as { fills: { kind: string; color?: Color }[] }).fills;
    const fill = fills[fillIndex];
    if (!fill || fill.kind !== "solid" || !fill.color) continue;
    before[l.id] = { ...fill.color };
    after[l.id] = { ...color };
    beforeC[l.id] = { ...fill.color };
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    path: `fills/${fillIndex}/color`,
    before,
    after,
  });
  emitSemantic({
    name: "set_fill_color",
    layerIds: layers.map((l) => l.id),
    fillIndex,
    before: layers[0] ? beforeC[layers[0].id] : { r: 0, g: 0, b: 0, a: 1 },
    after: color,
  });
}

export function addSolidFill() {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "fills" in l);
  if (layers.length === 0) return;
  const newFill = { kind: "solid", color: { r: 0.5, g: 0.5, b: 0.5, a: 1 }, opacity: 1, visible: true };
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const fills = (l as { fills: unknown[] }).fills;
    before[l.id] = [...fills];
    after[l.id] = [...fills, newFill];
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    path: "fills",
    before,
    after,
  });
  emitSemantic({
    name: "add_fill",
    layerIds: layers.map((l) => l.id),
    fillIndex: ((layers[0] as unknown) as { fills: unknown[] }).fills.length - 1,
  });
}

export function removeFill(fillIndex: number) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "fills" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const fills = (l as { fills: unknown[] }).fills;
    before[l.id] = [...fills];
    after[l.id] = fills.filter((_, i) => i !== fillIndex);
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    path: "fills",
    before,
    after,
  });
  emitSemantic({ name: "remove_fill", layerIds: layers.map((l) => l.id), fillIndex });
}

export function toggleFillVisibility(fillIndex: number) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "fills" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  let nextVisible = false;
  for (const l of layers) {
    const fill = ((l as unknown) as { fills: { visible: boolean }[] }).fills[fillIndex];
    if (!fill) continue;
    before[l.id] = fill.visible;
    after[l.id] = !fill.visible;
    nextVisible = !fill.visible;
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    path: `fills/${fillIndex}/visible`,
    before,
    after,
  });
  emitSemantic({
    name: "toggle_fill_visibility",
    layerIds: layers.map((l) => l.id),
    index: fillIndex,
    after: nextVisible,
  });
}

// One weight covers the whole stroke stack — UI shows a single weight field
// and every stroke on the layer must share it so the multi-stroke alpha
// composite renders as a single line. Updates every stroke's weight in one op.
export function setStrokeWeight(value: number) {
  const v = Math.max(0, value);
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "strokes" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const strokes = (l as { strokes: { weight: number }[] }).strokes;
    if (strokes.length === 0) continue;
    before[l.id] = strokes.map((sk) => ({ ...sk }));
    after[l.id] = strokes.map((sk) => ({ ...sk, weight: v }));
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    "strokes",
    before,
    after,
  );
}

export function addSolidStroke() {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "strokes" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const strokes = (l as { strokes: { weight: number }[] }).strokes;
    // Inherit weight from the existing stack so the single-weight UI invariant
    // holds when the user adds another color row.
    const inheritedWeight = strokes.length > 0 ? strokes[0].weight : 1;
    const newStroke = {
      paint: { kind: "solid", color: { r: 0, g: 0, b: 0, a: 1 }, opacity: 1, visible: true },
      weight: inheritedWeight,
      alignment: "inside",
      dash: null,
    };
    before[l.id] = [...strokes];
    after[l.id] = [...strokes, newStroke];
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    "strokes",
    before,
    after,
  );
}

export function addDropShadowEffect() {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "effects" in l);
  if (layers.length === 0) return;
  const effect = {
    kind: "drop_shadow" as const,
    x: 0,
    y: 4,
    blur: 4,
    spread: 0,
    color: { r: 0, g: 0, b: 0, a: 0.25 },
    visible: true,
  };
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const effs = (l as { effects: unknown[] }).effects;
    before[l.id] = [...effs];
    after[l.id] = [...effs, effect];
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    "effects",
    before,
    after,
  );
}

export function addLayerBlurEffect() {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "effects" in l);
  if (layers.length === 0) return;
  const effect = { kind: "layer_blur" as const, radius: 4, visible: true };
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const effs = (l as { effects: unknown[] }).effects;
    before[l.id] = [...effs];
    after[l.id] = [...effs, effect];
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    "effects",
    before,
    after,
  );
}

export function removeEffect(effectIndex: number) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "effects" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const effs = (l as { effects: unknown[] }).effects;
    before[l.id] = [...effs];
    after[l.id] = effs.filter((_, i) => i !== effectIndex);
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    "effects",
    before,
    after,
  );
}

export function toggleEffectVisibility(effectIndex: number) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "effects" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  let nextVisible = false;
  for (const l of layers) {
    const eff = ((l as unknown) as { effects: { visible: boolean }[] }).effects[effectIndex];
    if (!eff) continue;
    before[l.id] = eff.visible;
    after[l.id] = !eff.visible;
    nextVisible = !eff.visible;
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    path: `effects/${effectIndex}/visible`,
    before,
    after,
  });
  emitSemantic({
    name: "toggle_effect_visibility",
    layerIds: layers.map((l) => l.id),
    index: effectIndex,
    after: nextVisible,
  });
}

export function setEffectField(effectIndex: number, field: "x" | "y" | "blur" | "spread" | "radius", value: number) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "effects" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const eff = ((l as unknown) as { effects: Record<string, unknown>[] }).effects[effectIndex];
    if (!eff) continue;
    before[l.id] = eff[field];
    after[l.id] = value;
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    `effects/${effectIndex}/${field}`,
    before,
    after,
  );
}

export function setEffectColor(effectIndex: number, color: Color) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "effects" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const eff = ((l as unknown) as { effects: { color?: Color }[] }).effects[effectIndex];
    if (!eff || !eff.color) continue;
    before[l.id] = { ...eff.color };
    after[l.id] = { ...color };
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    `effects/${effectIndex}/color`,
    before,
    after,
    "color_picker",
  );
}

// Polygon sides count. Min 3 (geometric minimum for a polygon); max 60
// mirrors Figma's documented Star cap — Figma doesn't publish a polygon cap,
// 60 is a reasonable practical bound.
export function setPolygonSides(value: number) {
  const v = Math.max(3, Math.min(60, Math.round(value)));
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => l.type === "polygon");
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  const beforeN: Record<string, number> = {};
  const afterN: Record<string, number> = {};
  for (const l of layers) {
    const cur = (l as { sides: number }).sides;
    if (cur === v) continue;
    before[l.id] = cur;
    after[l.id] = v;
    beforeN[l.id] = cur;
    afterN[l.id] = v;
  }
  if (Object.keys(after).length === 0) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: Object.keys(after),
    path: "sides",
    before,
    after,
  });
  emitSemantic({
    name: "set_polygon_sides",
    layerIds: Object.keys(after),
    before: beforeN,
    after: afterN,
    trigger: "panel_input",
  });
}

// Star point count. Figma hard cap: 3..60.
export function setStarPoints(value: number) {
  const v = Math.max(3, Math.min(60, Math.round(value)));
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => l.type === "star");
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  const beforeN: Record<string, number> = {};
  const afterN: Record<string, number> = {};
  for (const l of layers) {
    const cur = (l as { points: number }).points;
    if (cur === v) continue;
    before[l.id] = cur;
    after[l.id] = v;
    beforeN[l.id] = cur;
    afterN[l.id] = v;
  }
  if (Object.keys(after).length === 0) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: Object.keys(after),
    path: "points",
    before,
    after,
  });
  emitSemantic({
    name: "set_star_points",
    layerIds: Object.keys(after),
    before: beforeN,
    after: afterN,
    trigger: "panel_input",
  });
}

// Star inner radius / "ratio". UI shows a percentage (10..100); store keeps
// 0.1..1. Below 10% the star degenerates into thin lines that read as
// rendering glitches, so the minimum is clamped at 0.1.
export function setStarInnerRatio(pct: number) {
  const v = Math.max(0.1, Math.min(1, pct / 100));
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => l.type === "star");
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  const beforeN: Record<string, number> = {};
  const afterN: Record<string, number> = {};
  for (const l of layers) {
    const cur = (l as { innerRatio: number }).innerRatio;
    // Compare in displayed-percent space so a focus+blur on the same integer
    // doesn't burn an undo entry.
    if (Math.round(cur * 100) === Math.round(v * 100)) continue;
    before[l.id] = cur;
    after[l.id] = v;
    beforeN[l.id] = cur;
    afterN[l.id] = v;
  }
  if (Object.keys(after).length === 0) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: Object.keys(after),
    path: "innerRatio",
    before,
    after,
  });
  emitSemantic({
    name: "set_star_inner_ratio",
    layerIds: Object.keys(after),
    before: beforeN,
    after: afterN,
    trigger: "panel_input",
  });
}

export function removeStroke(strokeIndex: number) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "strokes" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const strokes = (l as { strokes: unknown[] }).strokes;
    before[l.id] = [...strokes];
    after[l.id] = strokes.filter((_, i) => i !== strokeIndex);
  }
  dispatchPropertyWithSemantic(s.activePageId, layers.map((l) => l.id), "strokes", before, after);
}

export function toggleStrokeVisibility(strokeIndex: number) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "strokes" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const sk = (l as { strokes: { paint: { visible: boolean } }[] }).strokes[strokeIndex];
    if (!sk) continue;
    before[l.id] = sk.paint.visible;
    after[l.id] = !sk.paint.visible;
  }
  dispatchPropertyWithSemantic(s.activePageId, layers.map((l) => l.id), `strokes/${strokeIndex}/paint/visible`, before, after);
}

export function setStrokeColor(strokeIndex: number, color: Color) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "strokes" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const strokes = (l as { strokes: { paint: { color?: Color } }[] }).strokes;
    const sk = strokes[strokeIndex];
    if (!sk || !sk.paint.color) continue;
    before[l.id] = { ...sk.paint.color };
    after[l.id] = { ...color };
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    `strokes/${strokeIndex}/paint/color`,
    before,
    after,
    "color_picker",
  );
}
