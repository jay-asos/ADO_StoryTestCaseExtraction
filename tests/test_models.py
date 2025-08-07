import pytest
from src.models import UserStory, Requirement, StoryExtractionResult

class TestUserStory:
    def test_user_story_creation(self):
        """Test UserStory model creation"""
        story = UserStory(
            heading="Test Story",
            description="As a user, I want to test so that I can verify",
            acceptance_criteria=["Criteria 1", "Criteria 2"]
        )
        
        assert story.heading == "Test Story"
        assert story.description == "As a user, I want to test so that I can verify"
        assert len(story.acceptance_criteria) == 2
    
    def test_to_ado_format(self):
        """Test conversion to ADO format"""
        story = UserStory(
            heading="Login Feature",
            description="As a user, I want to login so that I can access my account",
            acceptance_criteria=["User can enter credentials", "System validates login"]
        )
        
        ado_format = story.to_ado_format()
        
        assert ado_format["System.Title"] == "Login Feature"
        
        # Check that description contains the original description and formatted acceptance criteria
        description = ado_format["System.Description"]
        assert "As a user, I want to login so that I can access my account" in description
        assert "<strong>Acceptance Criteria:</strong>" in description
        assert "• User can enter credentials" in description
        assert "• System validates login" in description
        assert "<br>" in description  # Check HTML formatting is used

class TestRequirement:
    def test_requirement_creation(self):
        """Test Requirement model creation"""
        requirement = Requirement(
            id=123,
            title="Test Requirement",
            description="This is a test requirement",
            state="Active",
            url="https://dev.azure.com/test"
        )
        
        assert requirement.id == 123
        assert requirement.title == "Test Requirement"
        assert requirement.description == "This is a test requirement"
        assert requirement.state == "Active"
        assert requirement.url == "https://dev.azure.com/test"

class TestStoryExtractionResult:
    def test_successful_extraction_result(self):
        """Test successful extraction result"""
        stories = [
            UserStory(
                heading="Story 1",
                description="Description 1",
                acceptance_criteria=["Criteria 1"]
            )
        ]
        
        result = StoryExtractionResult(
            requirement_id="123",
            requirement_title="Test Requirement",
            stories=stories,
            extraction_successful=True
        )
        
        assert result.requirement_id == "123"
        assert result.requirement_title == "Test Requirement"
        assert len(result.stories) == 1
        assert result.extraction_successful is True
        assert result.error_message is None
    
    def test_failed_extraction_result(self):
        """Test failed extraction result"""
        result = StoryExtractionResult(
            requirement_id="123",
            requirement_title="Test Requirement",
            stories=[],
            extraction_successful=False,
            error_message="AI service unavailable"
        )
        
        assert result.requirement_id == "123"
        assert result.extraction_successful is False
        assert result.error_message == "AI service unavailable"
        assert len(result.stories) == 0
