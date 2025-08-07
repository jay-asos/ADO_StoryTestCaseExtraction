import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.story_extractor import StoryExtractor
from src.models import Requirement, UserStory, StoryExtractionResult

class TestStoryExtractor:
    @pytest.fixture
    def extractor(self):
        """Create a StoryExtractor instance for testing"""
        with patch('src.story_extractor.OpenAI'):
            return StoryExtractor()
    
    @pytest.fixture
    def sample_requirement(self):
        """Sample requirement for testing"""
        return Requirement(
            id=123,
            title="User Authentication System",
            description="Implement a comprehensive user authentication system that allows users to register, login, and manage their accounts. The system should include password reset functionality and email verification.",
            state="Active"
        )
    
    def test_extract_stories_success(self, extractor, sample_requirement):
        """Test successful story extraction"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "stories": [
                {
                    "heading": "User Registration",
                    "description": "As a new user, I want to register an account so that I can access the system",
                    "acceptance_criteria": [
                        "User can enter email and password",
                        "System validates email format",
                        "Confirmation email is sent"
                    ]
                },
                {
                    "heading": "User Login",
                    "description": "As a registered user, I want to login so that I can access my account",
                    "acceptance_criteria": [
                        "User can enter credentials",
                        "System validates credentials",
                        "User is redirected to dashboard"
                    ]
                }
            ]
        })
        
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_stories(sample_requirement)
        
        assert result.extraction_successful is True
        assert len(result.stories) == 2
        assert result.stories[0].heading == "User Registration"
        assert result.stories[1].heading == "User Login"
        assert len(result.stories[0].acceptance_criteria) == 3
    
    def test_extract_stories_ai_failure(self, extractor, sample_requirement):
        """Test story extraction when AI fails"""
        extractor.client.chat.completions.create.side_effect = Exception("API Error")
        
        result = extractor.extract_stories(sample_requirement)
        
        assert result.extraction_successful is False
        assert result.error_message == "AI analysis failed: API Error"
        assert len(result.stories) == 0
    
    def test_extract_stories_invalid_json(self, extractor, sample_requirement):
        """Test story extraction with invalid JSON response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_stories(sample_requirement)
        
        assert result.extraction_successful is False
        assert "Failed to parse AI response as JSON" in result.error_message
    
    def test_build_extraction_prompt(self, extractor, sample_requirement):
        """Test prompt building for AI extraction"""
        prompt = extractor._build_extraction_prompt(sample_requirement)
        
        assert sample_requirement.title in prompt
        assert sample_requirement.description in prompt
        assert "JSON" in prompt
        assert "user stories" in prompt.lower()
        assert "acceptance criteria" in prompt.lower()
    
    def test_validate_stories_valid(self, extractor):
        """Test story validation with valid stories"""
        stories = [
            UserStory(
                heading="Valid Story Title",
                description="As a user, I want this feature so that I can benefit",
                acceptance_criteria=["Valid criteria 1", "Valid criteria 2"]
            )
        ]
        
        issues = extractor.validate_stories(stories)
        assert len(issues) == 0
    
    def test_validate_stories_invalid(self, extractor):
        """Test story validation with invalid stories"""
        stories = [
            UserStory(
                heading="",  # Too short
                description="Short",  # Too short
                acceptance_criteria=[]  # Empty
            ),
            UserStory(
                heading="A" * 101,  # Too long
                description="Valid description for the story",
                acceptance_criteria=[""]  # Empty criteria
            )
        ]
        
        issues = extractor.validate_stories(stories)
        
        assert len(issues) > 0
        assert any("Heading too short" in issue for issue in issues)
        assert any("Description too short" in issue for issue in issues)
        assert any("No acceptance criteria" in issue for issue in issues)
        assert any("Heading too long" in issue for issue in issues)
        assert any("Too short or empty" in issue for issue in issues)
    
    def test_analyze_requirement_with_ai_success(self, extractor, sample_requirement):
        """Test successful AI analysis"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "stories": [
                {
                    "heading": "Test Story",
                    "description": "Test description",
                    "acceptance_criteria": ["Test criteria"]
                }
            ]
        })
        
        extractor.client.chat.completions.create.return_value = mock_response
        
        stories = extractor._analyze_requirement_with_ai(sample_requirement)
        
        assert len(stories) == 1
        assert stories[0].heading == "Test Story"
        assert stories[0].description == "Test description"
        assert stories[0].acceptance_criteria == ["Test criteria"]
        
        # Verify OpenAI was called with correct parameters
        extractor.client.chat.completions.create.assert_called_once()
        call_args = extractor.client.chat.completions.create.call_args
        assert call_args[1]['model'] == 'gpt-4'
        assert call_args[1]['temperature'] == 0.3
        assert len(call_args[1]['messages']) == 2
