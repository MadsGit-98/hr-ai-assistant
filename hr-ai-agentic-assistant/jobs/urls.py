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
]