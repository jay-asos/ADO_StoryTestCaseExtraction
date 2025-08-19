#!/bin/zsh

# Kill any existing Python processes for our services
echo "🔄 Stopping existing services..."
pkill -f "python.*demo_enhanced_monitor.py|python.*monitor_api.py" || true

# Set up environment
export PYTHONPATH=/Users/jay/Documents/ADO_StoryTestCaseExtraction

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

echo "🚀 Starting Enhanced Monitor..."
python demo_enhanced_monitor.py &
MONITOR_PID=$!

# Wait a moment for the monitor to initialize
sleep 2

echo "🌐 Starting API Server..."
python src/monitor_api.py &
API_PID=$!

# Store PIDs for later cleanup
echo $MONITOR_PID > .monitor.pid
echo $API_PID > .api.pid

echo """
✨ Services Started Successfully!
📊 Enhanced Monitor (PID: $MONITOR_PID)
🌐 API Server (PID: $API_PID)

🔗 API endpoints available at:
   http://127.0.0.1:5001

💡 To stop services:
   ./stop_services.sh

📝 Logs:
   - Monitor: monitor_api.log
   - API: server.log
"""

# Wait for both processes
wait
