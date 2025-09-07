import logging
import json
from typing import List
from src.models_enhanced import EnhancedUserStory, StoryComplexityAnalysis, ComplexityFactor, ComplexityLevel
from config.settings import Settings
from src.ai_client import get_ai_client

# Set up logger
logger = logging.getLogger(__name__)

class EnhancedStoryCreator:
    """Creates enhanced user stories with complexity analysis"""
    
    def __init__(self):
        Settings.validate()
        self.ai_client = get_ai_client()
        
        # Log which AI service is being used
        ai_provider = getattr(Settings, 'AI_SERVICE_PROVIDER', 'OPENAI')
        logger.info(f"🤖 EnhancedStoryCreator: Initialized with AI provider '{ai_provider}'")
        if ai_provider == 'AZURE_OPENAI':
            deployment = getattr(Settings, 'AZURE_OPENAI_DEPLOYMENT_NAME', 'Unknown')
            logger.info(f"🔷 EnhancedStoryCreator: Using Azure OpenAI deployment '{deployment}'")
        else:
            model = getattr(Settings, 'OPENAI_MODEL', 'Unknown')
            logger.info(f"🔶 EnhancedStoryCreator: Using OpenAI model '{model}'")

    _JSON_FORMAT = '''
{
    "overall_complexity": "Low|Medium|High",
    "story_points": "number (1-13)",
    "factors": [
        {
            "name": "factor name",
            "assessment": "Low|Medium|High",
            "impact": "detailed impact description"
        }
    ],
    "rationale": "explanation of complexity assessment"
}'''

    def analyze_complexity(self, story_content: dict) -> StoryComplexityAnalysis:
        """Analyze the complexity of a user story using AI"""
        story_description = story_content['description']
        acceptance_criteria = story_content['acceptance_criteria']
        
        # Format acceptance criteria as text
        if isinstance(acceptance_criteria, list):
            logger.info("Converting list of acceptance criteria to text")
            criteria_text = "\n".join(f"- {ac}" for ac in acceptance_criteria)
        else:
            logger.info("Using acceptance criteria as is")
            criteria_text = acceptance_criteria
            
        logger.info("Preparing prompt", extra={'criteria_text': criteria_text})
            
        prompt = f"""
Please analyze this user story and assess its complexity:

Title: {story_content['heading']}

Description: {story_description}

Acceptance Criteria:
{criteria_text}

Analyze the complexity and provide:
1. Overall complexity level (Low/Medium/High)
2. Story points (Use Fibonacci: 1,2,3,5,8,13)
3. Identify complexity factors considering:
   - Technical complexity
   - Business rules complexity
   - Integration needs
   - Dependencies
   - Testing complexity
4. Provide rationale for the assessment

Return ONLY valid JSON using this exact format (no additional text):
{{
  "overall_complexity": "Low",
  "story_points": "3",
  "factors": [
    {{
      "name": "Technical Complexity",
      "assessment": "Medium",
      "impact": "Requires API integration and error handling"
    }}
  ],
  "rationale": "Story involves moderate technical implementation with standard API patterns"
}}"""

        try:
            logger.info("Sending request to AI service")
            result = self.ai_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert software project analyst specializing in story complexity assessment.
Your task is to analyze user stories and output valid JSON that conforms to the specified structure.
- Use only 'Low', 'Medium', or 'High' for complexity assessments
- Story points should be a number between 1 and 13 from the Fibonacci sequence
- Always ensure your output is valid JSON
- Return ONLY the JSON response, no additional text or explanations
- Do not wrap the JSON in markdown code blocks"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3  # Lower temperature for more consistent JSON output
            )
            
            # Log the raw AI response for debugging
            logger.debug(f"Raw AI response for complexity: {repr(result)}")
            logger.debug(f"AI response length: {len(result) if result else 0} characters")
            
            # Check if response is empty
            if not result or not result.strip():
                raise Exception("AI returned empty response for complexity analysis")
            
            # Clean up the response (remove markdown code blocks if present)
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:]  # Remove ```json
            if result.startswith('```'):
                result = result[3:]   # Remove ```
            if result.endswith('```'):
                result = result[:-3]  # Remove trailing ```
            result = result.strip()
            
            logger.debug(f"Cleaned AI response for complexity: {repr(result[:200])}...")
            
            # Parse the response
            try:
                # First try to parse as valid JSON
                analysis_dict = json.loads(result)
                logger.info("Successfully parsed complexity response as JSON")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error for complexity: {e}")
                logger.error(f"Failed to parse complexity response: {result[:500]}...")  # Log first 500 chars
                raise ValueError(f"Invalid JSON response from OpenAI: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in complexity analysis: {str(e)}")
            return StoryComplexityAnalysis(
                overall_complexity=ComplexityLevel.MEDIUM,
                story_points=3,
                factors=[
                    ComplexityFactor(
                        name="Default Assessment",
                        assessment=ComplexityLevel.MEDIUM,
                        impact="Automated complexity analysis failed, using default medium complexity"
                    )
                ],
                rationale=f"Automated analysis failed: {str(e)}"
            )

        # Convert to our model
        return StoryComplexityAnalysis(
            overall_complexity=ComplexityLevel(analysis_dict.get('overall_complexity', 'MEDIUM')),
            story_points=int(analysis_dict.get('story_points', 3)),
            factors=[
                ComplexityFactor(
                    name=factor.get('name', 'Unknown Factor'),
                    assessment=ComplexityLevel(factor.get('assessment', 'MEDIUM')),
                    impact=factor.get('impact', 'No impact description provided')
                ) for factor in analysis_dict.get('factors', [])
            ],
            rationale=analysis_dict.get('rationale', 'No rationale provided')
        )

    def create_enhanced_story(self, heading: str, description: str, acceptance_criteria: List[str]) -> EnhancedUserStory:
        """Create an enhanced user story with complexity analysis"""
        
        # First analyze the complexity
        story_content = {
            "heading": heading,
            "description": description,
            "acceptance_criteria": acceptance_criteria
        }
        
        complexity_analysis = self.analyze_complexity(story_content)
        
        # Create and return the enhanced story
        return EnhancedUserStory(
            heading=heading,
            description=description,
            acceptance_criteria=acceptance_criteria,
            complexity_analysis=complexity_analysis
        )
