#!/usr/bin/env bash
# Sync a Writer .ui file from the source tree to the built instdir/.
# Default target is notebookbar_cua.ui (the CUA variant forked in Phase 1.3).
# After sync: restart soffice to see the change. No rebuild needed for
# layout / label / icon-name edits.
#
# Run from anywhere — paths resolve relative to this script.
#
# Usage:
#   sync-ui.sh                 # sync notebookbar_cua.ui
#   sync-ui.sh <ui-file>       # sync a specific Writer UI file
#   sync-ui.sh --check-only    # only check for user-profile shadowing
#
# WSL caveat: this is bash, designed to run inside WSL alongside the build.
# Owner build path: ~/lo-dev/apps/libreoffice/... (separate from cua-bench
# OneDrive checkout). Either checkout works as long as the build's instdir
# exists.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LO_DIR="$APP_DIR/libreoffice-codebase"

SRC_DIR="$LO_DIR/sw/uiconfig/swriter/ui"
DEST_DIR="$LO_DIR/instdir/share/config/soffice.cfg/modules/swriter/ui"
USER_DIR="${HOME}/.config/libreoffice/4/user/config/soffice.cfg/modules/swriter/ui"

CHECK_ONLY=0
UI_FILE="notebookbar_cua.ui"

for arg in "$@"; do
  case "$arg" in
    --check-only) CHECK_ONLY=1 ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \?//'
      exit 0 ;;
    -*)
      echo "Unknown flag: $arg" >&2
      echo "Run with --help for usage." >&2
      exit 2 ;;
    *) UI_FILE="$arg" ;;
  esac
done

# --- User-profile shadow check ---
# vcl/source/control/notebookbar.cxx:32-44,86-89 — the runtime checks the
# user-profile UI path BEFORE the shared instdir path. Any notebookbar*.ui
# left in the user profile (e.g. from a manual customization) will silently
# shadow our instdir copy. This is the single most common reason "edits
# don't show up".

shadow_found=0
if [ -d "$USER_DIR" ]; then
  shopt -s nullglob
  shadows=( "$USER_DIR"/notebookbar*.ui )
  shopt -u nullglob
  if [ ${#shadows[@]} -gt 0 ]; then
    shadow_found=1
    echo "WARNING: user-profile notebookbar UI(s) will SHADOW your instdir edits:"
    for f in "${shadows[@]}"; do echo "  - $f"; done
    echo "  -> LibreOffice loads the user-profile copy BEFORE instdir."
    echo "  -> To resolve: rm '$USER_DIR'/notebookbar*.ui"
    echo
  fi
fi

if [ "$CHECK_ONLY" = "1" ]; then
  if [ "$shadow_found" = "1" ]; then
    exit 1
  fi
  echo "OK: no user-profile notebookbar UI shadow detected."
  exit 0
fi

# --- Sync ---
if [ ! -f "$SRC_DIR/$UI_FILE" ]; then
  echo "Error: source file not found: $SRC_DIR/$UI_FILE" >&2
  exit 1
fi

if [ ! -d "$DEST_DIR" ]; then
  echo "Error: instdir dest not found: $DEST_DIR" >&2
  echo "Has 'make sw' run successfully in $LO_DIR ?" >&2
  exit 1
fi

cp -v "$SRC_DIR/$UI_FILE" "$DEST_DIR/$UI_FILE"
echo
echo "Done. Restart soffice to see the change:"
echo "  pkill -f soffice 2>/dev/null; \"$LO_DIR/instdir/program/soffice\" --writer --norestore"
