#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOST="0.0.0.0"
PORT="${PORT:-${2:-8010}}"
PID_FILE="$REPO_ROOT/.fsdr_backend.pid"
LOG_DIR="$REPO_ROOT/logs"
LOG_FILE="$LOG_DIR/fsdr_backend.log"
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif [[ -x "/u01/venv/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="/u01/venv/bin/python"
else
  DEFAULT_PYTHON_BIN="$(command -v python3 || true)"
fi
PYTHON_BIN="${PYTHON_BIN:-$DEFAULT_PYTHON_BIN}"

is_running() {
  if [[ ! -f "$PID_FILE" ]]; then
    return 1
  fi

  local pid
  pid="$(<"$PID_FILE")"
  if [[ -z "$pid" ]]; then
    rm -f "$PID_FILE"
    return 1
  fi

  if kill -0 "$pid" 2>/dev/null; then
    return 0
  fi

  rm -f "$PID_FILE"
  return 1
}

is_listening() {
  ss -ltn "( sport = :$PORT )" 2>/dev/null | awk 'NR > 1 {print $4}' | grep -q ":$PORT$"
}

start_backend() {
  if [[ -z "$PYTHON_BIN" ]]; then
    printf 'python3 was not found in PATH\n' >&2
    return 1
  fi

  if is_running; then
    printf 'FSDR backend is already running with PID %s\n' "$(<"$PID_FILE")"
    return 0
  fi

  mkdir -p "$LOG_DIR"

  (
    cd "$REPO_ROOT"
    nohup "$PYTHON_BIN" -m uvicorn backend.main:app --host "$HOST" --port "$PORT" >>"$LOG_FILE" 2>&1 < /dev/null &
    echo $! > "$PID_FILE"
  )

  for _ in {1..10}; do
    if is_running && is_listening; then
      printf 'FSDR backend started with PID %s\n' "$(<"$PID_FILE")"
      printf 'URL: http://%s:%s\n' "$HOST" "$PORT"
      printf 'Log: %s\n' "$LOG_FILE"
      return 0
    fi
    sleep 1
  done

  rm -f "$PID_FILE"
  printf 'FSDR backend failed to start. Check %s\n' "$LOG_FILE" >&2
  return 1
}

stop_backend() {
  if ! is_running; then
    rm -f "$PID_FILE"
    printf 'FSDR backend is not running\n'
    return 0
  fi

  local pid
  pid="$(<"$PID_FILE")"
  kill "$pid"

  for _ in {1..10}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      rm -f "$PID_FILE"
      printf 'FSDR backend stopped\n'
      return 0
    fi
    sleep 1
  done

  printf 'Process %s did not stop after 10s\n' "$pid" >&2
  return 1
}

status_backend() {
  if is_running; then
    printf 'FSDR backend is running with PID %s\n' "$(<"$PID_FILE")"
    printf 'URL: http://%s:%s\n' "$HOST" "$PORT"
    printf 'Log: %s\n' "$LOG_FILE"
    return 0
  fi

  printf 'FSDR backend is not running\n'
  return 1
}

case "${1:-start}" in
  start)
    start_backend
    ;;
  stop)
    stop_backend
    ;;
  restart)
    stop_backend || true
    start_backend
    ;;
  status)
    status_backend
    ;;
  *)
    cat <<'EOF' >&2
Usage:
  ./scripts/run-backend.sh [start|stop|restart|status] [port]

Examples:
  ./scripts/run-backend.sh
  ./scripts/run-backend.sh start 8010
  ./scripts/run-backend.sh restart 8020
EOF
    exit 1
    ;;
esac
