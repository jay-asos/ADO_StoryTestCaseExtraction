# PowerShell version of start_services.sh

# Stop existing monitor_daemon.py processes
Write-Host "🔄 Stopping existing services..."
Get-Process | Where-Object { $_.Path -like '*python*' -and $_.CommandLine -match 'monitor_daemon.py' } | ForEach-Object { $_.Kill() }

# Set up environment
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $SCRIPT_DIR

# Load environment variables from .env file
if (Test-Path ".env") {
    Write-Host "📁 Loading environment variables from .env file..."
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "  ✅ Set $name"
        }
    }
} else {
    Write-Host "⚠️ No .env file found"
}

# Ensure logs directory exists
if (-not (Test-Path -Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Export configuration from monitor_config.json to environment
Write-Host "📝 Exporting configuration to environment..."
try {
    $monitorConfig = Get-Content "monitor_config.json" | ConvertFrom-Json
    $env:ADO_AUTO_TEST_CASE_EXTRACTION = $monitorConfig.auto_test_case_extraction
} catch {
    Write-Host "⚠️ Could not read monitor_config.json: $($_.Exception.Message)"
}

# Start the monitor API and dashboard
Write-Host "🚀 Starting Monitor API and Dashboard..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "scripts\monitor_daemon.py", "--mode", "api", "--port", "5001", "--config", "monitor_config.json"

Start-Sleep -Seconds 2

Write-Host "✅ Services started!"
Write-Host "🌐 Dashboard UI available at: http://localhost:5001/dashboard"
Write-Host "🔍 Monitor API available at: http://localhost:5001/api"
Write-Host "📝 Check logs/enhanced_epic_monitor.log for detailed logs"

# Activate virtual environment if it exists
if (Test-Path ".venv/Scripts/Activate.ps1") {
    Write-Host "🔌 Activating virtual environment..."
    . .venv/Scripts/Activate.ps1
}

# Verify config files exist
$configFiles = @("monitor_config.json", "monitor_config_enhanced.json")
foreach ($config in $configFiles) {
    if (-not (Test-Path $config)) {
        Write-Host "❌ Missing config file: $config"
    }
}
