// Bounded ring buffer for raw events; unbounded list for semantic events.
// Source: .analysis/engine-report.md §3.7, §6.6.

import type { RawEvent, SemanticEvent } from "@/types/events";

const RAW_CAPACITY = 10000;

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
}

class LoggerStore {
  rawEvents = new RingBuffer<RawEvent>(RAW_CAPACITY);
  semanticEvents: SemanticEvent[] = [];
  // Pub-sub for the dev panel
  private listeners = new Set<() => void>();

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
    return () => this.listeners.delete(fn);
  }

  private notify(): void {
    for (const fn of this.listeners) fn();
  }

  clear(): void {
    this.rawEvents.clear();
    this.semanticEvents = [];
    this.notify();
  }
}

export const logger = new LoggerStore();
export const RAW_BUFFER_CAPACITY = RAW_CAPACITY;
