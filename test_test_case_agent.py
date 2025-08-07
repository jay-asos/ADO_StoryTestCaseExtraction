#!/usr/bin/env python3
"""
Test script to verify the Test Case Extraction Agent functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.test_case_extractor import TestCaseExtractor
from src.models import UserStory

def test_test_case_extraction():
    """Test the test case extraction functionality"""
    
    # Create a sample user story
    sample_story = UserStory(
        heading="User Login Feature",
        description="As a user, I want to be able to log into the system using my email and password so that I can access my personalized dashboard and account information.",
        acceptance_criteria=[
            "User can enter valid email and password and successfully log in",
            "System displays appropriate error message for invalid credentials",
            "User remains logged in across browser sessions if 'Remember Me' is selected",
            "Account is locked after 3 failed login attempts",
            "User can reset password through email verification"
        ]
    )
    
    print("🧪 Testing Test Case Extraction Agent")
    print("=" * 50)
    
    print(f"\n📋 Sample User Story: {sample_story.heading}")
    print(f"Description: {sample_story.description}")
    print(f"Acceptance Criteria: {len(sample_story.acceptance_criteria)} items")
    
    # Initialize the test case extractor
    try:
        print("\n🔧 Initializing Test Case Extractor...")
        extractor = TestCaseExtractor()
        print("✅ Test Case Extractor initialized successfully")
        
        # Extract test cases
        print("\n🚀 Extracting test cases...")
        result = extractor.extract_test_cases(sample_story, "TEST-STORY-001")
        
        if result.extraction_successful:
            print(f"✅ Successfully extracted {len(result.test_cases)} test cases")
            print(f"📊 Story: {result.story_title} (ID: {result.story_id})")
            
            # Display test cases by type
            positive_tests = [tc for tc in result.test_cases if tc.test_type == "positive"]
            negative_tests = [tc for tc in result.test_cases if tc.test_type == "negative"]
            edge_tests = [tc for tc in result.test_cases if tc.test_type == "edge"]
            
            print(f"\n📈 Test Coverage:")
            print(f"  • Positive Tests: {len(positive_tests)}")
            print(f"  • Negative Tests: {len(negative_tests)}")
            print(f"  • Edge Cases: {len(edge_tests)}")
            
            print(f"\n🔍 Detailed Test Cases:")
            print("-" * 50)
            
            for i, test_case in enumerate(result.test_cases, 1):
                print(f"\n{i}. {test_case.title}")
                print(f"   Type: {test_case.test_type.upper()}")
                print(f"   Priority: {test_case.priority}")
                print(f"   Description: {test_case.description}")
                
                if test_case.preconditions:
                    print(f"   Preconditions: {len(test_case.preconditions)} items")
                
                print(f"   Test Steps: {len(test_case.test_steps)} steps")
                print(f"   Expected Result: {test_case.expected_result[:100]}{'...' if len(test_case.expected_result) > 100 else ''}")
            
            # Validate test cases
            print(f"\n🔍 Validating test cases...")
            issues = extractor.validate_test_cases(result.test_cases)
            
            if not issues:
                print("✅ All test cases passed validation")
            else:
                print(f"⚠️ Found {len(issues)} validation issues:")
                for issue in issues:
                    print(f"   • {issue}")
            
            # Test ADO format conversion
            print(f"\n🏗️ Testing ADO format conversion...")
            for test_case in result.test_cases[:2]:  # Test first 2 test cases
                ado_format = test_case.to_ado_format()
                print(f"   ✅ {test_case.title} -> ADO format OK")
                
        else:
            print(f"❌ Test case extraction failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_test_case_extraction()
