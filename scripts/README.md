# Scripts Directory

This directory contains utility scripts for managing the STAX application.

## 🚀 Quick Start

### Using the Enhanced Manager (Recommended)
```bash
# Start STAX (auto-detects Docker/local)
./scripts/stax-manager.sh start

# Force Docker mode
./scripts/stax-manager.sh docker

# Force local mode
./scripts/stax-manager.sh local

# Stop all services
./scripts/stax-manager.sh stop

# Check status
./scripts/stax-manager.sh status

# Restart services
./scripts/stax-manager.sh restart
```

### Using Individual Scripts
```bash
# Start services locally
./scripts/start_services.sh

# Stop services
./scripts/stop_services.sh
```

## 📁 Files in this directory

- `stax-manager.sh` - **Enhanced service manager** (recommended)
- `start_services.sh` - Legacy start script for local Python execution
- `stop_services.sh` - Legacy stop script
- `monitor_daemon.py` - Monitor daemon for local execution

## 🔧 Features

### Enhanced Manager (`stax-manager.sh`)
- ✅ Auto-detects Docker availability
- ✅ Falls back to local execution if Docker unavailable
- ✅ Configuration validation
- ✅ Colored output for better UX
- ✅ Status checking
- ✅ Proper service management

### Legacy Scripts
- `start_services.sh` - Direct Python execution
- `stop_services.sh` - Service cleanup

## 🌐 Access Points

Once started, access your application at:
- **Main Application**: http://localhost:5001
- **API Health Check**: http://localhost:5001/api/health
- **Dashboard**: http://localhost:5001/dashboard

## 📝 Notes

- All scripts are updated to work with the new folder structure
- Configuration files are expected in `../config/`
- Log files are written to `../logs/`
- The enhanced manager handles both Docker and local execution modes