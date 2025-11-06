"""
Unit tests for views (T013, T021, T029)
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from jobs.models import JobListing


class TestJobListingViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.job = JobListing.objects.create(
            title="Test Job",
            detailed_description="Test job description",
            required_skills=["Python", "Django"]
        )
    
    def test_job_listing_create_view(self):
        """T013: Unit test for create view functionality"""
        response = self.client.get(reverse('joblisting_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/joblisting_form.html')
        
        # Test form submission
        response = self.client.post(reverse('joblisting_create'), {
            'title': 'New Job',
            'detailed_description': 'New job description',
            'required_skills': 'Python, Django, JavaScript',
            'is_active': False
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertEqual(JobListing.objects.count(), 2)  # One from setup + one created
    
    def test_job_listing_detail_view(self):
        """T021: Unit test for detail view functionality"""
        response = self.client.get(reverse('joblisting_detail', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/joblisting_detail.html')
        self.assertContains(response, self.job.title)
    
    def test_job_listing_list_view(self):
        """Test list view functionality"""
        response = self.client.get(reverse('joblisting_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/joblisting_list.html')
        self.assertContains(response, self.job.title)
    
    def test_job_listing_update_view(self):
        """T029: Unit test for update view functionality"""
        response = self.client.get(reverse('joblisting_update', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/joblisting_form.html')
        
        # Test form submission to update
        response = self.client.post(reverse('joblisting_update', kwargs={'pk': self.job.pk}), {
            'title': 'Updated Job',
            'detailed_description': 'Updated description',
            'required_skills': 'Python, Updated Skill',
            'is_active': True,
            'version': self.job.modified_date.timestamp()  # Include version for optimistic locking
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, 'Updated Job')
    
    def test_job_listing_delete_view(self):
        """Test delete view functionality"""
        response = self.client.get(reverse('joblisting_delete', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/joblisting_confirm_delete.html')
        
        # Test deletion
        response = self.client.post(reverse('joblisting_delete', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertEqual(JobListing.objects.count(), 0)
    
    def test_activate_job_listing_view(self):
        """Test activate job listing functionality"""
        # Initially job is not active
        self.assertFalse(self.job.is_active)
        
        # Activate the job
        response = self.client.post(reverse('joblisting_activate', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect after activation
        
        # Check that job is now active
        self.job.refresh_from_db()
        self.assertTrue(self.job.is_active)