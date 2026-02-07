#!/bin/bash
# Setup script for Glimmer LED Controller

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
REQUIREMENTS="${SCRIPT_DIR}/requirements.txt"
CONFIG_DIR="${SCRIPT_DIR}/config"
CONFIG_EXAMPLE_DIR="${SCRIPT_DIR}/config.example"
CONFIG="${CONFIG_DIR}/config.jsonc"

echo "🚀 Setting up Glimmer LED Controller..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $(python3 --version)"
echo ""

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created at $VENV_DIR"
else
    echo "ℹ️ Virtual environment already exists at $VENV_DIR"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "${VENV_DIR}/bin/activate"
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip > /dev/null
echo "✅ pip upgraded"
echo ""

# Install requirements
if [ -f "$REQUIREMENTS" ]; then
    echo "📥 Installing requirements..."
    pip install -r "$REQUIREMENTS"
    echo "✅ Requirements installed"
else
    echo "⚠️ Warning: requirements.txt not found"
fi
echo ""

# Setup config (copy config.example to config if missing)
if [ ! -f "$CONFIG" ]; then
    if [ -d "$CONFIG_EXAMPLE_DIR" ]; then
        echo "📝 Creating config/ from config.example..."
        cp -r "$CONFIG_EXAMPLE_DIR" "$CONFIG_DIR"
        echo "✅ Config created at $CONFIG"
        echo "⚠️ Please review and edit config/config.jsonc if needed"
    else
        echo "⚠️ Warning: config.example not found"
    fi
else
    echo "ℹ️ Config already exists at $CONFIG"
fi
echo ""

chmod +x "${SCRIPT_DIR}/run.sh" 2>/dev/null || true

echo "✨ Setup complete!"
echo ""
read -p "Install systemd service (start on boot)? [y/N]: " INSTALL_SVC
if [[ "$INSTALL_SVC" =~ ^[yY] ]]; then
  echo "Installing service requires sudo."
  sudo -v
  SVC_FILE="/etc/systemd/system/glimmer.service"
  sed "s|@INSTALL_DIR@|${SCRIPT_DIR}|g" "${SCRIPT_DIR}/ops/systemd/glimmer.service" | sudo tee "$SVC_FILE" > /dev/null
  sudo systemctl daemon-reload
  sudo systemctl enable --now glimmer
  echo "  -> $SVC_FILE installed and started."
else
  echo "To run manually: ./run.sh"
  echo "  Simulator: ./run.sh --simulator"
fi
echo ""
