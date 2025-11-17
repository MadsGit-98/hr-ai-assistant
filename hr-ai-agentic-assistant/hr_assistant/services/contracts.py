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


def merge_applicant_id_list(left: List[int], right: List[int]) -> List[int]:
    """Reducer function to merge applicant_id_list - keep the original list since it shouldn't change during processing"""
    # Return the original list (left) to avoid conflicts
    # The original list should be preserved since it's an input parameter
    return left if left else right


def merge_job_criteria(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Reducer function to merge job_criteria - prioritize right (new) values while preserving existing keys"""
    # Merge the dictionaries, with right values taking precedence
    #merged = left.copy()
    #merged.update(right)
    return right


def merge_status(left: str, right: str) -> str:
    """Reducer function for status - keep the most recent status unless it's an empty string"""
    # Prioritize the right (new) status unless it's empty, then keep the left (current) status
    return right if right else left


def merge_total_count(left: int, right: int) -> int:
    """Reducer function for total_count - keep the left (original) value as it should remain constant"""
    # The total count should remain constant during processing, so we return the left (original) value
    return left


def merge_resume_texts(left: Dict[int, str], right: Dict[int, str]) -> Dict[int, str]:
    """Reducer function to merge resume_texts - combine both dictionaries"""
    # Merge the dictionaries, with right values taking precedence for duplicate keys
    merged = left.copy()
    merged.update(right)
    return merged


def merge_job_requirements(left: str, right: str) -> str:
    """Reducer function for job_requirements - keep the left (original) value as it shouldn't change"""
    # The job requirements should remain constant during processing, so we return the left (original) value
    return left


def merge_current_analysis_response(left: AIAnalysisResponse, right: AIAnalysisResponse) -> AIAnalysisResponse:
    """Reducer function for current_analysis_response - prioritize the right (newer) analysis response"""
    # Use the right (more recent) analysis response since it's more up-to-date
    return right


class GraphState(TypedDict):
    """
    State definition for the Supervisor graph
    """
    applicant_id_list: Annotated[List[int], merge_applicant_id_list]  # Annotated with reducer to handle multiple values
    job_criteria: Annotated[Dict[str, Any], merge_job_criteria]
    results: Annotated[List[AIAnalysisResponse], add]  # To append the results with AIAnalysisResponse from the parallel nodes
    status: Annotated[str, merge_status]
    current_index: Annotated[int, lambda x, y: max(x, y)]  # For aggregation
    error_count: Annotated[int, lambda x, y: x + y]  # For aggregation
    total_count: Annotated[int, merge_total_count]
    resume_texts: Annotated[Dict[int, str], merge_resume_texts]  # Store resume texts by applicant ID
    job_requirements: Annotated[str, merge_job_requirements]  # The job requirements to compare against
    current_analysis_response: Annotated[AIAnalysisResponse, merge_current_analysis_response] 