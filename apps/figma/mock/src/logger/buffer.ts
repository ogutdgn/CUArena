// Bounded ring buffers for raw + semantic events.
// Source: .analysis/engine-report.md §3.7, §6.6.

import type { RawEvent, SemanticEvent } from "@/types/events";

const RAW_CAPACITY = 500_000;
const SEMANTIC_CAPACITY = 10_000;

class RingBuffer<T> {
  private buf: T[] = [];
  private start = 0;
  private size = 0;
  constructor(private capacity: number) {}

  push(item: T): void {
    if (this.size < this.capacity) {
      this.buf[(this.start + this.size) % this.capacity] = item;
      this.size += 1;
    } else {
      this.buf[this.start] = item;
      this.start = (this.start + 1) % this.capacity;
    }
  }

  toArray(): T[] {
    const out: T[] = [];
    for (let i = 0; i < this.size; i++) {
      out.push(this.buf[(this.start + i) % this.capacity]);
    }
    return out;
  }

  clear(): void {
    this.buf = [];
    this.start = 0;
    this.size = 0;
  }

  get length(): number {
    return this.size;
  }

  load(items: T[]): void {
    this.clear();
    const start = Math.max(0, items.length - this.capacity);
    for (let i = start; i < items.length; i++) {
      this.push(items[i]);
    }
  }
}

class LoggerStore {
  rawEvents = new RingBuffer<RawEvent>(RAW_CAPACITY);
  semanticEvents = new RingBuffer<SemanticEvent>(SEMANTIC_CAPACITY);
  private listeners = new Set<() => void>();
  private clearHooks = new Set<() => void>();

  pushRaw(e: RawEvent): void {
    this.rawEvents.push(e);
    this.notify();
  }

  pushSemantic(e: SemanticEvent): void {
    this.semanticEvents.push(e);
    this.notify();
  }

  subscribe(fn: () => void): () => void {
    this.listeners.add(fn);
    return () => {
      this.listeners.delete(fn);
    };
  }

  private notify(): void {
    for (const fn of this.listeners) fn();
  }

  // Register a callback invoked when buffers are cleared. Used by semantic.ts
  // to reset its module-level lastEmittedRawId so a fresh session does not
  // splice raw-event ids from the previous one.
  onClear(fn: () => void): () => void {
    this.clearHooks.add(fn);
    return () => {
      this.clearHooks.delete(fn);
    };
  }

  clear(): void {
    this.rawEvents.clear();
    this.semanticEvents.clear();
    for (const fn of this.clearHooks) fn();
    this.notify();
  }

  hydrate(raw: RawEvent[], semantic: SemanticEvent[]): void {
    this.rawEvents.load(raw);
    this.semanticEvents.load(semantic);
    // Hydration represents a fresh baseline; semantic emitters should not
    // splice stale raw-id boundaries across reloads.
    for (const fn of this.clearHooks) fn();
    this.notify();
  }
}

export const logger = new LoggerStore();
export const RAW_BUFFER_CAPACITY = RAW_CAPACITY;
export const SEMANTIC_BUFFER_CAPACITY = SEMANTIC_CAPACITY;
