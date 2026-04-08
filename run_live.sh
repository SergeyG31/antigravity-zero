#!/bin/bash

# Antigravity P2P Sovereign - Live Launch Script
# This script initializes the virtual environment and starts both the Orchestrator and the Dashboard.

echo "🏛️  ANTIGRAVITY: ACTIVATING SOVEREIGN ENGINE..."

# 1. Path to Virtual Environment
VENV_PATH="/Users/sergeygalayev/Desktop/LiorBot_Improved/.venv"
PYTHON_BIN="$VENV_PATH/bin/python3"
STREAMLIT_BIN="$VENV_PATH/bin/streamlit"

# 2. Safety Check: Verify .env exists
if [ ! -f ".env" ]; then
    echo "❌  Error: .env file not found. Please create it first."
    exit 1
fi

# 3. Mode Selection
echo "--------------------------------------------------"
echo "Select Mode:"
echo "1) ⚡ LIVE MODE (Real Execution - DANGEROUS)"
echo "2) 🛡️ SHADOW MODE (Simulated Execution - SAFE)"
echo "--------------------------------------------------"
read -p "Enter choice [1-2]: " mode_choice

if [ "$mode_choice" == "1" ]; then
    echo "⚠️  WARNING: LIVE MODE ACTIVATED. REAL TRADES WILL BE EXECUTED."
    # Update config.py to SHADOW_MODE = False
    sed -i '' 's/SHADOW_MODE = True/SHADOW_MODE = False/g' config.py
else
    echo "🛡️  SHADOW MODE ACTIVATED. Monitoring only."
    sed -i '' 's/SHADOW_MODE = False/SHADOW_MODE = True/g' config.py
fi

# 4. Orchestrator Selection
echo "--------------------------------------------------"
echo "Select Orchestrator:"
echo "1) 📈 MEXC Stock Specialist (Main Strategy)"
echo "2) 🏛️ P2P Multi-Hub Sovereign (Classic Arp)"
echo "--------------------------------------------------"
read -p "Enter choice [1-2]: " orch_choice

if [ "$orch_choice" == "1" ]; then
    TARGET_MAIN="main_p2p.py"
else
    TARGET_MAIN="main.py"
fi

# 5. Launch Dashboard in background
echo "📊  Launching Tactical Dashboard on Port 8506..."
$STREAMLIT_BIN run dashboard_hud.py --server.port 8506 --server.headless true > /dev/null 2>&1 &
DASHBOARD_PID=$!
sleep 2
open http://localhost:8506

# 6. Launch Main Orchestrator

echo "🚀  Starting $TARGET_MAIN Core..."
echo "Press Ctrl+C to stop everything."
echo "--------------------------------------------------"

$PYTHON_BIN $TARGET_MAIN

# Cleanup on exit
kill $DASHBOARD_PID 2>/dev/null
echo ""
echo "🏛️  Sovereign Engine: OFFLINE. Cleanup complete."

