from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from jobs.models import JobListing, Applicant
import tempfile
import os
import json


class JobApplicantRelationshipTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a job listing for testing
        self.job_listing = JobListing.objects.create(
            title="Software Engineer",
            detailed_description="We are looking for a skilled software engineer...",
            required_skills=["Python", "Django", "JavaScript"],
            is_active=True
        )
        
        # Create an inactive job listing for testing
        self.inactive_job = JobListing.objects.create(
            title="Marketing Manager",
            detailed_description="We are looking for a marketing professional...",
            required_skills=["Marketing", "SEO", "Content Creation"],
            is_active=False
        )

    def test_applicant_creation_with_job_listing(self):
        """Test that applicants can be created with a job listing relationship"""
        applicant = Applicant.objects.create(
            job_listing=self.job_listing,
            applicant_name="John Doe",
            resume_file='test_resume.pdf',
            content_hash="a" * 64,
            file_size=2000,
            file_format="PDF"
        )
        
        self.assertEqual(applicant.job_listing, self.job_listing)
        self.assertEqual(applicant.applicant_name, "John Doe")
        
        # Check that the relationship works in reverse
        self.assertIn(applicant, self.job_listing.applicants.all())

    def test_applicant_validation_with_inactive_job_listing(self):
        """Test that validation prevents applicants from being added to inactive job listings"""
        applicant = Applicant(
            job_listing=self.inactive_job,  # Using inactive job
            applicant_name="John Doe",
            resume_file='test_resume.pdf',
            content_hash="a" * 64,
            file_size=2000,
            file_format="PDF"
        )
        
        with self.assertRaises(Exception):  # This will raise ValidationError
            applicant.full_clean()
    
    def test_applicant_model_allows_null_job_listing(self):
        """Test that the model allows null job listings for backward compatibility"""
        # Due to migration requirements, the field is nullable to support existing records
        # New records via the upload flow will always have a job listing
        applicant = Applicant(
            job_listing=None,  # This should be allowed for backward compatibility
            applicant_name="John Doe",
            resume_file='test_resume.pdf',
            content_hash="a" * 64,
            file_size=2000,
            file_format="PDF"
        )
        
        # The validation should pass since job_listing is nullable
        # (the upload view ensures job_listing is always set in practice)
        try:
            applicant.full_clean()
            # If validation passes, the model is correctly configured
            self.assertIsNone(applicant.job_listing)
        except ValidationError:
            self.fail("Applicant with null job_listing should be allowed for backward compatibility")

    def test_job_listing_applicants_relationship(self):
        """Test that the one-to-many relationship works properly"""
        # Create multiple applicants for the same job listing
        applicant1 = Applicant.objects.create(
            job_listing=self.job_listing,
            applicant_name="John Doe",
            resume_file='test_resume1.pdf',
            content_hash="a" * 64,
            file_size=2000,
            file_format="PDF"
        )
        
        applicant2 = Applicant.objects.create(
            job_listing=self.job_listing,
            applicant_name="Jane Smith",
            resume_file='test_resume2.pdf',
            content_hash="b" * 64,
            file_size=2500,
            file_format="PDF"
        )
        
        # Check that the job listing has both applicants
        self.assertEqual(self.job_listing.applicants.count(), 2)
        self.assertIn(applicant1, self.job_listing.applicants.all())
        self.assertIn(applicant2, self.job_listing.applicants.all())

    def test_multiple_job_listings_separation(self):
        """Test that applicants are properly associated with their respective job listings"""
        # Create applicants for active job
        applicant1 = Applicant.objects.create(
            job_listing=self.job_listing,
            applicant_name="John Doe",
            resume_file='test_resume1.pdf',
            content_hash="a" * 64,
            file_size=2000,
            file_format="PDF"
        )
        
        # Create applicants for inactive job
        applicant2 = Applicant.objects.create(
            job_listing=self.inactive_job,
            applicant_name="Jane Smith",
            resume_file='test_resume2.pdf',
            content_hash="b" * 64,
            file_size=2500,
            file_format="PDF"
        )
        
        # Check that each job listing has its own applicants
        self.assertEqual(self.job_listing.applicants.count(), 1)
        self.assertIn(applicant1, self.job_listing.applicants.all())
        self.assertNotIn(applicant2, self.job_listing.applicants.all())
        
        self.assertEqual(self.inactive_job.applicants.count(), 1)
        self.assertIn(applicant2, self.inactive_job.applicants.all())
        self.assertNotIn(applicant1, self.inactive_job.applicants.all())


class JobApplicantUploadViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('applicant_upload')
        
        # Create an active job listing
        self.active_job = JobListing.objects.create(
            title="Software Engineer",
            detailed_description="We are looking for a skilled software engineer...",
            required_skills=["Python", "Django", "JavaScript"],
            is_active=True
        )
        
        # Create an inactive job listing
        self.inactive_job = JobListing.objects.create(
            title="Marketing Manager",
            detailed_description="We are looking for a marketing professional...",
            required_skills=["Marketing", "SEO", "Content Creation"],
            is_active=False
        )

    def test_upload_with_active_job_listing(self):
        """Test that resume upload works when there's an active job listing"""
        # Create a simple PDF-like file with sufficient size (>1KB)
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 1\n/Kids [3 0 R]\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>' + b'x' * 1024  # Add extra data to ensure >1KB
        pdf_file = SimpleUploadedFile("test_resume.pdf", pdf_content, content_type="application/pdf")

        response = self.client.post(self.upload_url, {'resume_files': [pdf_file]}, format='multipart')

        # The response should be JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Check that the applicant was created with the active job listing
        # The name will be extracted from the filename "test_resume.pdf" -> "Test Resume"
        applicant = Applicant.objects.get(applicant_name="Test Resume")
        self.assertEqual(applicant.job_listing, self.active_job)

    def test_upload_with_no_active_job_listing(self):
        """Test that resume upload fails when there's no active job listing"""
        # Deactivate the active job
        self.active_job.is_active = False
        self.active_job.save()
        
        # Try to upload a file
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 1\n/Kids [3 0 R]\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>' + b'x' * 1024  # Add extra data to ensure >1KB
        pdf_file = SimpleUploadedFile("test_resume.pdf", pdf_content, content_type="application/pdf")

        response = self.client.post(self.upload_url, {'resume_files': [pdf_file]}, format='multipart')

        # The response should be JSON with an error
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
        self.assertIn('No active job listing', response_data['error'])

    def test_get_upload_page_with_active_job_listing(self):
        """Test that GET request to upload page succeeds when there's an active job listing"""
        response = self.client.get(self.upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resume Upload')

    def test_get_upload_page_with_no_active_job_listing(self):
        """Test that GET request redirects when there's no active job listing"""
        # Deactivate the active job
        self.active_job.is_active = False
        self.active_job.save()
        
        response = self.client.get(self.upload_url)
        # Should redirect to job listing page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('joblisting_list'))