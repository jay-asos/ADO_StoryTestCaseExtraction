#!/bin/zsh

# Kill any existing Python processes for our services
echo "🔄 Stopping existing services..."
pkill -f "python.*monitor.py|python.*monitor_api.py|python.*monitor_daemon.py" || true

# Set up environment
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"
export PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR

# Set default environment variables
export OPENAI_RETRY_DELAY=${OPENAI_RETRY_DELAY:-10}
export OPENAI_MAX_RETRIES=${OPENAI_MAX_RETRIES:-3}
export OPENAI_MODEL=${OPENAI_MODEL:-"gpt-4"}
export LOG_LEVEL=${LOG_LEVEL:-"DEBUG"}

# Ensure logs directory exists
mkdir -p logs

# Set up rotating logs for better visibility
echo "🔄 Rotating log files..."
for log in monitor_api.log logs/enhanced_epic_monitor.log; do
    if [ -f "$log" ]; then
        mv "$log" "${log}.old"
    fi
done

# Load .env file if it exists
if [ -f ".env" ]; then
    echo "📥 Loading .env file..."
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^#.*$ ]] && continue
        [[ -z $key ]] && continue
        # Remove quotes and export the variable
        value=$(echo "$value" | tr -d '"' | tr -d "'")
        export "$key=$value"
    done < .env
else
    echo "⚠️ Warning: .env file not found, using default settings"
fi

# Verify critical configuration
if ! grep -q "ADO_AUTO_TEST_CASE_EXTRACTION=" .env; then
    echo "ℹ️  Adding auto test case extraction setting..."
    echo "ADO_AUTO_TEST_CASE_EXTRACTION=true" >> .env
fi

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo "🔌 Activating virtual environment..."
    source .venv/bin/activate
fi

# Function to check if a port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
    return $?
}

# Wait for ports to be free
while check_port 5001; do
    echo "⏳ Waiting for port 5001 to be free..."
    sleep 1
done

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

# Start the monitor API server with improved logging and error handling
echo "🚀 Starting monitor API server..."
python3 monitor_daemon.py --mode api --port 5001 --config monitor_config.json 2>&1 &
MONITOR_API_PID=$!

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
