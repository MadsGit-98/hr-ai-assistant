from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from hr_assistant.services.resume_scoring import ResumeScoringService
from django.db.models import Q
from django.core.files.storage import default_storage
import os
from .models import JobListing, Applicant
from .forms import JobListingForm
from . import utils
# AI Resume Scoring Engine Views
import json

# Import resume parsing service
from .services.resume_parser import process_resume_upload


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

    def get_queryset(self):
        """
        Annotate job listings with applicant count for better performance
        """
        from django.db.models import Count
        return JobListing.objects.annotate(applicant_count=Count('applicants'))

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

            # Parse the resume text and save it to the database
            # We need to use the saved file from storage for parsing
            file_path = default_storage.path(applicant.resume_file.name)
            # Read the content to create a new file-like object
            with open(file_path, 'rb') as resume_file:
                content = resume_file.read()

            from django.core.files.uploadedfile import SimpleUploadedFile
            # Create a temporary file object for parsing
            temp_file = SimpleUploadedFile(
                name=applicant.resume_file.name,
                content=content,
                content_type='application/octet-stream'
            )
            # Process and parse the resume text
            process_resume_upload(temp_file, applicant)

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
        # Import logging for view-level debugging
        import logging
        ai_logger = logging.getLogger('ai_processing')

        try:
            ai_logger.info(f"ScoreResumesView received request for job_id: {job_id}")

            # Parse the request body
            data = json.loads(request.body)
            applicant_ids = data.get('applicant_ids', None)

            ai_logger.info(f"Request data: job_id={job_id}, applicant_ids={applicant_ids}")

            # Use the resume scoring service to initiate the process
            result = ResumeScoringService.initiate_scoring_process(job_id, applicant_ids)

            ai_logger.info(f"ResumeScoringService returned successfully: {result}")

            # Return success response
            response_data = {
                'status': 'accepted',
                'message': 'Resume scoring process initiated',
                'job_id': job_id,
                'applicant_count': result['applicant_count'],
                'tracking_id': f'score_job_{job_id}_{result["applicant_count"]}'
            }

            ai_logger.info(f"Returning response: {response_data}")
            return JsonResponse(response_data, status=202)  # 202 Accepted

        except JobListing.DoesNotExist:
            ai_logger.error(f'Job listing not found for ID: {job_id}')
            return JsonResponse({'error': 'Job listing not found'}, status=404)
        except Exception as e:
            ai_logger.error(f'Error processing request for job {job_id}: {str(e)}')
            import traceback
            ai_logger.error(f'Traceback: {traceback.format_exc()}')
            return JsonResponse({'error': f'Error processing request: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ScoringStatusView(View):
    """
    View to check scoring status for a job listing
    """
    def get(self, request, job_id):
        try:
            # Use the resume scoring service to get the status
            result = ResumeScoringService.get_scoring_status(job_id)

            return JsonResponse(result)

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

            # Use the resume scoring service to get the applicants
            result = ResumeScoringService.get_scored_applicants(job_id, status_filter, limit, offset)

            # Add email to each applicant record in the response
            for applicant_data in result['applicants']:
                try:
                    applicant = Applicant.objects.get(id=applicant_data['id'])
                    applicant_data['email'] = getattr(applicant, 'email', None)
                    # Update the analysis_date field to match the original format
                    if hasattr(applicant, 'analysis_timestamp') and applicant.analysis_timestamp:
                        applicant_data['analysis_date'] = applicant.analysis_timestamp
                except Applicant.DoesNotExist:
                    applicant_data['email'] = None
                    applicant_data['analysis_date'] = None

            return JsonResponse(result)
            
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
            # Use the resume scoring service to get the detailed analysis
            result = ResumeScoringService.get_detailed_analysis(applicant_id)

            return JsonResponse(result)

        except Applicant.DoesNotExist:
            return JsonResponse({'error': 'Applicant not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error retrieving analysis: {str(e)}'}, status=500)


from hr_assistant.services.report_utils import get_candidates_for_job
import json


class CandidateReportView(View):
    """
    Django Class-Based View for the candidate report page.
    Retrieves all analyzed candidates associated with the active job and renders the main report page.
    Handles query parameters for sorting and filtering.
    """
    template_name = 'jobs/scoring_results.html'

    def get(self, request, *args, **kwargs):
        # Get job_id from URL kwargs or default to active job if available
        job_id = kwargs.get('job_id')

        if not job_id:
            # If no job_id specified, try to get the active job
            active_job = JobListing.objects.filter(is_active=True).first()
            if active_job:
                job_id = active_job.id
            else:
                # If no active job, return empty list
                context = {
                    'job_id': None,
                    'candidates': [],
                    'job_title': 'No Active Job'
                }
                return render(request, self.template_name, context)

        # Get query parameters for sorting and filtering
        sort_by = request.GET.get('sort_by', 'overall_score')
        sort_order = request.GET.get('sort_order', 'desc')

        # Safely handle score threshold parameter, defaulting to 0 if invalid
        try:
            score_threshold = int(request.GET.get('score_threshold', 0))
        except ValueError:
            score_threshold = 0

        # Validate and limit score threshold (0-100 as per spec)
        if not (0 <= score_threshold <= 100):
            score_threshold = 0

        # Get candidates using the report utility function
        candidates = get_candidates_for_job(
            job_id=job_id,
            sort_by=sort_by,
            sort_order=sort_order,
            score_threshold=score_threshold
        )

        # Prepare candidate data for the template
        candidate_data = []
        for candidate in candidates:
            candidate_dict = {
                'id': candidate.id,
                'applicant_name': candidate.applicant_name,
                'overall_score': candidate.overall_score,
                'categorization': candidate.categorization,
                'quality_grade': candidate.quality_grade,
                'justification_summary': candidate.justification_summary or '',
                'is_shortlisted': candidate.is_shortlisted,
            }
            candidate_data.append(candidate_dict)

        # Get job title for context
        try:
            job = JobListing.objects.get(id=job_id)
            job_title = job.title
        except JobListing.DoesNotExist:
            job_title = 'Unknown Job'

        # Create context for the template
        context = {
            'job_id': job_id,
            'job_title': job_title,
            'candidates': candidate_data,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'score_threshold': score_threshold,
        }

        return render(request, self.template_name, context)


@csrf_exempt
def toggle_shortlist_status(request, candidate_id):
    """
    API endpoint to toggle the shortlist status of a candidate.
    """
    from hr_assistant.services.report_utils import toggle_shortlist_status as util_toggle_shortlist

    if request.method == 'POST':
        new_status = util_toggle_shortlist(candidate_id)

        if new_status is not False:  # False indicates the candidate was not found
            return JsonResponse({
                'candidate_id': candidate_id,
                'is_shortlisted': new_status,
                'message': 'Candidate shortlist status updated successfully'
            })
        else:
            return JsonResponse({
                'error': 'Candidate not found'
            }, status=404)
    else:
        return JsonResponse({
            'error': 'Invalid request method. Use POST.'
        }, status=400)


class ScoringResultsView(View):
    """
    View to display the results of the AI scoring process
    """
    def get(self, request):
        return render(request, 'jobs/scoring_results.html')


class CandidateReportAPIView(View):
    """
    API endpoint to return candidate data for the reporting page
    """
    def get(self, request):
        from hr_assistant.services.report_utils import get_candidates_for_job

        # Get job_id from query parameters or try to get active job
        job_id = request.GET.get('job_id')
        if not job_id:
            # Try to get the active job
            active_job = JobListing.objects.filter(is_active=True).first()
            if active_job:
                job_id = int(active_job.id)  # Convert to int immediately when getting from active job
            else:
                # If no active job, return empty list
                return JsonResponse({
                    'job_id': None,
                    'candidates': [],
                    'job_title': 'No Active Job'
                })
        else:
            job_id = int(job_id)

        # If we have a job_id (not None), use it to get candidates
        if job_id:
            # Get query parameters for sorting and filtering
            sort_by = request.GET.get('sort_by', 'overall_score')
            sort_order = request.GET.get('sort_order', 'desc')

            # Safely handle score threshold parameter, defaulting to 0 if invalid
            try:
                score_threshold = int(request.GET.get('score_threshold', 0))
            except ValueError:
                score_threshold = 0

            # Validate and limit score threshold (0-100 as per spec)
            if not (0 <= score_threshold <= 100):
                score_threshold = 0

            # Get candidates using the report utility function
            candidates = get_candidates_for_job(
                job_id=job_id,
                sort_by=sort_by,
                sort_order=sort_order,
                score_threshold=score_threshold
            )
        else:
            # If no job_id (None), return empty list
            candidates = []
            sort_by = 'overall_score'
            sort_order = 'desc'
            score_threshold = 0

        # Prepare candidate data for the API response
        candidate_data = []
        for candidate in candidates:
            candidate_dict = {
                'id': candidate.id,
                'applicant_name': candidate.applicant_name,
                'overall_score': candidate.overall_score,
                'categorization': candidate.categorization,
                'quality_grade': candidate.quality_grade,
                'justification_summary': candidate.justification_summary or '',
                'is_shortlisted': candidate.is_shortlisted,
            }
            candidate_data.append(candidate_dict)

        # Get job title for context
        if job_id:
            try:
                job = JobListing.objects.get(id=job_id)
                job_title = job.title
            except JobListing.DoesNotExist:
                job_title = 'Unknown Job'
        else:
            job_title = 'No Active Job'

        # Return JSON response
        return JsonResponse({
            'job_id': job_id,
            'job_title': job_title,
            'candidates': candidate_data,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'score_threshold': score_threshold,
        })