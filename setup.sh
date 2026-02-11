#!/bin/bash
# Interactive setup. Choose what to run; no parameters.

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
VENV_DIR="${ROOT}/venv"
REQUIREMENTS="${ROOT}/requirements.txt"
CONFIG_DIR="${ROOT}/config"
CONFIG_EXAMPLE_DIR="${ROOT}/config.example"
CONFIG="${CONFIG_DIR}/config.jsonc"

echo ""
echo "Glimmer setup — what would you like to do?"
echo "  1) Install essentials (venv, config)"
echo "  2) Install systemd (start on boot)"
echo "  3) Uninstall (stop, remove systemd)"
echo "  4) Exit"
echo ""
read -p "Choice [1-4]: " CHOICE

case "$CHOICE" in
  1)
    echo ""
    if ! command -v python3 &> /dev/null; then
      echo "Error: python3 not found. Please install Python 3.7+" >&2
      exit 1
    fi
    echo "Found $(python3 --version)"

    # Venv
    if [ ! -x "${VENV_DIR}/bin/python3" ]; then
      echo "Creating venv..."
      python3 -m venv "${VENV_DIR}"
      echo "  -> venv created."
    else
      echo "venv already exists."
    fi

    "${VENV_DIR}/bin/pip" install -q --upgrade pip 2>/dev/null || true
    [ -f "$REQUIREMENTS" ] && "${VENV_DIR}/bin/pip" install -q -r "$REQUIREMENTS"

    # Config
    if [ ! -f "$CONFIG" ]; then
      [ ! -d "$CONFIG_EXAMPLE_DIR" ] && { echo "Error: config.example not found." >&2; exit 1; }
      echo "Creating config/ from config.example..."
      cp -r "$CONFIG_EXAMPLE_DIR" "$CONFIG_DIR"
      echo "  -> config/config.jsonc created."
    fi
    read -p "Edit config/config.jsonc now? [y/N]: " EDIT
    [[ "$EDIT" =~ ^[yY] ]] && "${EDITOR:-vi}" "$CONFIG"

    chmod +x "$ROOT/run.sh"
    echo "Done. Use option 2 to install systemd."
    ;;
  2)
    read -p "Install systemd service (start on boot)? [y/N]: " Y
    if [[ "$Y" =~ ^[yY] ]]; then
      [ ! -x "${VENV_DIR}/bin/python3" ] && { echo "Error: venv not found. Run option 1 first." >&2; exit 1; }
      sudo -v
      SVC_FILE="/etc/systemd/system/glimmer.service"
      sed "s|@INSTALL_DIR@|$ROOT|g" "$ROOT/ops/systemd/glimmer.service" | sudo tee "$SVC_FILE" > /dev/null
      sudo systemctl daemon-reload
      sudo systemctl enable --now glimmer
      echo "  -> $SVC_FILE installed and started."
    fi
    ;;
  3)
    echo "==> Uninstalling Glimmer..."
    SVC_FILE="/etc/systemd/system/glimmer.service"
    if [ -f "$SVC_FILE" ]; then
      sudo -v
      sudo systemctl stop glimmer 2>/dev/null || true
      sudo systemctl disable glimmer 2>/dev/null || true
      sudo rm -f "$SVC_FILE"
      sudo systemctl daemon-reload
      echo "  -> systemd service removed."
    fi
    read -p "Remove config/ and venv? [y/N]: " Y
    if [[ "$Y" =~ ^[yY] ]]; then
      rm -rf "$CONFIG_DIR" "$VENV_DIR"
      echo "  -> config and venv removed."
    fi
    echo "Done."
    ;;
  4)
    echo "Bye."
    ;;
  *)
    echo "Invalid choice."
    exit 1
    ;;
esac
