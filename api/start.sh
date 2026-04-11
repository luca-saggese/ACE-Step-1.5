#!/usr/bin/env bash
# Start the ACE-Step Suno-compatible REST API server.
# Run from the repository root: ./api/start.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── Load .env if present ──────────────────────────────────────────
ENV_FILE="${SCRIPT_DIR}/.env"
if [[ -f "$ENV_FILE" ]]; then
    echo "[api] Loading ${ENV_FILE}"
    # Export only lines that look like KEY=value (skip comments, blanks)
    set -a
    # shellcheck disable=SC1090
    source <(grep -v '^\s*#' "$ENV_FILE" | grep -v '^\s*$')
    set +a
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-7080}"

# ── Ensure we use the project venv ───────────────────────────────
if [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
    PYTHON="${REPO_ROOT}/.venv/bin/python"
elif command -v uv &>/dev/null; then
    PYTHON="uv run python"
else
    PYTHON="python3"
fi

echo "[api] Starting ACE-Step Suno API on http://${HOST}:${PORT}"
echo "[api] Using Python: ${PYTHON}"

cd "$SCRIPT_DIR"
exec ${PYTHON} -m uvicorn app.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --log-level "${LOG_LEVEL:-info}"
