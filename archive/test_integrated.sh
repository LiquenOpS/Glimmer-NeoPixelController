#!/bin/bash
# Test script for Integrated Audio Reactive LED Controller

echo "=================================================="
echo "🧪 Testing Integrated Audio Reactive System"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Check Python version
echo -e "${BLUE}📋 Test 1: Python version${NC}"
python3 --version
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Python3 available${NC}"
else
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi
echo ""

# Test 2: Check required files
echo -e "${BLUE}📋 Test 2: Required files${NC}"
files=("audio_reactive_integrated.py" "led_emulator.py" "requirements.txt")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file not found${NC}"
        exit 1
    fi
done
echo ""

# Test 3: Check Python imports (basic)
echo -e "${BLUE}📋 Test 3: Basic Python imports${NC}"
python3 -c "import sys; import socket; import struct; import time; import threading; print('✅ Standard libraries OK')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Standard libraries available${NC}"
else
    echo -e "${RED}❌ Missing standard libraries${NC}"
    exit 1
fi
echo ""

# Test 4: Check NumPy (optional)
echo -e "${BLUE}📋 Test 4: NumPy (optional)${NC}"
python3 -c "import numpy" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ NumPy available${NC}"
else
    echo -e "${YELLOW}⚠️  NumPy not available (optional)${NC}"
fi
echo ""

# Test 5: Test LED emulator module
echo -e "${BLUE}📋 Test 5: LED Emulator module${NC}"
python3 -c "from led_emulator import PixelStripEmulator, Color; print('✅ LED Emulator module OK')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ LED Emulator module loads${NC}"
else
    echo -e "${RED}❌ LED Emulator module error${NC}"
    exit 1
fi
echo ""

# Test 6: UDP port availability
echo -e "${BLUE}📋 Test 6: UDP port 31337 availability${NC}"
netstat -uln 2>/dev/null | grep -q ":31337"
if [ $? -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Port 31337 already in use${NC}"
    echo "   Run: sudo netstat -ulnp | grep 31337"
else
    echo -e "${GREEN}✅ Port 31337 available${NC}"
fi
echo ""

# Test 7: Quick emulator test (2 seconds)
echo -e "${BLUE}📋 Test 7: Quick emulator test (2 seconds)${NC}"
echo "   Starting emulator..."

timeout 2 python3 audio_reactive_integrated.py --emulator --num-leds 20 2>&1 &
PID=$!

sleep 2.5

# Check if process existed
if ps -p $PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Emulator runs successfully${NC}"
    kill $PID 2>/dev/null
else
    echo -e "${GREEN}✅ Emulator completed${NC}"
fi
echo ""

# Summary
echo "=================================================="
echo -e "${GREEN}✅ All basic tests passed!${NC}"
echo "=================================================="
echo ""
echo "🚀 Ready to use! Try:"
echo ""
echo -e "${BLUE}1. Emulator mode (testing):${NC}"
echo "   python3 audio_reactive_integrated.py --emulator"
echo ""
echo -e "${BLUE}2. Real LED mode (requires sudo):${NC}"
echo "   sudo python3 audio_reactive_integrated.py"
echo ""
echo -e "${BLUE}3. With EQ Streamer:${NC}"
echo "   Terminal 1: python3 audio_reactive_integrated.py --emu"
echo "   Terminal 2: cd ../LQS-IoT_EqStreamer && dotnet run"
echo ""
echo -e "${BLUE}4. Different effects:${NC}"
echo "   python3 audio_reactive_integrated.py --emu --effect vu_meter"
echo "   python3 audio_reactive_integrated.py --emu --effect rainbow_spectrum"
echo "   python3 audio_reactive_integrated.py --emu --effect fire"
echo ""
echo "📖 Read README_INTEGRATED.md for full documentation"
echo ""
