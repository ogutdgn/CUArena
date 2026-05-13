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
import { getLayerPositionValue, transformForLayerPositionValue } from "../src/engine/positionCoordinates";
import { selectionOutlineGeometry } from "../src/ui/overlays/selectionOverlayGeometry";
import { resizeSingleTransformedLayer } from "../src/engine/resizeGeometry";
import { resizeLineEndpointFromWorld } from "../src/engine/lineGeometry";
import { applyReparent, applySetTransform } from "../src/engine/ops";
import { deleteSelection } from "../src/engine/commands";
import { dispatch, makeOpId, undo } from "../src/engine/dispatch";
import { placementForPastedLayer } from "../src/engine/pastePlacement";
import { frameLabelGeometry } from "../src/engine/frameLabelsGeometry";
import { pannedViewportFromClientDelta } from "../src/engine/viewportPan";
import { textEditorCssMatrix } from "../src/ui/overlays/textEditorGeometry";
import { applyFrameContainmentForLayers, getFrameContainmentMoves } from "../src/engine/frameContainment";
import { rotateSelectionAroundVisualCenter } from "../src/engine/selectionTransforms";
import { flipSelection } from "../src/engine/transformCommands";
import { useStore, type AppState } from "../src/engine/store";
import type { Frame, Layer, Line, Page, Polygon, Rectangle, Text } from "../src/types/scene";

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
    aspectRatioLocked: false,
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

function resetStoreForRegression(state: AppState): void {
  useStore.setState((s) => {
    Object.assign(s, state);
  });
}

function withMockedBrowserStorage<T>(run: () => T): T {
  const previousWindow = (globalThis as { window?: unknown }).window;
  const previousLocalStorage = (globalThis as { localStorage?: unknown }).localStorage;
  const previousSessionStorage = (globalThis as { sessionStorage?: unknown }).sessionStorage;
  const local: Storage = {
    length: 0,
    clear() {},
    getItem() { return null; },
    key() { return null; },
    removeItem() {},
    setItem() {
      throw new DOMException("quota", "QuotaExceededError");
    },
  };
  const session = new Map<string, string>();
  const sessionStorageMock: Storage = {
    get length() { return session.size; },
    clear() { session.clear(); },
    getItem(key) { return session.get(key) ?? null; },
    key(index) { return Array.from(session.keys())[index] ?? null; },
    removeItem(key) { session.delete(key); },
    setItem(key, value) { session.set(key, value); },
  };
  const windowMock = {
    location: { href: "http://localhost:5173/?sessionId=quota-test" },
    history: { state: null, replaceState() {} },
    addEventListener() {},
  };
  (globalThis as { window?: unknown }).window = windowMock;
  (globalThis as { localStorage?: unknown }).localStorage = local;
  (globalThis as { sessionStorage?: unknown }).sessionStorage = sessionStorageMock;
  try {
    return run();
  } finally {
    (globalThis as { window?: unknown }).window = previousWindow;
    (globalThis as { localStorage?: unknown }).localStorage = previousLocalStorage;
    (globalThis as { sessionStorage?: unknown }).sessionStorage = previousSessionStorage;
  }
}

function assertClose(actual: number, expected: number, message: string): void {
  assert(Math.abs(actual - expected) < 0.001, `${message}: expected ${expected}, got ${actual}`);
}

function assertMirroredPoint(
  before: { x: number; y: number },
  after: { x: number; y: number },
  center: { x: number; y: number },
  axis: "horizontal" | "vertical",
  message: string,
): void {
  if (axis === "horizontal") {
    assertClose(after.x, 2 * center.x - before.x, `${message} x`);
    assertClose(after.y, before.y, `${message} y`);
  } else {
    assertClose(after.x, before.x, `${message} x`);
    assertClose(after.y, 2 * center.y - before.y, `${message} y`);
  }
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

withMockedBrowserStorage(() => {
  const sessionPath = require.resolve("../src/util/session.ts");
  delete require.cache[sessionPath];
  const { resolveSessionInfo } = require("../src/util/session.ts") as typeof import("../src/util/session");
  const info = resolveSessionInfo();
  assert(info.sessionId.length > 0, "session resolution should survive localStorage quota errors");
  assert(info.requestedSessionId === "quota-test", "session resolution should still report the requested id");
});

const flipVerticalState = makeState({ ...rect, id: "flip-vertical-rect", rotation: 0, scaleX: 1, scaleY: 1 });
resetStoreForRegression(flipVerticalState);
const flipVerticalBefore = localPointToWorld(useStore.getState(), useStore.getState().nodesById["flip-vertical-rect"] as Rectangle, { x: 12, y: 7 });
flipSelection("vertical", "panel_button");
const verticallyFlipped = useStore.getState().nodesById["flip-vertical-rect"] as Rectangle;
const flipVerticalAfter = localPointToWorld(useStore.getState(), verticallyFlipped, { x: 12, y: 7 });
assertMirroredPoint(flipVerticalBefore, flipVerticalAfter, { x: rect.x + rect.w / 2, y: rect.y + rect.h / 2 }, "vertical", "single-layer vertical flip should mirror across the horizontal centerline");

const flipHorizontalState = makeState({ ...rect, id: "flip-horizontal-rect", rotation: 0, scaleX: 1, scaleY: 1 });
resetStoreForRegression(flipHorizontalState);
const flipHorizontalBefore = localPointToWorld(useStore.getState(), useStore.getState().nodesById["flip-horizontal-rect"] as Rectangle, { x: 12, y: 7 });
flipSelection("horizontal", "panel_button");
const horizontallyFlipped = useStore.getState().nodesById["flip-horizontal-rect"] as Rectangle;
const flipHorizontalAfter = localPointToWorld(useStore.getState(), horizontallyFlipped, { x: 12, y: 7 });
assertMirroredPoint(flipHorizontalBefore, flipHorizontalAfter, { x: rect.x + rect.w / 2, y: rect.y + rect.h / 2 }, "horizontal", "single-layer horizontal flip should mirror across the vertical centerline");

const pointingTriangle: Polygon = {
  id: "pointing-triangle",
  parentId: "page-1",
  type: "polygon",
  name: "Pointing Triangle",
  x: 0,
  y: 0,
  w: 100,
  h: 80,
  rotation: 90,
  scaleX: 1,
  scaleY: 1,
  visible: true,
  locked: false,
  opacity: 1,
  constraints: { horizontal: "left", vertical: "top" },
  fills: [],
  strokes: [],
  effects: [],
  sides: 3,
};
const pointingState = makeState(pointingTriangle as unknown as Rectangle);
resetStoreForRegression(pointingState);
const triangleTipBefore = localPointToWorld(useStore.getState(), useStore.getState().nodesById["pointing-triangle"] as Polygon, { x: 50, y: 0 });
flipSelection("horizontal", "panel_button");
const mirroredTriangle = useStore.getState().nodesById["pointing-triangle"] as Polygon;
const triangleTipAfter = localPointToWorld(useStore.getState(), mirroredTriangle, { x: 50, y: 0 });
assertMirroredPoint(triangleTipBefore, triangleTipAfter, { x: pointingTriangle.x + pointingTriangle.w / 2, y: pointingTriangle.y + pointingTriangle.h / 2 }, "horizontal", "rotated triangle horizontal flip should move its tip to the other side");
assert(mirroredTriangle.rotation !== pointingTriangle.rotation, "rotated triangle horizontal flip should update stored rotation, not only scale");

const multiFlipLeft: Rectangle = { ...rect, id: "multi-flip-left", x: 0, y: 0, w: 50, h: 40, rotation: 0, scaleX: 1, scaleY: 1 };
const multiFlipRight: Rectangle = { ...rect, id: "multi-flip-right", x: 200, y: 0, w: 50, h: 40, rotation: 0, scaleX: 1, scaleY: 1 };
const multiHorizontalFlipState = makeMultiSelectionState([multiFlipLeft, multiFlipRight]);
resetStoreForRegression(multiHorizontalFlipState);
flipSelection("horizontal", "panel_button");
const flippedLeft = useStore.getState().nodesById["multi-flip-left"] as Rectangle;
const flippedRight = useStore.getState().nodesById["multi-flip-right"] as Rectangle;
assert(Math.abs(flippedLeft.x - 200) < 0.001, "multi-selection horizontal flip should mirror left item across selection center");
assert(Math.abs(flippedRight.x - 0) < 0.001, "multi-selection horizontal flip should mirror right item across selection center");
assert(flippedLeft.scaleX === -1 && flippedRight.scaleX === -1, "multi-selection horizontal flip should mirror each selected root");

const multiFlipTop: Rectangle = { ...rect, id: "multi-flip-top", x: 0, y: 0, w: 50, h: 40, rotation: 0, scaleX: 1, scaleY: 1 };
const multiFlipBottom: Rectangle = { ...rect, id: "multi-flip-bottom", x: 0, y: 160, w: 50, h: 40, rotation: 0, scaleX: 1, scaleY: 1 };
const multiVerticalFlipState = makeMultiSelectionState([multiFlipTop, multiFlipBottom]);
resetStoreForRegression(multiVerticalFlipState);
flipSelection("vertical", "panel_button");
const flippedTopBox = worldAABBOfLayer(useStore.getState(), useStore.getState().nodesById["multi-flip-top"] as Rectangle);
const flippedBottomBox = worldAABBOfLayer(useStore.getState(), useStore.getState().nodesById["multi-flip-bottom"] as Rectangle);
assert(Math.abs(flippedTopBox.y - 160) < 0.001, "multi-selection vertical flip should mirror top item across selection center");
assert(Math.abs(flippedBottomBox.y - 0) < 0.001, "multi-selection vertical flip should mirror bottom item across selection center");

const flipFrame: Frame = {
  id: "flip-frame",
  parentId: "page-1",
  type: "frame",
  name: "Flip Frame",
  x: 0,
  y: 0,
  w: 200,
  h: 200,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  visible: true,
  locked: false,
  opacity: 1,
  constraints: { horizontal: "left", vertical: "top" },
  fills: [],
  strokes: [],
  effects: [],
  cornerRadius: 0,
  clipsContent: true,
  children: [],
};
const flipTriangle: Polygon = {
  id: "flip-triangle",
  parentId: "flip-frame",
  type: "polygon",
  name: "Triangle",
  x: 40,
  y: 30,
  w: 80,
  h: 70,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  visible: true,
  locked: false,
  opacity: 1,
  constraints: { horizontal: "left", vertical: "top" },
  fills: [],
  strokes: [],
  effects: [],
  sides: 3,
};
flipFrame.children = [flipTriangle];
const frameAndChildFlipState = makeNestedState(flipFrame, flipTriangle as unknown as Rectangle);
frameAndChildFlipState.selectionByPage[frameAndChildFlipState.activePageId] = ["flip-frame", "flip-triangle"];
resetStoreForRegression(frameAndChildFlipState);
const framePointBefore = localPointToWorld(useStore.getState(), useStore.getState().nodesById["flip-frame"] as Frame, { x: 20, y: 30 });
flipSelection("vertical", "panel_button");
const rootFlippedFrame = useStore.getState().nodesById["flip-frame"] as Frame;
const nestedTriangle = useStore.getState().nodesById["flip-triangle"] as Polygon;
const framePointAfter = localPointToWorld(useStore.getState(), rootFlippedFrame, { x: 20, y: 30 });
assertMirroredPoint(framePointBefore, framePointAfter, { x: flipFrame.x + flipFrame.w / 2, y: flipFrame.y + flipFrame.h / 2 }, "vertical", "frame+child vertical flip should mirror the selected root frame");
assert(nestedTriangle.scaleX === 1, "frame+child vertical flip should not additionally flip the nested child horizontally");
assert(nestedTriangle.scaleY === 1, "frame+child vertical flip should not double-apply vertical flip to the nested child");
assert(nestedTriangle.rotation === 0, "frame+child vertical flip should leave the nested child's own rotation untouched");

const deleteUndoState = makeState({
  ...rect,
  id: "delete-undo-rect",
  parentId: "page-1",
  rotation: 0,
});
deleteUndoState.document.pages[0].children = [];
deleteUndoState.nodesById = { [deleteUndoState.activePageId]: deleteUndoState.document.pages[0] };
deleteUndoState.selectionByPage[deleteUndoState.activePageId] = [];
resetStoreForRegression(deleteUndoState);
dispatch({
  id: makeOpId(),
  timestamp: 0,
  kind: "create_node",
  pageId: deleteUndoState.activePageId,
  parentId: deleteUndoState.activePageId,
  indexInParent: 0,
  node: { ...rect, id: "delete-undo-rect", parentId: deleteUndoState.activePageId, rotation: 0 },
});
useStore.setState((s) => {
  s.selectionByPage[s.activePageId] = ["delete-undo-rect"];
});
deleteSelection("keyboard_canvas");
assert(useStore.getState().document.pages[0].children.length === 0, "delete should remove the created layer before undo");
undo();
assert(
  useStore.getState().document.pages[0].children.some((layer) => layer.id === "delete-undo-rect"),
  "undo after deleting a freshly created layer should restore that layer",
);

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

const panelMoveFrame: Frame = {
  ...frame,
  id: "panel-frame",
  parentId: "page-1",
  x: 0,
  y: 0,
  w: 100,
  h: 100,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  clipsContent: true,
  children: [],
};
const panelMoveChild: Rectangle = {
  ...child,
  id: "panel-child",
  parentId: "panel-frame",
  x: 20,
  y: 20,
  w: 20,
  h: 20,
};
const panelMoveState = makeNestedState(panelMoveFrame, panelMoveChild);
applySetTransform(panelMoveState, {
  id: "op-panel-move",
  timestamp: 0,
  kind: "set_transform",
  pageId: panelMoveState.activePageId,
  ids: [panelMoveChild.id],
  before: { [panelMoveChild.id]: { x: 20, y: 20, w: 20, h: 20, rotation: 0, scaleX: 1, scaleY: 1 } },
  after: { [panelMoveChild.id]: { x: 130, y: 20, w: 20, h: 20, rotation: 0, scaleX: 1, scaleY: 1 } },
});
applyFrameContainmentForLayers(panelMoveState, [panelMoveChild.id]);
const panelMovedChild = panelMoveState.nodesById[panelMoveChild.id] as Rectangle;
assert(panelMovedChild.parentId === "page-1", "panel X/Y transform should eject a frame child once overlap drops below the exit threshold");
assert(Math.abs(panelMovedChild.x - 130) < 0.001, "panel frame ejection should preserve the child's world x");
assert(Math.abs(panelMovedChild.y - 20) < 0.001, "panel frame ejection should preserve the child's world y");

const panelHalfOutFrame: Frame = { ...panelMoveFrame, id: "panel-half-frame", children: [] };
const panelHalfOutChild: Rectangle = {
  ...panelMoveChild,
  id: "panel-half-child",
  parentId: "panel-half-frame",
  x: 90,
  y: 20,
};
const panelHalfOutState = makeNestedState(panelHalfOutFrame, panelHalfOutChild);
const conservativeExitMoves = getFrameContainmentMoves(panelHalfOutState, [panelHalfOutChild.id]);
assert(conservativeExitMoves.length === 0, "canvas hysteresis should keep a half-overlapping frame child nested");
const panelExitMoves = getFrameContainmentMoves(panelHalfOutState, [panelHalfOutChild.id], { exitRatio: 0.6 });
assert(panelExitMoves.length === 1 && panelExitMoves[0].toParentId === "page-1", "panel containment should eject once less than 60% of the layer remains in the frame");

const zFrame: Frame = {
  ...frame,
  id: "z-target-frame",
  parentId: "page-1",
  x: 0,
  y: 0,
  w: 200,
  h: 160,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  clipsContent: true,
  children: [],
};
const zRect: Rectangle = {
  ...rect,
  id: "z-bottom-rect",
  parentId: "page-1",
  x: 20,
  y: 20,
  w: 120,
  h: 100,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
};
const zPoly1: Polygon = {
  ...rect,
  id: "z-poly-1",
  parentId: "page-1",
  type: "polygon",
  name: "Polygon 1",
  x: 40,
  y: 40,
  w: 50,
  h: 50,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  sides: 5,
  cornerRadius: 0,
};
const zPoly2: Polygon = {
  ...zPoly1,
  id: "z-poly-2",
  name: "Polygon 2",
  x: 80,
  y: 50,
};
const zState = makeMultiSelectionState([zFrame, zRect, zPoly1, zPoly2]);
zState.selectionByPage[zState.activePageId] = [zRect.id, zPoly1.id, zPoly2.id];
const zMoves = getFrameContainmentMoves(zState, [zRect.id, zPoly1.id, zPoly2.id]);
for (const move of zMoves) {
  applyReparent(zState, {
    id: `z-order-reparent-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zState.activePageId,
    moves: [move],
  });
}
const zFrameAfter = zState.nodesById[zFrame.id] as Frame;
assert(
  zFrameAfter.children.map((layer) => layer.id).join(",") === [zRect.id, zPoly1.id, zPoly2.id].join(","),
  "batch frame containment should preserve selected siblings' z-order inside the target frame",
);
const zShuffledFrame: Frame = { ...zFrame, id: "z-shuffled-frame", children: [] };
const zShuffledRect: Rectangle = { ...zRect, id: "z-shuffled-rect", parentId: "page-1", x: 20, y: 20 };
const zShuffledPoly1: Polygon = { ...zPoly1, id: "z-shuffled-poly-1", parentId: "page-1", x: 40, y: 40 };
const zShuffledPoly2: Polygon = { ...zPoly2, id: "z-shuffled-poly-2", parentId: "page-1", x: 80, y: 50 };
const zShuffledState = makeMultiSelectionState([zShuffledFrame, zShuffledRect, zShuffledPoly1, zShuffledPoly2]);
const zShuffledMoves = getFrameContainmentMoves(
  zShuffledState,
  [zShuffledPoly2.id, zShuffledRect.id, zShuffledPoly1.id],
  { orderIds: [zShuffledRect.id, zShuffledPoly1.id, zShuffledPoly2.id] },
);
assert(zShuffledMoves.length === 3, `shuffled containment should produce three moves; got ${zShuffledMoves.length}`);
for (const move of zShuffledMoves) {
  applyReparent(zShuffledState, {
    id: `z-shuffled-reparent-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zShuffledState.activePageId,
    moves: [move],
  });
}
const zShuffledFrameAfter = zShuffledState.nodesById[zShuffledFrame.id] as Frame;
const zShuffledActual = zShuffledFrameAfter.children.map((layer) => layer.id).join(",");
const zShuffledExpected = [zShuffledRect.id, zShuffledPoly1.id, zShuffledPoly2.id].join(",");
assert(
  zShuffledActual === zShuffledExpected,
  `batch frame containment should preserve scene z-order even when selection order is shuffled; got ${zShuffledActual}`,
);
const zPanelFrame: Frame = { ...zFrame, id: "z-panel-frame", children: [] };
const zPanelRect: Rectangle = { ...zRect, id: "z-panel-rect", parentId: "page-1", x: 20, y: 20 };
const zPanelPoly1: Polygon = { ...zPoly1, id: "z-panel-poly-1", parentId: "page-1", x: 40, y: 40 };
const zPanelPoly2: Polygon = { ...zPoly2, id: "z-panel-poly-2", parentId: "page-1", x: 80, y: 50 };
const zPanelState = makeMultiSelectionState([zPanelFrame, zPanelRect, zPanelPoly1, zPanelPoly2]);
const zPanelMoves = getFrameContainmentMoves(zPanelState, [zPanelPoly2.id, zPanelRect.id, zPanelPoly1.id]);
for (const move of zPanelMoves) {
  applyReparent(zPanelState, {
    id: `z-panel-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zPanelState.activePageId,
    moves: [move],
  });
}
const zPanelFrameAfter = zPanelState.nodesById[zPanelFrame.id] as Frame;
assert(
  zPanelFrameAfter.children.map((layer) => layer.id).join(",") === [zPanelRect.id, zPanelPoly1.id, zPanelPoly2.id].join(","),
  "panel frame containment should default to scene z-order when selection order is shuffled",
);

const zPartialFrame: Frame = { ...zFrame, id: "z-partial-frame", children: [] };
const zPartialRect: Rectangle = { ...zRect, id: "z-partial-rect", parentId: "page-1", x: 120, y: 20, w: 200, h: 120 };
const zPartialPoly1: Polygon = { ...zPoly1, id: "z-partial-poly-1", parentId: "page-1", x: 130, y: 40 };
const zPartialPoly2: Polygon = { ...zPoly2, id: "z-partial-poly-2", parentId: "page-1", x: 150, y: 70 };
const zPartialState = makeMultiSelectionState([zPartialFrame, zPartialRect, zPartialPoly1, zPartialPoly2]);
const zPartialMoves = getFrameContainmentMoves(
  zPartialState,
  [zPartialRect.id, zPartialPoly1.id, zPartialPoly2.id],
  { orderIds: [zPartialRect.id, zPartialPoly1.id, zPartialPoly2.id] },
);
assert(
  zPartialMoves.length === 0,
  "multi-selection frame containment should wait for the whole selection union instead of nesting individual shapes early",
);

const zSplitFrame: Frame = { ...zFrame, id: "z-split-frame", children: [] };
const zSplitRect: Rectangle = { ...zRect, id: "z-split-rect", parentId: "page-1", x: 20, y: 20 };
const zSplitPoly1: Polygon = { ...zPoly1, id: "z-split-poly-1", parentId: "page-1", x: 40, y: 40 };
const zSplitPoly2: Polygon = { ...zPoly2, id: "z-split-poly-2", parentId: "page-1", x: 80, y: 50 };
const zSplitState = makeMultiSelectionState([zSplitFrame, zSplitRect, zSplitPoly1, zSplitPoly2]);
const zSplitFirstMoves = getFrameContainmentMoves(zSplitState, [zSplitPoly1.id, zSplitPoly2.id]);
for (const move of zSplitFirstMoves) {
  applyReparent(zSplitState, {
    id: `z-split-first-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zSplitState.activePageId,
    moves: [move],
  });
}
const zSplitSecondMoves = getFrameContainmentMoves(
  zSplitState,
  [zSplitRect.id, zSplitPoly1.id, zSplitPoly2.id],
  { orderIds: [zSplitRect.id, zSplitPoly1.id, zSplitPoly2.id] },
);
for (const move of zSplitSecondMoves) {
  applyReparent(zSplitState, {
    id: `z-split-second-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zSplitState.activePageId,
    moves: [move],
  });
}
const zSplitFrameAfter = zSplitState.nodesById[zSplitFrame.id] as Frame;
assert(
  zSplitFrameAfter.children.map((layer) => layer.id).join(",") === [zSplitRect.id, zSplitPoly1.id, zSplitPoly2.id].join(","),
  "frame containment should preserve z-order when selected layers enter the frame across multiple nesting passes",
);
const zAroundFrame: Frame = { ...zFrame, id: "z-around-frame", children: [] };
const zAroundRect: Rectangle = { ...zRect, id: "z-around-rect", parentId: "page-1", x: 20, y: 20 };
const zAroundPoly1: Polygon = { ...zPoly1, id: "z-around-poly-1", parentId: "z-around-frame", x: 40, y: 40 };
const zAroundPoly2: Polygon = { ...zPoly2, id: "z-around-poly-2", parentId: "page-1", x: 80, y: 50 };
zAroundFrame.children = [zAroundPoly1];
const zAroundState = makeMultiSelectionState([zAroundFrame, zAroundRect, zAroundPoly2]);
zAroundState.nodesById[zAroundPoly1.id] = zAroundPoly1;
const zAroundMoves = getFrameContainmentMoves(
  zAroundState,
  [zAroundRect.id, zAroundPoly1.id, zAroundPoly2.id],
  { orderIds: [zAroundRect.id, zAroundPoly1.id, zAroundPoly2.id] },
);
for (const move of zAroundMoves) {
  applyReparent(zAroundState, {
    id: `z-around-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zAroundState.activePageId,
    moves: [move],
  });
}
const zAroundFrameAfter = zAroundState.nodesById[zAroundFrame.id] as Frame;
assert(
  zAroundFrameAfter.children.map((layer) => layer.id).join(",") === [zAroundRect.id, zAroundPoly1.id, zAroundPoly2.id].join(","),
  "frame containment should adjust later toIndex values when inserting around an already-nested selected sibling",
);
const zMixedFrame: Frame = { ...zFrame, id: "z-mixed-frame", children: [] };
const zMixedLow: Rectangle = { ...zRect, id: "z-mixed-low", parentId: "page-1", x: 20, y: 20 };
const zMixedMid: Polygon = { ...zPoly1, id: "z-mixed-mid", parentId: "z-mixed-frame", x: -120, y: -120 };
const zMixedHigh: Polygon = { ...zPoly2, id: "z-mixed-high", parentId: "page-1", x: 80, y: 50 };
const zMixedNeutral: Rectangle = { ...zRect, id: "z-mixed-neutral", parentId: "z-mixed-frame", x: 130, y: 20, w: 20, h: 20 };
zMixedFrame.children = [zMixedMid, zMixedNeutral];
const zMixedState = makeMultiSelectionState([zMixedFrame, zMixedLow, zMixedHigh]);
zMixedState.nodesById[zMixedMid.id] = zMixedMid;
zMixedState.nodesById[zMixedNeutral.id] = zMixedNeutral;
const zMixedMoves = getFrameContainmentMoves(
  zMixedState,
  [zMixedMid.id, zMixedLow.id, zMixedHigh.id],
  { orderIds: [zMixedLow.id, zMixedMid.id, zMixedHigh.id] },
);
for (const move of zMixedMoves) {
  applyReparent(zMixedState, {
    id: `z-mixed-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zMixedState.activePageId,
    moves: [move],
  });
}
const zMixedFrameAfter = zMixedState.nodesById[zMixedFrame.id] as Frame;
assert(
  zMixedFrameAfter.children.map((layer) => layer.id).join(",") === [zMixedLow.id, zMixedNeutral.id, zMixedHigh.id].join(","),
  "frame containment should not anchor inserts against selected siblings that are leaving the same frame",
);
const zSingleMixedFrame: Frame = { ...zFrame, id: "z-single-mixed-frame", children: [] };
const zSingleMixedMid: Polygon = { ...zPoly1, id: "z-single-mixed-mid", parentId: "z-single-mixed-frame", x: -120, y: -120 };
const zSingleMixedHigh: Polygon = { ...zPoly2, id: "z-single-mixed-high", parentId: "page-1", x: 80, y: 50 };
const zSingleMixedNeutral: Rectangle = { ...zRect, id: "z-single-mixed-neutral", parentId: "z-single-mixed-frame", x: 130, y: 20, w: 20, h: 20 };
zSingleMixedFrame.children = [zSingleMixedMid, zSingleMixedNeutral];
const zSingleMixedState = makeMultiSelectionState([zSingleMixedFrame, zSingleMixedHigh]);
zSingleMixedState.nodesById[zSingleMixedMid.id] = zSingleMixedMid;
zSingleMixedState.nodesById[zSingleMixedNeutral.id] = zSingleMixedNeutral;
const zSingleMixedMoves = getFrameContainmentMoves(
  zSingleMixedState,
  [zSingleMixedHigh.id, zSingleMixedMid.id],
  { orderIds: [zSingleMixedMid.id, zSingleMixedHigh.id] },
);
for (const move of zSingleMixedMoves) {
  applyReparent(zSingleMixedState, {
    id: `z-single-mixed-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zSingleMixedState.activePageId,
    moves: [move],
  });
}
const zSingleMixedFrameAfter = zSingleMixedState.nodesById[zSingleMixedFrame.id] as Frame;
assert(
  zSingleMixedFrameAfter.children.map((layer) => layer.id).join(",") === [zSingleMixedNeutral.id, zSingleMixedHigh.id].join(","),
  "single frame insert should remain stable when a selected target sibling leaves before or after it",
);
const zSingleMixedExitFirstFrame: Frame = { ...zFrame, id: "z-single-mixed-exit-first-frame", children: [] };
const zSingleMixedExitFirstMid: Polygon = {
  ...zPoly1,
  id: "z-single-mixed-exit-first-mid",
  parentId: "z-single-mixed-exit-first-frame",
  x: -120,
  y: -120,
};
const zSingleMixedExitFirstHigh: Polygon = { ...zPoly2, id: "z-single-mixed-exit-first-high", parentId: "page-1", x: 80, y: 50 };
const zSingleMixedExitFirstNeutral: Rectangle = {
  ...zRect,
  id: "z-single-mixed-exit-first-neutral",
  parentId: "z-single-mixed-exit-first-frame",
  x: 130,
  y: 20,
  w: 20,
  h: 20,
};
zSingleMixedExitFirstFrame.children = [zSingleMixedExitFirstMid, zSingleMixedExitFirstNeutral];
const zSingleMixedExitFirstState = makeMultiSelectionState([zSingleMixedExitFirstFrame, zSingleMixedExitFirstHigh]);
zSingleMixedExitFirstState.nodesById[zSingleMixedExitFirstMid.id] = zSingleMixedExitFirstMid;
zSingleMixedExitFirstState.nodesById[zSingleMixedExitFirstNeutral.id] = zSingleMixedExitFirstNeutral;
const zSingleMixedExitFirstMoves = getFrameContainmentMoves(
  zSingleMixedExitFirstState,
  [zSingleMixedExitFirstMid.id, zSingleMixedExitFirstHigh.id],
  { orderIds: [zSingleMixedExitFirstMid.id, zSingleMixedExitFirstHigh.id] },
);
assert(
  zSingleMixedExitFirstMoves[0]?.id === zSingleMixedExitFirstHigh.id,
  "frame containment should process frame-entering moves before selected siblings exit that same frame",
);
for (const move of zSingleMixedExitFirstMoves) {
  applyReparent(zSingleMixedExitFirstState, {
    id: `z-single-mixed-exit-first-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zSingleMixedExitFirstState.activePageId,
    moves: [move],
  });
}
const zSingleMixedExitFirstFrameAfter = zSingleMixedExitFirstState.nodesById[zSingleMixedExitFirstFrame.id] as Frame;
assert(
  zSingleMixedExitFirstFrameAfter.children.map((layer) => layer.id).join(",") === [zSingleMixedExitFirstNeutral.id, zSingleMixedExitFirstHigh.id].join(","),
  "single frame insert should preserve z-order when the exiting selected child is processed first",
);
const zExitFallbackFrame: Frame = { ...zFrame, id: "z-exit-fallback-frame", parentId: "page-1", x: 0, y: 0, children: [] };
const zExitFallbackLow: Rectangle = { ...zRect, id: "z-exit-fallback-low", parentId: "z-exit-fallback-frame", x: -120, y: -120 };
const zExitFallbackNeutral: Rectangle = { ...zRect, id: "z-exit-fallback-neutral", parentId: "page-1", x: 240, y: 20, w: 20, h: 20 };
const zExitFallbackHigh: Polygon = { ...zPoly2, id: "z-exit-fallback-high", parentId: "page-1", x: 280, y: 50 };
zExitFallbackFrame.children = [zExitFallbackLow];
const zExitFallbackState = makeMultiSelectionState([zExitFallbackFrame, zExitFallbackNeutral, zExitFallbackHigh]);
zExitFallbackState.nodesById[zExitFallbackLow.id] = zExitFallbackLow;
const zExitFallbackMoves = getFrameContainmentMoves(
  zExitFallbackState,
  [zExitFallbackLow.id, zExitFallbackHigh.id],
  { orderIds: [zExitFallbackLow.id, zExitFallbackHigh.id] },
);
for (const move of zExitFallbackMoves) {
  applyReparent(zExitFallbackState, {
    id: `z-exit-fallback-${move.id}`,
    timestamp: 0,
    kind: "reparent",
    pageId: zExitFallbackState.activePageId,
    moves: [move],
  });
}
assert(
  zExitFallbackState.document.pages[0].children.map((layer) => layer.id).join(",") ===
    [zExitFallbackFrame.id, zExitFallbackLow.id, zExitFallbackNeutral.id, zExitFallbackHigh.id].join(","),
  "frame exit should preserve fallback position around unrelated siblings when selected order is already satisfied",
);

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

const rotateGroupTop: Rectangle = { ...rect, id: "rotate-group-top", x: 0, y: 0, w: 100, h: 50, rotation: 0, scaleX: 1, scaleY: 1 };
const rotateGroupBottom: Rectangle = { ...rect, id: "rotate-group-bottom", x: 0, y: 150, w: 100, h: 50, rotation: 0, scaleX: 1, scaleY: 1 };
const rotateGroupState = makeMultiSelectionState([rotateGroupTop, rotateGroupBottom]);
const rotateGroupBeforeTopCenter = localPointToWorld(rotateGroupState, rotateGroupTop, { x: 50, y: 25 });
const rotateGroupBeforeBottomCenter = localPointToWorld(rotateGroupState, rotateGroupBottom, { x: 50, y: 25 });
const rotateGroupAfter = rotateSelectionAroundVisualCenter(rotateGroupState, [rotateGroupTop, rotateGroupBottom], 90);
applySetTransform(rotateGroupState, {
  id: "rotate-group-op",
  timestamp: 0,
  kind: "set_transform",
  pageId: rotateGroupState.activePageId,
  ids: [rotateGroupTop.id, rotateGroupBottom.id],
  before: {},
  after: rotateGroupAfter,
});
const rotateGroupTopAfter = rotateGroupState.nodesById[rotateGroupTop.id] as Rectangle;
const rotateGroupBottomAfter = rotateGroupState.nodesById[rotateGroupBottom.id] as Rectangle;
const rotateGroupAfterTopCenter = localPointToWorld(rotateGroupState, rotateGroupTopAfter, { x: 50, y: 25 });
const rotateGroupAfterBottomCenter = localPointToWorld(rotateGroupState, rotateGroupBottomAfter, { x: 50, y: 25 });
assert(Math.abs(rotateGroupBeforeTopCenter.x - rotateGroupAfterTopCenter.x) > 1, "multi-selection rotation should move the first layer around the group center");
assert(Math.abs(rotateGroupBeforeBottomCenter.x - rotateGroupAfterBottomCenter.x) > 1, "multi-selection rotation should move the second layer around the group center");
assert(Math.abs(rotateGroupAfterTopCenter.y - rotateGroupAfterBottomCenter.y) < 0.001, "multi-selection rotation should turn the vertical stack into a horizontal stack");
assert(rotateGroupTopAfter.rotation === 90 && rotateGroupBottomAfter.rotation === 90, "multi-selection rotation should still rotate each selected layer by the requested angle");

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

const topLevelPositionRect: Rectangle = {
  ...rect,
  id: "top-level-position",
  parentId: "page-1",
  x: 10,
  y: 20,
  w: 100,
  h: 50,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
};
const topLevelPositionState = makeState(topLevelPositionRect);
const topLevelPosition = getLayerPositionValue(topLevelPositionState, topLevelPositionRect);
assert(topLevelPosition.x === 60 && topLevelPosition.y === 45, "top-level Position X/Y should describe the layer center relative to the page origin");
const centeredTopLevel = transformForLayerPositionValue(topLevelPositionState, topLevelPositionRect, { x: 0, y: 0 });
assert(centeredTopLevel.x === -50 && centeredTopLevel.y === -25, "top-level Position 0,0 should place the layer center on the page origin");

const positionFrame: Frame = {
  ...frame,
  id: "position-frame",
  parentId: "page-1",
  x: 100,
  y: 100,
  w: 200,
  h: 100,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  children: [],
};
const positionChild: Rectangle = {
  ...child,
  id: "position-child",
  parentId: positionFrame.id,
  x: 0,
  y: 0,
  w: 20,
  h: 20,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
};
const positionNestedState = makeNestedState(positionFrame, positionChild);
const nestedPosition = getLayerPositionValue(positionNestedState, positionChild);
assert(nestedPosition.x === -90 && nestedPosition.y === -40, "nested Position X/Y should be relative to the parent visual center");
const centeredNested = transformForLayerPositionValue(positionNestedState, positionChild, { x: 0, y: 0 });
assert(centeredNested.x === 90 && centeredNested.y === 40, "nested Position 0,0 should place the child center on the parent center");
const resizedCenterPreserved = transformForLayerPositionValue(positionNestedState, positionChild, nestedPosition, { w: 40, h: 30 });
assert(resizedCenterPreserved.x === -10 && resizedCenterPreserved.y === -5, "panel size changes should preserve the center-origin Position value");

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
const textMatrix = textEditorCssMatrix(textState, nestedText, { x: 0, y: 0, zoom: 1 }, { left: 0, top: 0, width: 1000, height: 800 });
assert(textMatrix.endsWith(", 540, 455)"), "text editor overlay should use centered viewport and parent-aware world position while editing inside a frame");

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

const pasteFrame: Frame = {
  ...frame,
  id: "paste-frame",
  parentId: "page-1",
  x: 200,
  y: 140,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  children: [],
};
const pasteSource: Rectangle = {
  ...child,
  id: "paste-source",
  parentId: pasteFrame.id,
  x: 24,
  y: 32,
};
const pasteState = makeNestedState(pasteFrame, pasteSource);
pasteState.focusContextByPage[pasteState.activePageId] = null;
const pastedPlacement = placementForPastedLayer(pasteState, pasteSource, { dx: 10, dy: 10 });
assert(pastedPlacement.parentId === pasteFrame.id, "paste should keep a copied frame child inside the same frame");
assert(pastedPlacement.placement === "into_frame", "paste into an existing frame should log into_frame placement");
assert(pastedPlacement.x === pasteSource.x + 10, "same-frame paste should keep the normal x offset in frame-local space");
assert(pastedPlacement.y === pasteSource.y + 10, "same-frame paste should keep the normal y offset in frame-local space");
