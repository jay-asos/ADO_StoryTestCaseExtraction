#!/usr/bin/env python3
"""
Enhanced CLI for ADO Story Extractor with EPIC change detection and synchronization.
"""

import argparse
import sys
import json
from typing import Optional, Dict

from src.agent import StoryExtractionAgent
from config.settings import Settings

def print_separator():
    print("=" * 60)

def print_epic_sync_result(result):
    """Print the results of EPIC synchronization"""
    print(f"\n📊 EPIC Synchronization Results:")
    print(f"   EPIC ID: {result.epic_id}")
    print(f"   EPIC Title: {result.epic_title}")
    print(f"   Success: {'✅' if result.sync_successful else '❌'}")
    
    if result.sync_successful:
        print(f"   📝 Created Stories: {len(result.created_stories)} ({result.created_stories})")
        print(f"   🔄 Updated Stories: {len(result.updated_stories)} ({result.updated_stories})")
        print(f"   ⏸️  Unchanged Stories: {len(result.unchanged_stories)} ({result.unchanged_stories})")
        
        total_changes = len(result.created_stories) + len(result.updated_stories)
        print(f"   📈 Total Changes: {total_changes}")
    else:
        print(f"   ❌ Error: {result.error_message}")

def sync_epic_command(agent: StoryExtractionAgent, epic_id: str, snapshot_file: Optional[str] = None):
    """Synchronize an EPIC with change detection"""
    print(f"🔄 Synchronizing EPIC {epic_id}...")
    
    # Load stored snapshot if provided
    stored_snapshot = None
    if snapshot_file:
        try:
            with open(snapshot_file, 'r') as f:
                stored_snapshot = json.load(f)
            print(f"📁 Loaded snapshot from {snapshot_file}")
        except FileNotFoundError:
            print(f"⚠️  Snapshot file {snapshot_file} not found, treating as initial sync")
        except Exception as e:
            print(f"❌ Error loading snapshot: {e}")
            return
    
    # Perform synchronization
    result = agent.synchronize_epic(epic_id, stored_snapshot)
    print_epic_sync_result(result)
    
    # Save new snapshot if sync was successful
    if result.sync_successful and snapshot_file:
        new_snapshot = agent.get_epic_snapshot(epic_id)
        if new_snapshot:
            try:
                with open(snapshot_file, 'w') as f:
                    json.dump(new_snapshot, f, indent=2)
                print(f"💾 Updated snapshot saved to {snapshot_file}")
            except Exception as e:
                print(f"❌ Error saving snapshot: {e}")

def preview_epic_changes(agent: StoryExtractionAgent, epic_id: str):
    """Preview what changes would be made to an EPIC without applying them"""
    print(f"👁️  Previewing changes for EPIC {epic_id}...")
    
    # Get current snapshot
    current_snapshot = agent.get_epic_snapshot(epic_id)
    if current_snapshot:
        print(f"📸 Current EPIC snapshot:")
        print(f"   Title: {current_snapshot['title']}")
        print(f"   State: {current_snapshot['state']}")
        print(f"   Content Hash: {current_snapshot['content_hash'][:12]}...")
        if current_snapshot['last_modified']:
            print(f"   Last Modified: {current_snapshot['last_modified']}")
    
    # Preview stories that would be extracted
    result = agent.preview_stories(epic_id)
    if result.extraction_successful:
        print(f"\n📝 Would extract {len(result.stories)} stories:")
        for i, story in enumerate(result.stories, 1):
            print(f"   {i}. {story.heading}")
            print(f"      Description: {story.description[:100]}...")
            print(f"      Acceptance Criteria: {len(story.acceptance_criteria)} items")
    else:
        print(f"❌ Preview failed: {result.error_message}")

def test_cases_command(agent: StoryExtractionAgent, story_id: str, upload: bool = False):
    """Generate test cases for a user story"""
    print(f"🧪 Generating test cases for User Story {story_id}...")
    
    try:
        # Extract test cases
        result = agent.extract_test_cases_for_story(story_id)
        
        if not result.extraction_successful:
            print(f"❌ Failed to extract test cases: {result.error_message}")
            return
        
        print(f"✅ Successfully generated {len(result.test_cases)} test cases")
        print(f"   📋 Story: {result.story_title}")
        print()
        
        # Display test cases by type
        positive_tests = [tc for tc in result.test_cases if tc.test_type == "positive"]
        negative_tests = [tc for tc in result.test_cases if tc.test_type == "negative"]
        edge_tests = [tc for tc in result.test_cases if tc.test_type == "edge"]
        
        print(f"📊 Test Case Distribution:")
        print(f"  🟢 Positive Tests: {len(positive_tests)}")
        print(f"  🔴 Negative Tests: {len(negative_tests)}")
        print(f"  🟡 Edge Case Tests: {len(edge_tests)}")
        print()
        
        # Display each test case
        for i, test_case in enumerate(result.test_cases, 1):
            type_icon = "🟢" if test_case.test_type == "positive" else "🔴" if test_case.test_type == "negative" else "🟡"
            print(f"{type_icon} Test Case {i}: {test_case.title}")
            print(f"   Type: {test_case.test_type.upper()}")
            print(f"   Priority: {test_case.priority}")
            print(f"   Description: {test_case.description}")
            
            if test_case.preconditions:
                print(f"   Preconditions: {len(test_case.preconditions)} items")
                for j, precond in enumerate(test_case.preconditions, 1):
                    print(f"     {j}. {precond}")
            
            print(f"   Test Steps: {len(test_case.test_steps)} steps")
            for j, step in enumerate(test_case.test_steps, 1):
                print(f"     {j}. {step}")
            
            print(f"   Expected Result: {test_case.expected_result}")
            print()
        
        if upload:
            print(f"📤 Uploading test cases to Azure DevOps...")
            try:
                # For now, we'll skip the actual upload in CLI and just show what would be uploaded
                print("⚠️  Note: Upload functionality requires the story to be converted to UserStory format.")
                print("   Use the web dashboard or API for uploading test cases.")
            except Exception as e:
                print(f"❌ Upload failed: {str(e)}")
                return
        
    except Exception as e:
        print(f"💥 Error generating test cases: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced ADO Story Extractor with EPIC synchronization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Synchronize an EPIC and detect changes
  python main_enhanced.py sync-epic 12345
  
  # Synchronize with snapshot tracking
  python main_enhanced.py sync-epic 12345 --snapshot snapshots/epic_12345.json
  
  # Preview changes without applying them
  python main_enhanced.py preview-epic 12345
  
  # Process single requirement (original functionality)  
  python main_enhanced.py process 12345
  
  # Process all requirements
  python main_enhanced.py process-all

  # Generate test cases for a user story
  python main_enhanced.py test-cases 67890
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync EPIC command
    sync_parser = subparsers.add_parser('sync-epic', help='Synchronize an EPIC with change detection')
    sync_parser.add_argument('epic_id', help='EPIC ID to synchronize')
    sync_parser.add_argument('--snapshot', help='Path to snapshot file for change tracking')
    
    # Preview EPIC command
    preview_parser = subparsers.add_parser('preview-epic', help='Preview changes for an EPIC')
    preview_parser.add_argument('epic_id', help='EPIC ID to preview')
    
    # Test cases command
    test_cases_parser = subparsers.add_parser('test-cases', help='Generate test cases for a user story')
    test_cases_parser.add_argument('story_id', help='User Story ID to generate test cases for')
    test_cases_parser.add_argument('--upload', action='store_true', help='Upload test cases to ADO')
    
    # Original commands
    process_parser = subparsers.add_parser('process', help='Process a single requirement')
    process_parser.add_argument('requirement_id', help='Requirement ID to process')
    process_parser.add_argument('--no-upload', action='store_true', help='Preview only, do not upload to ADO')
    
    process_all_parser = subparsers.add_parser('process-all', help='Process all requirements')
    process_all_parser.add_argument('--state', help='Filter by state (e.g., Active, New)')
    process_all_parser.add_argument('--no-upload', action='store_true', help='Preview only, do not upload to ADO')
    
    summary_parser = subparsers.add_parser('summary', help='Get summary of a requirement')
    summary_parser.add_argument('requirement_id', help='Requirement ID to summarize')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Validate settings
    try:
        Settings.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please ensure all required environment variables are set.")
        return
    
    print_separator()
    print("🚀 Enhanced ADO Story Extractor")
    print_separator()
    
    # Initialize agent
    agent = StoryExtractionAgent()
    
    try:
        if args.command == 'sync-epic':
            sync_epic_command(agent, args.epic_id, args.snapshot)
            
        elif args.command == 'preview-epic':
            preview_epic_changes(agent, args.epic_id)
            
        elif args.command == 'test-cases':
            upload = args.upload
            test_cases_command(agent, args.story_id, upload)
            
        elif args.command == 'process':
            upload = not args.no_upload
            result = agent.process_requirement_by_id(args.requirement_id, upload_to_ado=upload)
            if result.extraction_successful:
                print(f"✅ Successfully processed requirement {args.requirement_id}")
                print(f"📝 Extracted {len(result.stories)} user stories")
                for i, story in enumerate(result.stories, 1):
                    print(f"   {i}. {story.heading}")
            else:
                print(f"❌ Failed to process requirement: {result.error_message}")
                
        elif args.command == 'process-all':
            upload = not args.no_upload
            results = agent.process_all_requirements(state_filter=args.state, upload_to_ado=upload)
            successful = len([r for r in results if r.extraction_successful])
            total_stories = sum(len(r.stories) for r in results)
            print(f"✅ Processed {successful}/{len(results)} requirements successfully")
            print(f"📝 Total stories extracted: {total_stories}")
            
        elif args.command == 'summary':
            summary = agent.get_requirement_summary(args.requirement_id)
            if 'error' in summary:
                print(f"❌ {summary['error']}")
            else:
                req = summary['requirement']
                children = summary['child_stories']
                print(f"📋 Requirement Summary:")
                print(f"   ID: {req['id']}")
                print(f"   Title: {req['title']}")
                print(f"   State: {req['state']}")
                print(f"   Description: {req['description']}")
                print(f"   Child Stories: {children['count']} ({children['ids']})")
                
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    print_separator()
    print("✅ Operation completed successfully!")

if __name__ == "__main__":
    sys.exit(main())
