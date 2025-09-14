#!/bin/zsh

# STAX Services Stop Script
# Updated for new folder structure

# Set up environment - navigate to project root
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
cd "$PROJECT_ROOT"

# Function to check if a port is in use
check_port() {
    nc -z localhost $1 >/dev/null 2>&1
    return $?
}

# Try to stop services gracefully via API first
if check_port 5001; then
    echo "Attempting graceful shutdown via API..."
    
    # Stop the monitor first
    echo "Stopping monitor service..."
    MONITOR_STOP=$(curl -s -w "%{http_code}" -X POST http://localhost:5001/api/monitor/stop)
    if [ $? -eq 0 ]; then
        echo "Monitor stop request sent successfully"
    else
        echo "Warning: Monitor stop request failed"
    fi
    sleep 2  # Give the monitor time to clean up
    
    # Stop the server
    echo "Shutting down API server..."
    SERVER_STOP=$(curl -s -w "%{http_code}" -X POST http://localhost:5001/api/shutdown)
    if [ $? -eq 0 ]; then
        echo "Server shutdown request sent successfully"
    else
        echo "Warning: Server shutdown request failed"
    fi
    sleep 3  # Give the server time to shutdown gracefully
    
    # Double check if the server is still responding
    if check_port 5001; then
        echo "Warning: Server still running after graceful shutdown attempt"
        
        # Find and kill all Python processes serving on port 5001
        echo "Attempting to kill all Python processes on port 5001..."
        PIDS=$(lsof -t -i:5001)
        if [ ! -z "$PIDS" ]; then
            echo "Found processes on port 5001: $PIDS"
            for PID in $PIDS; do
                echo "Killing process $PID..."
                kill -TERM $PID 2>/dev/null || true
                sleep 1
                # If still running, force kill
                if kill -0 $PID 2>/dev/null; then
                    echo "Force killing process $PID..."
                    kill -9 $PID 2>/dev/null || true
                fi
            done
        fi
    else
        echo "Server stopped successfully"
    fi
fi

# Kill the stored PIDs if they exist
if [ -f .monitor.pid ]; then
    MONITOR_PID=$(cat .monitor.pid)
    echo "Stopping Enhanced Monitor (PID: $MONITOR_PID)..."
    kill -TERM $MONITOR_PID 2>/dev/null || true
    sleep 1
    # If process still exists, force kill
    if kill -0 $MONITOR_PID 2>/dev/null; then
        echo "Force stopping Monitor..."
        kill -9 $MONITOR_PID 2>/dev/null || true
    fi
    rm .monitor.pid
fi

if [ -f .api.pid ]; then
    API_PID=$(cat .api.pid)
    echo "Stopping API Server (PID: $API_PID)..."
    kill -TERM $API_PID 2>/dev/null || true
    sleep 1
    # If process still exists, force kill
    if kill -0 $API_PID 2>/dev/null; then
        echo "Force stopping API..."
        kill -9 $API_PID 2>/dev/null || true
    fi
    rm .api.pid
fi

# Clean up any remaining processes as a last resort
echo "Checking for any remaining processes..."
REMAINING=$(pgrep -f "python.*demo_enhanced_monitor.py|python.*monitor_api.py|python.*monitor_daemon.py|flask.*run" || true)
if [ ! -z "$REMAINING" ]; then
    echo "Cleaning up remaining processes..."
    # Try graceful shutdown first
    pkill -TERM -f "python.*demo_enhanced_monitor.py|python.*monitor_api.py|python.*monitor_daemon.py|flask.*run" || true
    sleep 2
    # Force kill if still running
    pkill -9 -f "python.*demo_enhanced_monitor.py|python.*monitor_api.py|python.*monitor_daemon.py|flask.*run" 2>/dev/null || true
fi

# Final check for port 5001
if check_port 5001; then
    echo "Warning: Port 5001 is still in use. You may need to manually kill the process:"
    echo "lsof -i:5001"
    echo "kill -9 <PID>"
else
    echo "Port 5001 is free"
fi

echo "✅ All services stopped successfully!"
