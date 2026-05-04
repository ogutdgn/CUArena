# Log Export — Architecture Options & Decisions

This document records the approaches we considered for extracting the session log
from the test-app browser to the test-verifier, why we chose what we chose, and
how to migrate to a different approach later.

---

## The core problem

The session log lives in the **browser's sessionStorage** — it is not on disk, not
reachable by HTTP by default. To extract it, you need one of:

- **Browser-side JS** to read and deliver the data somewhere
- **CDP (Chrome DevTools Protocol)** to programmatically read sessionStorage from
  outside the browser
- **A server relay** that the browser POSTs to

---

## Approaches considered

### Option A — CDP / Playwright connect (original approach)

The export script launches Playwright and connects to a Chrome instance that was
started with `--remote-debugging-port=9222`. It reads sessionStorage directly via
the Chrome DevTools Protocol.

**Pros:**
- Works with any running Chrome, no app changes needed
- Can read sessionStorage from any tab

**Cons:**
- Chrome must be launched with a special flag (`--remote-debugging-port=9222`)
- Requires Playwright installed (`pip install playwright && playwright install chromium`)
- Developer must remember to use a special Chrome launch command
- Awkward in Docker: you'd need to start Chrome yourself with the right flags

**When to use:** Legacy / manual sessions where you cannot modify the app.

---

### Option B — Vite dev-server relay (current approach)

A Vite plugin (`devLogRelayPlugin` in `vite.config.ts`) adds a tiny in-memory
HTTP relay at `POST/GET /dev-log`. `persist.ts` posts the log payload there on
every flush (~250 ms). The export script does a plain HTTP GET.

**Pros:**
- Zero extra dependencies — pure stdlib `urllib`
- Developer uses normal Chrome, normal workflow
- Relay is guarded by `apply: "serve"` and `import.meta.env.DEV` so it never
  ships in a production build
- Simple and auditable — two small code additions

**Cons:**
- Requires `npm run dev` (Vite server) to be running
- Only holds the *latest* snapshot (not a history of snapshots)
- In-memory only — server restart loses the log
- Not suitable for Docker/CI out of the box (no Vite dev server in production)

**Current choice. Works well for the human-developer inner loop.**

---

### Option C — Test harness reads via page.evaluate (CUA / Docker)

When a CUA agent controls the browser via Playwright, the test harness already
has full CDP / `page.evaluate()` access. No extra relay needed — the harness
reads sessionStorage directly at session end.

```python
# Inside the CUA harness, after the agent finishes:
storage = page.evaluate("""() => {
    const out = {};
    for (let i = 0; i < sessionStorage.length; i++) {
        const k = sessionStorage.key(i);
        if (k) out[k] = sessionStorage.getItem(k);
    }
    return out;
}""")
# Then reconstruct_log(storage) to get the combined log object.
```

**Pros:**
- No export script, no relay, no extra server
- Works in Docker with a headless browser
- The harness owns the full lifecycle (start → interact → extract → score)

**Cons:**
- Requires the test harness itself to handle log extraction
- Not useful for a human manually testing the app

**This is the right approach for automated CUA evaluation in Docker/CI.**

---

## How to migrate

### From Option B → Option A (back to CDP)

1. Revert `vite.config.ts` — remove `devLogRelayPlugin` and its import of `Plugin`
2. Revert `persist.ts` — remove the `fetch("/dev-log", …)` block and `_sessionId`
3. Restore `scripts/requirements.txt` to `playwright>=1.40.0`
4. Restore the original `export_log.py` (it's in git history on the
   `ogutdgn/vibe-fixes` branch pre-refactor)

### From Option B → Option C (CUA harness)

1. The Vite relay can stay (it does no harm in dev)
2. In the CUA test harness, after agent completion:
   - Call `page.evaluate()` to dump sessionStorage (see snippet above)
   - Call `reconstruct_log(storage)` (copy the function from `export_log.py`)
   - Pass the log directly to the verifier, skipping `export_log.py` entirely
3. `export_log.py` becomes dev-only tooling, not part of the automated pipeline

### Adding persistence to Option B (if server restarts are a concern)

Replace the in-memory `latestLog` variable in `devLogRelayPlugin` with a file
write to `test-verifier/logs/.dev-log-latest.json`. The GET endpoint reads from
that file instead of memory. No other changes needed.

---

## Decision summary

| Context | Recommended approach |
|---|---|
| Developer inner loop (`npm run dev`) | **Option B** — Vite relay (current) |
| Automated CUA agent (Docker / CI) | **Option C** — harness reads via page.evaluate |
| Legacy / no app modifications allowed | **Option A** — CDP / Playwright connect |
