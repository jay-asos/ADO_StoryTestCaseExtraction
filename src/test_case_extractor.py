"""
Test Case Extractor using AI to generate comprehensive test cases from user stories
"""

import json
import logging
from typing import List, Dict, Any

from src.models import UserStory, TestCase, TestCaseExtractionResult
from config.settings import Settings
from src.ai_client import get_ai_client


class TestCaseExtractor:
    """Extracts test cases from user stories using AI"""

    def __init__(self):
        self.settings = Settings()
        self.ai_client = get_ai_client()
        self.logger = logging.getLogger(__name__)
        
        # Log which AI service is being used
        ai_provider = getattr(Settings, 'AI_SERVICE_PROVIDER', 'OPENAI')
        self.logger.info(f"🤖 TestCaseExtractor: Initialized with AI provider '{ai_provider}'")
        if ai_provider == 'AZURE_OPENAI':
            deployment = getattr(Settings, 'AZURE_OPENAI_DEPLOYMENT_NAME', 'Unknown')
            self.logger.info(f"🔷 TestCaseExtractor: Using Azure OpenAI deployment '{deployment}'")
        else:
            model = getattr(Settings, 'OPENAI_MODEL', 'Unknown')
            self.logger.info(f"🔶 TestCaseExtractor: Using OpenAI model '{model}'")

    def extract_test_cases(self, user_story: UserStory, parent_story_id: str = None) -> TestCaseExtractionResult:
        """Extract test cases from a user story using AI"""

        try:
            self.logger.info(f"Starting test case extraction for story: {user_story.heading}")

            # Prepare the prompt for AI service
            prompt = self._build_extraction_prompt(user_story)

            # Call AI service with better error handling
            try:
                response_content = self.ai_client.chat_completion(
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=3000
                )
                
                # Validate that we got a response
                if not response_content or not response_content.strip():
                    raise ValueError("Empty response from AI service")
                
                self.logger.debug(f"AI response length: {len(response_content)} characters")
                
            except Exception as ai_error:
                error_msg = f"AI service error: {str(ai_error)}"
                self.logger.error(error_msg)
                
                # Return a result with a generic test case
                generic_test_case = TestCase(
                    title="Validate User Story - AI Service Unavailable",
                    description="Generic test case created when AI service was unavailable",
                    test_type="positive",
                    test_steps=[
                        "1. Review the user story requirements",
                        "2. Execute the main functionality manually",  
                        "3. Verify expected behavior",
                        "4. Document any issues found"
                    ],
                    expected_result="Functionality works as described in the user story.",
                    preconditions=["System is available for testing"],
                    priority="Medium",
                    parent_story_id=parent_story_id
                )
                
                return TestCaseExtractionResult(
                    story_id=parent_story_id or "unknown",
                    story_title=user_story.heading,
                    test_cases=[generic_test_case],
                    extraction_successful=False,
                    error_message=error_msg
                )

            # Parse the response
            test_cases = self._parse_test_cases_response(response_content)
            
            # Validate that we got some test cases
            if not test_cases:
                self.logger.warning("No test cases were extracted from AI response")
                # Create a fallback test case
                fallback_test_case = TestCase(
                    title="Manual Validation Required",
                    description="Please manually create test cases for this user story",
                    test_type="positive",
                    test_steps=["1. Review user story", "2. Create appropriate test cases"],
                    expected_result="Test cases are created and validated.",
                    preconditions=["User story is well-defined"],
                    priority="Medium",
                    parent_story_id=parent_story_id
                )
                test_cases = [fallback_test_case]

            self.logger.info(f"Successfully extracted {len(test_cases)} test cases")
            
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

For each test case, you MUST provide:
1. A clear, descriptive title that SPECIFICALLY describes what is being tested
   - Bad example: "Functional Test Case"
   - Good examples: 
     - "Verify Login with Valid Credentials"
     - "Handle Invalid Password Input"
     - "Check Email Field Maximum Length"
2. Test type (must be one of: positive, negative, edge_case)
3. A brief description of the test objective
4. Detailed test steps (numbered list of specific actions)
5. Clear expected result (complete sentence ending with a period)
6. Prerequisites (environment, data, or system state needed)

Important: The title is critical and must follow these rules:
1. Be specific to the test case's purpose
2. Always start with an action verb like Verify, Validate, Check, Test, Handle, or Ensure
3. Never use generic titles like 'Functional Test Case' or 'Test Case 1'

Examples of good titles:
- "Verify Login with Valid Credentials"
- "Test Empty Password Field Validation"
- "Handle Invalid Email Format"
- "Ensure Session Timeout After Inactivity"
- "Validate Maximum Password Length"
- "Check Error Message for Failed Login"

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
            
            # Handle extra data after JSON by finding the valid JSON portion
            # Look for the JSON object boundaries
            json_start = response_content.find('{')
            if json_start == -1:
                self.logger.warning("No JSON object found in response, trying fallback parsing")
                return self._fallback_parse_test_cases(response_content)
                
            # Find the matching closing brace for the first opening brace
            brace_count = 0
            json_end = json_start
            for i, char in enumerate(response_content[json_start:], json_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
            
            # Extract only the JSON portion
            if json_end > json_start:
                json_content = response_content[json_start:json_end]
                self.logger.debug(f"Extracted JSON content: {json_content[:200]}...")
            else:
                json_content = response_content

            # Parse JSON
            parsed_response = json.loads(json_content)
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
            
            # Log more details about the response for debugging
            if len(response_content) > 500:
                self.logger.error(f"Response content (first 500 chars): {response_content[:500]}")
                self.logger.error(f"Response content (last 200 chars): ...{response_content[-200:]}")
            else:
                self.logger.error(f"Response content: {response_content}")
            
            # Check if there's valid JSON at the beginning
            json_start = response_content.find('{')
            if json_start != -1:
                self.logger.info("Attempting to extract valid JSON portion from response...")
                # Try to extract just the JSON part using the improved logic
                try:
                    # Find the matching closing brace for the first opening brace
                    brace_count = 0
                    json_end = json_start
                    for i, char in enumerate(response_content[json_start:], json_start):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i + 1
                                break
                    
                    if json_end > json_start:
                        json_content = response_content[json_start:json_end]
                        self.logger.info(f"Attempting to parse extracted JSON: {json_content[:100]}...")
                        parsed_response = json.loads(json_content)
                        test_cases_data = parsed_response.get("test_cases", [])
                        
                        # Continue with the same parsing logic
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

                        self.logger.info(f"Successfully recovered and parsed {len(test_cases)} test cases from partial JSON")
                        return test_cases
                        
                except json.JSONDecodeError as recovery_error:
                    self.logger.error(f"Failed to parse even the extracted JSON: {str(recovery_error)}")
                except Exception as recovery_error:
                    self.logger.error(f"Error during JSON recovery: {str(recovery_error)}")

            # Fallback: Try to extract test cases using text parsing
            self.logger.info("Falling back to text-based parsing...")
            return self._fallback_parse_test_cases(response_content)

        except Exception as e:
            self.logger.error(f"Error parsing test cases: {str(e)}")
            return []

    def _fallback_parse_test_cases(self, content: str) -> List[TestCase]:
        """Fallback method to parse test cases when JSON parsing fails"""

        test_cases = []

        # Try multiple parsing strategies
        
        # Strategy 1: Look for structured text patterns
        import re
        
        # Pattern for test case blocks
        test_case_pattern = r'(?i)(?:test\s*case|title|tc\s*\d+)[:\-\s]*([^\n]+)'
        title_matches = re.findall(test_case_pattern, content)
        
        if title_matches:
            self.logger.info(f"Found {len(title_matches)} potential test case titles using regex")
            for i, title in enumerate(title_matches[:10]):  # Limit to 10 test cases
                test_case = TestCase(
                    title=title.strip(),
                    description=f"Generated from AI response - Test case {i+1}",
                    test_type="positive",
                    test_steps=[f"Execute test scenario: {title.strip()}"],
                    expected_result="System behaves as expected.",
                    preconditions=["System is available and accessible"],
                    priority="Medium",
                    parent_story_id=None
                )
                test_cases.append(test_case)
                
            if test_cases:
                self.logger.info(f"Regex parsing extracted {len(test_cases)} test cases")
                return test_cases

        # Strategy 2: Simple text-based parsing (original fallback)
        lines = content.split('\n')
        current_test = None

        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for lines that might be titles
            if any(keyword in line.lower() for keyword in ['title:', 'test:', 'tc', '1.', '2.', '3.', '4.', '5.']):
                if current_test:
                    test_cases.append(current_test)

                # Clean up the title
                title = line
                for prefix in ['Title:', 'Test:', 'TC', '1.', '2.', '3.', '4.', '5.']:
                    if title.startswith(prefix):
                        title = title[len(prefix):].strip()
                        break
                
                if not title:
                    title = f"Test Case {len(test_cases) + 1}"

                current_test = TestCase(
                    title=title,
                    description="Parsed from AI response",
                    test_type="positive",
                    test_steps=[],
                    expected_result="System behaves as expected.",
                    preconditions=["System is available"],
                    priority="Medium",
                    parent_story_id=None
                )
            elif current_test and line:
                if line.startswith('Steps:') or line.startswith('Expected:') or line.startswith('Description:'):
                    continue
                elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    current_test.test_steps.append(line[1:].strip())
                elif len(current_test.test_steps) < 5:  # Add as a step if we don't have many yet
                    current_test.test_steps.append(line)

        if current_test:
            test_cases.append(current_test)

        # Strategy 3: If still no test cases, create a generic one
        if not test_cases:
            self.logger.warning("No test cases could be parsed, creating a generic test case")
            generic_test = TestCase(
                title="Validate User Story Functionality",
                description="Generic test case created when AI response could not be parsed",
                test_type="positive", 
                test_steps=[
                    "1. Review the user story requirements",
                    "2. Execute the main functionality",
                    "3. Verify the expected behavior",
                    "4. Validate any acceptance criteria"
                ],
                expected_result="All functionality works as expected according to the user story.",
                preconditions=["System is available and properly configured"],
                priority="Medium",
                parent_story_id=None
            )
            test_cases.append(generic_test)

        self.logger.info(f"Fallback parsing extracted {len(test_cases)} test cases")
        return test_cases
