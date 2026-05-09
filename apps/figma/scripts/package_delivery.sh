#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_PATH="${1:-${APP_DIR}/figma-delivery1_${STAMP}.tar.gz}"

cd "${APP_DIR}"

tar -czf "${OUT_PATH}" \
  --exclude='.venv' \
  --exclude='mock/node_modules' \
  --exclude='mock/dist' \
  --exclude='mock/venv' \
  --exclude='scripts/logs' \
  --exclude='scripts/scores' \
  --exclude='app-docs/helper' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  README.md \
  requirements.txt \
  docker-compose.yml \
  docker \
  mock \
  verifier \
  scripts \
  delivery-1 \
  cua-eval

echo "Wrote package: ${OUT_PATH}"
