from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import os

OPENAI_RETRY_DELAY = int(os.getenv('OPENAI_RETRY_DELAY', 5))

class TestCase(BaseModel):
    """Model representing a test case extracted from a user story"""
    title: str = Field(..., description="Title of the test case")
    description: str = Field(..., description="Detailed description of what the test case validates")
    test_type: str = Field(..., description="Type of test case: 'positive', 'negative', or 'edge'")
    preconditions: List[str] = Field(default_factory=list, description="Prerequisites for the test")
    test_steps: List[str] = Field(..., description="Step-by-step test execution instructions")
    expected_result: str = Field(..., description="Expected outcome of the test")
    priority: str = Field(default="Medium", description="Test priority: 'High', 'Medium', or 'Low'")
    parent_story_id: Optional[str] = Field(None, description="ID of the parent user story")
    
    def get_formatted_steps(self) -> str:
        """Format test steps for Azure DevOps"""
        if not self.test_steps:
            return ""
        return "<br>".join([f"{i+1}. {step}" for i, step in enumerate(self.test_steps)])

    def to_ado_format(self) -> dict:
        """Convert to Azure DevOps test case format"""
        # Format preconditions and test steps as HTML lists
        preconditions_html = "<br>".join([f"• {condition}" for condition in self.preconditions]) if self.preconditions else "None"
        test_steps_html = "<br>".join([f"{i+1}. {step}" for i, step in enumerate(self.test_steps)])
        
        # Create full description with all test details
        full_description = f"""
<strong>Test Type:</strong> {self.test_type.title()}<br>
<strong>Description:</strong> {self.description}<br><br>
<strong>Preconditions:</strong><br>{preconditions_html}<br><br>
<strong>Test Steps:</strong><br>{test_steps_html}<br><br>
<strong>Expected Result:</strong><br>{self.expected_result}
        """.strip()
        
        return {
            "System.Title": self.title,
            "System.Description": full_description,
            "Microsoft.VSTS.Common.Priority": self.priority,
            "Microsoft.VSTS.TCM.TestCaseType": self.test_type.title()
        }

class UserStory(BaseModel):
    """Model representing a user story extracted from a requirement"""
    heading: str = Field(..., description="Title/heading of the user story")
    description: str = Field(..., description="Detailed description of what the user wants")
    acceptance_criteria: List[str] = Field(..., description="List of acceptance criteria")
    test_cases: List[TestCase] = Field(default_factory=list, description="Associated test cases")
    
    def to_ado_format(self) -> dict:
        """Convert to Azure DevOps work item format with acceptance criteria in description"""
        # Format acceptance criteria as HTML bulleted list for proper ADO display
        acceptance_criteria_html = "<br>".join([f"• {criteria}" for criteria in self.acceptance_criteria])
        
        # Combine description with acceptance criteria using HTML formatting
        # ADO description field expects HTML format for proper newline rendering
        full_description = f"{self.description}<br><br><strong>Acceptance Criteria:</strong><br>{acceptance_criteria_html}"
        
        return {
            "System.Title": self.heading,
            "System.Description": full_description
        }

class Requirement(BaseModel):
    """Model representing an ADO requirement"""
    id: str  # Changed from int to str
    title: str
    description: str
    state: str
    url: Optional[str] = None
    @staticmethod
    def from_ado_work_item(work_item: Any) -> "Requirement":
        """Create a Requirement instance from an Azure DevOps work item object."""
        fields = getattr(work_item, 'fields', {})
        return Requirement(
            id=str(getattr(work_item, 'id', '')),
            title=fields.get("System.Title", ""),
            description=fields.get("System.Description", ""),
            state=fields.get("System.State", ""),
            url=getattr(work_item, 'url', None)
        )


class StoryExtractionResult(BaseModel):
    """Result of story extraction from a requirement"""
    requirement_id: str  # Changed to str to handle both numeric and text IDs
    requirement_title: str
    stories: List[UserStory]
    extraction_successful: bool = True
    error_message: Optional[str] = None

class ExistingUserStory(BaseModel):
    """Model representing an existing user story in ADO"""
    id: int
    title: str
    description: str
    state: str
    parent_id: Optional[int] = None
    
class ChangeDetectionResult(BaseModel):
    """Result of change detection for an EPIC"""
    epic_id: str
    epic_title: str
    has_changes: bool = False
    changes_detected: List[str] = Field(default_factory=list)
    last_modified: Optional[datetime] = None
    existing_stories: List[ExistingUserStory] = Field(default_factory=list)
    new_stories: List[UserStory] = Field(default_factory=list)
    stories_to_update: List[Dict[str, Any]] = Field(default_factory=list)
    stories_to_create: List[UserStory] = Field(default_factory=list)
    
class TestCaseExtractionResult(BaseModel):
    """Result of test case extraction from a user story"""
    story_id: str
    story_title: str
    test_cases: List[TestCase]
    extraction_successful: bool = True
    error_message: Optional[str] = None
    created_issue_ids: List[int] = Field(default_factory=list, description="IDs of created Issue work items for test cases")

class EpicSyncResult(BaseModel):
    """Result of synchronizing an EPIC with its user stories"""
    epic_id: str
    epic_title: str
    sync_successful: bool = True
    created_stories: List[int] = Field(default_factory=list)
    updated_stories: List[int] = Field(default_factory=list)
    unchanged_stories: List[int] = Field(default_factory=list)
    created_test_cases: List[int] = Field(default_factory=list)  # Track created test cases
    error_message: Optional[str] = None
    
class RequirementSnapshot(BaseModel):
    """Snapshot of a requirement for change tracking"""
    id: int
    title: str
    description: str
    state: str
    last_modified: Optional[datetime] = None
    content_hash: Optional[str] = None  # Hash of title + description for quick comparison
