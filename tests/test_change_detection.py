#!/usr/bin/env python3
"""
Test script to demonstrate EPIC change detection capabilities and limitations.

This script tests the current change detection system and proposes improvements.
"""

from src.monitor import EpicChangeMonitor, MonitorConfig
from src.agent import StoryExtractionAgent
import json
import time

def test_change_detection():
    """Test the change detection system comprehensively"""
    
    print("=" * 60)
    print("EPIC Change Detection System Analysis")
    print("=" * 60)
    
    # Configure with different settings to test behavior
    configs = {
        'restrictive': {
            'skip_duplicate_check': False,
            'auto_sync': True,
            'poll_interval_seconds': 1800,
            'epic_ids': [],
            'auto_extract_new_epics': True,
            'log_level': 'INFO'
        },
        'permissive': {
            'skip_duplicate_check': True,
            'auto_sync': True,
            'poll_interval_seconds': 1800,
            'epic_ids': [],
            'auto_extract_new_epics': True,
            'log_level': 'INFO'
        }
    }
    
    # Test EPIC 151 (has existing stories)
    epic_id = '151'
    
    for config_name, config_data in configs.items():
        print(f"\n{config_name.upper()} CONFIGURATION TEST")
        print("-" * 40)
        
        config = MonitorConfig(**config_data)
        monitor = EpicChangeMonitor(config)
        
        # Add EPIC to monitoring
        success = monitor.add_epic(epic_id)
        print(f"Added EPIC {epic_id} to monitoring: {success}")
        
        epic_state = monitor.monitored_epics.get(epic_id)
        if epic_state:
            print(f"EPIC state:")
            print(f"  - stories_extracted: {epic_state.stories_extracted}")
            print(f"  - in processed_epics: {epic_id in monitor.processed_epics}")
            print(f"  - has_snapshot: {epic_state.last_snapshot is not None}")
        
        # Test change detection methods
        print(f"\nChange Detection Tests:")
        
        # 1. Content change detection
        content_changes = monitor._check_for_epic_changes(epic_id)
        print(f"  1. Content changes detected: {content_changes}")
        
        # 2. Should extract stories
        should_extract = monitor._should_extract_stories(epic_id)
        print(f"  2. Should extract stories: {should_extract}")
        
        # 3. Force check
        force_result = monitor.force_check(epic_id)
        has_changes = force_result.get(epic_id, {}).get('has_changes', False)
        print(f"  3. Force check has changes: {has_changes}")
        
        # Summary for this configuration
        will_create_stories = content_changes and should_extract
        print(f"\nSUMMARY for {config_name} config:")
        print(f"  - Will create new stories if changes detected: {will_create_stories}")
        print(f"  - Reason: {'✓ Both change detection and extraction logic pass' if will_create_stories else '✗ Extraction blocked by processed EPIC state'}")

def demonstrate_issue():
    """Demonstrate the core issue with change-based story extraction"""
    
    print("\n" + "=" * 60)
    print("CORE ISSUE DEMONSTRATION")
    print("=" * 60)
    
    print("""
The current system has a fundamental limitation:

1. ✅ DETECTION: The system CAN detect changes in EPICs (title, description, state)
2. ❌ ACTION: But it WON'T create new stories for EPICs that already have stories

This happens because:
- The _should_extract_stories() method checks if stories_extracted = True
- If True, it immediately returns False, regardless of the skip_duplicate_check setting
- Even significant EPIC changes won't trigger new story creation

EXAMPLE SCENARIO:
1. EPIC 151: "Change Team Member Role to Admin via REST API" (has 3 stories)
2. You update the EPIC with major new requirements
3. System detects the change ✅
4. System decides NOT to extract stories ❌ (because stories_extracted = True)
5. Result: New requirements are ignored
""")

def propose_solution():
    """Propose a solution for change-based story extraction"""
    
    print("\n" + "=" * 60)
    print("PROPOSED SOLUTION")
    print("=" * 60)
    
    print("""
OPTION 1: Modify _should_extract_stories() logic
- Add a configuration option: enable_change_based_extraction
- When enabled, allow story extraction if significant changes are detected
- Compare current vs. previous snapshots and calculate a "change significance score"

OPTION 2: Add incremental story extraction
- Create new stories only for new/changed content sections
- Use AI to identify which parts of the EPIC are new/modified
- Generate stories for only the incremental changes

OPTION 3: Manual override for changed EPICs  
- Add a "force re-extraction" feature in the dashboard
- Allow users to manually trigger story extraction for changed EPICs
- Clear the processed state temporarily for re-processing

RECOMMENDED: Combine all three approaches
- Automatic detection with significance scoring (Option 1)
- Smart incremental extraction (Option 2)  
- Manual override capability (Option 3)
""")

def test_with_fresh_epic():
    """Test with an EPIC that doesn't have processed state"""
    
    print("\n" + "=" * 60)
    print("TEST WITH FRESH EPIC (No processed state)")
    print("=" * 60)
    
    # Use an EPIC that hasn't been processed yet
    fresh_epic_id = '28'  # This might not be processed
    
    config = MonitorConfig(
        skip_duplicate_check=True,
        auto_sync=True,
        poll_interval_seconds=1800,
        epic_ids=[],
        auto_extract_new_epics=True,
        log_level='INFO'
    )
    
    monitor = EpicChangeMonitor(config)
    
    # Remove from processed epics if it exists
    if fresh_epic_id in monitor.processed_epics:
        monitor.processed_epics.remove(fresh_epic_id)
        print(f"Removed EPIC {fresh_epic_id} from processed list for testing")
    
    # Add to monitoring
    success = monitor.add_epic(fresh_epic_id)
    print(f"Added EPIC {fresh_epic_id} to monitoring: {success}")
    
    epic_state = monitor.monitored_epics.get(fresh_epic_id)
    if epic_state:
        print(f"EPIC state:")
        print(f"  - stories_extracted: {epic_state.stories_extracted}")
        print(f"  - in processed_epics: {fresh_epic_id in monitor.processed_epics}")
        
        # Test if this one would allow story extraction
        should_extract = monitor._should_extract_stories(fresh_epic_id)
        print(f"  - Should extract stories: {should_extract}")
        
        if should_extract:
            print("✅ This EPIC would allow story extraction if changes are detected!")
        else:
            print("❌ Even this EPIC won't allow story extraction")

if __name__ == "__main__":
    test_change_detection()
    demonstrate_issue() 
    propose_solution()
    test_with_fresh_epic()
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("""
The system CAN detect changes but WON'T act on them for processed EPICs.
This is a significant limitation for change-driven story extraction.

To enable change-based story extraction, you need to modify:
1. The _should_extract_stories() method logic
2. Add configuration options for change-based processing
3. Implement change significance scoring
4. Add manual override capabilities

The current system works well for:
✅ Initial EPIC processing (new EPICs)
✅ Change detection and logging
✅ Preventing duplicate processing

But it doesn't support:
❌ Change-driven story creation
❌ Incremental story extraction
❌ Re-processing of modified EPICs
""")
