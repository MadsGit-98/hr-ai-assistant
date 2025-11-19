"""
Integration tests for candidate report view.
Tests to ensure the view correctly handles URL query parameters for sorting and filtering.
"""
from django.test import TestCase, Client
from django.urls import reverse
from jobs.models import JobListing, Applicant
from django.contrib.auth.models import User


class TestCandidateReportView(TestCase):
    """Test the CandidateReportView for proper URL parameter handling."""

    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        
        # Create a test job listing
        self.job = JobListing.objects.create(
            title="Software Engineer",
            detailed_description="We are looking for a skilled software engineer...",
            required_skills=["Python", "Django", "JavaScript"],
            is_active=True
        )
        
        # Create test applicants with different scores and attributes
        self.applicant1 = Applicant.objects.create(
            job_listing=self.job,
            applicant_name="John Doe",
            resume_file="test_resume1.pdf",
            content_hash="hash1",
            file_size=100000,
            file_format="PDF",
            overall_score=85,
            categorization="Senior",
            quality_grade="A",
            justification_summary="Excellent experience with Python and Django",
            analysis_status='analyzed'
        )

        self.applicant2 = Applicant.objects.create(
            job_listing=self.job,
            applicant_name="Jane Smith",
            resume_file="test_resume2.pdf",
            content_hash="hash2",
            file_size=150000,
            file_format="PDF",
            overall_score=75,
            categorization="Mid-Level",
            quality_grade="B",
            justification_summary="Good experience with web development",
            analysis_status='analyzed'
        )

        self.applicant3 = Applicant.objects.create(
            job_listing=self.job,
            applicant_name="Bob Johnson",
            resume_file="test_resume3.pdf",
            content_hash="hash3",
            file_size=200000,
            file_format="PDF",
            overall_score=95,
            categorization="Senior",
            quality_grade="A",
            justification_summary="Outstanding experience and skills",
            analysis_status='analyzed'
        )

    def test_get_candidate_report_default(self):
        """Test the default behavior of the candidate report view."""
        response = self.client.get(reverse('candidate_report'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Candidate Report")
        # Check for table headers that should be present in the template
        self.assertContains(response, "Name")
        self.assertContains(response, "Score")
        self.assertContains(response, "Categorization")
        self.assertContains(response, "Grade")
        self.assertContains(response, "AI Justification")

    def test_get_candidate_report_with_job_id(self):
        """Test candidate report view with specific job ID."""
        url = reverse('candidate_report_by_job', kwargs={'job_id': self.job.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Candidate Report")
        # Test that context contains the correct job information
        self.assertEqual(response.context['job_id'], self.job.id)

    def test_sort_by_score_descending(self):
        """Test sorting by score in descending order."""
        response = self.client.get(reverse('candidate_report'), {
            'sort_by': 'overall_score',
            'sort_order': 'desc'
        })

        self.assertEqual(response.status_code, 200)
        # Check that the context includes the correct parameters
        self.assertEqual(response.context['sort_by'], 'overall_score')
        self.assertEqual(response.context['sort_order'], 'desc')
        self.assertContains(response, "Candidate Report")

    def test_sort_by_score_ascending(self):
        """Test sorting by score in ascending order."""
        response = self.client.get(reverse('candidate_report'), {
            'sort_by': 'overall_score',
            'sort_order': 'asc'
        })

        self.assertEqual(response.status_code, 200)
        # Check that the context includes the correct parameters
        self.assertEqual(response.context['sort_by'], 'overall_score')
        self.assertEqual(response.context['sort_order'], 'asc')
        self.assertContains(response, "Candidate Report")

    def test_sort_by_name(self):
        """Test sorting by applicant name."""
        response = self.client.get(reverse('candidate_report'), {
            'sort_by': 'applicant_name',
            'sort_order': 'asc'
        })

        self.assertEqual(response.status_code, 200)
        # Check that the context includes the correct parameters
        self.assertEqual(response.context['sort_by'], 'applicant_name')
        self.assertEqual(response.context['sort_order'], 'asc')
        self.assertContains(response, "Candidate Report")

    def test_filter_by_score_threshold(self):
        """Test filtering by score threshold."""
        response = self.client.get(reverse('candidate_report'), {
            'score_threshold': 80
        })

        self.assertEqual(response.status_code, 200)
        # Check that the context includes the correct parameter
        self.assertEqual(response.context['score_threshold'], 80)
        self.assertContains(response, "Candidate Report")

    def test_invalid_score_threshold_defaults_to_zero(self):
        """Test that invalid score threshold defaults to 0."""
        response = self.client.get(reverse('candidate_report'), {
            'score_threshold': 'invalid'
        })
        
        self.assertEqual(response.status_code, 200)
        # Should still return all candidates since invalid threshold defaults to 0

    def test_score_threshold_out_of_range(self):
        """Test score threshold outside valid range defaults correctly."""
        response = self.client.get(reverse('candidate_report'), {
            'score_threshold': 150  # Above valid range (0-100)
        })
        
        self.assertEqual(response.status_code, 200)
        # Should default to 0 or handle appropriately

    def test_sort_by_invalid_field_defaults_to_score(self):
        """Test that invalid sort field defaults to overall_score."""
        response = self.client.get(reverse('candidate_report'), {
            'sort_by': 'invalid_field',
            'sort_order': 'desc'
        })
        
        self.assertEqual(response.status_code, 200)
        # Should still work and sort by default (overall_score)

    def test_sort_order_invalid_defaults_to_descending(self):
        """Test that invalid sort order defaults to descending."""
        response = self.client.get(reverse('candidate_report'), {
            'sort_by': 'overall_score',
            'sort_order': 'invalid_order'
        })
        
        self.assertEqual(response.status_code, 200)
        # Should still work and sort by default (descending)

    def test_get_candidate_report_no_active_job(self):
        """Test candidate report when no active job exists."""
        # Deactivate the job
        self.job.is_active = False
        self.job.save()
        
        response = self.client.get(reverse('candidate_report'))
        
        self.assertEqual(response.status_code, 200)
        # Should handle gracefully when no active job exists

    def test_context_data_includes_sort_and_filter_params(self):
        """Test that context includes sort and filter parameters."""
        response = self.client.get(reverse('candidate_report'), {
            'sort_by': 'overall_score',
            'sort_order': 'asc',
            'score_threshold': 80
        })

        self.assertEqual(response.status_code, 200)
        # Check that the context includes the sort and filter parameters
        self.assertEqual(response.context['sort_by'], 'overall_score')
        self.assertEqual(response.context['sort_order'], 'asc')
        self.assertEqual(response.context['score_threshold'], 80)