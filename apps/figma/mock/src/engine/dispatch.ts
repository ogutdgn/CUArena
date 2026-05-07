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
  const selectionAfter = [...(state.selectionByPage[tx.pageId] ?? [])];
  const focusContextAfter = state.focusContextByPage[tx.pageId] ?? null;

  pushUndoEntry({
    id: tx.id,
    timestamp: tx.startTimestamp,
    pageId: tx.pageId,
    ops: undoableOps,
    selectionBefore: [...tx.selectionBefore],
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
    state.selectionByPage[tx.pageId] = [...tx.selectionBefore];
    state.focusContextByPage[tx.pageId] = tx.focusContextBefore;
  });
}

function pushUndoEntry(entry: UndoEntry): void {
  useStore.setState((state) => {
    state.undoStack.push(entry);
    if (state.undoStack.length > UNDO_STACK_MAX) state.undoStack.shift();
    state.redoStack = [];
  });
  // Item #15 diagnostic. Lets a live repro distinguish "stack empties at N"
  // (entries consumed) from "many micro-entries flood the stack" (per-tick
  // dispatches not batched into transactions). DEV-only so prod builds stay
  // quiet.
  if (import.meta.env.DEV) {
    const ops = entry.ops.map((o) => o.kind).join(",");
    console.debug(
      `[undo] push id=${entry.id} ops=${ops} stack=${useStore.getState().undoStack.length}`,
    );
  }
}

export function dispatch(op: Op, opts: DispatchOptions = {}): void {
  if (opts.transactionId) {
    // Transaction path: snapshot was captured at openTransaction time.
    useStore.setState((state) => {
      applyOp(state as AppState, op);
    });
    const tx = openTransactions.get(opts.transactionId);
    if (tx) tx.ops.push(op);
    return;
  }

  const undoable = UNDOABLE_KINDS.has(op.kind) && !opts.skipUndo;

  // Capture pre-mutation selection/focus snapshot BEFORE applyOp so deletes
  // (which clear stale ids) and other mutations don't bury the prior state.
  let preSnapshot: {
    pageId: string;
    selectionBefore: string[];
    focusContextBefore: string | null;
  } | null = null;
  if (undoable) {
    const pre = useStore.getState();
    preSnapshot = {
      pageId: pre.activePageId,
      selectionBefore: [...(pre.selectionByPage[pre.activePageId] ?? [])],
      focusContextBefore: pre.focusContextByPage[pre.activePageId] ?? null,
    };
  }

  useStore.setState((state) => {
    applyOp(state as AppState, op);
  });

  if (undoable && preSnapshot) {
    const post = useStore.getState();
    pushUndoEntry({
      id: op.id,
      timestamp: op.timestamp,
      pageId: preSnapshot.pageId,
      ops: [op],
      selectionBefore: preSnapshot.selectionBefore,
      selectionAfter: [...(post.selectionByPage[preSnapshot.pageId] ?? [])],
      focusContextBefore: preSnapshot.focusContextBefore,
      focusContextAfter: post.focusContextByPage[preSnapshot.pageId] ?? null,
    });
  }
}

export function undo(): void {
  const state = useStore.getState();
  const entry = state.undoStack[state.undoStack.length - 1];
  if (import.meta.env.DEV) {
    console.debug(
      `[undo] invoke stack=${state.undoStack.length} entry=${entry ? entry.id : "(empty)"}`,
    );
  }
  if (!entry) return;
  useStore.setState((s) => {
    for (let i = entry.ops.length - 1; i >= 0; i--) {
      applyInverse(s as AppState, entry.ops[i]);
    }
    // Only restore selection/focus if the captured page still exists. After
    // an operation that removed a page (e.g. redo of `delete_page` reverting
    // an undo), the entry's pageId no longer points at any document page and
    // re-creating an entry would leave stale per-page state.
    if (s.document.pages.some((p) => p.id === entry.pageId)) {
      s.selectionByPage[entry.pageId] = [...entry.selectionBefore];
      s.focusContextByPage[entry.pageId] = entry.focusContextBefore;
    }
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
    // See `undo` above — skip selection restore if the captured page was
    // removed by the redone op (e.g. redo of delete_page).
    if (s.document.pages.some((p) => p.id === entry.pageId)) {
      s.selectionByPage[entry.pageId] = [...entry.selectionAfter];
      s.focusContextByPage[entry.pageId] = entry.focusContextAfter;
    }
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
