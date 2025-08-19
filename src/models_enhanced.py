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
        # Format description with technical context and business requirements
        formatted_description = (
            f"{self.description}\n\n"
            "**Complexity Analysis:**\n"
        )
        
        if self.complexity_analysis:
            formatted_description += (
                f"- Overall Complexity: {self.complexity_analysis.overall_complexity}\n"
                f"- Story Points: {self.complexity_analysis.story_points}\n"
                f"- Rationale: {self.complexity_analysis.rationale}\n\n"
                "**Complexity Factors:**\n"
            )
            for factor in self.complexity_analysis.factors:
                formatted_description += f"\n- {factor.name} (Impact: {factor.assessment.value})\n  {factor.impact}"

        # Format acceptance criteria as a string with line breaks
        if isinstance(self.acceptance_criteria, list):
            formatted_ac = "\n\n".join(self.acceptance_criteria)
        else:
            formatted_ac = str(self.acceptance_criteria)

        # Return Azure DevOps fields
        return {
            "System.Title": self.heading,
            "System.Description": formatted_description,
            "Microsoft.VSTS.Common.AcceptanceCriteria": formatted_ac,  # Format AC as string with line breaks
            "System.State": "New",  # Set initial state as New
            "Microsoft.VSTS.Scheduling.StoryPoints": self.complexity_analysis.story_points if self.complexity_analysis else None
        }
