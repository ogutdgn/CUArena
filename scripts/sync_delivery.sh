#!/usr/bin/env bash
# Sync delivery-1/task_NN/verifier.py from test-verifier/tasks/task_NN_*.py
# Run from repo root.

set -euo pipefail
cd "$(dirname "$0")/.."

count=0
for f in test-verifier/tasks/task_*.py; do
  base=$(basename "$f")
  [[ "$base" == "__init__.py" ]] && continue
  nn=$(echo "$base" | sed -E 's/task_([0-9]+)_.*/\1/')
  dst="delivery-1/task_${nn}/verifier.py"
  if [[ ! -d "delivery-1/task_${nn}" ]]; then
    echo "SKIP: no delivery-1/task_${nn}/ directory"
    continue
  fi
  cp "$f" "$dst"
  count=$((count + 1))
done
echo "synced $count verifiers"
