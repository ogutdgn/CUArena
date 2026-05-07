// High-level commands for editing a layer's properties (fired from panel inputs).
// Each command captures snapshot before/after and dispatches the appropriate op
// + a semantic event.

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { getSelectedLayers } from "./selectors";
import type { Layer } from "@/types/scene";
import type { TransformMap } from "@/types/ops";
import type { Color } from "@/types/scene";

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

export function setTransformField(field: "x" | "y" | "w" | "h" | "rotation", value: number) {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return;
  const before: TransformMap = {};
  const after: TransformMap = {};
  for (const l of layers) {
    const t = txtuple(l);
    before[l.id] = { ...t };
    after[l.id] = { ...t, [field]: field === "w" || field === "h" ? Math.max(1, value) : value };
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_transform",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    before,
    after,
  });
  if (field === "rotation") {
    const beforeR: Record<string, number> = {};
    const afterR: Record<string, number> = {};
    for (const l of layers) {
      beforeR[l.id] = l.rotation;
      afterR[l.id] = value;
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
      beforeR[l.id] = { x: l.x, y: l.y };
      afterR[l.id] = { x: field === "x" ? value : l.x, y: field === "y" ? value : l.y };
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

export function setCornerRadius(value: number) {
  const v = Math.max(0, value);
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "cornerRadius" in l);
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  const beforeS: Record<string, number | [number, number, number, number]> = {};
  const afterS: Record<string, number | [number, number, number, number]> = {};
  for (const l of layers) {
    const cr = (l as { cornerRadius: number | [number, number, number, number] }).cornerRadius;
    before[l.id] = cr;
    after[l.id] = v;
    beforeS[l.id] = cr;
    afterS[l.id] = v;
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
    before[l.id] = strokes[0].weight;
    after[l.id] = v;
  }
  dispatchPropertyWithSemantic(
    s.activePageId,
    layers.map((l) => l.id),
    "strokes/0/weight",
    before,
    after,
  );
}

export function addSolidStroke() {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => "strokes" in l);
  if (layers.length === 0) return;
  const newStroke = {
    paint: { kind: "solid", color: { r: 0, g: 0, b: 0, a: 1 }, opacity: 1, visible: true },
    weight: 1,
    alignment: "inside",
    dash: null,
  };
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    const strokes = (l as { strokes: unknown[] }).strokes;
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
