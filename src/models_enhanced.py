from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ComplexityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class ComplexityFactor(BaseModel):
    name: str
    assessment: ComplexityLevel
    impact: str

class StoryComplexityAnalysis(BaseModel):
    overall_complexity: ComplexityLevel
    story_points: int = Field(ge=1, le=13)  # Using Fibonacci sequence for story points (1,2,3,5,8,13)
    factors: List[ComplexityFactor]
    rationale: str

class EnhancedUserStory(BaseModel):
    heading: str
    description: str
    acceptance_criteria: str | List[str]  # Accept either a string or list of strings
    complexity_analysis: Optional[StoryComplexityAnalysis] = None

    def to_ado_format(self) -> dict:
        """Convert the story to ADO work item format"""
        print(f"[DEBUG] EnhancedUserStory.to_ado_format() called for: {self.heading}")
        print(f"[DEBUG] Has complexity_analysis: {self.complexity_analysis is not None}")
        
        # Use the description as-is (already contains Technical Context and Business Requirements)
        formatted_description = self.description

        # Format acceptance criteria as HTML for better ADO display
        if isinstance(self.acceptance_criteria, list):
            # Use HTML formatting for cleaner display in ADO
            formatted_ac = "<br>".join([f"• {criteria}" for criteria in self.acceptance_criteria])
        else:
            formatted_ac = str(self.acceptance_criteria)

        # Return Azure DevOps fields
        result = {
            "System.Title": self.heading,
            "System.Description": formatted_description,
            "Microsoft.VSTS.Common.AcceptanceCriteria": formatted_ac,
            "System.State": "New",
            "Microsoft.VSTS.Scheduling.StoryPoints": self.complexity_analysis.story_points if self.complexity_analysis else None
        }
        
        print(f"[DEBUG] EnhancedUserStory.to_ado_format() returning {len(result)} fields: {list(result.keys())}")
        if self.complexity_analysis:
            print(f"[DEBUG] Story Points value: {self.complexity_analysis.story_points}")
        return result
