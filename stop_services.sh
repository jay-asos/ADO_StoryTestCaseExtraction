#!/bin/zsh

# Kill the stored PIDs if they exist
if [ -f .monitor.pid ]; then
    MONITOR_PID=$(cat .monitor.pid)
    echo "Stopping Enhanced Monitor (PID: $MONITOR_PID)..."
    kill $MONITOR_PID 2>/dev/null || true
    rm .monitor.pid
fi

if [ -f .api.pid ]; then
    API_PID=$(cat .api.pid)
    echo "Stopping API Server (PID: $API_PID)..."
    kill $API_PID 2>/dev/null || true
    rm .api.pid
fi

# Kill any remaining Python processes for our services
echo "Cleaning up any remaining processes..."
pkill -f "python.*demo_enhanced_monitor.py|python.*monitor_api.py" || true

echo "✅ All services stopped successfully!"
