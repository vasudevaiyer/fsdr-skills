#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8010}"
LOG_DIR="${LOG_DIR:-$REPO_ROOT/logs}"
LOG_FILE="${LOG_FILE:-$LOG_DIR/fsdr_backend.log}"
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif [[ -x "/u01/venv/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="/u01/venv/bin/python"
else
  DEFAULT_PYTHON_BIN="$(command -v python3 || true)"
fi
PYTHON_BIN="${PYTHON_BIN:-$DEFAULT_PYTHON_BIN}"

if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  printf 'Configured Python binary is not executable: %s
' "$PYTHON_BIN" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"
cd "$REPO_ROOT"
exec "$PYTHON_BIN" -m uvicorn backend.main:app --host "$HOST" --port "$PORT"
