#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOST="0.0.0.0"
PORT="${PORT:-${2:-8010}}"
PID_FILE="$REPO_ROOT/.fsdr_backend.pid"
ENV_FILE="$REPO_ROOT/.fsdr-backend.env"
LOG_DIR="$REPO_ROOT/logs"
LOG_FILE="$LOG_DIR/fsdr_backend.log"
SERVICE_NAME="fsdr-backend.service"
SERVICE_SOURCE="$REPO_ROOT/fsdr-backend.service"
SERVICE_TARGET="/etc/systemd/system/$SERVICE_NAME"
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif [[ -x "/u01/venv/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="/u01/venv/bin/python"
else
  DEFAULT_PYTHON_BIN="$(command -v python3 || true)"
fi
PYTHON_BIN="${PYTHON_BIN:-$DEFAULT_PYTHON_BIN}"
AI_CLASSIFIER_ENABLED="${AI_CLASSIFIER_ENABLED:-true}"
AI_CLASSIFIER_TIMEOUT_SECONDS="${AI_CLASSIFIER_TIMEOUT_SECONDS:-10}"
AI_CLASSIFIER_OCI_GENAI_ENDPOINT="${AI_CLASSIFIER_OCI_GENAI_ENDPOINT:-https://inference.generativeai.us-chicago-1.oci.oraclecloud.com}"
AI_CLASSIFIER_OCI_MODEL_ID="${AI_CLASSIFIER_OCI_MODEL_ID:-cohere.command-a-03-2025}"
AI_CLASSIFIER_OCI_COMPARTMENT_ID="${AI_CLASSIFIER_OCI_COMPARTMENT_ID:-ocid1.compartment.oc1..aaaaaaaag6bo6trbwxybykokjrb247qosteeo7gt632yczn5kmoqeu4oe6aq}"
OCI_CONFIG_PATH="${OCI_CONFIG_PATH:-/home/opc/.oci/config}"
OCI_PROFILE="${OCI_PROFILE:-DEFAULT}"
SUDO=""
if [[ ${EUID} -ne 0 ]]; then
  SUDO="sudo"
fi

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

systemd_available() {
  command -v systemctl >/dev/null 2>&1 && [[ -d /run/systemd/system ]]
}

service_installed() {
  [[ -f "$SERVICE_TARGET" ]]
}

write_env_file() {
  mkdir -p "$LOG_DIR"
  cat > "$ENV_FILE" <<EOF
HOST=$HOST
PORT=$PORT
PYTHON_BIN=$PYTHON_BIN
LOG_DIR=$LOG_DIR
LOG_FILE=$LOG_FILE
AI_CLASSIFIER_ENABLED=$AI_CLASSIFIER_ENABLED
AI_CLASSIFIER_TIMEOUT_SECONDS=$AI_CLASSIFIER_TIMEOUT_SECONDS
AI_CLASSIFIER_OCI_GENAI_ENDPOINT=$AI_CLASSIFIER_OCI_GENAI_ENDPOINT
AI_CLASSIFIER_OCI_MODEL_ID=$AI_CLASSIFIER_OCI_MODEL_ID
AI_CLASSIFIER_OCI_COMPARTMENT_ID=$AI_CLASSIFIER_OCI_COMPARTMENT_ID
OCI_CONFIG_PATH=$OCI_CONFIG_PATH
OCI_PROFILE=$OCI_PROFILE
EOF
}

install_service() {
  if ! systemd_available; then
    printf 'systemd is not available on this host
' >&2
    return 1
  fi

  if [[ ! -f "$SERVICE_SOURCE" ]]; then
    printf 'Service file not found: %s
' "$SERVICE_SOURCE" >&2
    return 1
  fi

  if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
    printf 'Configured Python binary is not executable: %s
' "$PYTHON_BIN" >&2
    return 1
  fi

  write_env_file
  $SUDO cp "$SERVICE_SOURCE" "$SERVICE_TARGET"
  $SUDO chmod 0644 "$SERVICE_TARGET"
  $SUDO systemctl daemon-reload
  $SUDO systemctl enable "$SERVICE_NAME"
  printf 'Installed and enabled %s
' "$SERVICE_NAME"
}

uninstall_service() {
  if ! service_installed; then
    printf '%s is not installed
' "$SERVICE_NAME"
    return 0
  fi

  $SUDO systemctl disable --now "$SERVICE_NAME" || true
  $SUDO rm -f "$SERVICE_TARGET"
  $SUDO systemctl daemon-reload
  printf 'Removed %s
' "$SERVICE_NAME"
}

start_with_systemd() {
  write_env_file
  $SUDO systemctl start "$SERVICE_NAME"
  $SUDO systemctl --no-pager --full status "$SERVICE_NAME" || true
}

stop_with_systemd() {
  $SUDO systemctl stop "$SERVICE_NAME"
  printf 'Stopped %s
' "$SERVICE_NAME"
}

status_with_systemd() {
  $SUDO systemctl --no-pager --full status "$SERVICE_NAME"
}

logs_with_systemd() {
  $SUDO journalctl -u "$SERVICE_NAME" -n 80 --no-pager
}

start_with_nohup() {
  if [[ -z "$PYTHON_BIN" ]]; then
    printf 'python3 was not found in PATH
' >&2
    return 1
  fi

  if is_running; then
    printf 'FSDR backend is already running with PID %s
' "$(<"$PID_FILE")"
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
      printf 'FSDR backend started with PID %s
' "$(<"$PID_FILE")"
      printf 'URL: http://%s:%s
' "$HOST" "$PORT"
      printf 'Log: %s
' "$LOG_FILE"
      return 0
    fi
    sleep 1
  done

  rm -f "$PID_FILE"
  printf 'FSDR backend failed to start. Check %s
' "$LOG_FILE" >&2
  return 1
}

stop_with_nohup() {
  if ! is_running; then
    rm -f "$PID_FILE"
    printf 'FSDR backend is not running
'
    return 0
  fi

  local pid
  pid="$(<"$PID_FILE")"
  kill "$pid"

  for _ in {1..10}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      rm -f "$PID_FILE"
      printf 'FSDR backend stopped
'
      return 0
    fi
    sleep 1
  done

  printf 'Process %s did not stop after 10s
' "$pid" >&2
  return 1
}

status_with_nohup() {
  if is_running; then
    printf 'FSDR backend is running with PID %s
' "$(<"$PID_FILE")"
    printf 'URL: http://%s:%s
' "$HOST" "$PORT"
    printf 'Log: %s
' "$LOG_FILE"
    return 0
  fi

  printf 'FSDR backend is not running
'
  return 1
}

start_backend() {
  if service_installed; then
    start_with_systemd
  else
    start_with_nohup
  fi
}

stop_backend() {
  if service_installed; then
    stop_with_systemd
  else
    stop_with_nohup
  fi
}

restart_backend() {
  if service_installed; then
    write_env_file
    $SUDO systemctl restart "$SERVICE_NAME"
    $SUDO systemctl --no-pager --full status "$SERVICE_NAME" || true
  else
    stop_with_nohup || true
    start_with_nohup
  fi
}

status_backend() {
  if service_installed; then
    status_with_systemd
  else
    status_with_nohup
  fi
}

case "${1:-start}" in
  start)
    start_backend
    ;;
  stop)
    stop_backend
    ;;
  restart)
    restart_backend
    ;;
  status)
    status_backend
    ;;
  install-service)
    install_service
    ;;
  uninstall-service)
    uninstall_service
    ;;
  logs)
    if service_installed; then
      logs_with_systemd
    elif [[ -f "$LOG_FILE" ]]; then
      tail -n 80 "$LOG_FILE"
    else
      printf 'No backend logs found yet
'
    fi
    ;;
  *)
    cat <<'EOF' >&2
Usage:
  ./scripts/run-backend.sh [start|stop|restart|status|install-service|uninstall-service|logs] [port]

Examples:
  ./scripts/run-backend.sh
  ./scripts/run-backend.sh start 8010
  ./scripts/run-backend.sh restart 8020
  ./scripts/run-backend.sh install-service
  ./scripts/run-backend.sh logs
EOF
    exit 1
    ;;
esac
