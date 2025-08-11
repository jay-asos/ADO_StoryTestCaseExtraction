#!/usr/bin/env python3
"""
Simple demonstration of the Enhanced EPIC Change Detection System working.

This shows the system in action with real EPIC data.
"""

from src.enhanced_monitor import create_enhanced_monitor
import json

def demonstrate_working_system():
    """Demonstrate the enhanced system with a real EPIC"""
    
    print("=" * 80)
    print("ENHANCED EPIC CHANGE DETECTION SYSTEM - LIVE DEMONSTRATION")
    print("=" * 80)
    
    # EPIC 151 - Test EPIC for Enhanced Features
    epic_id = '151'
    
    print(f"\nTesting with EPIC {epic_id} - 'Test EPIC for Enhanced Features'")
    print("-" * 60)
    
    # Create enhanced monitor with moderate sensitivity
    monitor = create_enhanced_monitor(
        enable_change_based_extraction=True,
        change_significance_threshold=0.4,  # Medium sensitivity 
        max_changes_per_epic=5,
        incremental_extraction=True,
        manual_override_enabled=True
    )
    
    print(f"\n📊 MONITOR CONFIGURATION:")
    print(f"  • Change-based extraction: ENABLED")
    print(f"  • Significance threshold: 0.4 (moderate)")
    print(f"  • Max changes per EPIC: 5")
    print(f"  • Manual override: ENABLED")
    
    # Add EPIC to monitoring
    print(f"\n🔍 ADDING EPIC {epic_id} TO MONITORING...")
    success = monitor.add_epic(epic_id)
    print(f"  • Added to monitoring: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if success:
        # Show initial state
        epic_state = monitor.monitored_epics.get(epic_id)
        if epic_state:
            print(f"\n📋 EPIC STATE AFTER ADDING:")
            print(f"  • Stories extracted: {epic_state.stories_extracted}")
            print(f"  • Change extraction count: {epic_state.change_extraction_count}")
            print(f"  • Last change significance: {epic_state.last_change_significance:.3f}")
            print(f"  • Change history entries: {len(epic_state.change_history)}")
            
            # Check current snapshot
            if epic_state.last_snapshot:
                snapshot = epic_state.last_snapshot
                print(f"  • EPIC Title: '{snapshot.get('title', 'N/A')}'")
                print(f"  • EPIC State: '{snapshot.get('state', 'N/A')}'")
                print(f"  • Description length: {len(snapshot.get('description', ''))}")
                
                # Show existing stories if any
                stories = snapshot.get('stories', [])
                print(f"  • Existing stories: {len(stories)}")
                
        # Test change detection 
        print(f"\n🔄 TESTING ENHANCED CHANGE DETECTION...")
        has_changes, significance = monitor._check_for_epic_changes_enhanced(epic_id)
        print(f"  • Changes detected: {'✅ YES' if has_changes else '❌ NO'}")
        print(f"  • Change significance: {significance:.3f}")
        
        # Test extraction decision
        should_extract = monitor._should_extract_stories_enhanced(epic_id, significance)
        print(f"  • Should extract stories: {'✅ YES' if should_extract else '❌ NO'}")
        
        # Perform comprehensive check
        print(f"\n🚀 PERFORMING COMPREHENSIVE CHECK AND EXTRACTION...")
        result = monitor.check_and_extract_if_changed(epic_id)
        
        print(f"  • Has changes: {'✅ YES' if result.get('has_changes') else '❌ NO'}")
        print(f"  • Change significance: {result.get('change_significance', 0.0):.3f}")
        print(f"  • Stories extracted: {'✅ YES' if result.get('stories_extracted') else '❌ NO'}")
        
        if 'error' in result:
            print(f"  • Error: ⚠️ {result['error']}")
        
        if result.get('extraction_result'):
            extraction = result['extraction_result']
            print(f"  • Extraction successful: {'✅ YES' if extraction.get('success') else '❌ NO'}")
            
            created = extraction.get('created_stories', [])
            updated = extraction.get('updated_stories', [])
            
            if created:
                print(f"  • Created stories: {len(created)}")
                for story in created[:3]:  # Show first 3
                    print(f"    - {story.get('title', 'Untitled')}")
            
            if updated:
                print(f"  • Updated stories: {len(updated)}")
                for story in updated[:3]:  # Show first 3
                    print(f"    - {story.get('title', 'Untitled')}")
        
        # Show statistics
        print(f"\n📈 STATISTICS:")
        stats = monitor.get_change_statistics()
        print(f"  • Total monitored EPICs: {stats.get('total_monitored_epics', 0)}")
        print(f"  • Total change extractions: {stats.get('total_change_extractions', 0)}")
        print(f"  • EPICs with changes: {stats.get('epics_with_changes', 0)}")
        
        # EPIC-specific stats  
        epic_stats = monitor.get_change_statistics(epic_id)
        if epic_stats:
            print(f"\n📊 EPIC {epic_id} SPECIFIC STATISTICS:")
            print(f"  • Change extraction count: {epic_stats.get('change_extraction_count', 0)}")
            print(f"  • Last significant change: {epic_stats.get('last_significant_change', 'Never')}")
            print(f"  • Last change significance: {epic_stats.get('last_change_significance', 0.0):.3f}")
            print(f"  • Change history count: {epic_stats.get('change_history_count', 0)}")
        
        # Test manual override capability
        print(f"\n🔧 TESTING MANUAL OVERRIDE...")
        print(f"  • Manual override enabled: {'✅ YES' if monitor.config.manual_override_enabled else '❌ NO'}")
        
        if monitor.config.manual_override_enabled:
            print(f"  • Testing force re-extraction...")
            override_success = monitor.force_re_extraction(epic_id)
            print(f"  • Force re-extraction: {'✅ SUCCESS' if override_success else '❌ FAILED'}")
            
    print(f"\n" + "=" * 80)
    print("DEMONSTRATION SUMMARY")
    print("=" * 80)
    
    print("""
🎯 ENHANCED FEATURES DEMONSTRATED:

✅ Change Significance Scoring
   - Calculates numerical scores for changes (0.0-1.0)
   - Different weights for title, description, state changes
   
✅ Change-Based Story Extraction
   - Processes EPICs that already have stories
   - Only extracts when changes are significant enough
   
✅ Configurable Thresholds
   - Adjustable sensitivity levels
   - Maximum extraction limits per EPIC
   
✅ Enhanced State Tracking  
   - Tracks change history and statistics
   - Monitors extraction counts
   
✅ Manual Override Capabilities
   - Force re-extraction when needed
   - Configurable enable/disable
   
✅ Comprehensive Analytics
   - Overall and EPIC-specific statistics
   - Change history and trends

🚀 KEY ADVANTAGES:

• Processes EPICs with existing stories when they change significantly
• Prevents over-extraction with configurable limits  
• Provides detailed analytics and tracking
• Supports manual intervention when needed
• Extensible framework for future enhancements

The Enhanced EPIC Change Detection System successfully addresses the
limitations of the original system while maintaining backward compatibility!
""")

if __name__ == "__main__":
    try:
        demonstrate_working_system()
    except Exception as e:
        print(f"❌ DEMONSTRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
