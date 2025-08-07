#!/usr/bin/env python3

print("[STARTUP] Program starting...")

import argparse
import sys
from src.agent import StoryExtractionAgent
from config.settings import Settings

print("[STARTUP] Settings and Agent imported")

def main():
    print("[MAIN] Entering main function")
    parser = argparse.ArgumentParser(description="Extract user stories from ADO requirements using AI")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process single requirement
    process_cmd = subparsers.add_parser('process', help='Process a single requirement')
    process_cmd.add_argument('requirement_id', type=str, help='ID of the requirement to process (can be string or int)')
    process_cmd.add_argument('--no-upload', action='store_true', help='Do not upload extracted stories to ADO')

    # Process all requirements
    process_all_cmd = subparsers.add_parser('process-all', help='Process all requirements')
    process_all_cmd.add_argument('--state', type=str, help='Filter requirements by state (e.g., "Active", "New")')
    process_all_cmd.add_argument('--no-upload', action='store_true', help='Extract stories but do not upload to ADO')
    
    # Preview stories
    preview_cmd = subparsers.add_parser('preview', help='Preview extracted stories without uploading')
    preview_cmd.add_argument('requirement_id', type=str, help='ID of the requirement to preview (can be string or int)')

    # Get summary
    summary_cmd = subparsers.add_parser('summary', help='Get requirement summary')
    summary_cmd.add_argument('requirement_id', type=str, help='ID of the requirement (can be string or int)')

    # Validate config
    config_cmd = subparsers.add_parser('validate-config', help='Validate configuration settings')
    
    # Check work item types
    types_cmd = subparsers.add_parser('check-types', help='Check available work item types in the project')
    
    # Show ADO format
    format_cmd = subparsers.add_parser('show-format', help='Show how stories will be formatted in Azure DevOps')
    format_cmd.add_argument('requirement_id', type=str, help='ID of the requirement to show format for')
    
   # Extract test cases as issues
    extract_test_cases_cmd = subparsers.add_parser('extract-test-cases', help='Extract test cases for a user story and create them as Issues')
    extract_test_cases_cmd.add_argument('story_id', type=str, help='ID of the user story to extract test cases for')
    extract_test_cases_cmd.add_argument('--no-upload', action='store_true', help='Extract test cases but do not create Issues in ADO')

    # Extract test cases for epic
    extract_epic_tests_cmd = subparsers.add_parser('extract-epic-test-cases', help='Extract test cases for all stories in an epic as Issues')
    extract_epic_tests_cmd.add_argument('epic_id', type=str, help='ID of the epic to extract test cases for')
    extract_epic_tests_cmd.add_argument('--no-upload', action='store_true', help='Extract test cases but do not create Issues in ADO')

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        print(f"[DEBUG] Starting command: {args.command}")
        if args.command == 'validate-config':
            validate_config()
            return
        
        # Initialize agent for all commands except validate-config
        agent = StoryExtractionAgent()

        if args.command == 'process':
            print(f"[DEBUG] Processing requirement ID: {args.requirement_id}")
            result = agent.process_requirement_by_id(
                args.requirement_id, 
                upload_to_ado=not args.no_upload
            )
            print(f"\n[RESULT] Processing completed for requirement ID: {args.requirement_id}")
            print(f"Extraction Successful: {getattr(result, 'extraction_successful', False)}")
            if getattr(result, 'error_message', None):
                print(f"Error: {result.error_message}")
            if hasattr(result, 'stories') and result.stories:
                print(f"Stories Extracted: {len(result.stories)}")
                for i, story in enumerate(result.stories, 1):
                    print(f"  Story {i}: {getattr(story, 'heading', '')}")
            else:
                print("No stories extracted.")
            return

        elif args.command == 'process-all':
            results = agent.process_all_requirements(
                state_filter=args.state,
                upload_to_ado=not args.no_upload
            )
            print_batch_results(results)
        
        elif args.command == 'preview':
            result = agent.preview_stories(args.requirement_id)
            print_extraction_result(result, preview=True)
        
        elif args.command == 'summary':
            summary = agent.get_requirement_summary(args.requirement_id)
            print_summary(summary)
        
        elif args.command == 'check-types':
            check_work_item_types(agent)
        
        elif args.command == 'show-format':
            show_ado_format(agent, args.requirement_id)

        elif args.command == 'extract-test-cases':
            extract_test_cases(agent, args.story_id, not args.no_upload)

        elif args.command == 'extract-epic-test-cases':
            extract_epic_test_cases(agent, args.epic_id, not args.no_upload)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def validate_config():
    """Validate configuration settings"""
    try:
        Settings.validate()
        print("✅ Configuration is valid")
        print(f"Organization: {Settings.ADO_ORGANIZATION}")
        print(f"Project: {Settings.ADO_PROJECT}")
        print(f"Base URL: {Settings.ADO_BASE_URL}")
        print("✅ All required settings are present")
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}", file=sys.stderr)
        print("\nPlease check your .env file and ensure all required variables are set:")
        print("- ADO_ORGANIZATION")
        print("- ADO_PROJECT")
        print("- ADO_PAT")
        print("- OPENAI_API_KEY")
        sys.exit(1)

def print_extraction_result(result, preview=False):
    """Print the result of story extraction"""
    print(f"\n{'='*60}")
    print(f"Requirement #{result.requirement_id}: {result.requirement_title}")
    print(f"{'='*60}")
    
    if not result.extraction_successful:
        print(f"❌ Extraction failed: {result.error_message}")
        return
    
    if not result.stories:
        print("No stories extracted from this requirement.")
        return
    
    print(f"✅ Successfully extracted {len(result.stories)} user stories")
    if preview:
        print("(Preview mode - stories not uploaded to ADO)\n")
    else:
        print("(Stories uploaded to ADO)\n")
    
    for i, story in enumerate(result.stories, 1):
        print(f"Story {i}: {story.heading}")
        print(f"Description: {story.description}")
        print("Acceptance Criteria:")
        for j, criteria in enumerate(story.acceptance_criteria, 1):
            print(f"  {j}. {criteria}")
        print("-" * 40)

def print_batch_results(results):
    """Print results from batch processing"""
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING RESULTS")
    print(f"{'='*60}")
    
    successful = [r for r in results if r.extraction_successful]
    failed = [r for r in results if not r.extraction_successful]
    total_stories = sum(len(r.stories) for r in successful)
    
    print(f"Total requirements processed: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total stories extracted: {total_stories}")
    
    if failed:
        print(f"\n❌ Failed requirements:")
        for result in failed:
            print(f"  - #{result.requirement_id}: {result.error_message}")
    
    if successful:
        print(f"\n✅ Successful requirements:")
        for result in successful:
            print(f"  - #{result.requirement_id}: {len(result.stories)} stories extracted")

def print_summary(summary):
    """Print requirement summary"""
    if "error" in summary:
        print(f"❌ Error: {summary['error']}")
        return
    
    req = summary["requirement"]
    stories = summary["child_stories"]
    
    print(f"\n{'='*60}")
    print(f"REQUIREMENT SUMMARY")
    print(f"{'='*60}")
    print(f"ID: {req['id']}")
    print(f"Title: {req['title']}")
    print(f"State: {req['state']}")
    print(f"Description: {req['description']}")
    print(f"\nChild Stories: {stories['count']}")
    if stories['ids']:
        print(f"Story IDs: {', '.join(map(str, stories['ids']))}")

def check_work_item_types(agent):
    """Check available work item types in the project"""
    try:
        work_item_types = agent.ado_client.get_work_item_types()
        
        print(f"\n{'='*60}")
        print(f"AVAILABLE WORK ITEM TYPES")
        print(f"{'='*60}")
        print(f"Project: {Settings.ADO_PROJECT}")
        print(f"Organization: {Settings.ADO_ORGANIZATION}")
        print(f"\nFound {len(work_item_types)} work item types:")
        
        for i, work_type in enumerate(work_item_types, 1):
            print(f"  {i}. {work_type}")
        
        print(f"\n{'='*60}")
        print(f"CURRENT CONFIGURATION")
        print(f"{'='*60}")
        print(f"Requirement Type: {Settings.REQUIREMENT_TYPE}")
        print(f"User Story Type: {Settings.USER_STORY_TYPE}")
        
        # Check if configured types exist
        if Settings.REQUIREMENT_TYPE in work_item_types:
            print(f"✅ Requirement type '{Settings.REQUIREMENT_TYPE}' is available")
        else:
            print(f"❌ Requirement type '{Settings.REQUIREMENT_TYPE}' is NOT available")
            
        if Settings.USER_STORY_TYPE in work_item_types:
            print(f"✅ User story type '{Settings.USER_STORY_TYPE}' is available")
        else:
            print(f"❌ User story type '{Settings.USER_STORY_TYPE}' is NOT available")
            print("\n💡 Suggested alternatives:")
            for work_type in work_item_types:
                if any(keyword in work_type.lower() for keyword in ['story', 'task', 'item', 'backlog']):
                    print(f"   - {work_type}")
        
    except Exception as e:
        print(f"❌ Error checking work item types: {str(e)}")

def show_ado_format(agent, requirement_id):
    """Show how stories will be formatted in Azure DevOps"""
    try:
        result = agent.preview_stories(requirement_id)
        
        if not result.extraction_successful:
            print(f"❌ Failed to extract stories: {result.error_message}")
            return
        
        print(f"\n{'='*80}")
        print(f"AZURE DEVOPS WORK ITEM FORMAT PREVIEW")
        print(f"{'='*80}")
        print(f"Requirement: {result.requirement_title}")
        print(f"Stories will be created as: {Settings.USER_STORY_TYPE}")
        print(f"\nTotal Stories: {len(result.stories)}")
        
        for i, story in enumerate(result.stories, 1):
            ado_format = story.to_ado_format()
            
            print(f"\n{'-'*80}")
            print(f"STORY {i} - ADO WORK ITEM FIELDS:")
            print(f"{'-'*80}")
            
            print(f"\n🏷️  System.Title:")
            print(f"{ado_format['System.Title']}")
            
            print(f"\n📝 System.Description:")
            print(f"{ado_format['System.Description']}")
            
            print(f"\n📊 Work Item Type: {Settings.USER_STORY_TYPE}")
        
        print(f"\n{'='*80}")
        print(f"NOTE: The acceptance criteria are now included in the Description field")
        print(f"as requested, formatted with bullet points and a clear heading.")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"❌ Error showing ADO format: {str(e)}")

def extract_test_cases(agent, story_id, upload_to_ado):
    """Extract test cases for a user story and create them as Issues"""
    try:
        result = agent.extract_test_cases_as_issues(story_id, upload_to_ado=upload_to_ado)

        print(f"\n{'='*60}")
        print(f"TEST CASE EXTRACTION RESULTS")
        print(f"{'='*60}")
        print(f"Story ID: {story_id}")
        print(f"Story Title: {result.story_title}")

        if not result.extraction_successful:
            print(f"❌ Extraction failed: {result.error_message}")
            return

        print(f"✅ Successfully extracted {len(result.test_cases)} test cases")
        if upload_to_ado and result.created_issue_ids:
            print(f"✅ Created {len(result.created_issue_ids)} Issues in ADO")
            print(f"Issue IDs: {', '.join(map(str, result.created_issue_ids))}")
        elif upload_to_ado:
            print("(Test cases extracted but no Issues were created)")
        else:
            print("(Preview mode - test cases not uploaded to ADO)")

        print(f"\nTest Cases:")
        for i, test_case in enumerate(result.test_cases, 1):
            print(f"\n{i}. {test_case.title}")
            print(f"   Type: {test_case.test_type}")
            print(f"   Priority: {test_case.priority}")
            print(f"   Description: {test_case.description}")
            if test_case.preconditions:
                print(f"   Preconditions: {', '.join(test_case.preconditions)}")
            print(f"   Steps: {len(test_case.test_steps)} steps")
            print(f"   Expected: {test_case.expected_result}")

    except Exception as e:
        print(f"❌ Error extracting test cases: {str(e)}")

def extract_epic_test_cases(agent, epic_id, upload_to_ado):
    """Extract test cases for all stories in an epic as Issues"""
    try:
        results = agent.extract_test_cases_for_epic_stories(epic_id, upload_to_ado=upload_to_ado)

        print(f"\n{'='*60}")
        print(f"EPIC TEST CASE EXTRACTION RESULTS")
        print(f"{'='*60}")
        print(f"Epic ID: {epic_id}")

        if not results:
            print("❌ No stories found in epic or extraction failed")
            return

        successful_stories = [r for r in results.values() if r.extraction_successful]
        failed_stories = [r for r in results.values() if not r.extraction_successful]
        total_test_cases = sum(len(r.test_cases) for r in successful_stories)
        total_issues_created = sum(len(r.created_issue_ids) for r in successful_stories)

        print(f"✅ Processed {len(results)} stories")
        print(f"✅ Successfully extracted test cases from {len(successful_stories)} stories")
        print(f"Total Test Cases: {total_test_cases}")

        if upload_to_ado:
            print(f"✅ Created {total_issues_created} Issues in ADO")
        else:
            print("(Preview mode - test cases not uploaded to ADO)")

        if failed_stories:
            print(f"\n❌ Failed stories: {len(failed_stories)}")
            for story in failed_stories:
                print(f"   Story {story.story_id}: {story.error_message}")

        print(f"\nStory Summary:")
        for story_id, result in results.items():
            if result.extraction_successful:
                issue_count = len(result.created_issue_ids) if upload_to_ado else len(result.test_cases)
                print(f"   Story {story_id}: {len(result.test_cases)} test cases" +
                      (f" → {len(result.created_issue_ids)} Issues created" if upload_to_ado and result.created_issue_ids else ""))

    except Exception as e:
        print(f"❌ Error extracting epic test cases: {str(e)}")

if __name__ == "__main__":
    main()
