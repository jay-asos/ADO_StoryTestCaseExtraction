#!/usr/bin/env python3
"""
CLI script for running the EPIC monitoring daemon with both standalone and API modes.
"""

import argparse
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent  # Go up one level from scripts/ to project root
sys.path.insert(0, str(project_root))

from src.monitor import EpicChangeMonitor, MonitorConfig, create_default_config, load_config_from_file


def run_standalone_monitor(config: MonitorConfig):
    """Run the monitor in standalone mode (no API)"""
    print("🚀 Starting EPIC Change Monitor (Standalone Mode)")
    print(f"📊 Configuration:")
    print(f"   Poll interval: {config.poll_interval_seconds} seconds")
    print(f"   Auto-sync: {config.auto_sync}")
    print(f"   Epic IDs: {config.epic_ids}")
    print(f"   Log level: {config.log_level}")
    print("=" * 60)
    
    monitor = EpicChangeMonitor(config)
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal, shutting down...")
        monitor.stop()
    except Exception as e:
        print(f"❌ Monitor failed: {e}")
        return 1
    
    return 0


def run_api_mode(config: MonitorConfig, host: str, port: int, debug: bool):
    """Run the monitor with REST API"""
    try:
        from src.monitor_api import MonitorAPI
    except ImportError as e:
        print(f"❌ Failed to import Flask dependencies: {e}")
        print("💡 Try installing Flask: pip install flask")
        return 1
    
    print("🚀 Starting EPIC Change Monitor API Server")
    print(f"📊 Configuration:")
    print(f"   API Host: {host}:{port}")
    print(f"   Poll interval: {config.poll_interval_seconds} seconds")
    print(f"   Auto-sync: {config.auto_sync}")
    print(f"   Epic IDs: {config.epic_ids}")
    print(f"   Debug mode: {debug}")
    print("=" * 60)
    print("🌐 Web Dashboard: http://{host}:{port}/".format(host=host if host != '0.0.0.0' else '127.0.0.1', port=port))
    print("🌐 API Documentation: http://{host}:{port}/api".format(host=host if host != '0.0.0.0' else '127.0.0.1', port=port))
    print(f"🔍 Health Check: http://{host}:{port}/api/health")
    print("=" * 60)
    
    api = MonitorAPI(config, port=port)
    
    try:
        api.run(host=host, debug=debug)
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal, shutting down...")
        if api.monitor:
            api.monitor.stop()
    except Exception as e:
        print(f"❌ API server failed: {e}")
        return 1
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="EPIC Change Monitor Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create default configuration
  python monitor_daemon.py --create-config
  
  # Run in standalone mode (no API)
  python monitor_daemon.py --mode standalone
  
  # Run with REST API
  python monitor_daemon.py --mode api --host 0.0.0.0 --port 8080
  
  # Run with custom configuration
  python monitor_daemon.py --config my_config.json --mode api
        """
    )
    
    parser.add_argument('--mode', choices=['standalone', 'api'], default='standalone',
                       help='Monitoring mode: standalone or with REST API')
    parser.add_argument('--config', default='config/monitor_config.json',
                       help='Configuration file path')
    parser.add_argument('--create-config', action='store_true',
                       help='Create default configuration file and exit')
    
    # API-specific arguments
    parser.add_argument('--host', default='127.0.0.1',
                       help='API server host (api mode only)')
    parser.add_argument('--port', type=int, default=5000,
                       help='API server port (api mode only)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode (api mode only)')
    
    args = parser.parse_args()
    
    # Create default configuration if requested
    if args.create_config:
        try:
            config = create_default_config(args.config)
            print(f"✅ Created default configuration: {args.config}")
            print("\n📝 Edit the configuration file to customize:")
            print(f"   - epic_ids: List of EPIC IDs to monitor")
            print(f"   - poll_interval_seconds: How often to check for changes")
            print(f"   - auto_sync: Whether to automatically sync changes")
            return 0
        except Exception as e:
            print(f"❌ Failed to create configuration: {e}")
            return 1
    
    # Load configuration
    try:
        if os.path.exists(args.config):
            config = load_config_from_file(args.config)
            print(f"📁 Loaded configuration from: {args.config}")
        else:
            print(f"⚠️  Configuration file not found: {args.config}")
            print("📝 Creating default configuration...")
            config = create_default_config(args.config)
            print(f"✅ Created: {args.config}")
            print("💡 Edit the configuration file to add your EPIC IDs")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return 1
    
    # Validate configuration
    if not config.epic_ids:
        print("⚠️  No EPIC IDs configured for monitoring")
        print("💡 Epic IDs can be added later through the API")
    
    # Run in selected mode
    if args.mode == 'standalone':
        return run_standalone_monitor(config)
    elif args.mode == 'api':
        return run_api_mode(config, args.host, args.port, args.debug)
    else:
        print(f"❌ Unknown mode: {args.mode}")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
