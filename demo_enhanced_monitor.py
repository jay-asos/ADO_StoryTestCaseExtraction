#!/usr/bin/env python3
"""
Demonstration script for enhanced monitor features
"""

import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.monitor import MonitorConfig, EpicChangeMonitor, load_config_from_file


def demonstrate_enhanced_features():
    """Demonstrate the enhanced monitoring features"""
    print("🚀 Enhanced EPIC Monitor Features Demo")
    print("=" * 50)
    
    # Load enhanced configuration
    config_file = "monitor_config_enhanced.json"
    try:
        config = load_config_from_file(config_file)
        print(f"✅ Loaded configuration from {config_file}")
    except:
        print(f"⚠️  Could not load {config_file}, using defaults")
        config = MonitorConfig()
    
    # Create monitor with enhanced features
    monitor = EpicChangeMonitor(config)
    
    print("\n📊 Configuration Summary:")
    print(f"  Poll Interval: {config.poll_interval_seconds} seconds")
    print(f"  Auto Sync: {config.auto_sync}")
    print(f"  Auto Extract New EPICs: {config.auto_extract_new_epics}")
    print(f"  Skip Duplicate Check: {config.skip_duplicate_check}")
    print(f"  Extraction Cooldown: {config.extraction_cooldown_hours} hours")
    print(f"  Content Hash Comparison: {config.enable_content_hash_comparison}")
    
    # Demonstrate content hash functionality
    print("\n🔍 Content Hash Demo:")
    sample_epic = {
        'title': 'Sample EPIC for Demo',
        'description': 'This is a demonstration EPIC',
        'state': 'Active',
        'priority': 'Medium'
    }
    
    hash_value = monitor._calculate_content_hash(sample_epic)
    print(f"  Content Hash: {hash_value}")
    
    # Demonstrate cooldown check
    print("\n⏰ Cooldown Period Demo:")
    cooldown_result = monitor._check_cooldown_period("demo_epic", 1)
    print(f"  Can extract stories (1 hour cooldown): {cooldown_result}")
    
    # Demonstrate statistics
    print("\n📈 Monitoring Statistics:")
    stats = monitor.get_monitoring_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Demonstrate reset functionality
    print("\n🔄 Reset Processed State Demo:")
    monitor.processed_epics.add("demo_reset_epic")
    print(f"  Before reset - Epic in processed: {'demo_reset_epic' in monitor.processed_epics}")
    
    success = monitor.reset_epic_processed_state("demo_reset_epic")
    print(f"  Reset successful: {success}")
    print(f"  After reset - Epic in processed: {'demo_reset_epic' in monitor.processed_epics}")
    
    # Demonstrate enhanced status
    print("\n📋 Enhanced Status Keys:")
    status = monitor.get_status()
    for key in status.keys():
        print(f"  - {key}")
    
    print("\n" + "=" * 50)
    print("✨ Enhanced features demonstration complete!")
    
    return monitor


def show_api_usage_examples():
    """Show how to use the new API methods"""
    print("\n💻 API Usage Examples:")
    print("-" * 30)
    
    print("""
# 1. Reset an EPIC's processed state to allow re-extraction
monitor.reset_epic_processed_state("123")

# 2. Check if an EPIC is in cooldown period
can_extract = monitor._check_cooldown_period("123", hours=12)

# 3. Calculate content hash for change detection
hash_value = monitor._calculate_content_hash(epic_snapshot)

# 4. Get detailed monitoring statistics
stats = monitor.get_monitoring_statistics()

# 5. Get enhanced status with statistics
status = monitor.get_status()

# 6. Configuration options for enhanced features
config = MonitorConfig(
    extraction_cooldown_hours=12,      # 12-hour cooldown between extractions
    enable_content_hash_comparison=True, # Use hash-based change detection
    skip_duplicate_check=False         # Enable duplicate prevention
)
""")


def main():
    """Main demonstration function"""
    try:
        monitor = demonstrate_enhanced_features()
        show_api_usage_examples()
        
        print("\n🎯 Key Benefits:")
        print("  • Prevents duplicate story creation")
        print("  • Efficient change detection with content hashing")
        print("  • Configurable cooldown periods")
        print("  • Detailed monitoring statistics")
        print("  • Reset capability for re-extraction")
        print("  • Enhanced status reporting")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
