from django.urls import path
from . import views

urlpatterns = [
    # Resume upload endpoint
    path('upload/', views.ApplicantUploadView.as_view(), name='applicant_upload'),

    # T018: URL for creating job listings
    path('', views.JobListingCreateView.as_view(), name='joblisting_create'),

    # T027: URLs for detail and list views
    path('list/', views.JobListingListView.as_view(), name='joblisting_list'),
    path('<int:pk>/', views.JobListingDetailView.as_view(), name='joblisting_detail'),

    # T034: URLs for update and delete
    path('<int:pk>/edit/', views.JobListingUpdateView.as_view(), name='joblisting_update'),
    path('<int:pk>/delete/', views.JobListingDeleteView.as_view(), name='joblisting_delete'),

    # T037: URL for activate endpoint
    path('<int:pk>/activate/', views.activate_job_listing, name='joblisting_activate'),

    # AI Resume Scoring API endpoints (for the new feature)
    path('api/job-listings/<int:job_id>/score-resumes/', views.ScoreResumesView.as_view(), name='score_resumes'),
    path('api/job-listings/<int:job_id>/scoring-status/', views.ScoringStatusView.as_view(), name='scoring_status'),
    path('api/job-listings/<int:job_id>/scored-applicants/', views.ScoredApplicantsView.as_view(), name='scored_applicants'),
    path('api/applicants/<int:applicant_id>/detailed-analysis/', views.DetailedAnalysisView.as_view(), name='detailed_analysis'),

    # AI Resume Scoring Results page
    path('scoring-results/', views.ScoringResultsView.as_view(), name='scoring_results'),

    # Candidate Reporting and Shortlisting Feature
    path('scoring_results/', views.CandidateReportView.as_view(), name='candidate_report'),
    path('jobs/<int:job_id>/candidates/', views.CandidateReportView.as_view(), name='candidate_report_by_job'),
    path('api/candidates/', views.CandidateReportAPIView.as_view(), name='candidate_report_api'),
]