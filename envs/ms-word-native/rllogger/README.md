# rllogger — the three-stream logger, in C++

The instrumentation module written for the **native (Qt6 + LibreOfficeKit) Word
attempt**: a LibreOffice-buildable module (`Library_rllogger.mk` /
`Module_rllogger.mk`) linked into the binary, default-on, writing to
`~/.lo-rl-logs/<sessionId>/`.

It implements the same log contract every environment in this repo speaks
([`docs/log-contract.md`](../../../docs/log-contract.md)):

| Source file | Stream | What it captures |
|---|---|---|
| `source/RawCapture.cxx` | **raw** | every input event (pointer, key, wheel) — forensics |
| `source/SemanticEmitter.cxx` | **semantic** | every meaningful operation the engine dispatches — this is what makes a run *gradeable* |
| `source/OutcomeSnapshot.cxx` | **outcome** | live snapshot of document state + summary counts |
| `source/CommandMap.cxx` | — | UNO command → semantic operation mapping |
| `source/Persist.cxx` | — | session directory + flush policy |
| `util/rllogger-export.py` | — | export a session to the verifier's input format |

**Status: preserved, not live.** The native line was superseded by the Electron
clone in [`envs/ms-word/`](../../ms-word/) — see
[`docs/decisions/engine-rent-vs-own.md`](../../../docs/decisions/engine-rent-vs-own.md).
This module is kept because it is the reason that decision was made: writing it
is what showed that a rented engine only yields a semantic stream where you can
reach *inside* the dispatcher, which is exactly the seam a vendored engine
denies you.
