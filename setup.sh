#!/bin/bash
# Setup script for Glimmer LED Controller

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
REQUIREMENTS="${SCRIPT_DIR}/requirements.txt"
CONFIG_EXAMPLE="${SCRIPT_DIR}/config.json.example"
CONFIG="${SCRIPT_DIR}/config.json"

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
    echo "ℹ️  Virtual environment already exists at $VENV_DIR"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "${VENV_DIR}/bin/activate"
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null
echo "✅ pip upgraded"
echo ""

# Install requirements
if [ -f "$REQUIREMENTS" ]; then
    echo "📥 Installing requirements..."
    pip install -r "$REQUIREMENTS"
    echo "✅ Requirements installed"
else
    echo "⚠️  Warning: requirements.txt not found"
fi
echo ""

# Setup config file
if [ ! -f "$CONFIG" ]; then
    if [ -f "$CONFIG_EXAMPLE" ]; then
        echo "📝 Creating config.json from example..."
        cp "$CONFIG_EXAMPLE" "$CONFIG"
        echo "✅ Config file created at $CONFIG"
        echo "   ⚠️  Please review and edit config.json if needed"
    else
        echo "⚠️  Warning: config.json.example not found"
    fi
else
    echo "ℹ️  Config file already exists at $CONFIG"
fi
echo ""

echo "✨ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source ${VENV_DIR}/bin/activate"
echo ""
echo "To run the controller:"
echo "  python3 main.py"
echo ""
echo "For simulator mode:"
echo "  python3 main.py --simulator"
echo ""
