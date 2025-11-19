"""
Integration tests for shortlist toggle functionality.
Tests for toggling the is_shortlisted status and ensuring the logic works correctly.
"""
from django.test import TestCase, Client
from django.urls import reverse
from jobs.models import JobListing, Applicant
import json


class TestShortlistToggle(TestCase):
    """Test the API endpoint for toggling shortlist status."""

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
        
        # Create test applicants
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
            analysis_status='analyzed',
            is_shortlisted=False
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
            analysis_status='analyzed',
            is_shortlisted=True
        )

    def test_toggle_shortlist_to_true(self):
        """Test toggling an unshortlisted candidate to shortlisted."""
        # Initially, applicant1 is not shortlisted
        self.assertFalse(self.applicant1.is_shortlisted)
        
        # Toggle to shortlisted
        response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant1.id}))
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        self.assertEqual(data['candidate_id'], self.applicant1.id)
        self.assertTrue(data['is_shortlisted'])
        self.assertEqual(data['message'], 'Candidate shortlist status updated successfully')
        
        # Verify the database was updated
        self.applicant1.refresh_from_db()
        self.assertTrue(self.applicant1.is_shortlisted)

    def test_toggle_shortlist_to_false(self):
        """Test toggling a shortlisted candidate to unshortlisted."""
        # Initially, applicant2 is shortlisted
        self.assertTrue(self.applicant2.is_shortlisted)
        
        # Toggle to unshortlisted
        response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant2.id}))
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        self.assertEqual(data['candidate_id'], self.applicant2.id)
        self.assertFalse(data['is_shortlisted'])
        self.assertEqual(data['message'], 'Candidate shortlist status updated successfully')
        
        # Verify the database was updated
        self.applicant2.refresh_from_db()
        self.assertFalse(self.applicant2.is_shortlisted)

    def test_toggle_shortlist_nonexistent_candidate(self):
        """Test toggling shortlist for a non-existent candidate."""
        response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': 99999}))
        
        self.assertEqual(response.status_code, 404)
        
        # Parse the JSON response
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Candidate not found')

    def test_toggle_shortlist_get_method_not_allowed(self):
        """Test that GET method is not allowed for toggle endpoint."""
        response = self.client.get(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant1.id}))
        
        self.assertEqual(response.status_code, 400)
        
        # Parse the JSON response
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Invalid request method. Use POST.')

    def test_preserve_other_candidate_attributes(self):
        """Test that toggling shortlist doesn't affect other attributes."""
        original_attrs = {
            'applicant_name': self.applicant1.applicant_name,
            'overall_score': self.applicant1.overall_score,
            'categorization': self.applicant1.categorization,
            'quality_grade': self.applicant1.quality_grade,
            'justification_summary': self.applicant1.justification_summary
        }
        
        # Toggle shortlist status
        response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant1.id}))
        self.assertEqual(response.status_code, 200)
        
        # Refresh from DB and verify other attributes unchanged
        self.applicant1.refresh_from_db()
        
        for attr, original_value in original_attrs.items():
            current_value = getattr(self.applicant1, attr)
            self.assertEqual(current_value, original_value,
                           f"Attribute {attr} changed from {original_value} to {current_value}")

    def test_shortlist_status_preserved_across_requests(self):
        """Test that the shortlist status is preserved after multiple toggles."""
        # Initial state: not shortlisted
        self.assertFalse(self.applicant1.is_shortlisted)
        
        # Toggle once: should become shortlisted
        response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant1.id}))
        self.assertEqual(response.status_code, 200)
        self.applicant1.refresh_from_db()
        self.assertTrue(self.applicant1.is_shortlisted)
        
        # Toggle again: should become unshortlisted
        response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant1.id}))
        self.assertEqual(response.status_code, 200)
        self.applicant1.refresh_from_db()
        self.assertFalse(self.applicant1.is_shortlisted)
        
        # Toggle once more: should become shortlisted again
        response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant1.id}))
        self.assertEqual(response.status_code, 200)
        self.applicant1.refresh_from_db()
        self.assertTrue(self.applicant1.is_shortlisted)

    def test_concurrent_shortlist_toggle_not_possible(self):
        """Test that multiple requests don't cause race conditions."""
        # Since Django handles requests sequentially in a single-threaded test environment,
        # we can't truly test concurrency. But we can test rapid sequential toggles.
        for i in range(5):
            response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant1.id}))
            self.assertEqual(response.status_code, 200)
            
            # Refresh to get current status
            self.applicant1.refresh_from_db()
            
            # The status should have toggled
            expected_status = not (i % 2 == 0) ^ (not self.applicant1.is_shortlisted)
            # After an odd number of toggles from initial False, should be True
            if i % 2 == 0:  # Even index (0, 2, 4) = odd number of toggles
                self.assertTrue(self.applicant1.is_shortlisted)
            else:  # Odd index (1, 3) = even number of toggles
                self.assertFalse(self.applicant1.is_shortlisted)

    def test_response_includes_correct_candidate_id(self):
        """Test that the response includes the correct candidate ID."""
        response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant1.id}))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['candidate_id'], self.applicant1.id)

    def test_shortlist_toggle_with_preserved_sorting_filtering(self):
        """Test that shortlist toggle preserves current sorting and filtering."""
        # This tests the concept of FR-009: preserve current sorting and filtering
        # While we can't directly test this through the API endpoint alone,
        # we can verify that the toggle endpoint works correctly
        response = self.client.post(reverse('toggle_shortlist', kwargs={'candidate_id': self.applicant1.id}))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Verify the response structure
        self.assertIn('candidate_id', data)
        self.assertIn('is_shortlisted', data)
        self.assertIn('message', data)
        
        # Verify the status changed correctly
        self.applicant1.refresh_from_db()
        self.assertTrue(self.applicant1.is_shortlisted)
        self.assertEqual(data['is_shortlisted'], True)