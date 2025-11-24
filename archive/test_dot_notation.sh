#!/bin/bash

# Test script for dot notation support

API_BASE="http://localhost:8080/api"

echo "=========================================="
echo "Testing Dot Notation Support"
echo "=========================================="
echo ""
echo "Make sure audio_reactive_integrated.py is running!"
echo ""

# Test 1: Simple dot notation
echo "Test 1: Update single value with dot notation"
echo "--------------------------------------------"
curl -X POST "$API_BASE/config" \
  -H "Content-Type: application/json" \
  -d '{"rotation.period": 15.0}' \
  -s | python3 -m json.tool
echo ""
sleep 2

# Test 2: Multiple dot notation values
echo "Test 2: Update multiple values with dot notation"
echo "------------------------------------------------"
curl -X POST "$API_BASE/config" \
  -H "Content-Type: application/json" \
  -d '{
    "rotation.period": 20.0,
    "rotation.enabled": true,
    "audio.volume_compensation": 2.0,
    "audio.auto_gain": false
  }' \
  -s | python3 -m json.tool
echo ""
sleep 2

# Test 3: Mixed format (hierarchical + dot notation)
echo "Test 3: Mixed format (hierarchical + dot notation)"
echo "---------------------------------------------------"
curl -X POST "$API_BASE/config" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "audio_dynamic",
    "audio": {
      "static_effect": "fire"
    },
    "rotation.period": 25.0,
    "rainbow.brightness": 180
  }' \
  -s | python3 -m json.tool
echo ""
sleep 2

# Test 4: Rainbow settings with dot notation
echo "Test 4: Rainbow settings with dot notation"
echo "-------------------------------------------"
curl -X POST "$API_BASE/config" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "rainbow",
    "rainbow.speed": 10,
    "rainbow.brightness": 200
  }' \
  -s | python3 -m json.tool
echo ""
sleep 3

# Test 5: Get final config
echo "Test 5: Get final configuration"
echo "--------------------------------"
curl -X GET "$API_BASE/config" -s | python3 -m json.tool
echo ""
sleep 2

# Test 6: Invalid dot notation (should return 400)
echo "Test 6: Invalid dot notation (Error Test)"
echo "------------------------------------------"
echo "Testing with invalid key: invalid.key"
curl -X POST "$API_BASE/config" \
  -H "Content-Type: application/json" \
  -d '{"invalid.key": 123}' \
  -s | python3 -m json.tool
echo ""
sleep 2

# Test 7: Partially invalid dot notation
echo "Test 7: Partially invalid dot notation"
echo "---------------------------------------"
echo "Testing with valid and invalid keys"
curl -X POST "$API_BASE/config" \
  -H "Content-Type: application/json" \
  -d '{
    "rotation.period": 15.0,
    "invalid.field": 999
  }' \
  -s | python3 -m json.tool
echo ""

echo ""
echo "=========================================="
echo "All tests completed!"
echo "Valid dot notation keys:"
echo "  - audio.static_effect"
echo "  - audio.volume_compensation"
echo "  - audio.auto_gain"
echo "  - rotation.enabled"
echo "  - rotation.period"
echo "  - rainbow.speed"
echo "  - rainbow.brightness"
echo "=========================================="
