# Usage

Day-to-day commands for running the built fork and inspecting the
log output. For full build setup, branch flow, and conventions see
[`AGENTS.md`](../AGENTS.md). For the roadmap see
[`docs/architecture/ROADMAP.md`](architecture/ROADMAP.md).

---

## Running soffice

After a successful build (`make` in the WSL workspace), launch from
`instdir/program/`. All commands below assume cwd =
`apps/libreoffice/libreoffice-codebase/` — `cd` there first.

```sh
cd ~/cua-bench-lo/apps/libreoffice/libreoffice-codebase
instdir/program/soffice --writer            # open Writer
instdir/program/soffice --calc              # open Calc
instdir/program/soffice --impress           # open Impress
instdir/program/soffice --writer --norestore  # skip recovery dialog
```

The logger runs automatically — no env var needed.

---

## Where logs go

Each soffice run creates a session directory under a platform default:

| OS | Default base |
|---|---|
| Linux / macOS | `$HOME/.lo-rl-logs/` |
| Windows | `%LOCALAPPDATA%\lo-rl-logs\` (or `%USERPROFILE%\.lo-rl-logs\`) |
| fallback | `<system temp>/lo-rl-logs/` |

Session directory name format: `YYYY-MM-DD-HHMMSS-pid<PID>`. The
most recent 50 directories are kept; older ones are pruned at startup.

Inside one session:

```
~/.lo-rl-logs/2026-05-18-180510-pid920771/
├── raw.jsonl       # VCL events: keys, mouse, focus, etc. (append-only)
├── semantic.jsonl  # .uno:* dispatches with args, trigger, range (append-only)
└── outcome.jsonl   # Current doc state, overwritten every 250 ms
```

---

## Inspecting logs

Find the most recent session:

```sh
SESSION=$(ls -t ~/.lo-rl-logs | head -1)
echo "$SESSION"
cd ~/.lo-rl-logs/$SESSION
```

Quick event distribution:

```sh
grep -oP '"type":"[^"]+' raw.jsonl | sort | uniq -c | sort -rn
```

Live tail while soffice is still open:

```sh
tail -f semantic.jsonl
```

Pretty-print one outcome snapshot:

```sh
jq . outcome.jsonl
```

Filter semantic events by trigger (e.g. only keyboard shortcuts):

```sh
jq 'select(.trigger=="shortcut")' semantic.jsonl
```

Filter by command:

```sh
jq 'select(.name=="format_bold")' semantic.jsonl
```

---

## Consolidating to one JSON

For RL training / replay pipelines that expect one document per
session:

```sh
SESSION=$(ls -t ~/.lo-rl-logs | head -1)
rllogger/util/rllogger-export.py ~/.lo-rl-logs/$SESSION -o session.json
```

Output shape (matches cua-bench's `exportLog()`):

```json
{
  "schemaVersion": 1,
  "sessionId":     "2026-05-18-180510-pid920771",
  "exportedAt":    1779148999311,
  "raw":           [<every raw event>],
  "semantic":      [<every semantic event>],
  "outcome":       <last outcome snapshot, or null>
}
```

Tolerates a torn trailing line in raw / semantic (possible after a
hard kill of soffice) — earlier lines are unaffected.

---

## Common workflows

### Smoke test the logger in a clean directory

```sh
cd ~/lo-dev && rm -rf /tmp/rl-test
LO_RL_LOG_DIR=/tmp/rl-test instdir/program/soffice --writer --norestore
# do something in Writer, close it
SESSION=$(ls -t /tmp/rl-test | head -1)
cat /tmp/rl-test/$SESSION/semantic.jsonl
```

### Disable the logger entirely

```sh
LO_RL_LOG_DISABLE=1 instdir/program/soffice --writer
```

Zero-overhead path: no session dir, no hooks.

### Redirect logs elsewhere

```sh
LO_RL_LOG_DIR=/path/to/training-data instdir/program/soffice --writer
```

Useful for CI runs that want logs in a known location.

### Headless smoke (CI-friendly)

```sh
LO_RL_LOG_DIR=/tmp/rl-test \
  timeout 15 instdir/program/soffice --headless --terminate_after_init --norestore
# Should exit 0 with session_start + session_end in semantic.jsonl.
```

---

## Accessing logs from Windows

WSL files live at `\\wsl.localhost\Ubuntu\home\<user>\.lo-rl-logs\`
and are directly browsable from Windows Explorer or VS Code:

```powershell
code \\wsl.localhost\Ubuntu\home\ogutd\.lo-rl-logs
```

No NTFS-through-9P slowdown for reads from Windows; writes still
happen on WSL ext4.

---

## Rebuilding after a logger change

The logger lives in `rllogger/` plus a 5-line wiring patch in
`desktop/source/app/sofficemain.cxx`. Incremental builds:

```sh
make rllogger          # rebuild rllogger lib only
make rllogger desktop  # also relink libsofficeapp.so
```

`make sw sc sd` does NOT pick up logger changes — `sofficemain` is
in `desktop`, not the app modules.

---

## Ribbon iteration (no-rebuild loop)

When editing the Writer notebookbar (ribbon) — adding / removing /
renaming buttons, swapping icons, restructuring groups — **no rebuild
is needed**. The `.ui` XML is read from `instdir/` at startup. Inner
loop is ~5 seconds.

Files involved (see also [`docs/ui/ribbon-anatomy.md`](ui/ribbon-anatomy.md)):

- **Edit:** `sw/uiconfig/swriter/ui/notebookbar_cua.ui` (forked variant
  — the one we own). Do NOT edit vanilla `notebookbar.ui` directly.
- **Synced to (runtime location):** `instdir/share/config/soffice.cfg/modules/swriter/ui/notebookbar_cua.ui`
- **Sync helper:** [`apps/libreoffice/scripts/sync-ui.sh`](../scripts/sync-ui.sh)

Workflow:

```sh
# 1. Edit
$EDITOR apps/libreoffice/libreoffice-codebase/sw/uiconfig/swriter/ui/notebookbar_cua.ui

# 2. Sync source -> instdir (script handles default filename, paths)
./apps/libreoffice/scripts/sync-ui.sh

# 3. Restart soffice
pkill -f soffice 2>/dev/null
apps/libreoffice/libreoffice-codebase/instdir/program/soffice --writer --norestore
```

### Important caveat — user-profile UI shadowing

`vcl/source/control/notebookbar.cxx:32-44,86-89` — LibreOffice
checks the **user-profile** UI path *before* the shared `instdir/`
path:

```
${HOME}/.config/libreoffice/4/user/config/soffice.cfg/modules/swriter/ui/
```

If any `notebookbar*.ui` file ever ended up there (manual drop, prior
LO customization), **all your `instdir/` edits will be silently
ignored**. `sync-ui.sh` warns when this is the case:

```sh
./apps/libreoffice/scripts/sync-ui.sh --check-only
```

To resolve: `rm ~/.config/libreoffice/4/user/config/soffice.cfg/modules/swriter/ui/notebookbar*.ui`
and re-run the sync.

### Important caveat — `View → User Interface` picker overwrites CUA

The `View → User Interface` picker dialog (`cui/source/dialogs/uipickerdlg.cxx`)
is hardcoded to 7 built-in modes (Standard Toolbar / Tabbed / Single
Toolbar / Sidebar / Tabbed Compact / Groupedbar Compact / Contextual
Single) as fixed radio buttons. **Custom XCU variants (including our
CUA mode) do not appear in the picker**, and the dialog defaults its
selection to "Standard Toolbar" when the active variant isn't
recognized.

**Do not click "Apply to Writer" or "Apply to All" in this dialog
while CUA is active** — it will silently overwrite the CUA default
with whatever radio button is selected. Recovery is a removal of the
user-profile override in
`~/.config/libreoffice/4/user/registrymodifications.xcu` (any
`ActiveWriter` line) followed by a soffice restart.

To verify the currently-active Writer variant from terminal (no UI
needed):

```sh
grep ActiveWriter ~/.config/libreoffice/4/user/registrymodifications.xcu 2>/dev/null
# empty result = using XCU shipped default = notebookbar_cua.ui
# any value = user-profile override is winning
```

See [`docs/ui/README.md`](ui/README.md) §Gotcha for the full picker
discussion.

### What does NOT work in the no-rebuild loop

- **New icon SVG files**: icons are packed into `images_<theme>.zip`
  at build time; swapping a file in `icon-themes/` requires `make sw`.
  Pointing an existing button to a **different** already-installed
  icon (XML `icon-name` swap) is rebuild-free.
- **Registry / .xcu / .xcs changes** (e.g. variant registration,
  palette tuning): need `make sw` to pick up changes to
  `officecfg/`.
- **VCL paint code** (border radius, padding, focus rect): C++ change
  + rebuild.
- **In-process reload of the same file**: `SfxNotebookBar::StateMethod`
  skips reload when the active variant XML file hasn't changed name
  (`sfx2/source/notebookbar/SfxNotebookBar.cxx:465-470`). Restart is
  the reliable path; in-process you can re-switch the variant via
  Tools → Toolbar Layout to force a reload.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `instdir/program/soffice` not found | Build didn't finish or you're outside `apps/libreoffice/libreoffice-codebase/` |
| Session dir created but logs empty | Logger crashed during `initialize` — check stderr for `rllogger:` lines |
| `semantic.jsonl` has events but `trigger: "menu"` for shortcuts | Stale binary — rebuild with `make rllogger desktop` |
| `outcome.jsonl` empty in headless smoke | Expected — `--terminate_after_init` exits before the 250 ms timer fires |
| `Permission denied` running `rllogger-export.py` | `chmod +x rllogger/util/rllogger-export.py` (should already be 755 in git) |
