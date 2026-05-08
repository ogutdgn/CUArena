import {
  localToWorld,
  localPointToWorld,
  computeVectorNetworkBounds,
  resolveCreationParentId,
  worldAABBOfLayer,
  worldOrientedCornersOfLayer,
  worldToParentLocal,
  layerToWorldMatrix,
  parentToWorldMatrix,
  invertMatrix,
  multiplyMatrices,
  transformFromLocalMatrix,
} from "../src/engine/coordinates";
import { computeSnap, snapBboxFromStartAABBs } from "../src/engine/snap";
import { selectionOutlineGeometry } from "../src/ui/overlays/selectionOverlayGeometry";
import { resizeSingleTransformedLayer } from "../src/engine/resizeGeometry";
import { resizeLineEndpointFromWorld } from "../src/engine/lineGeometry";
import { applyReparent, applySetTransform } from "../src/engine/ops";
import { frameLabelGeometry } from "../src/engine/frameLabelsGeometry";
import { pannedViewportFromClientDelta } from "../src/engine/viewportPan";
import { textEditorCssMatrix } from "../src/ui/overlays/textEditorGeometry";
import type { AppState } from "../src/engine/store";
import type { Frame, Layer, Line, Page, Rectangle, Text } from "../src/types/scene";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function makeState(layer: Layer): AppState {
  const page: Page = {
    id: "page-1",
    type: "page",
    name: "Page 1",
    children: [layer],
    backgroundColor: { r: 1, g: 1, b: 1, a: 1 },
    backgroundHidden: false,
  };
  return {
    document: { id: "doc-1", schemaVersion: 1, name: "Untitled", pages: [page] },
    activePageId: page.id,
    nodesById: { [page.id]: page, [layer.id]: layer },
    selectionByPage: { [page.id]: [layer.id] },
    focusContextByPage: { [page.id]: null },
    viewportByPage: { [page.id]: { x: 0, y: 0, zoom: 1 } },
    activeTool: "move",
    productMode: "design",
    editMode: { kind: "none" },
    clipboard: null,
    hoveredNodeId: null,
    cursorWorld: null,
    dragPreview: { kind: null, data: null },
    snapLines: [],
    snapMeasures: [],
    contextMenu: null,
    renamingLayerId: null,
    penPreview: null,
    pencilPreview: null,
    insertionCursor: null,
    vectorEditSelected: null,
    spaceDown: false,
    openDropdown: null,
    openModal: null,
    uiHidden: false,
    activeRightTab: "design",
    rotateReadout: null,
    toasts: [],
    prototypePreview: null,
    undoStack: [],
    redoStack: [],
    sessionId: "session-1",
  };
}

function makeNestedState(frame: Frame, selectedChild: Rectangle): AppState {
  frame.children = [selectedChild];
  const state = makeState(frame);
  state.nodesById[selectedChild.id] = selectedChild;
  state.selectionByPage[state.activePageId] = [selectedChild.id];
  return state;
}

function makeMultiSelectionState(layers: Layer[]): AppState {
  const state = makeState(layers[0]);
  const page = state.document.pages[0];
  page.children = layers;
  state.nodesById = { [page.id]: page };
  for (const layer of layers) state.nodesById[layer.id] = layer;
  state.selectionByPage[state.activePageId] = layers.map((layer) => layer.id);
  return state;
}

const rect: Rectangle = {
  id: "rect-1",
  parentId: "page-1",
  type: "rectangle",
  name: "Rectangle 1",
  x: 10,
  y: 20,
  w: 100,
  h: 50,
  rotation: 90,
  scaleX: 1,
  scaleY: 1,
  visible: true,
  locked: false,
  opacity: 1,
  constraints: { horizontal: "left", vertical: "top" },
  fills: [{ kind: "solid", visible: true, opacity: 1, color: { r: 1, g: 0, b: 0, a: 1 } }],
  strokes: [],
  cornerRadius: 0,
  effects: [],
};

const curvedBounds = computeVectorNetworkBounds({
  vertices: [
    { x: 0, y: 0, handleType: "mirror" },
    { x: 100, y: 0, handleType: "mirror" },
  ],
  segments: [
    {
      fromIndex: 0,
      toIndex: 1,
      handleFrom: { dx: 0, dy: 100 },
      handleTo: { dx: 0, dy: 100 },
    },
  ],
  closed: false,
});
assert(curvedBounds.maxY > 0 && curvedBounds.maxY < 100, "vector bounds should use cubic curve extrema, not raw handle endpoints");
assert(Math.abs(curvedBounds.maxY - 75) < 0.001, "pen vector selection bounds should be tight to the rendered bezier curve");

const pan1 = pannedViewportFromClientDelta({ x: 100, y: 200, zoom: 2 }, { x: 10, y: 20 }, { x: 30, y: 50 });
assert(pan1.x === 90 && pan1.y === 185, "hand pan should derive viewport from stable client-pixel delta");
const pan2 = pannedViewportFromClientDelta({ x: 100, y: 200, zoom: 2 }, { x: 10, y: 20 }, { x: 50, y: 80 });
assert(pan2.x === 80 && pan2.y === 170, "hand pan should keep accumulating smoothly as client delta grows");

const geom = selectionOutlineGeometry(makeState(rect));
assert(geom.kind === "single_oriented", "rotated single selection should render an oriented outline");
assert(geom.points.some((p) => p.y < rect.y), "oriented outline should extend above the unrotated bbox after 90deg rotation");
assert(geom.points.some((p) => p.y > rect.y + rect.h), "oriented outline should include the rotated far edge");

const rectState = makeState(rect);
const resizeAfterRotate = resizeSingleTransformedLayer(
  rectState,
  [rect.id],
  { [rect.id]: { x: rect.x, y: rect.y, w: rect.w, h: rect.h, rotation: rect.rotation, scaleX: rect.scaleX, scaleY: rect.scaleY } },
  "e",
  localPointToWorld(rectState, rect, { x: rect.w + 20, y: rect.h / 2 }),
);
assert(resizeAfterRotate?.[rect.id]?.w === rect.w + 20, "rotated selection east handle should resize in layer-local space");
assert(resizeAfterRotate?.[rect.id]?.h === rect.h, "rotated selection side resize should preserve height");

const frame: Frame = {
  id: "frame-1",
  parentId: "page-1",
  type: "frame",
  name: "Frame 1",
  x: 30,
  y: 40,
  w: 120,
  h: 80,
  rotation: 15,
  scaleX: -1,
  scaleY: 1,
  visible: true,
  locked: false,
  opacity: 1,
  constraints: { horizontal: "left", vertical: "top" },
  fills: [],
  strokes: [],
  effects: [],
  cornerRadius: 0,
  clipsContent: false,
  children: [],
};

const child: Rectangle = {
  ...rect,
  id: "child-rect",
  parentId: "frame-1",
  x: 10,
  y: 10,
  w: 20,
  h: 20,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
};
const flippedFrame: Frame = {
  ...frame,
  rotation: 0,
  scaleX: -1,
  scaleY: 1,
  children: [child],
};
const nestedState = makeNestedState(flippedFrame, child);
const childCorners = worldOrientedCornersOfLayer(nestedState, child);
const childMinX = Math.min(...childCorners.map((p) => p.x));
const childMaxX = Math.max(...childCorners.map((p) => p.x));
assert(childMinX === 120 && childMaxX === 140, "child outline should follow a flipped parent frame");

const childGeom = selectionOutlineGeometry(nestedState);
assert(childGeom.kind === "single_oriented", "nested child selection should use oriented geometry");
assert(Math.min(...childGeom.points.map((p) => p.x)) === childMinX, "selection outline should use transformed child corners");

const multiRotated: Rectangle = { ...rect, id: "multi-rotated", rotation: 90, scaleX: 1, scaleY: 1 };
const multiFlipped: Rectangle = { ...rect, id: "multi-flipped", x: 200, y: 10, w: 80, h: 40, rotation: 0, scaleX: -1, scaleY: 1 };
const multiState = makeMultiSelectionState([multiRotated, multiFlipped]);
const multiGeom = selectionOutlineGeometry(multiState);
const a = worldAABBOfLayer(multiState, multiRotated);
const b = worldAABBOfLayer(multiState, multiFlipped);
const expectedMulti = {
  x: Math.min(a.x, b.x),
  y: Math.min(a.y, b.y),
  w: Math.max(a.x + a.w, b.x + b.w) - Math.min(a.x, b.x),
  h: Math.max(a.y + a.h, b.y + b.h) - Math.min(a.y, b.y),
};
assert(multiGeom.kind === "axis_aligned", "multi-selection should use a single axis-aligned visual union");
assert(Math.abs(multiGeom.bbox.x - expectedMulti.x) < 0.001, "multi-selection outline x should include transformed visual bounds");
assert(Math.abs(multiGeom.bbox.y - expectedMulti.y) < 0.001, "multi-selection outline y should include transformed visual bounds");
assert(Math.abs(multiGeom.bbox.w - expectedMulti.w) < 0.001, "multi-selection outline width should include transformed visual bounds");
assert(Math.abs(multiGeom.bbox.h - expectedMulti.h) < 0.001, "multi-selection outline height should include transformed visual bounds");

const transformedLine: Line = {
  id: "line-1",
  parentId: "page-1",
  type: "line",
  name: "Line 1",
  x: 20,
  y: 30,
  w: 100,
  h: 1,
  rotation: 90,
  scaleX: -1,
  scaleY: 1,
  visible: true,
  locked: false,
  opacity: 1,
  constraints: { horizontal: "left", vertical: "top" },
  p1: { x: 0, y: 0 },
  p2: { x: 100, y: 0 },
  strokes: [{ paint: { kind: "solid", color: { r: 1, g: 1, b: 1, a: 1 }, opacity: 1, visible: true }, weight: 1, alignment: "center", dash: null }],
  effects: [],
};
const lineState = makeState(transformedLine);
const draggedLineEndpointWorld = { x: 80, y: 140 };
const resizedLine = resizeLineEndpointFromWorld(lineState, transformedLine, "p2", draggedLineEndpointWorld);
const resizedLineLayer: Line = { ...transformedLine, ...resizedLine.transform, p1: resizedLine.p1, p2: resizedLine.p2 };
const resizedLineState = makeState(resizedLineLayer);
const resizedP1World = localPointToWorld(resizedLineState, resizedLineLayer, resizedLineLayer.p1);
const resizedP2World = localPointToWorld(resizedLineState, resizedLineLayer, resizedLineLayer.p2);
const originalP1World = localPointToWorld(lineState, transformedLine, transformedLine.p1);
assert(Math.abs(resizedP1World.x - originalP1World.x) < 0.001, "line endpoint resize should keep the fixed endpoint stable after rotate/flip");
assert(Math.abs(resizedP1World.y - originalP1World.y) < 0.001, "line endpoint resize should not drift the fixed endpoint after rotate/flip");
assert(Math.abs(resizedP2World.x - draggedLineEndpointWorld.x) < 0.001, "line endpoint resize should place p2 at the dragged world point after rotate/flip");
assert(Math.abs(resizedP2World.y - draggedLineEndpointWorld.y) < 0.001, "line endpoint resize should normalize bbox while preserving the dragged endpoint");

const flippedRootState = makeState({ ...rect, rotation: 0, scaleX: -1, scaleY: 1 });
const flippedRoot = flippedRootState.nodesById[rect.id] as Rectangle;
const flippedOrigin = localToWorld(flippedRootState, flippedRoot.parentId, { x: flippedRoot.x, y: flippedRoot.y });
const flippedMoveLocal = worldToParentLocal(flippedRootState, flippedRoot.parentId, { x: flippedOrigin.x + 15, y: flippedOrigin.y + 5 });
assert(flippedMoveLocal.x === flippedRoot.x + 15, "moving a flipped root layer should use its parent-space origin, not its mirrored visual corner");
assert(flippedMoveLocal.y === flippedRoot.y + 5, "moving a flipped root layer should not jump vertically");

const rotatedSnapLayer: Rectangle = {
  ...rect,
  id: "rotated-snap-layer",
  x: 100,
  y: 100,
  w: 100,
  h: 50,
  rotation: 90,
  scaleX: 1,
  scaleY: 1,
};
const rotatedSnapState = makeState(rotatedSnapLayer);
const rotatedSnapVisualBbox = worldAABBOfLayer(rotatedSnapState, rotatedSnapLayer);
const snapCandidate = { x: 200, y: 100, w: 40, h: 40 };
const dragSnapBbox = snapBboxFromStartAABBs({ [rotatedSnapLayer.id]: rotatedSnapVisualBbox }, [rotatedSnapLayer.id]);
assert(Math.abs(dragSnapBbox.x - rotatedSnapVisualBbox.x) < 0.001, "drag snap bbox should start from the rotated layer's visual AABB x");
assert(Math.abs(dragSnapBbox.w - rotatedSnapVisualBbox.w) < 0.001, "drag snap bbox should use the rotated layer's visual AABB width");
const snapToVisualRight = computeSnap(rotatedSnapVisualBbox, snapCandidate.x - (rotatedSnapVisualBbox.x + rotatedSnapVisualBbox.w), 0, [snapCandidate], 1);
assert(snapToVisualRight.lines.some((line) => line.axis === "x" && line.x === snapCandidate.x), "snap guides should align from a rotated layer's visual AABB");

const innerFrame: Frame = {
  ...frame,
  id: "inner-frame",
  parentId: "frame-1",
  name: "Inner Frame",
  x: 20,
  y: 20,
  w: 40,
  h: 30,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  children: [],
};
const nestedFrameParent: Frame = { ...frame, rotation: 0, scaleX: 1, scaleY: 1, children: [innerFrame] };
const nestedFrameState = makeState(nestedFrameParent);
nestedFrameState.nodesById[innerFrame.id] = innerFrame;
const labels = frameLabelGeometry(nestedFrameState, 1);
assert(labels.length === 1 && labels[0].id === nestedFrameParent.id, "only outermost frame titles should render on canvas");
assert(labels[0].x === nestedFrameParent.x, "frame title should anchor at the visual top-left corner");

const startChildOrigin = localToWorld(nestedState, flippedFrame.id, { x: child.x, y: child.y });
const draggedChildLocal = worldToParentLocal(nestedState, flippedFrame.id, {
  x: startChildOrigin.x + 10,
  y: startChildOrigin.y,
});
assert(draggedChildLocal.x === 0, "dragging right inside a flipped parent should convert through the parent matrix");
assert(draggedChildLocal.y === child.y, "dragging horizontally inside a flipped parent should preserve local y");

const nestedText: Text = {
  id: "text-in-frame",
  parentId: flippedFrame.id,
  type: "text",
  name: "Text",
  x: 10,
  y: 15,
  w: 100,
  h: 24,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  visible: true,
  locked: false,
  opacity: 1,
  constraints: { horizontal: "left", vertical: "top" },
  content: "",
  runs: [],
  fontFamily: "Inter",
  fontWeight: 400,
  fontSize: 16,
  lineHeight: { type: "auto" },
  letterSpacing: { type: "px", value: 0 },
  hAlign: "left",
  vAlign: "top",
  fills: [{ kind: "solid", color: { r: 1, g: 1, b: 1, a: 1 }, opacity: 1, visible: true }],
  strokes: [],
  effects: [],
  resizingMode: "auto_width",
};
const textFrame: Frame = { ...flippedFrame, scaleX: 1, children: [nestedText] };
const textState = makeState(textFrame);
textState.nodesById[nestedText.id] = nestedText;
const textMatrix = textEditorCssMatrix(textState, nestedText, { x: 0, y: 0, zoom: 1 }, { left: 0, top: 0 });
assert(textMatrix.endsWith(", 40, 55)"), "text editor overlay should use parent-aware world position while editing inside a frame");

const reparentFromFlippedFrame: Frame = {
  ...flippedFrame,
  id: "reparent-flipped-frame",
  parentId: "page-1",
  rotation: 25,
  scaleX: -1,
  children: [],
};
const reparentFromFlippedChild: Rectangle = {
  ...child,
  id: "reparent-from-flipped-child",
  parentId: reparentFromFlippedFrame.id,
  x: 12,
  y: 18,
  rotation: 15,
};
const reparentFromFlippedState = makeNestedState(reparentFromFlippedFrame, reparentFromFlippedChild);
reparentFromFlippedState.selectionByPage[reparentFromFlippedState.activePageId] = [reparentFromFlippedChild.id];
const beforeReparentCorners = worldOrientedCornersOfLayer(reparentFromFlippedState, reparentFromFlippedChild);
const dragStartWorldMatrix = layerToWorldMatrix(reparentFromFlippedState, reparentFromFlippedChild);
const preReparentLocalTransform = {
  x: reparentFromFlippedChild.x,
  y: reparentFromFlippedChild.y,
  w: reparentFromFlippedChild.w,
  h: reparentFromFlippedChild.h,
  rotation: reparentFromFlippedChild.rotation,
  scaleX: reparentFromFlippedChild.scaleX,
  scaleY: reparentFromFlippedChild.scaleY,
};
applyReparent(reparentFromFlippedState, {
  id: "reparent-test",
  timestamp: 0,
  kind: "reparent",
  pageId: reparentFromFlippedState.activePageId,
  moves: [{
    id: reparentFromFlippedChild.id,
    fromParentId: reparentFromFlippedFrame.id,
    fromIndex: 0,
    toParentId: reparentFromFlippedState.activePageId,
    toIndex: 1,
  }],
});
const reparentedOutChild = reparentFromFlippedState.nodesById[reparentFromFlippedChild.id] as Rectangle;
const afterReparentCorners = worldOrientedCornersOfLayer(reparentFromFlippedState, reparentedOutChild);
for (let i = 0; i < beforeReparentCorners.length; i++) {
  assert(Math.abs(afterReparentCorners[i].x - beforeReparentCorners[i].x) < 0.001, "reparenting out of a rotated/flipped frame should preserve visual corner x");
  assert(Math.abs(afterReparentCorners[i].y - beforeReparentCorners[i].y) < 0.001, "reparenting out of a rotated/flipped frame should preserve visual corner y");
}
const draggedWorldMatrix = { ...dragStartWorldMatrix, e: dragStartWorldMatrix.e + 10, f: dragStartWorldMatrix.f };
const draggedLocalMatrix = multiplyMatrices(
  invertMatrix(parentToWorldMatrix(reparentFromFlippedState, reparentedOutChild.parentId)),
  draggedWorldMatrix,
);
const dragAfterReparentTransform = transformFromLocalMatrix(reparentedOutChild, draggedLocalMatrix);
applySetTransform(reparentFromFlippedState, {
  id: "drag-after-reparent-test",
  timestamp: 0,
  kind: "set_transform",
  pageId: reparentFromFlippedState.activePageId,
  ids: [reparentedOutChild.id],
  before: { [reparentedOutChild.id]: preReparentLocalTransform },
  after: { [reparentedOutChild.id]: dragAfterReparentTransform },
});
const afterDragPostReparentCorners = worldOrientedCornersOfLayer(reparentFromFlippedState, reparentedOutChild);
for (let i = 0; i < afterReparentCorners.length; i++) {
  assert(Math.abs(afterDragPostReparentCorners[i].x - (afterReparentCorners[i].x + 10)) < 0.001, "drag after reparent should preserve live rotation/flip while moving x");
  assert(Math.abs(afterDragPostReparentCorners[i].y - afterReparentCorners[i].y) < 0.001, "drag after reparent should not restore stale parent transform state");
}

const reparentDuringDragFrame: Frame = {
  ...frame,
  id: "drag-target-frame",
  parentId: "page-1",
  x: 100,
  y: 80,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  children: [],
};
const reparentedChild: Rectangle = {
  ...child,
  id: "dragged-into-frame",
  parentId: "drag-target-frame",
  x: 0,
  y: 0,
};
const reparentDuringDragState = makeNestedState(reparentDuringDragFrame, reparentedChild);
const intendedWorldOrigin = { x: 30, y: 40 };
const intendedLocalAfterParentSwitch = worldToParentLocal(reparentDuringDragState, reparentDuringDragFrame.id, intendedWorldOrigin);
reparentedChild.x = intendedLocalAfterParentSwitch.x;
reparentedChild.y = intendedLocalAfterParentSwitch.y;
const preservedOrigin = localPointToWorld(reparentDuringDragState, reparentedChild, { x: 0, y: 0 });
assert(Math.abs(preservedOrigin.x - intendedWorldOrigin.x) < 0.001, "drag move after reparent should keep using the original world origin");
assert(Math.abs(preservedOrigin.y - intendedWorldOrigin.y) < 0.001, "drag move after reparent should not jump between old/new parent spaces");

const rotatedFrame: Frame = {
  ...frame,
  id: "rotated-frame",
  parentId: "page-1",
  x: 100,
  y: 100,
  w: 100,
  h: 60,
  rotation: 90,
  scaleX: 1,
  scaleY: 1,
  children: [],
};
const rotatedFrameState = makeState(rotatedFrame);
assert(
  resolveCreationParentId(rotatedFrameState, { x: 105, y: 105 }) === "page-1",
  "creation parent hit-test must ignore the frame's old unrotated bounds",
);
assert(
  resolveCreationParentId(rotatedFrameState, { x: 150, y: 130 }) === "rotated-frame",
  "creation parent hit-test should use the rotated frame's actual visual bounds",
);

const localPoint = { x: 20, y: 10 };
const worldPoint = localToWorld(rotatedFrameState, rotatedFrame.id, localPoint);
const roundTrip = worldToParentLocal(rotatedFrameState, rotatedFrame.id, worldPoint);
assert(Math.abs(roundTrip.x - localPoint.x) < 0.001, "parent local x should round-trip through rotated parent matrix");
assert(Math.abs(roundTrip.y - localPoint.y) < 0.001, "parent local y should round-trip through rotated parent matrix");
