import json
import re
import time
import logging
from typing import List

from config.settings import Settings
from src.models import Requirement, StoryExtractionResult, UserStory
from src.models_enhanced import EnhancedUserStory
from src.enhanced_story_creator import EnhancedStoryCreator
from src.ai_client import get_ai_client

class StoryExtractor:
    """AI-powered extractor that analyzes requirements and creates enhanced user stories"""
    
    def __init__(self):
        Settings.validate()
        self.ai_client = get_ai_client()
        self.story_creator = EnhancedStoryCreator()
        self.logger = logging.getLogger("StoryExtractor")
        self.logger.setLevel(logging.DEBUG)
        
        # Log which AI service is being used
        ai_provider = getattr(Settings, 'AI_SERVICE_PROVIDER', 'OPENAI')
        self.logger.info(f"🤖 StoryExtractor: Initialized with AI provider '{ai_provider}'")
        if ai_provider == 'AZURE_OPENAI':
            deployment = getattr(Settings, 'AZURE_OPENAI_DEPLOYMENT_NAME', 'Unknown')
            self.logger.info(f"🔷 StoryExtractor: Using Azure OpenAI deployment '{deployment}'")
        else:
            model = getattr(Settings, 'OPENAI_MODEL', 'Unknown')
            self.logger.info(f"🔶 StoryExtractor: Using OpenAI model '{model}'")
    
    def extract_stories(self, requirement: Requirement, existing_stories: List[dict] = None) -> StoryExtractionResult:
        """Extract enhanced user stories from a requirement using AI, avoiding duplicates"""
        self.logger.info(f"Starting story extraction for requirement: {requirement.id}")
        self.logger.debug(f"Requirement details: {json.dumps(requirement.__dict__, indent=2)}")
        try:
            self.logger.debug("Analyzing requirement with AI...")
            stories = self._analyze_requirement_with_ai(requirement)
            self.logger.info(f"Found {len(stories)} potential stories")
            # Filter out duplicates and convert EnhancedUserStory to UserStory
            filtered_stories = []
            existing_stories = existing_stories or []
            self.logger.debug(f"Checking against {len(existing_stories)} existing stories")
            for story in stories:
                if not any(
                    story.heading == es.get('heading') and
                    story.description == es.get('description') and
                    story.acceptance_criteria == es.get('acceptance_criteria')
                    for es in existing_stories
                ):
                    # Convert EnhancedUserStory to UserStory
                    if isinstance(story, EnhancedUserStory):
                        # Handle case where acceptance_criteria might be a string
                        if isinstance(story.acceptance_criteria, str):
                            acceptance_criteria = [story.acceptance_criteria]
                        else:
                            acceptance_criteria = list(story.acceptance_criteria)

                        user_story = UserStory(
                            heading=story.heading,
                            description=story.description,
                            acceptance_criteria=acceptance_criteria,
                            test_cases=[]  # Empty list since test cases are generated later
                        )
                        filtered_stories.append(user_story)
            return StoryExtractionResult(
                requirement_id=str(requirement.id),
                requirement_title=requirement.title,
                stories=filtered_stories,
                extraction_successful=True
            )
        except Exception as e:
            return StoryExtractionResult(
                requirement_id=str(requirement.id),
                requirement_title=requirement.title,
                stories=[],
                extraction_successful=False,
                error_message=str(e)
            )
    
    def _analyze_requirement_with_ai(self, requirement: Requirement) -> List[EnhancedUserStory]:
        """Use AI to analyze requirement and extract enhanced user stories"""
        
        prompt = self._build_extraction_prompt(requirement)
        
        try:
            # Use the unified AI client for chat completion
            content = self.ai_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert business analyst specialized in breaking down requirements into user stories. 
                        You should extract actionable user stories from requirements, ensuring each story follows the standard format:
                        - Clear, concise heading
                        - Detailed description following 'As a [user], I want [goal] so that [benefit]' format, including both Technical Context and Business Requirements sections
                        - Specific, testable acceptance criteria in Given/When/Then format
                        
                        Format your description with clear sections:
                        ```
                        As a [user], I want [goal] so that [benefit]
                        
                        Technical Context:
                        - Technical requirement 1
                        - Technical requirement 2
                        
                        Business Requirements:
                        - Business requirement 1
                        - Business requirement 2
                        ```
                        
                        Format acceptance criteria as an array of strings, each following Given/When/Then format:
                        ```
                        Given [initial context/state]
                        When [action/trigger occurs]
                        Then [expected outcome]
                        And [additional outcomes if any]
                        ```

                        Example acceptance criteria:
                        ```
                        "Given the user is on the login page
                        When they enter valid credentials and click login
                        Then they should be redirected to the dashboard
                        And their username should be displayed in the header"
                        ```
                        ```
                        
                        Return your response as valid JSON only, with no additional text."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Log the raw AI response for debugging
            self.logger.debug(f"Raw AI response: {repr(content)}")
            self.logger.debug(f"AI response length: {len(content)} characters")
            
            # Check if response is empty
            if not content or not content.strip():
                raise Exception("AI returned empty response")
            
            # Clean up the response (remove markdown code blocks if present)
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.startswith('```'):
                content = content[3:]   # Remove ```
            if content.endswith('```'):
                content = content[:-3]  # Remove trailing ```
            content = content.strip()
            
            self.logger.debug(f"Cleaned AI response: {repr(content[:200])}...")
            
            # Parse JSON response
            try:
                stories_data = json.loads(content)
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parse error: {e}")
                self.logger.error(f"Failed to parse response: {content[:500]}...")  # Log first 500 chars
                raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
            
            # Convert to EnhancedUserStory objects
            stories = []
            for story_data in stories_data.get("stories", []):
                # Create an enhanced story with complexity analysis
                story = self.story_creator.create_enhanced_story(
                    heading=story_data["heading"],
                    description=story_data["description"],
                    acceptance_criteria=story_data.get("acceptance_criteria", [])
                    if isinstance(story_data.get("acceptance_criteria"), list)
                    else story_data.get("acceptance_criteria", "").split("\n")
                )
                stories.append(story)
            
            return stories
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _build_extraction_prompt(self, requirement: Requirement) -> str:
        """Build the prompt for AI analysis"""
        return f"""
Please analyze the following requirement and extract user stories from it.

**Requirement Title:** {requirement.title}

**Requirement Description:** 
{requirement.description}

**Instructions:**
1. Break down this requirement into 2-5 logical user stories
2. Each story should be focused on a single piece of functionality
3. Ensure stories are independent and deliverable
4. Write clear acceptance criteria that are testable

**Required JSON Response Format:**
{{
    "stories": [
        {{
            "heading": "Short, descriptive title for the story",
            "description": "Detailed description preferably in 'As a [user], I want [goal] so that [benefit]' format",
            "acceptance_criteria": [
                "Specific, testable criteria 1",
                "Specific, testable criteria 2",
                "Specific, testable criteria 3"
            ]
        }}
    ]
}}

Return only valid JSON, no additional text.
"""
    
    def validate_stories(self, stories: List[EnhancedUserStory]) -> List[str]:
        """Validate a list of enhanced user stories"""
        issues = []
        
        for i, story in enumerate(stories):
            story_num = i + 1
            
            # Check heading
            if not story.heading or len(story.heading.strip()) < 5:
                issues.append(f"Story {story_num}: Heading too short or missing")
            
            if len(story.heading) > 100:
                issues.append(f"Story {story_num}: Heading too long (over 100 characters)")
            
            # Check description
            if not story.description or len(story.description.strip()) < 10:
                issues.append(f"Story {story_num}: Description too short or missing")
            
            # Check acceptance criteria
            if not story.acceptance_criteria:
                issues.append(f"Story {story_num}: No acceptance criteria provided")
            elif len(story.acceptance_criteria) < 1:
                issues.append(f"Story {story_num}: At least one acceptance criteria required")
            
            # Check each acceptance criteria
            for j, criteria in enumerate(story.acceptance_criteria):
                if not criteria or len(criteria.strip()) < 5:
                    issues.append(f"Story {story_num}, Criteria {j+1}: Too short or empty")
        
        return issues
