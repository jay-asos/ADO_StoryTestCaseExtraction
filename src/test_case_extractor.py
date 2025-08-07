import json
import re
import time
from typing import List
from openai import OpenAI
from openai import RateLimitError

from config.settings import Settings
from src.models import UserStory, TestCase, TestCaseExtractionResult

class TestCaseExtractor:
    """AI-powered extractor that analyzes user stories and creates comprehensive test cases"""
    
    def __init__(self):
        Settings.validate()
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
    
    def extract_test_cases(self, user_story: UserStory, parent_story_id: str = None) -> TestCaseExtractionResult:
        """Extract test cases from a user story using AI"""
        try:
            test_cases = self._analyze_story_with_ai(user_story)
            
            # Set parent story ID for all test cases
            for test_case in test_cases:
                test_case.parent_story_id = parent_story_id or user_story.heading
            
            return TestCaseExtractionResult(
                story_id=parent_story_id or user_story.heading,
                story_title=user_story.heading,
                test_cases=test_cases,
                extraction_successful=True
            )
            
        except Exception as e:
            return TestCaseExtractionResult(
                story_id=parent_story_id or user_story.heading,
                story_title=user_story.heading,
                test_cases=[],
                extraction_successful=False,
                error_message=str(e)
            )
    
    def _analyze_story_with_ai(self, user_story: UserStory) -> List[TestCase]:
        """Use OpenAI to analyze user story and extract comprehensive test cases with retry logic"""
        
        prompt = self._build_extraction_prompt(user_story)
        retries = Settings.OPENAI_MAX_RETRIES
        delay = Settings.OPENAI_RETRY_DELAY
        
        for i in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are an expert QA engineer specialized in creating comprehensive test cases from user stories. 
                            You should extract test cases that cover:
                            - Positive scenarios (happy path)
                            - Negative scenarios (error cases, invalid inputs)
                            - Edge cases (boundary conditions, extreme values)
                            
                            Each test case should be:
                            - Clear and specific
                            - Executable by a human tester
                            - Include detailed steps and expected results
                            - Cover different types of testing scenarios
                            
                            Return your response as valid JSON only, with no additional text."""
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=3000
                )
                
                content = response.choices[0].message.content.strip()
                
                # Parse JSON response
                test_data = json.loads(content)
                
                # Convert to TestCase objects
                test_cases = []
                for test_case_data in test_data.get("test_cases", []):
                    test_case = TestCase(
                        title=test_case_data["title"],
                        description=test_case_data["description"],
                        test_type=test_case_data["test_type"],
                        preconditions=test_case_data.get("preconditions", []),
                        test_steps=test_case_data["test_steps"],
                        expected_result=test_case_data["expected_result"],
                        priority=test_case_data.get("priority", "Medium")
                    )
                    test_cases.append(test_case)
                
                return test_cases
                
            except RateLimitError:
                if i < retries - 1:
                    print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    raise Exception("Rate limit still exceeded after multiple retries.")
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
            except Exception as e:
                raise Exception(f"AI analysis failed: {str(e)}")
        
        return []
    
    def _build_extraction_prompt(self, user_story: UserStory) -> str:
        """Build the prompt for AI test case extraction"""
        acceptance_criteria_text = "\n".join([f"- {criteria}" for criteria in user_story.acceptance_criteria])
        
        return f"""
Please analyze the following user story and create comprehensive test cases covering positive, negative, and edge case scenarios.

**User Story Title:** {user_story.heading}

**User Story Description:** 
{user_story.description}

**Acceptance Criteria:**
{acceptance_criteria_text}

**Instructions:**
1. Create 4-8 test cases that thoroughly test this user story
2. Include at least 2 positive test cases (happy path scenarios)
3. Include at least 2 negative test cases (error scenarios, invalid inputs)
4. Include at least 1 edge case (boundary conditions, extreme values)
5. Each test case should have clear, executable steps
6. Ensure test cases are independent and can be run separately
7. Set appropriate priority (High/Medium/Low) based on criticality

**Required JSON Response Format:**
{{
    "test_cases": [
        {{
            "title": "Clear, descriptive test case title",
            "description": "What this test case validates",
            "test_type": "positive|negative|edge",
            "preconditions": [
                "Prerequisite 1",
                "Prerequisite 2"
            ],
            "test_steps": [
                "Step 1: Action to perform",
                "Step 2: Next action",
                "Step 3: Final action"
            ],
            "expected_result": "Clear description of expected outcome",
            "priority": "High|Medium|Low"
        }}
    ]
}}

**Test Type Guidelines:**
- positive: Normal flow, valid inputs, expected user behavior
- negative: Invalid inputs, error conditions, unauthorized access
- edge: Boundary values, extreme conditions, limit testing

Return only valid JSON, no additional text.
"""
    
    def validate_test_cases(self, test_cases: List[TestCase]) -> List[str]:
        """Validate extracted test cases and return any issues found"""
        issues = []
        
        # Check for minimum coverage
        positive_tests = [tc for tc in test_cases if tc.test_type == "positive"]
        negative_tests = [tc for tc in test_cases if tc.test_type == "negative"]
        edge_tests = [tc for tc in test_cases if tc.test_type == "edge"]
        
        if len(positive_tests) < 1:
            issues.append("At least 1 positive test case is required")
        if len(negative_tests) < 1:
            issues.append("At least 1 negative test case is required")
        if len(edge_tests) < 1:
            issues.append("At least 1 edge case test is recommended")
        
        for i, test_case in enumerate(test_cases):
            test_num = i + 1
            
            # Check title
            if not test_case.title or len(test_case.title.strip()) < 5:
                issues.append(f"Test Case {test_num}: Title too short or missing")
            
            # Check description
            if not test_case.description or len(test_case.description.strip()) < 10:
                issues.append(f"Test Case {test_num}: Description too short or missing")
            
            # Check test steps
            if not test_case.test_steps or len(test_case.test_steps) < 1:
                issues.append(f"Test Case {test_num}: At least one test step required")
            
            # Check expected result
            if not test_case.expected_result or len(test_case.expected_result.strip()) < 5:
                issues.append(f"Test Case {test_num}: Expected result too short or missing")
            
            # Validate test type
            if test_case.test_type not in ["positive", "negative", "edge"]:
                issues.append(f"Test Case {test_num}: Invalid test type '{test_case.test_type}'")
            
            # Validate priority
            if test_case.priority not in ["High", "Medium", "Low"]:
                issues.append(f"Test Case {test_num}: Invalid priority '{test_case.priority}'")
        
        return issues
