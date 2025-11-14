"""
Resume scoring service interface
"""
from typing import List, Dict, Any
from django.utils import timezone
from django.db.models import Q
from hr_assistant.services.ai_analysis import create_supervisor_graph
from hr_assistant.services.contracts import GraphState, AIAnalysisResponse
from jobs.models import Applicant, JobListing
from datetime import timedelta
from hr_assistant.services.logging import (
    log_ai_processing_start, log_ai_processing_complete,
    handle_ai_errors, AIProcessingError
)
from django.db import transaction


class ResumeScoringService:
    """
    Service class to handle resume scoring operations
    """

    @staticmethod
    @handle_ai_errors(context="initiate_scoring_process")
    def initiate_scoring_process(job_id: int, applicant_ids: List[int] = None) -> Dict[str, Any]:
        """
        Initiate the scoring process for applicants against a job listing
        """
        # Validate inputs
        if job_id <= 0:
            raise AIProcessingError("Invalid job_id provided", error_code="INVALID_JOB_ID")

        if applicant_ids is not None and not isinstance(applicant_ids, list):
            raise AIProcessingError("applicant_ids must be a list of integers", error_code="INVALID_APPLICANT_IDS")

        if applicant_ids is not None and not all(isinstance(aid, int) and aid > 0 for aid in applicant_ids):
            raise AIProcessingError("All applicant IDs must be positive integers", error_code="INVALID_APPLICANT_IDS")

        # Get the job listing
        try:
            job_listing = JobListing.objects.get(id=job_id)
        except JobListing.DoesNotExist:
            raise AIProcessingError(f"Job listing with ID {job_id} does not exist", error_code="JOB_NOT_FOUND")

        # Get applicants for the job
        if applicant_ids:
            applicants = Applicant.objects.filter(
                id__in=applicant_ids,
                job_listing=job_listing
            )
            # Validate that all requested applicant IDs exist and belong to this job
            found_applicant_ids = set(applicants.values_list('id', flat=True))
            requested_applicant_ids = set(applicant_ids)
            missing_applicant_ids = requested_applicant_ids - found_applicant_ids
            if missing_applicant_ids:
                raise AIProcessingError(
                    f"Applicants with IDs {list(missing_applicant_ids)} not found for job {job_id}",
                    error_code="APPLICANTS_NOT_FOUND"
                )
        else:
            applicants = Applicant.objects.filter(job_listing=job_listing)

        if not applicants.exists():
            raise AIProcessingError("No applicants found for the specified job listing", error_code="NO_APPLICANTS")

        # Check if there's already a scoring process running
        # Check for applicants that have been in 'processing' status for too long (e.g., 1 minute for testing, should be longer in production)
        old_processing_applicants = Applicant.objects.filter(
            job_listing=job_listing,
            processing_status='processing'
        ).filter(
            # If analysis_timestamp is set but is old, or if it's null but upload_date is old
            (
                Q(analysis_timestamp__lt=timezone.now() - timedelta(minutes=1)) |
                Q(analysis_timestamp__isnull=True, upload_date__lt=timezone.now() - timedelta(minutes=1))
            )
        )

        # Reset their status to 'pending' so they can be processed again
        if old_processing_applicants.exists():
            old_processing_applicants.update(processing_status='pending', analysis_timestamp=None)

        # Check again for any remaining processing applicants
        processing_applicants = Applicant.objects.filter(
            job_listing=job_listing,
            processing_status='processing'
        )
        if processing_applicants.exists():
            # Return a list of applicants currently processing to help with debugging
            processing_list = list(processing_applicants.values('id', 'applicant_name'))
            raise AIProcessingError(
                "Another scoring process is currently running. Please wait for it to complete.",
                error_code="PROCESS_LOCKED",
                additional_data={'processing_applicants': processing_list}
            )

        # Update processing status to 'processing' for selected applicants
        applicants.update(processing_status='processing')

        # Prepare initial state for the graph
        initial_state = GraphState(
            applicant_id_list=[a.id for a in applicants],
            job_criteria=job_listing.required_skills,
            results=[],
            status='processing',
            current_index=0,
            error_count=0,
            total_count=len(applicants),
            resume_texts={a.id: a.parsed_resume_text or "" for a in applicants},  # Use empty string if None
            job_requirements=job_listing.detailed_description or ""
        )

        # Log the start of processing
        for applicant_id in initial_state['applicant_id_list']:
            log_ai_processing_start(applicant_id, job_id)

        # Create and run the supervisor graph
        graph = create_supervisor_graph()
        result = graph.invoke(initial_state)

        # Process results and update applicant status
        processed_count = 0
        error_count = 0
        for result_item in result.get('results', []):
            try:
                with transaction.atomic():
                    applicant = Applicant.objects.select_for_update().get(id=result_item.applicant_id)
                    applicant.overall_score = result_item.overall_score
                    applicant.quality_grade = result_item.quality_grade
                    applicant.categorization = result_item.categorization
                    applicant.justification_summary = result_item.justification_summary
                    applicant.processing_status = 'completed'
                    applicant.analysis_status = 'analyzed'  # Update analysis status when completed
                    applicant.analysis_timestamp = timezone.now()  # Add analysis timestamp
                    applicant.save()

                    # Log completion
                    log_ai_processing_complete(
                        result_item.applicant_id,
                        {
                            'overall_score': result_item.overall_score,
                            'quality_grade': result_item.quality_grade
                        }
                    )
                    processed_count += 1
            except Applicant.DoesNotExist:
                # Log error but continue processing other applicants
                print(f"Applicant with ID {result_item.applicant_id} not found")
                error_count += 1
            except Exception as e:
                # Log error for this specific applicant but continue processing others
                print(f"Error updating applicant {result_item.applicant_id}: {str(e)}")
                error_count += 1

        return {
            'status': 'success',
            'job_id': job_id,
            'applicant_count': len(applicants),
            'processed_count': processed_count,
            'error_count': error_count,
            'results': result
        }
    
    @staticmethod
    @handle_ai_errors(context="get_scoring_status")
    def get_scoring_status(job_id: int) -> Dict[str, Any]:
        """
        Get the current status of the scoring process for a job listing
        """
        job_listing = JobListing.objects.get(id=job_id)
        
        # Get all applicants for this job
        all_applicants = Applicant.objects.filter(job_listing=job_listing)
        total_count = all_applicants.count()
        
        # Count by status
        completed_count = all_applicants.filter(processing_status='completed').count()
        processing_count = all_applicants.filter(processing_status='processing').count()
        error_count = all_applicants.filter(processing_status='error').count()
        
        # Determine overall status
        if completed_count == total_count and total_count > 0:
            overall_status = 'completed'
        elif processing_count > 0:
            overall_status = 'processing'
        elif error_count > 0:
            overall_status = 'error'
        elif total_count == 0:
            overall_status = 'no_applicants'
        else:
            overall_status = 'pending'
        
        return {
            'job_id': job_id,
            'status': overall_status,
            'total_applicants': total_count,
            'completed_count': completed_count,
            'processing_count': processing_count,
            'error_count': error_count,
            'message': f'Processing {completed_count} of {total_count} applicants'
        }
    
    @staticmethod
    @handle_ai_errors(context="get_scored_applicants")
    def get_scored_applicants(job_id: int, status_filter: str = None, 
                            limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get applicants with their scores for a job listing
        """
        # Build query
        applicants_query = Applicant.objects.filter(job_listing_id=job_id)
        
        if status_filter:
            applicants_query = applicants_query.filter(processing_status=status_filter)
        
        # Apply ordering (by score, descending by default)
        applicants_query = applicants_query.order_by('-overall_score')
        
        # Apply pagination
        total_count = applicants_query.count()
        applicants = applicants_query[offset:offset+limit]
        
        # Serialize applicants
        applicant_data = []
        for applicant in applicants:
            applicant_data.append({
                'id': applicant.id,
                'name': applicant.applicant_name,
                'overall_score': applicant.overall_score,
                'quality_grade': applicant.quality_grade,
                'categorization': applicant.categorization,
                'justification_summary': applicant.justification_summary,
                'processing_status': applicant.processing_status,
                'upload_date': applicant.upload_date.isoformat() if applicant.upload_date else None,
            })
        
        return {
            'job_id': job_id,
            'applicants': applicant_data,
            'total_count': total_count,
            'filtered_count': len(applicant_data),
            'limit': limit,
            'offset': offset
        }
    
    @staticmethod
    @handle_ai_errors(context="get_detailed_analysis")
    def get_detailed_analysis(applicant_id: int) -> Dict[str, Any]:
        """
        Get detailed analysis for a specific applicant
        """
        applicant = Applicant.objects.get(id=applicant_id)
        
        return {
            'applicant_id': applicant.id,
            'name': applicant.applicant_name,
            'overall_score': applicant.overall_score,
            'quality_grade': applicant.quality_grade,
            'categorization': applicant.categorization,
            'justification_summary': applicant.justification_summary,
            'detailed_analysis': applicant.justification_summary,
            'processing_status': applicant.processing_status,
            'upload_date': applicant.upload_date.isoformat() if applicant.upload_date else None,
        }
    
    @staticmethod
    @handle_ai_errors(context="filter_and_sort_applicants")
    def filter_and_sort_applicants(
        job_id: int, 
        score_min: int = None, 
        score_max: int = None,
        grade_filter: str = None,
        category_filter: str = None,
        sort_by: str = 'overall_score',
        sort_order: str = 'desc',
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Filter and sort applicants based on scores and categories
        """
        # Build query
        applicants_query = Applicant.objects.filter(job_listing_id=job_id).exclude(overall_score__isnull=True)
        
        # Apply filters
        if score_min is not None:
            applicants_query = applicants_query.filter(overall_score__gte=score_min)
        if score_max is not None:
            applicants_query = applicants_query.filter(overall_score__lte=score_max)
        if grade_filter:
            applicants_query = applicants_query.filter(quality_grade=grade_filter.upper())
        if category_filter:
            applicants_query = applicants_query.filter(categorization=category_filter)
        
        # Apply ordering
        order_field = sort_by
        if sort_order == 'desc':
            order_field = f'-{sort_by}'
        
        applicants_query = applicants_query.order_by(order_field)
        
        # Apply pagination
        total_count = applicants_query.count()
        applicants = applicants_query[offset:offset+limit]
        
        # Serialize applicants
        applicant_data = []
        for applicant in applicants:
            applicant_data.append({
                'id': applicant.id,
                'name': applicant.applicant_name,
                'overall_score': applicant.overall_score,
                'quality_grade': applicant.quality_grade,
                'categorization': applicant.categorization,
                'justification_summary': applicant.justification_summary,
                'processing_status': applicant.processing_status,
            })
        
        return {
            'job_id': job_id,
            'applicants': applicant_data,
            'total_count': total_count,
            'filtered_count': len(applicant_data),
            'limit': limit,
            'offset': offset
        }