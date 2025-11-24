# PowerShell version of stop_services.sh

# Function to check if a port is in use
function Test-PortOpen {
    param(
        [int]$Port
    )
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect('localhost', $Port)
        $tcp.Close()
        return $true
    } catch {
        return $false
    }
}

# Try to stop services gracefully via API first
if (Test-PortOpen -Port 5001) {
    Write-Host "Attempting graceful shutdown via API..."

    # Stop the monitor first
    Write-Host "Stopping monitor service..."
    try {
        $monitorStop = Invoke-WebRequest -Uri "http://localhost:5001/api/monitor/stop" -Method POST -UseBasicParsing -ErrorAction Stop
        Write-Host "Monitor stop request sent successfully"
    } catch {
        Write-Host "Warning: Monitor stop request failed"
    }
    Start-Sleep -Seconds 2

    # Stop the server
    Write-Host "Shutting down API server..."
    try {
        $serverStop = Invoke-WebRequest -Uri "http://localhost:5001/api/shutdown" -Method POST -UseBasicParsing -ErrorAction Stop
        Write-Host "Server shutdown request sent successfully"
    } catch {
        Write-Host "Warning: Server shutdown request failed"
    }
    Start-Sleep -Seconds 3

    # Double check if the server is still responding
    if (Test-PortOpen -Port 5001) {
        Write-Host "Warning: Server still running after graceful shutdown attempt"
        # Find and kill all Python processes serving on port 5001
        Write-Host "Attempting to kill all Python processes on port 5001..."
        $pids = Get-NetTCPConnection -LocalPort 5001 -State Listen | Select-Object -ExpandProperty OwningProcess
        foreach ($pid in $pids) {
            try {
                Stop-Process -Id $pid -Force
                Write-Host "Killed process with PID $pid"
            } catch {
                Write-Host "Failed to kill process with PID $pid"
            }
        }
    }
} else {
    Write-Host "Port 5001 is not in use. No services to stop."
}

# Also kill any lingering monitor_daemon.py processes
Get-Process | Where-Object { $_.Path -like '*python*' -and $_.CommandLine -match 'monitor_daemon.py' } | ForEach-Object { $_.Kill() }
Write-Host "All services stopped."
