#!/bin/bash
# Entrypoint for Glimmer (used by systemd or manual run). Activates venv and starts main.py.

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

VENV_PYTHON="${ROOT}/venv/bin/python3"
if [ ! -x "$VENV_PYTHON" ]; then
  echo "Error: venv not found. Run ./setup.sh first." >&2
  exit 1
fi

exec "$VENV_PYTHON" "$ROOT/main.py" "$@"
