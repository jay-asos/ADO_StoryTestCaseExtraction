#!/usr/bin/env python3
"""
Simple test to verify the Test Case models and basic structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import TestCase, UserStory, TestCaseExtractionResult

def test_test_case_models():
    """Test the test case models and structure"""
    
    print("🧪 Testing Test Case Models")
    print("=" * 50)
    
    # Test TestCase model
    print("\n📋 Testing TestCase model...")
    
    test_case = TestCase(
        title="Valid Login Test",
        description="Test successful login with valid credentials",
        test_type="positive",
        preconditions=["User has valid account", "System is online"],
        test_steps=[
            "Navigate to login page",
            "Enter valid email address",
            "Enter valid password",
            "Click login button"
        ],
        expected_result="User is successfully logged in and redirected to dashboard",
        priority="High"
    )
    
    print(f"✅ TestCase created: {test_case.title}")
    print(f"   Type: {test_case.test_type}")
    print(f"   Priority: {test_case.priority}")
    print(f"   Preconditions: {len(test_case.preconditions)}")
    print(f"   Steps: {len(test_case.test_steps)}")
    
    # Test ADO format conversion
    print("\n🏗️ Testing ADO format conversion...")
    ado_format = test_case.to_ado_format()
    
    print("✅ ADO format conversion successful:")
    print(f"   Title: {ado_format['System.Title']}")
    print(f"   Description length: {len(ado_format['System.Description'])}")
    print(f"   Priority: {ado_format.get('Microsoft.VSTS.Common.Priority', 'Not set')}")
    
    # Test UserStory with test cases
    print("\n📄 Testing UserStory model...")
    
    user_story = UserStory(
        heading="User Authentication",
        description="As a user, I want to authenticate securely",
        acceptance_criteria=[
            "User can log in with valid credentials",
            "System rejects invalid credentials"
        ],
        test_cases=[test_case]
    )
    
    print(f"✅ UserStory created: {user_story.heading}")
    print(f"   Test cases: {len(user_story.test_cases)}")
    
    # Test TestCaseExtractionResult
    print("\n📊 Testing TestCaseExtractionResult...")
    
    more_test_cases = []
    for i in range(3):
        tc = TestCase(
            title=f"Test Case {i+1}",
            description=f"Description for test case {i+1}",
            test_type=["positive", "negative", "edge"][i % 3],
            test_steps=[f"Step 1 for test {i+1}", f"Step 2 for test {i+1}"],
            expected_result=f"Expected result for test {i+1}",
            priority=["High", "Medium", "Low"][i % 3]
        )
        more_test_cases.append(tc)
    
    result = TestCaseExtractionResult(
        story_id="STORY-123",
        story_title="Sample Story",
        test_cases=more_test_cases,
        extraction_successful=True
    )
    
    print(f"✅ TestCaseExtractionResult created:")
    print(f"   Story ID: {result.story_id}")
    print(f"   Story Title: {result.story_title}")
    print(f"   Test Cases: {len(result.test_cases)}")
    print(f"   Success: {result.extraction_successful}")
    
    # Test different test case types
    print("\n🔍 Test Case Types Distribution:")
    positive_count = len([tc for tc in result.test_cases if tc.test_type == "positive"])
    negative_count = len([tc for tc in result.test_cases if tc.test_type == "negative"])
    edge_count = len([tc for tc in result.test_cases if tc.test_type == "edge"])
    
    print(f"   Positive: {positive_count}")
    print(f"   Negative: {negative_count}")
    print(f"   Edge: {edge_count}")
    
    # Test priority distribution
    print("\n🎯 Priority Distribution:")
    high_priority = len([tc for tc in result.test_cases if tc.priority == "High"])
    medium_priority = len([tc for tc in result.test_cases if tc.priority == "Medium"])
    low_priority = len([tc for tc in result.test_cases if tc.priority == "Low"])
    
    print(f"   High: {high_priority}")
    print(f"   Medium: {medium_priority}")
    print(f"   Low: {low_priority}")
    
    print("\n✅ All model tests passed successfully!")
    
    # Test JSON serialization (useful for API responses)
    print("\n🔄 Testing JSON serialization...")
    try:
        import json
        
        # Convert test case to dict for JSON serialization
        tc_dict = {
            'title': test_case.title,
            'description': test_case.description,
            'test_type': test_case.test_type,
            'preconditions': test_case.preconditions,
            'test_steps': test_case.test_steps,
            'expected_result': test_case.expected_result,
            'priority': test_case.priority,
            'parent_story_id': test_case.parent_story_id
        }
        
        json_str = json.dumps(tc_dict, indent=2)
        print("✅ JSON serialization successful")
        print(f"   JSON length: {len(json_str)} characters")
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")

if __name__ == "__main__":
    test_test_case_models()
