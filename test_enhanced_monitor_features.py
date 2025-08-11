#!/usr/bin/env python3
"""
Test script for enhanced monitor features
"""

import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.monitor import MonitorConfig, EpicChangeMonitor


def test_content_hash_functionality():
    """Test the content hashing functionality"""
    print("Testing content hash functionality...")
    
    # Create monitor with default config
    config = MonitorConfig(
        poll_interval_seconds=60,
        auto_sync=False,  # Disable auto-sync for testing
        enable_content_hash_comparison=True
    )
    
    monitor = EpicChangeMonitor(config)
    
    # Test hash calculation with sample data
    snapshot1 = {
        'title': 'Test EPIC',
        'description': 'This is a test EPIC',
        'state': 'New',
        'priority': 'High'
    }
    
    snapshot2 = {
        'title': 'Test EPIC',
        'description': 'This is a test EPIC',
        'state': 'New',
        'priority': 'High'
    }
    
    snapshot3 = {
        'title': 'Test EPIC Modified',
        'description': 'This is a test EPIC',
        'state': 'New',
        'priority': 'High'
    }
    
    hash1 = monitor._calculate_content_hash(snapshot1)
    hash2 = monitor._calculate_content_hash(snapshot2)
    hash3 = monitor._calculate_content_hash(snapshot3)
    
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    print(f"Hash 3: {hash3}")
    
    assert hash1 == hash2, "Identical snapshots should have same hash"
    assert hash1 != hash3, "Different snapshots should have different hashes"
    
    print("✅ Content hash functionality works correctly")


def test_cooldown_period():
    """Test the cooldown period functionality"""
    print("\nTesting cooldown period functionality...")
    
    config = MonitorConfig(
        extraction_cooldown_hours=1,  # 1 hour cooldown
        auto_sync=False
    )
    
    monitor = EpicChangeMonitor(config)
    
    # Test with no previous sync (should allow extraction)
    result1 = monitor._check_cooldown_period("123")
    print(f"No previous sync: {result1}")
    assert result1 == True, "Should allow extraction when no previous sync"
    
    # Simulate a recent sync
    from src.monitor import EpicMonitorState
    recent_time = (datetime.now() - timedelta(minutes=30)).isoformat()
    monitor.monitored_epics["123"] = EpicMonitorState(
        epic_id="123",
        last_check=datetime.now(),
        last_sync_result={'timestamp': recent_time, 'success': True}
    )
    
    result2 = monitor._check_cooldown_period("123", 1)
    print(f"Recent sync (30 min ago): {result2}")
    assert result2 == False, "Should prevent extraction during cooldown"
    
    # Simulate an old sync
    old_time = (datetime.now() - timedelta(hours=2)).isoformat()
    monitor.monitored_epics["123"].last_sync_result['timestamp'] = old_time
    
    result3 = monitor._check_cooldown_period("123", 1)
    print(f"Old sync (2 hours ago): {result3}")
    assert result3 == True, "Should allow extraction after cooldown"
    
    print("✅ Cooldown period functionality works correctly")


def test_reset_processed_state():
    """Test the reset processed state functionality"""
    print("\nTesting reset processed state functionality...")
    
    config = MonitorConfig(auto_sync=False)
    monitor = EpicChangeMonitor(config)
    
    # Add an epic to processed state
    epic_id = "456"
    monitor.processed_epics.add(epic_id)
    
    from src.monitor import EpicMonitorState
    monitor.monitored_epics[epic_id] = EpicMonitorState(
        epic_id=epic_id,
        last_check=datetime.now(),
        stories_extracted=True
    )
    
    print(f"Before reset - Epic in processed: {epic_id in monitor.processed_epics}")
    print(f"Before reset - Stories extracted: {monitor.monitored_epics[epic_id].stories_extracted}")
    
    # Reset the state
    success = monitor.reset_epic_processed_state(epic_id)
    
    print(f"Reset successful: {success}")
    print(f"After reset - Epic in processed: {epic_id in monitor.processed_epics}")
    print(f"After reset - Stories extracted: {monitor.monitored_epics[epic_id].stories_extracted}")
    
    assert success == True, "Reset should be successful"
    assert epic_id not in monitor.processed_epics, "Epic should be removed from processed"
    assert monitor.monitored_epics[epic_id].stories_extracted == False, "Stories extracted should be False"
    
    print("✅ Reset processed state functionality works correctly")


def test_monitoring_statistics():
    """Test the monitoring statistics functionality"""
    print("\nTesting monitoring statistics functionality...")
    
    config = MonitorConfig(auto_sync=False)
    monitor = EpicChangeMonitor(config)
    
    # Clear any existing processed epics for clean test
    monitor.processed_epics.clear()
    
    # Add some test data
    from src.monitor import EpicMonitorState
    
    # Epic with extracted stories
    monitor.monitored_epics["100"] = EpicMonitorState(
        epic_id="100",
        last_check=datetime.now(),
        stories_extracted=True,
        extracted_stories=[{"id": "1001"}, {"id": "1002"}],
        last_sync_result={'success': True, 'timestamp': datetime.now().isoformat()},
        last_snapshot={'title': 'Epic 1'}
    )
    monitor.processed_epics.add("100")
    
    # Epic with errors
    monitor.monitored_epics["200"] = EpicMonitorState(
        epic_id="200",
        last_check=datetime.now(),
        consecutive_errors=2,
        last_sync_result={'success': False, 'timestamp': datetime.now().isoformat()}
    )
    
    # Epic without snapshot
    monitor.monitored_epics["300"] = EpicMonitorState(
        epic_id="300",
        last_check=datetime.now()
    )
    
    stats = monitor.get_monitoring_statistics()
    
    print("Monitoring Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    assert stats['total_epics_monitored'] == 3, "Should have 3 monitored epics"
    assert stats['epics_with_stories_extracted'] == 1, "Should have 1 epic with extracted stories"
    assert stats['epics_with_errors'] == 1, "Should have 1 epic with errors"
    assert stats['epics_with_snapshots'] == 1, "Should have 1 epic with snapshot"
    assert stats['total_extracted_stories'] == 2, "Should have 2 total extracted stories"
    assert stats['successful_syncs'] == 1, "Should have 1 successful sync"
    assert stats['failed_syncs'] == 1, "Should have 1 failed sync"
    
    print("✅ Monitoring statistics functionality works correctly")


def test_enhanced_status():
    """Test the enhanced status functionality"""
    print("\nTesting enhanced status functionality...")
    
    config = MonitorConfig(auto_sync=False)
    monitor = EpicChangeMonitor(config)
    
    # Add test epic
    from src.monitor import EpicMonitorState
    monitor.monitored_epics["789"] = EpicMonitorState(
        epic_id="789",
        last_check=datetime.now(),
        stories_extracted=True,
        extracted_stories=[{"id": "7001"}],
        last_snapshot={'title': 'Test Epic'}
    )
    
    status = monitor.get_status()
    
    print("Enhanced Status Keys:")
    for key in status.keys():
        print(f"  - {key}")
    
    assert 'statistics' in status, "Status should include statistics"
    assert 'monitored_epics' in status, "Status should include monitored epics"
    
    epic_status = status['monitored_epics']['789']
    assert 'stories_extracted' in epic_status, "Epic status should include stories_extracted"
    assert 'extracted_stories_count' in epic_status, "Epic status should include extracted_stories_count"
    assert epic_status['extracted_stories_count'] == 1, "Should show correct story count"
    
    print("✅ Enhanced status functionality works correctly")


def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Monitor Features")
    print("=" * 50)
    
    try:
        test_content_hash_functionality()
        test_cooldown_period()
        test_reset_processed_state()
        test_monitoring_statistics()
        test_enhanced_status()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
