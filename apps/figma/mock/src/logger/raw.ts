// Raw DOM event capture. Source: .analysis/engine-report.md §6.

import type { RawEvent } from "@/types/events";
import { logger } from "./buffer";
import { uid } from "@/util/id";

let sessionStartedAt = 0;
let installed = false;
let lastPointerMoveFrame = 0;
let pointerMoveBuffered: PointerEvent | null = null;
let wheelAccumulator: { dx: number; dy: number; ts: number } | null = null;

function modifiersFrom(e: { altKey?: boolean; shiftKey?: boolean; ctrlKey?: boolean; metaKey?: boolean }) {
  return {
    alt: !!e.altKey,
    shift: !!e.shiftKey,
    ctrl: !!e.ctrlKey,
    meta: !!e.metaKey,
  };
}

function targetIdOf(t: EventTarget | null): string | null {
  if (!t || !(t instanceof Element)) return null;
  // Find nearest ancestor with data-id (set on chrome elements + canvas nodes)
  const el = t.closest<HTMLElement>("[data-id]");
  return el?.dataset.id ?? null;
}

function makeRaw(type: string, fields: Record<string, unknown>, target: EventTarget | null, mods: ReturnType<typeof modifiersFrom>): RawEvent {
  return {
    eventId: uid("raw"),
    type,
    timestamp: performance.now(),
    sessionTime: performance.now() - sessionStartedAt,
    fields,
    targetId: targetIdOf(target),
    modifiers: mods,
  };
}

function pushPointerMoveFrame(): void {
  lastPointerMoveFrame = 0;
  const e = pointerMoveBuffered;
  pointerMoveBuffered = null;
  if (!e) return;
  logger.pushRaw(
    makeRaw(
      "pointermove",
      {
        clientX: e.clientX,
        clientY: e.clientY,
        button: e.button,
        buttons: e.buttons,
        pointerType: e.pointerType,
        pointerId: e.pointerId,
      },
      e.target,
      modifiersFrom(e),
    ),
  );
}

function flushWheel(): void {
  if (!wheelAccumulator) return;
  const w = wheelAccumulator;
  wheelAccumulator = null;
  logger.pushRaw(
    makeRaw(
      "wheel",
      { deltaX: w.dx, deltaY: w.dy },
      null,
      { alt: false, shift: false, ctrl: false, meta: false },
    ),
  );
}

const handlers = {
  pointerdown(e: PointerEvent) {
    logger.pushRaw(
      makeRaw(
        "pointerdown",
        {
          clientX: e.clientX,
          clientY: e.clientY,
          button: e.button,
          buttons: e.buttons,
          pointerType: e.pointerType,
          pointerId: e.pointerId,
        },
        e.target,
        modifiersFrom(e),
      ),
    );
  },
  pointermove(e: PointerEvent) {
    pointerMoveBuffered = e;
    if (lastPointerMoveFrame === 0) {
      lastPointerMoveFrame = requestAnimationFrame(pushPointerMoveFrame);
    }
  },
  pointerup(e: PointerEvent) {
    logger.pushRaw(
      makeRaw(
        "pointerup",
        {
          clientX: e.clientX,
          clientY: e.clientY,
          button: e.button,
          buttons: e.buttons,
          pointerType: e.pointerType,
          pointerId: e.pointerId,
        },
        e.target,
        modifiersFrom(e),
      ),
    );
  },
  click(e: MouseEvent) {
    logger.pushRaw(
      makeRaw(
        "click",
        { clientX: e.clientX, clientY: e.clientY, button: e.button },
        e.target,
        modifiersFrom(e),
      ),
    );
  },
  dblclick(e: MouseEvent) {
    logger.pushRaw(
      makeRaw(
        "dblclick",
        { clientX: e.clientX, clientY: e.clientY, button: e.button },
        e.target,
        modifiersFrom(e),
      ),
    );
  },
  contextmenu(e: MouseEvent) {
    logger.pushRaw(
      makeRaw(
        "contextmenu",
        { clientX: e.clientX, clientY: e.clientY },
        e.target,
        modifiersFrom(e),
      ),
    );
  },
  keydown(e: KeyboardEvent) {
    logger.pushRaw(
      makeRaw(
        "keydown",
        {
          key: e.key,
          code: e.code,
          repeat: e.repeat,
          targetTag: (e.target as HTMLElement | null)?.tagName ?? null,
        },
        e.target,
        modifiersFrom(e),
      ),
    );
  },
  keyup(e: KeyboardEvent) {
    logger.pushRaw(
      makeRaw(
        "keyup",
        {
          key: e.key,
          code: e.code,
        },
        e.target,
        modifiersFrom(e),
      ),
    );
  },
  wheel(e: WheelEvent) {
    if (!wheelAccumulator) {
      wheelAccumulator = { dx: 0, dy: 0, ts: performance.now() };
      setTimeout(flushWheel, 16);
    }
    wheelAccumulator.dx += e.deltaX;
    wheelAccumulator.dy += e.deltaY;
  },
  copy(_e: ClipboardEvent) {
    logger.pushRaw(makeRaw("copy", {}, null, { alt: false, shift: false, ctrl: false, meta: false }));
  },
  cut(_e: ClipboardEvent) {
    logger.pushRaw(makeRaw("cut", {}, null, { alt: false, shift: false, ctrl: false, meta: false }));
  },
  paste(e: ClipboardEvent) {
    const kinds: string[] = [];
    if (e.clipboardData) {
      for (const item of e.clipboardData.items) kinds.push(item.kind + "/" + item.type);
    }
    logger.pushRaw(
      makeRaw("paste", { kinds }, null, { alt: false, shift: false, ctrl: false, meta: false }),
    );
  },
  resize() {
    logger.pushRaw(
      makeRaw(
        "resize",
        { innerWidth: window.innerWidth, innerHeight: window.innerHeight },
        null,
        { alt: false, shift: false, ctrl: false, meta: false },
      ),
    );
  },
  visibilitychange() {
    logger.pushRaw(
      makeRaw(
        "visibilitychange",
        { visibilityState: document.visibilityState },
        null,
        { alt: false, shift: false, ctrl: false, meta: false },
      ),
    );
  },
};

export function installRawCapture(): void {
  if (installed) return;
  installed = true;
  sessionStartedAt = performance.now();

  // Capture-phase listeners on window so we see events before any handlers stop them.
  window.addEventListener("pointerdown", handlers.pointerdown, { capture: true });
  window.addEventListener("pointermove", handlers.pointermove, { capture: true });
  window.addEventListener("pointerup", handlers.pointerup, { capture: true });
  window.addEventListener("click", handlers.click, { capture: true });
  window.addEventListener("dblclick", handlers.dblclick, { capture: true });
  window.addEventListener("contextmenu", handlers.contextmenu, { capture: true });
  window.addEventListener("keydown", handlers.keydown, { capture: true });
  window.addEventListener("keyup", handlers.keyup, { capture: true });
  window.addEventListener("wheel", handlers.wheel, { capture: true, passive: true });
  window.addEventListener("copy", handlers.copy, { capture: true });
  window.addEventListener("cut", handlers.cut, { capture: true });
  window.addEventListener("paste", handlers.paste, { capture: true });
  window.addEventListener("resize", handlers.resize);
  document.addEventListener("visibilitychange", handlers.visibilitychange);
}

export function uninstallRawCapture(): void {
  if (!installed) return;
  installed = false;
  window.removeEventListener("pointerdown", handlers.pointerdown, { capture: true } as never);
  window.removeEventListener("pointermove", handlers.pointermove, { capture: true } as never);
  window.removeEventListener("pointerup", handlers.pointerup, { capture: true } as never);
  window.removeEventListener("click", handlers.click, { capture: true } as never);
  window.removeEventListener("dblclick", handlers.dblclick, { capture: true } as never);
  window.removeEventListener("contextmenu", handlers.contextmenu, { capture: true } as never);
  window.removeEventListener("keydown", handlers.keydown, { capture: true } as never);
  window.removeEventListener("keyup", handlers.keyup, { capture: true } as never);
  window.removeEventListener("wheel", handlers.wheel, { capture: true } as never);
  window.removeEventListener("copy", handlers.copy, { capture: true } as never);
  window.removeEventListener("cut", handlers.cut, { capture: true } as never);
  window.removeEventListener("paste", handlers.paste, { capture: true } as never);
  window.removeEventListener("resize", handlers.resize);
  document.removeEventListener("visibilitychange", handlers.visibilitychange);
}

export function getMostRecentRawId(): string | null {
  const arr = logger.rawEvents.toArray();
  return arr.length > 0 ? arr[arr.length - 1].eventId : null;
}
