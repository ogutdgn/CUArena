// Central op dispatcher. Wraps every state mutation so Immer can produce a
// new draft per dispatch. Maintains undo/redo stacks and transaction scope.

import { useStore, type AppState, type UndoEntry } from "./store";
import { applyOp, applyInverse } from "./ops";
import { UNDOABLE_KINDS, type Op } from "@/types/ops";
import { uid } from "@/util/id";
import { emitSemantic } from "@/logger/semantic";

const UNDO_STACK_MAX = 1000;

interface DispatchOptions {
  transactionId?: string;
  skipUndo?: boolean;
}

interface OpenTransaction {
  id: string;
  startTimestamp: number;
  ops: Op[];
  selectionBefore: string[];
  focusContextBefore: string | null;
  pageId: string;
}

const openTransactions = new Map<string, OpenTransaction>();

export function openTransaction(): string {
  const state = useStore.getState();
  const tid = uid("tx");
  openTransactions.set(tid, {
    id: tid,
    startTimestamp: performance.now(),
    ops: [],
    selectionBefore: [...(state.selectionByPage[state.activePageId] ?? [])],
    focusContextBefore: state.focusContextByPage[state.activePageId] ?? null,
    pageId: state.activePageId,
  });
  return tid;
}

export function commitTransaction(tid: string): void {
  const tx = openTransactions.get(tid);
  if (!tx) return;
  openTransactions.delete(tid);
  if (tx.ops.length === 0) return;

  const undoableOps = tx.ops.filter((op) => UNDOABLE_KINDS.has(op.kind));
  if (undoableOps.length === 0) return;

  const state = useStore.getState();
  const selectionAfter = [...(state.selectionByPage[state.activePageId] ?? [])];
  const focusContextAfter = state.focusContextByPage[state.activePageId] ?? null;

  pushUndoEntry({
    id: tx.id,
    timestamp: tx.startTimestamp,
    ops: undoableOps,
    selectionBefore: tx.selectionBefore,
    selectionAfter,
    focusContextBefore: tx.focusContextBefore,
    focusContextAfter,
  });
}

export function abortTransaction(tid: string): void {
  const tx = openTransactions.get(tid);
  if (!tx) return;
  openTransactions.delete(tid);
  if (tx.ops.length === 0) return;
  useStore.setState((state) => {
    for (let i = tx.ops.length - 1; i >= 0; i--) {
      applyInverse(state as AppState, tx.ops[i]);
    }
    state.selectionByPage[state.activePageId] = tx.selectionBefore;
    state.focusContextByPage[state.activePageId] = tx.focusContextBefore;
  });
}

function pushUndoEntry(entry: UndoEntry): void {
  useStore.setState((state) => {
    state.undoStack.push(entry);
    if (state.undoStack.length > UNDO_STACK_MAX) state.undoStack.shift();
    state.redoStack = [];
  });
}

export function dispatch(op: Op, opts: DispatchOptions = {}): void {
  // Apply to draft.
  useStore.setState((state) => {
    applyOp(state as AppState, op);
  });

  if (opts.transactionId) {
    const tx = openTransactions.get(opts.transactionId);
    if (tx) tx.ops.push(op);
  } else if (UNDOABLE_KINDS.has(op.kind) && !opts.skipUndo) {
    const state = useStore.getState();
    pushUndoEntry({
      id: op.id,
      timestamp: op.timestamp,
      ops: [op],
      selectionBefore: state.selectionByPage[state.activePageId] ?? [],
      selectionAfter: state.selectionByPage[state.activePageId] ?? [],
      focusContextBefore: state.focusContextByPage[state.activePageId] ?? null,
      focusContextAfter: state.focusContextByPage[state.activePageId] ?? null,
    });
  }
}

export function undo(): void {
  const state = useStore.getState();
  const entry = state.undoStack[state.undoStack.length - 1];
  if (!entry) return;
  useStore.setState((s) => {
    for (let i = entry.ops.length - 1; i >= 0; i--) {
      applyInverse(s as AppState, entry.ops[i]);
    }
    s.selectionByPage[s.activePageId] = [...entry.selectionBefore];
    s.focusContextByPage[s.activePageId] = entry.focusContextBefore;
    s.undoStack.pop();
    s.redoStack.push(entry);
  });
  emitSemantic({
    name: "undo",
    revertedOpKind: entry.ops[entry.ops.length - 1]?.kind ?? "",
    revertedOpId: entry.id,
  });
}

export function redo(): void {
  const state = useStore.getState();
  const entry = state.redoStack[state.redoStack.length - 1];
  if (!entry) return;
  useStore.setState((s) => {
    for (const op of entry.ops) {
      applyOp(s as AppState, op);
    }
    s.selectionByPage[s.activePageId] = [...entry.selectionAfter];
    s.focusContextByPage[s.activePageId] = entry.focusContextAfter;
    s.redoStack.pop();
    s.undoStack.push(entry);
  });
  emitSemantic({
    name: "redo",
    reappliedOpKind: entry.ops[entry.ops.length - 1]?.kind ?? "",
    reappliedOpId: entry.id,
  });
}

export function canUndo(): boolean {
  return useStore.getState().undoStack.length > 0;
}

export function canRedo(): boolean {
  return useStore.getState().redoStack.length > 0;
}

export function makeOpId(): string {
  return uid("op");
}
