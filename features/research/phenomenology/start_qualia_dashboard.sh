#!/bin/bash
# Start the Qualia Real-time Dashboard

echo "🧠 Starting Qualia Dashboard Server..."
echo "===================================="
echo ""

# Check if ActivityWatch is running
if pgrep -x "aw-server" > /dev/null || pgrep -x "aw-qt" > /dev/null; then
    echo "✅ ActivityWatch detected - will use real behavioral data"
else
    echo "⚠️  ActivityWatch not running - will use demo data"
    echo "   To use real data, start ActivityWatch first:"
    echo "   $ aw-qt &"
    echo ""
fi

# Check dependencies
echo "Checking dependencies..."
python3 -c "import aiohttp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing aiohttp. Installing..."
    pip install aiohttp aiohttp-cors
fi

# Start the server
echo ""
echo "Starting server on http://localhost:8765"
echo "Open your browser to see the real-time phenomenological dashboard!"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
python3 ../../src/phenomenology/qualia_realtime_server.py