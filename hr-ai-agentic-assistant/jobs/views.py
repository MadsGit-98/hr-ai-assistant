from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
import os
from .models import JobListing, Applicant
from .forms import JobListingForm
from . import utils
# AI Resume Scoring Engine Views
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from hr_assistant.services.ai_analysis import create_supervisor_graph
from hr_assistant.services.contracts import GraphState
from hr_assistant.services.logging import log_ai_processing_start, log_ai_processing_complete
from django.core.exceptions import ObjectDoesNotExist
import json
from typing import Dict, Any


class JobListingCreateView(CreateView):
    """
    Implement JobListingCreateView for T016
    """
    model = JobListing
    form_class = JobListingForm
    template_name = 'jobs/joblisting_form.html'
    success_url = reverse_lazy('joblisting_list')

    def form_valid(self, form):
        """
        Add success message on successful creation
        """
        messages.success(self.request, 'Job listing created successfully!')
        return super().form_valid(form)


class JobListingDetailView(DetailView):
    """
    Implement JobListingDetailView for T023
    """
    model = JobListing
    template_name = 'jobs/joblisting_detail.html'

    def get_context_data(self, **kwargs):
        """
        Add rendered description to context
        """
        context = super().get_context_data(**kwargs)
        context['rendered_description'] = self.object.get_rendered_description()
        return context


class JobListingListView(ListView):
    """
    Implement JobListingListView for T024
    """
    model = JobListing
    template_name = 'jobs/joblisting_list.html'
    context_object_name = 'job_listings'

    def get_context_data(self, **kwargs):
        """
        Add has_active_listing to context to conditionally show upload button
        """
        context = super().get_context_data(**kwargs)
        context['has_active_listing'] = JobListing.objects.filter(is_active=True).exists()
        return context


class JobListingUpdateView(UpdateView):
    """
    Implement JobListingUpdateView for T031
    """
    model = JobListing
    form_class = JobListingForm
    template_name = 'jobs/joblisting_form.html'
    success_url = reverse_lazy('joblisting_list')

    def get_form_kwargs(self):
        """
        Add version field to form to support optimistic locking for T035
        """
        kwargs = super().get_form_kwargs()
        # Add the current version to form initial data if it's an update
        if self.object:
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['version'] = self.object.modified_date.timestamp()
        return kwargs

    def form_valid(self, form):
        """
        Add success message on successful update and implement concurrency check for T035
        """
        # For a proof-of-concept, we'll implement a simple optimistic locking mechanism
        # Check if the object has been modified since it was loaded by comparing timestamps
        original_version = self.request.POST.get('version')
        if original_version:
            # Convert string timestamp back to float
            original_version = float(original_version)
            # Get current version from database
            current_obj = JobListing.objects.get(pk=self.object.pk)
            current_version = current_obj.modified_date.timestamp()

            # If versions don't match, another user has modified the record
            if original_version != current_version:
                form.add_error(None, "Another user has modified this job listing. Please refresh and try again.")
                return self.form_invalid(form)

        # Proceed with saving if no conflict
        messages.success(self.request, 'Job listing updated successfully!')
        return super().form_valid(form)


class JobListingDeleteView(DeleteView):
    """
    Implement JobListingDeleteView for T032
    """
    model = JobListing
    template_name = 'jobs/joblisting_confirm_delete.html'
    success_url = reverse_lazy('joblisting_list')

    def delete(self, request, *args, **kwargs):
        """
        Add success message on successful deletion
        """
        messages.success(request, 'Job listing deleted successfully!')
        return super().delete(request, *args, **kwargs)


def activate_job_listing(request, pk):
    """
    Add activate endpoint to set job listing as active for T036
    """
    job_listing = get_object_or_404(JobListing, pk=pk)
    # The model's save method handles deactivating other listings
    job_listing.is_active = True
    job_listing.save()
    messages.success(request, f'"{job_listing.title}" is now the active job listing!')
    return redirect('joblisting_list')


class ApplicantUploadView(View):
    """
    View to handle multi-file resume uploads with validation and duplicate detection
    """

    def get(self, request):
        """
        Display the upload form with drag-and-drop interface
        """
        # Get the active job listing
        active_job_listing = JobListing.objects.filter(is_active=True).first()
        if not active_job_listing:
            messages.error(request, 'No active job listing found. Please activate a job listing before uploading resumes.')
            return redirect('joblisting_list')

        return render(request, 'jobs/upload.html', {
            'active_job_listing': active_job_listing
        })

    def post(self, request):
        """
        Handle file uploads with validation and duplicate detection
        """
        uploaded_files = request.FILES.getlist('resume_files')
        results = []

        # Ensure there's an active job listing before processing uploads
        active_job_listing = JobListing.objects.filter(is_active=True).first()
        if not active_job_listing:
            return JsonResponse({
                'success': False,
                'error': 'No active job listing found. Please activate a job listing before uploading resumes.'
            })

        for uploaded_file in uploaded_files:
            result = self.process_single_file(uploaded_file, active_job_listing)
            results.append(result)

        # Return JSON response for AJAX processing
        return JsonResponse({
            'success': True,
            'results': results
        })

    def process_single_file(self, uploaded_file, job_listing):
        """
        Process a single uploaded file with validation and duplicate detection
        """
        result = {
            'filename': uploaded_file.name,
            'status': 'error',
            'message': '',
            'duplicates': []
        }

        # T009: Implement file type validation (PDF/DOCX)
        if not utils.validate_file_type(uploaded_file):
            result['message'] = f'Invalid file type for {uploaded_file.name}. Only PDF and DOCX files are allowed.'
            return result

        # T010: Implement file size validation (max 10MB)
        if not utils.validate_file_size(uploaded_file, max_size=settings.FILE_UPLOAD_MAX_MEMORY_SIZE):
            result['message'] = f'File size exceeds 10MB limit for {uploaded_file.name}.'
            return result

        # Calculate content hash for duplicate detection
        content_hash = utils.calculate_file_hash(uploaded_file)

        # Check for content-based duplicates
        content_duplicate = utils.check_duplicate_content(content_hash)

        # Extract applicant name from filename
        applicant_name = utils.extract_applicant_name_from_filename(uploaded_file.name)

        # Check for name-based duplicates
        name_duplicate = utils.check_duplicate_name(applicant_name)

        # Prepare duplicate information
        duplicates = []
        if content_duplicate:
            duplicates.append({
                'type': 'content',
                'message': 'A resume with identical content already exists'
            })

        if name_duplicate:
            duplicates.append({
                'type': 'name',
                'message': f'A resume for {applicant_name} already exists'
            })

        # T025, T026: Handle duplicate detection before saving
        if duplicates:
            result['duplicates'] = duplicates
            result['status'] = 'duplicate'
            result['content_hash'] = content_hash
            result['applicant_name'] = applicant_name
            return result

        # If no duplicates, save the file
        try:
            # Create applicant record linked to the active job listing
            applicant = Applicant(
                job_listing=job_listing,
                applicant_name=applicant_name,
                resume_file=uploaded_file,
                content_hash=content_hash,
                file_size=uploaded_file.size,
                file_format=os.path.splitext(uploaded_file.name)[1][1:].upper(),  # Extract extension without the dot
                analysis_status='pending'  # Set the required analysis_status field
            )
            applicant.full_clean()  # Run model validation
            applicant.save()

            result['status'] = 'success'
            result['message'] = f'{uploaded_file.name} uploaded successfully'
            result['applicant_id'] = applicant.id
        except Exception as e:
            result['message'] = f'Error saving {uploaded_file.name}: {str(e)}'

        return result

@method_decorator(csrf_exempt, name='dispatch')
class ScoreResumesView(View):
    """
    View to initiate resume scoring for a job listing
    """
    def post(self, request, job_id):
        try:
            # Get the job listing
            job_listing = JobListing.objects.get(id=job_id)
            
            # Parse the request body
            data = json.loads(request.body)
            applicant_ids = data.get('applicant_ids', None)
            
            # Get applicants for the job
            if applicant_ids:
                applicants = Applicant.objects.filter(
                    id__in=applicant_ids,
                    job_listing=job_listing
                )
            else:
                applicants = Applicant.objects.filter(job_listing=job_listing)
            
            # Check if there's already a scoring process running
            # (Based on clarification that only one scoring process should run at a time)
            from django.utils import timezone
            from datetime import timedelta
            
            # Check for applicants that have been in 'processing' status for too long (e.g., 30 minutes)
            # This handles cases where a previous process might have crashed or stalled
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
                return JsonResponse({
                    'error': 'Another scoring process is currently running. Please wait for it to complete.',
                    'processing_applicants': processing_list
                }, status=423)  # Locked status code
            
            # Update processing status to 'processing' for selected applicants
            applicants.update(processing_status='processing')
            
            # Prepare initial state for the graph
            initial_state = GraphState(
                applicant_id_list=[a.id for a in applicants],
                job_criteria=job_listing.required_skills,  # Assuming this contains the job requirements
                results=[],
                status='processing',
                current_index=0,
                error_count=0,
                total_count=len(applicants),
                resume_texts={a.id: a.parsed_resume_text for a in applicants},
                job_requirements=job_listing.detailed_description
            )
            
            # Log the start of processing
            for applicant_id in initial_state['applicant_id_list']:
                log_ai_processing_start(applicant_id, job_id)
            
            # Create and run the supervisor graph with error handling
            graph = create_supervisor_graph()
            result = graph.invoke(initial_state)
            
            # Process results and update applicant status
            for result_item in result.get('results', []):
                try:
                    applicant = Applicant.objects.get(id=result_item.applicant_id)
                    applicant.overall_score = result_item.overall_score
                    applicant.quality_grade = result_item.quality_grade
                    applicant.categorization = result_item.categorization
                    applicant.justification_summary = result_item.justification_summary
                    applicant.processing_status = 'completed'
                    applicant.analysis_status = 'analyzed'  # Update analysis status when completed
                    applicant.save()
                    
                    # Log completion
                    log_ai_processing_complete(
                        result_item.applicant_id,
                        {
                            'overall_score': result_item.overall_score,
                            'quality_grade': result_item.quality_grade
                        }
                    )
                except Applicant.DoesNotExist:
                    # Log error but continue processing other applicants
                    print(f"Applicant with ID {result_item.applicant_id} not found")
            
            # Return success response
            return JsonResponse({
                'status': 'accepted',
                'message': 'Resume scoring process initiated',
                'job_id': job_id,
                'applicant_count': len(applicants),
                'tracking_id': f'score_job_{job_id}_{len(applicants)}'
            }, status=202)  # 202 Accepted
            
        except JobListing.DoesNotExist:
            return JsonResponse({'error': 'Job listing not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error processing request: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ScoringStatusView(View):
    """
    View to check scoring status for a job listing
    """
    def get(self, request, job_id):
        try:
            job_listing = JobListing.objects.get(id=job_id)
            
            # Get all applicants for this job
            all_applicants = Applicant.objects.filter(job_listing=job_listing)
            total_count = all_applicants.count()
            
            # Count by status
            completed_count = all_applicants.filter(processing_status='completed').count()
            processing_count = all_applicants.filter(processing_status='processing').count()
            error_count = all_applicants.filter(processing_status='error').count()
            
            # Determine overall status
            if completed_count == total_count:
                overall_status = 'completed'
            elif processing_count > 0:
                overall_status = 'processing'
            elif error_count > 0:
                overall_status = 'error'
            else:
                overall_status = 'pending'
            
            return JsonResponse({
                'job_id': job_id,
                'status': overall_status,
                'total_applicants': total_count,
                'completed_count': completed_count,
                'processing_count': processing_count,
                'error_count': error_count,
                'message': f'Processing {completed_count} of {total_count} applicants'
            })
            
        except JobListing.DoesNotExist:
            return JsonResponse({'error': 'Job listing not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error checking status: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ScoredApplicantsView(View):
    """
    View to get applicants with their scores for a job listing
    """
    def get(self, request, job_id):
        try:
            # Get query parameters
            status_filter = request.GET.get('status')
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
            
            # Get job listing
            job_listing = JobListing.objects.get(id=job_id)
            
            # Build query
            applicants_query = Applicant.objects.filter(job_listing=job_listing)
            
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
                    'email': applicant.email if hasattr(applicant, 'email') else None,
                    'overall_score': applicant.overall_score,
                    'quality_grade': applicant.quality_grade,
                    'categorization': applicant.categorization,
                    'justification_summary': applicant.justification_summary,
                    'processing_status': applicant.processing_status,
                    'analysis_date': applicant.analysis_timestamp
                })
            
            return JsonResponse({
                'job_id': job_id,
                'applicants': applicant_data,
                'total_count': total_count,
                'filtered_count': len(applicant_data)
            })
            
        except JobListing.DoesNotExist:
            return JsonResponse({'error': 'Job listing not found'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid parameter value'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error retrieving applicants: {str(e)}'}, status=500)


# Additional view for detailed analysis (User Story 2)
@method_decorator(csrf_exempt, name='dispatch')
class DetailedAnalysisView(View):
    """
    View to get detailed analysis for a specific applicant
    """
    def get(self, request, applicant_id):
        try:
            applicant = Applicant.objects.get(id=applicant_id)
            
            # Return detailed analysis information
            return JsonResponse({
                'applicant_id': applicant.id,
                'name': applicant.applicant_name,
                'overall_score': applicant.overall_score,
                'quality_grade': applicant.quality_grade,
                'categorization': applicant.categorization,
                'justification_summary': applicant.justification_summary,
                'detailed_analysis': applicant.justification_summary,  # Using the summary as the detailed analysis
                'processing_status': applicant.processing_status,
                'analysis_date': applicant.analysis_timestamp
            })
            
        except Applicant.DoesNotExist:
            return JsonResponse({'error': 'Applicant not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error retrieving analysis: {str(e)}'}, status=500)


class ScoringResultsView(View):
    """
    View to display the results of the AI scoring process
    """
    def get(self, request):
        return render(request, 'jobs/scoring_results.html')