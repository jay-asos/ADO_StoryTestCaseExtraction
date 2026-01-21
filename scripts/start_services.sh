#!/bin/zsh

# STAX Services Startup Script
# Updated for new folder structure

echo "🔄 Stopping any existing services..."
pkill -f "python.*monitor_daemon.py" || true
pkill -f "python.*main.py" || true

# Set up environment - navigate to project root
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
cd "$PROJECT_ROOT"
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT

echo ""
echo "📁 Working directory: $(pwd)"
echo ""

# Ensure logs directory exists
mkdir -p logs

# Load environment variables from config
if [ -f "config/.env" ]; then
    echo "📝 Loading environment from config/.env..."
    set -a
    source config/.env
    set +a
else
    echo "⚠️  Warning: config/.env not found"
fi

# Export configuration from monitor_config.json to environment
echo "📝 Exporting configuration to environment..."
if [ -f "config/monitor_config.json" ]; then
    export ADO_AUTO_TEST_CASE_EXTRACTION=$(jq -r '.auto_test_case_extraction' config/monitor_config.json 2>/dev/null || echo "false")
else
    echo "⚠️  Warning: config/monitor_config.json not found"
fi

# Verify config files exist
CONFIG_FILES=("config/monitor_config.json" "config/monitor_config_enhanced.json")
for config in "${CONFIG_FILES[@]}"; do
    if [ ! -f "$config" ]; then
        echo "❌ Error: $config not found!"
        exit 1
    fi
done

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo "🔌 Activating virtual environment..."
    source .venv/bin/activate
fi

echo ""
echo "🚀 Starting Monitor API and Dashboard..."
echo "📝 Using config: config/monitor_config.json"
echo "📝 Log file: logs/enhanced_epic_monitor.log"
echo ""

# Start the monitor daemon with live logging
echo "📊 Starting monitor daemon with live output..."
python3 scripts/monitor_daemon.py --mode api --port 5001 --config config/monitor_config.json &
MONITOR_API_PID=$!

# Wait a moment for the API to start
echo "⏳ Waiting for API to start..."
sleep 3

# Check if the process is still running
if ! kill -0 $MONITOR_API_PID 2>/dev/null; then
    echo ""
    echo "❌ Error: Monitor API failed to start!"
    echo "📝 Check the output above for error details"
    echo "📝 Application log:"
    tail -10 logs/enhanced_epic_monitor.log 2>/dev/null || echo "No application log found"
    exit 1
fi

# Test if the API is responding
echo "🔍 Testing API response..."
if curl -f --silent --connect-timeout 5 http://localhost:5001/api/health > /dev/null 2>&1; then
    echo ""
    echo "✅ Services started successfully!"
    echo "📊 Monitor API Server PID: $MONITOR_API_PID"
    echo ""
    echo "🌐 Access points:"
    echo "   - Dashboard: http://localhost:5001/dashboard"
    echo "   - API Documentation: http://localhost:5001/api"
    echo "   - Health Check: http://localhost:5001/api/health"
    echo ""
    echo "�� Log locations:"
    echo "   - Startup: logs/monitor_startup.log"
    echo "   - Application: logs/enhanced_epic_monitor.log"
    echo ""
    echo "📊 To monitor services:"
    echo "   tail -f logs/enhanced_epic_monitor.log"
    echo ""
    echo "🛑 To stop services:"
    echo "   ./scripts/stop_services.sh"
    echo ""
else
    echo ""
    echo "❌ Error: API is not responding!"
    echo "📝 Check the output above for error details"
    kill $MONITOR_API_PID 2>/dev/null || true
    exit 1
fi

# Wait for the process if running in foreground mode
if [ "${1:-}" = "foreground" ]; then
    echo "🔄 Running in foreground mode. Press Ctrl+C to stop."
    echo ""
    wait $MONITOR_API_PID
fi
