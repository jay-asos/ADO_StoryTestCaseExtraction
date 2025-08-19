import json
import re
import time
from typing import List
from openai import OpenAI
from openai import RateLimitError

from config.settings import Settings
from src.models import Requirement, StoryExtractionResult
from src.models_enhanced import EnhancedUserStory
from src.enhanced_story_creator import EnhancedStoryCreator

class StoryExtractor:
    """AI-powered extractor that analyzes requirements and creates enhanced user stories"""
    
    def __init__(self):
        Settings.validate()
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.story_creator = EnhancedStoryCreator()
    
    def extract_stories(self, requirement: Requirement, existing_stories: List[dict] = None) -> StoryExtractionResult:
        """Extract enhanced user stories from a requirement using AI, avoiding duplicates"""
        try:
            stories = self._analyze_requirement_with_ai(requirement)
            # Filter out duplicates
            filtered_stories = []
            existing_stories = existing_stories or []
            for story in stories:
                if not any(
                    story.heading == es.get('heading') and
                    story.description == es.get('description') and
                    story.acceptance_criteria == es.get('acceptance_criteria')
                    for es in existing_stories
                ):
                    filtered_stories.append(story)
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
        """Use OpenAI to analyze requirement and extract enhanced user stories with retry logic"""
        
        prompt = self._build_extraction_prompt(requirement)
        retries = Settings.OPENAI_MAX_RETRIES
        delay = Settings.OPENAI_RETRY_DELAY
        
        for i in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
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
                            
                            Format acceptance criteria as array of strings, each following:
                            ```
                            Feature Name Given: [context] When: [action] Then: [expected result] And: [additional conditions]
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
                
                content = response.choices[0].message.content.strip()
                
                # Parse JSON response
                stories_data = json.loads(content)
                
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
