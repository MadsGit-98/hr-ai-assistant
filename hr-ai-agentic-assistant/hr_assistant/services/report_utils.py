"""
Utility functions for candidate reporting and filtering functionality.
Contains report filtering, sorting logic as specified in the implementation plan.
"""
from django.db import models
from jobs.models import Applicant
from typing import List, Dict, Any, Optional


def get_candidates_for_job(job_id: int, 
                          sort_by: str = 'overall_score', 
                          sort_order: str = 'desc', 
                          score_threshold: int = 0) -> List[Applicant]:
    """
    Retrieve and process candidates for a specific job with filtering and sorting.
    
    Args:
        job_id: ID of the job listing
        sort_by: Field to sort by ('overall_score', 'applicant_name', 'categorization', 'quality_grade')
        sort_order: Sort direction ('asc' or 'desc')
        score_threshold: Minimum score threshold for filtering (0-100 range)
        
    Returns:
        List of Applicant objects filtered, sorted and limited to 500 as per spec
    """
    # Validate inputs
    if sort_by not in ['overall_score', 'applicant_name', 'categorization', 'quality_grade']:
        sort_by = 'overall_score'  # default
        
    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'  # default
        
    if not (0 <= score_threshold <= 100):
        score_threshold = 0  # default
        
    # Get all applicants for the job that have analysis completed
    candidates = Applicant.objects.filter(
        job_listing_id=job_id,
        analysis_status='analyzed'  # Only include analyzed candidates
    ).exclude(overall_score__isnull=True)  # Exclude if overall_score is null
    
    # Apply score threshold filter in-memory (as per plan decision)
    candidates_list = list(candidates)
    
    # Filter based on score threshold
    if score_threshold > 0:
        candidates_list = [c for c in candidates_list if c.overall_score and c.overall_score >= score_threshold]
    
    # Apply sorting in-memory (as per plan decision to handle SQLite constraints)
    reverse_sort = (sort_order == 'desc')
    
    if sort_by == 'overall_score':
        candidates_list.sort(key=lambda x: x.overall_score or 0, reverse=reverse_sort)
    elif sort_by == 'applicant_name':
        candidates_list.sort(key=lambda x: x.applicant_name.lower(), reverse=reverse_sort)
    elif sort_by == 'categorization':
        candidates_list.sort(key=lambda x: x.categorization or '', reverse=reverse_sort)
    elif sort_by == 'quality_grade':
        candidates_list.sort(key=lambda x: x.quality_grade or '', reverse=reverse_sort)
    
    # Limit to 500 candidates as per spec requirement FR-011
    return candidates_list[:500]


def sort_candidates(candidates: List[Applicant], 
                   sort_by: str = 'overall_score', 
                   sort_order: str = 'desc') -> List[Applicant]:
    """
    Sort a list of candidates based on a specific field.
    
    Args:
        candidates: List of Applicant objects to sort
        sort_by: Field to sort by ('overall_score', 'applicant_name', 'categorization', 'quality_grade')
        sort_order: Sort direction ('asc' or 'desc')
        
    Returns:
        Sorted list of Applicant objects
    """
    if sort_by not in ['overall_score', 'applicant_name', 'categorization', 'quality_grade']:
        sort_by = 'overall_score'  # default
        
    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'  # default
        
    reverse_sort = (sort_order == 'desc')
    
    if sort_by == 'overall_score':
        return sorted(candidates, key=lambda x: x.overall_score or 0, reverse=reverse_sort)
    elif sort_by == 'applicant_name':
        return sorted(candidates, key=lambda x: x.applicant_name.lower(), reverse=reverse_sort)
    elif sort_by == 'categorization':
        return sorted(candidates, key=lambda x: x.categorization or '', reverse=reverse_sort)
    elif sort_by == 'quality_grade':
        return sorted(candidates, key=lambda x: x.quality_grade or '', reverse=reverse_sort)
    
    return candidates


def filter_candidates_by_score(candidates: List[Applicant], 
                               score_threshold: int = 0) -> List[Applicant]:
    """
    Filter candidates based on a minimum score threshold.
    
    Args:
        candidates: List of Applicant objects to filter
        score_threshold: Minimum score threshold for filtering (0-100 range)
        
    Returns:
        Filtered list of Applicant objects
    """
    if not (0 <= score_threshold <= 100):
        score_threshold = 0  # default
        
    if score_threshold <= 0:
        return candidates
        
    return [c for c in candidates if c.overall_score and c.overall_score >= score_threshold]


