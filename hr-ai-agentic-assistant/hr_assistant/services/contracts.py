"""
Data contracts for AI Resume Scoring Engine
"""
from typing import TypedDict, List, Dict, Any, Annotated
from pydantic import BaseModel, Field
from operator import add


class AIAnalysisResponse(BaseModel):
    """
    Data contract for AI analysis response
    """
    overall_score: int = Field(ge=0, le=100, description="Score between 0-100")
    quality_grade: str = Field(description="Grade A, B, C, D, or F")
    categorization: str = Field(description="Senior, Mid-Level, Junior, or Mismatched")
    justification_summary: str = Field(description="Explanation of the scoring")
    applicant_id: int = Field(description="Reference to the applicant being scored")


class GraphState(TypedDict):
    """
    State definition for the Supervisor graph
    """
    applicant_id_list: List[int]
    job_criteria: Dict[str, Any]
    results: Annotated[List[AIAnalysisResponse], add]  # To append the results with AIAnalysisResponse from the parallel nodes
    status: str
    current_index: Annotated[int, lambda x, y: max(x, y)]  # For aggregation
    error_count: Annotated[int, lambda x, y: x + y]  # For aggregation
    total_count: int
    resume_texts: Dict[int, str]  # Store resume texts by applicant ID
    job_requirements: str  # The job requirements to compare against
    current_analysis_response: AIAnalysisResponse 