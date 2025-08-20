"""
Test Case Extractor using OpenAI to generate comprehensive test cases from user stories
"""

import json
import logging
from typing import List, Dict, Any
import openai
from openai import OpenAI

from src.models import UserStory, TestCase, TestCaseExtractionResult
from config.settings import Settings


class TestCaseExtractor:
    """Extracts test cases from user stories using AI"""

    def __init__(self):
        self.settings = Settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)

    def extract_test_cases(self, user_story: UserStory, parent_story_id: str = None) -> TestCaseExtractionResult:
        """Extract test cases from a user story using AI"""

        try:
            self.logger.info(f"Starting test case extraction for story: {user_story.heading}")

            # Prepare the prompt for OpenAI
            prompt = self._build_extraction_prompt(user_story)

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )

            # Parse the response
            response_content = response.choices[0].message.content
            test_cases = self._parse_test_cases_response(response_content)

            return TestCaseExtractionResult(
                story_id=parent_story_id or "unknown",
                story_title=user_story.heading,
                test_cases=test_cases,
                extraction_successful=True,
                error_message=""
            )

        except Exception as e:
            error_msg = f"Failed to extract test cases: {str(e)}"
            self.logger.error(error_msg)

            return TestCaseExtractionResult(
                story_id=parent_story_id or "unknown",
                story_title=user_story.heading,
                test_cases=[],
                extraction_successful=False,
                error_message=error_msg
            )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for test case extraction"""
        return """You are an expert QA engineer specializing in creating comprehensive test cases from user stories.

Your task is to analyze user stories and generate detailed test cases that cover:
- Positive test scenarios (happy path)
- Negative test scenarios (error cases)
- Edge cases and boundary conditions
- UI/UX validation where applicable
- Data validation and business rule testing

For each test case, provide:
1. A clear, descriptive title that indicates what is being tested
2. Test type (must be one of: positive, negative, edge_case)
3. A brief description of the test objective
4. Detailed test steps (numbered list of specific actions)
5. Clear expected result (complete sentence ending with a period)
6. Prerequisites (environment, data, or system state needed)

Format your response as JSON with the following structure:
{
  "test_cases": [
    {
      "title": "Test case title",
      "description": "Brief description of what this test validates",
      "test_type": "positive|negative|edge_case",
      "steps": [
        "Step 1: Action to perform",
        "Step 2: Next action",
        "Step 3: Verification step"
      ],
      "expected_result": "Expected outcome of the test",
      "prerequisites": "Any setup needed before test execution",
      "test_data": "Specific data needed for the test"
    }
  ]
}

Ensure test cases are practical, executable, and provide good coverage of the functionality."""

    def _build_extraction_prompt(self, user_story: UserStory) -> str:
        """Build the extraction prompt from user story details"""

        prompt = f"""Please generate comprehensive test cases for the following user story:

**Story Title:** {user_story.heading}

**Description:** {user_story.description}

**Acceptance Criteria:**"""

        for i, criteria in enumerate(user_story.acceptance_criteria, 1):
            prompt += f"\n{i}. {criteria}"

        prompt += """

Generate test cases that thoroughly validate this user story, including positive scenarios, negative scenarios, and edge cases. Focus on creating practical, executable test cases that a QA engineer could implement."""

        return prompt

    def _parse_test_cases_response(self, response_content: str) -> List[TestCase]:
        """Parse the AI response into TestCase objects"""

        try:
            # Clean up the response content
            response_content = response_content.strip()

            # Handle case where response might be wrapped in markdown code blocks
            if response_content.startswith("```json"):
                response_content = response_content[7:]  # Remove ```json
            if response_content.endswith("```"):
                response_content = response_content[:-3]  # Remove ```

            # Fix common JavaScript-like syntax issues in JSON
            import re
            response_content = re.sub(r'"a"\.repeat\(\d+\)', '"a" * 255', response_content)
            response_content = re.sub(r'//.*$', '', response_content, flags=re.MULTILINE)  # Remove JS comments

            # Parse JSON
            parsed_response = json.loads(response_content)
            test_cases_data = parsed_response.get("test_cases", [])

            test_cases = []
            for tc_data in test_cases_data:
                # Handle field name mismatch: steps vs test_steps
                steps = tc_data.get("test_steps", tc_data.get("steps", []))

                # Ensure prerequisites is a list if it's a string
                prerequisites = tc_data.get("prerequisites", "")
                if isinstance(prerequisites, str):
                    prerequisites = [prerequisites] if prerequisites else []

                # Format test steps as numbered steps if they're not already
                formatted_steps = []
                for i, step in enumerate(steps, 1):
                    if not step.strip().startswith(str(i)):
                        formatted_steps.append(f"{i}. {step}")
                    else:
                        formatted_steps.append(step)

                # Ensure expected result is a complete sentence
                expected_result = tc_data.get("expected_result", "")
                if not expected_result.endswith('.'):
                    expected_result += '.'

                # Generate a descriptive title if none provided
                title = tc_data.get("title")
                if not title:
                    # Create a title from test description or first test step
                    description = tc_data.get("description", "").strip()
                    first_step = next((step for step in formatted_steps if step), "")
                    title = description or first_step.split(".", 1)[-1].strip() or "Validate User Story"

                test_case = TestCase(
                    title=title,
                    description=tc_data.get("description", ""),
                    test_type=tc_data.get("test_type", "positive"),
                    test_steps=formatted_steps,
                    expected_result=expected_result,
                    preconditions=prerequisites,
                    priority=tc_data.get("priority", "Medium"),
                    parent_story_id=None
                )
                test_cases.append(test_case)

            self.logger.info(f"Successfully parsed {len(test_cases)} test cases")
            return test_cases

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            self.logger.error(f"Response content: {response_content}")

            # Fallback: Try to extract test cases using text parsing
            return self._fallback_parse_test_cases(response_content)

        except Exception as e:
            self.logger.error(f"Error parsing test cases: {str(e)}")
            return []

    def _fallback_parse_test_cases(self, content: str) -> List[TestCase]:
        """Fallback method to parse test cases when JSON parsing fails"""

        test_cases = []

        # Simple text-based parsing as fallback
        lines = content.split('\n')
        current_test = None

        for line in lines:
            line = line.strip()
            if line.startswith('Title:') or line.startswith('Test:') or line.startswith('TC'):
                if current_test:
                    test_cases.append(current_test)

                title = line.split(':', 1)[1].strip() if ':' in line else line
                current_test = TestCase(
                    title=title,
                    description="Parsed from AI response",
                    test_type="positive",
                    steps=[],
                    expected_result="",
                    prerequisites="",
                    test_data=""
                )
            elif current_test and line:
                if line.startswith('Steps:') or line.startswith('Expected:'):
                    continue
                elif line.startswith('-') or line.startswith('•'):
                    current_test.steps.append(line[1:].strip())

        if current_test:
            test_cases.append(current_test)

        self.logger.info(f"Fallback parsing extracted {len(test_cases)} test cases")
        return test_cases
