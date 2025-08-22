#!/bin/zsh

# Kill any existing monitor processes
echo "🔄 Stopping existing services..."
pkill -f "python.*monitor_daemon.py" || true

# Set up environment
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"
export PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR

# Ensure logs directory exists
mkdir -p logs

# Export configuration from monitor_config.json to environment
echo "📝 Exporting configuration to environment..."
export ADO_AUTO_TEST_CASE_EXTRACTION=$(jq -r '.auto_test_case_extraction' monitor_config.json)

# Start the monitor API and dashboard
echo "� Starting Monitor API and Dashboard..."
python3 monitor_daemon.py --mode api --port 5001 --config monitor_config.json &

# Wait a moment for the API to start
sleep 2

echo "✅ Services started!"
echo "� Dashboard UI available at: http://localhost:5001/dashboard"
echo "🔍 Monitor API available at: http://localhost:5001/api"
echo "📝 Check logs/enhanced_epic_monitor.log for detailed logs"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo "🔌 Activating virtual environment..."
    source .venv/bin/activate
fi

# Verify config files exist
CONFIG_FILES=("monitor_config.json" "monitor_config_enhanced.json")
for config in "${CONFIG_FILES[@]}"; do
    if [ ! -f "$config" ]; then
        echo "❌ Error: $config not found!"
        exit 1
    fi
done

# Ensure logs directory exists
mkdir -p logs

# Monitor API is already running from the previous command
echo "✨ Monitor API is already running..."

# Verify monitor API server started
sleep 2
if ! ps -p $MONITOR_API_PID > /dev/null; then
    echo "❌ Error: Monitor API server failed to start! Check logs/enhanced_epic_monitor.log for details."
    exit 1
fi

echo "✅ Services started successfully!"
echo "📊 Monitor API Server PID: $MONITOR_API_PID"
echo "📝 Log locations:"
echo "   - Monitor API: logs/enhanced_epic_monitor.log"
echo "   - API Access: monitor_api.log"
echo ""
echo "🌐 Access points:"
echo "   - Dashboard: http://127.0.0.1:5001/"
echo "   - API Documentation: http://127.0.0.1:5001/api"
echo "   - Health Check: http://127.0.0.1:5001/api/health"
echo ""
echo "📊 To monitor services:"
echo "   tail -f monitor_api.log"
echo "   tail -f logs/enhanced_epic_monitor.log"

# Wait for process
wait $MONITOR_API_PID
