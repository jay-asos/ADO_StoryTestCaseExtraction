#!/usr/bin/env python3
"""
Integration test script for ADO client test case creation
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ado_client import ADOClient
from src.models import UserStory
from src.test_case_extractor import TestCaseExtractor

def run_integration_test():
    """Test the test case creation with actual ADO integration"""
    
    print("\n🔄 Starting ADO Integration Test")
    print("=" * 50)
    
    # Create ADO client
    try:
        print("\n🔧 Initializing ADO Client...")
        ado_client = ADOClient()
        print("✅ ADO Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize ADO Client: {e}")
        return

    # Create a test story
    try:
        print("\n📝 Creating test user story...")
        story_data = {
            "System.Title": f"Test Story for Title Handling ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
            "System.Description": "This is a test story for validating test case title handling.",
            "System.State": "New"
        }
        story_id = ado_client.create_work_item("User Story", fields=story_data)["id"]
        print(f"✅ Created test story with ID: {story_id}")
    except Exception as e:
        print(f"❌ Failed to create test story: {e}")
        return

    # Define test cases with different title scenarios
    test_cases = [
        # Case 1: Explicit title
        {
            "title": "Integration Test Case - Explicit Title",
            "description": "Test case with an explicitly provided title",
            "test_type": "functional",
            "priority": "Medium",
            "test_steps": ["1. Execute test with explicit title", "2. Verify results"],
            "expected_result": "Test case is created with provided title"
        },
        # Case 2: No title but with description
        {
            "description": "Test case with descriptive text but no title",
            "test_type": "functional",
            "priority": "Medium",
            "test_steps": ["1. Execute test without title", "2. Verify title is generated from description"],
            "expected_result": "Test case is created with title from description"
        },
        # Case 3: Minimal info
        {
            "test_type": "functional",
            "priority": "Medium",
            "test_steps": ["1. Execute test with minimal info", "2. Verify default title"],
            "expected_result": "Test case is created with default title"
        }
    ]

    # Create and verify test cases
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n🧪 Creating test case {i}/3...")
            print(f"Initial title: {test_case.get('title', '(None)')}")
            print(f"Description: {test_case.get('description', '(None)')}")
            
            # Create the test case
            work_item_id = ado_client.create_test_case(test_case, str(story_id))
            
            # Verify the created test case
            work_item = ado_client.wit_client.get_work_item(id=work_item_id)
            final_title = work_item.fields.get('System.Title', '')
            
            print(f"✅ Created test case {work_item_id}")
            print(f"Final title: {final_title}")
            
        except Exception as e:
            print(f"❌ Failed to create test case {i}: {e}")
            continue

    print("\n✨ Integration test completed")

if __name__ == '__main__':
    run_integration_test()
