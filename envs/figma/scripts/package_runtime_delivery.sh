#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${1:-${APP_DIR}/runtime-delivery_${STAMP}}"
OUT_BASENAME="$(basename "${OUT_DIR}")"

MOCK_IMAGE="${FIGMA_MOCK_IMAGE:-cua-bench-figma-mock:delivery1}"
VERIFIER_IMAGE="${FIGMA_VERIFIER_IMAGE:-cua-bench-figma-verifier:delivery1}"
HOST_PORT="${FIGMA_HOST_PORT:-5173}"

echo "Preparing runtime-only delivery package..."
echo "  app dir   : ${APP_DIR}"
echo "  out dir   : ${OUT_DIR}"
echo "  mock img  : ${MOCK_IMAGE}"
echo "  verifier  : ${VERIFIER_IMAGE}"
echo "  host port : ${HOST_PORT}"

mkdir -p "${OUT_DIR}/images" "${OUT_DIR}/out"

echo "Building runtime images..."
docker build -t "${MOCK_IMAGE}" \
  -f "${APP_DIR}/docker/Dockerfile.mock" \
  "${APP_DIR}/../.."

docker build -t "${VERIFIER_IMAGE}" \
  -f "${APP_DIR}/docker/Dockerfile.verifier" \
  "${APP_DIR}/../.."

echo "Exporting images..."
docker save -o "${OUT_DIR}/images/mock_image.tar" "${MOCK_IMAGE}"
docker save -o "${OUT_DIR}/images/verifier_image.tar" "${VERIFIER_IMAGE}"

cp "${APP_DIR}/docker-compose.runtime.yml" "${OUT_DIR}/docker-compose.yml"
cp "${APP_DIR}/delivery-1/RUNTIME_ONLY_DELIVERY.md" "${OUT_DIR}/README.md"

cat > "${OUT_DIR}/.env" <<EOF
FIGMA_MOCK_IMAGE=${MOCK_IMAGE}
FIGMA_VERIFIER_IMAGE=${VERIFIER_IMAGE}
FIGMA_HOST_PORT=${HOST_PORT}
EOF

cat > "${OUT_DIR}/run_host.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SELF_DIR}"

cmd="${1:-help}"
shift || true

case "${cmd}" in
  load-images)
    docker load -i images/mock_image.tar
    docker load -i images/verifier_image.tar
    ;;
  up)
    docker compose up -d mock
    ;;
  down)
    docker compose down
    ;;
  score)
    task="${1:-task_01}"
    shift || true
    docker compose run --rm verifier python3 scripts/run_task.py --host mock "${task}" "$@"
    ;;
  export-log)
    task="${1:-}"
    shift || true
    if [[ -n "${task}" ]]; then
      docker compose run --rm verifier python3 scripts/run_task.py --host mock export-log "${task}" "$@"
    else
      docker compose run --rm verifier python3 scripts/run_task.py --host mock export-log "$@"
    fi
    ;;
  help|*)
    cat <<USAGE
Usage:
  ./run_host.sh load-images
  ./run_host.sh up
  ./run_host.sh score task_01 [--session-id <uuid>]
  ./run_host.sh export-log [task_01] [--session-id <uuid>]
  ./run_host.sh down
USAGE
    ;;
esac
EOF
chmod +x "${OUT_DIR}/run_host.sh"

echo "Creating compressed archive..."
(
  cd "$(dirname "${OUT_DIR}")"
  tar -czf "${OUT_BASENAME}.tar.gz" "${OUT_BASENAME}"
)

echo
echo "Runtime-only package ready:"
echo "  folder : ${OUT_DIR}"
echo "  tar.gz : ${OUT_DIR}.tar.gz"
echo
echo "Client flow:"
echo "  1) cd ${OUT_BASENAME}"
echo "  2) ./run_host.sh load-images"
echo "  3) ./run_host.sh up"
echo "  4) open http://127.0.0.1:${HOST_PORT}"
echo "  5) ./run_host.sh score task_01"
echo "Outputs are written to: ${OUT_BASENAME}/out"
