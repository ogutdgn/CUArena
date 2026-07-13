# Step 0 — Stage: launch the app and reach its workspace

## Goal

Start the target application in a clean, repeatable state and get it to its **workspace** — the
state where a user actually creates/edits the app's primary artifact. Record how you got there so
every later run replays it without thinking.

Workspace vs. launcher: template galleries, welcome screens, sign-in prompts and recent-file
lists are NOT the workspace. You are there when the main working canvas plus the primary command
surfaces (ribbon / toolbars / menus) are visible and interactive.

## How (agent decides the details)

- Find or create a launch method that lands in the workspace. Launching with a document/file
  argument often skips the launcher entirely.
- If the app needs a working file, create a **fixture** (a minimal scratch document) and store it
  under `configs/fixtures/<app>/`. **Never open the fixture itself — always launch a throwaway
  copy** from the OS temp dir. (Lesson: cloud-synced folders silently enable AutoSave in some
  apps; the original gets mutated and close-time save dialogs disappear.)
- Dismiss first-run/nag popups; note their titles for the app's config.
- Record the app's real version (the running process's binary — not the launcher stub's).
- Write the entry route (launch args and/or click steps) to
  `kb/<app>/scripts/drive/ready_route.json` so it can be replayed mechanically.

## Rules

- **R0.1** All common rules (CR1–CR8, `playbook/README.md`) bind: journal every action, never
  save/send/delete, prove claims, honest `unexplored`.
- **R0.2** The app instance must NEVER touch real user data or accounts.
- **R0.3** Never open the canonical fixture itself — always launch a throwaway copy from the OS
  temp dir. (LESSONS: cloud-synced folders silently enable AutoSave; the original mutates and
  save dialogs vanish.)

## Proof (step is done only with all of these)

1. A screenshot of the reached workspace (window-true, not a screen-region grab).
2. `ready_route.json` exists — and a **second cold launch replaying it reaches the workspace
   without any judgment calls** (journal shows the replay).
3. Version recorded in `kb/<app>/version.json`.
4. Journal contains the full launch story, including any dismissed popups.
