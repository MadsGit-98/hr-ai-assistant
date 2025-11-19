"""
Unit tests for candidate reporting functionality.
Tests for report utility functions to confirm correct in-memory sorting and threshold filtering logic.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from jobs.models import JobListing, Applicant
from hr_assistant.services.report_utils import (
    get_candidates_for_job,
    sort_candidates,
    filter_candidates_by_score,
    toggle_shortlist_status
)
from datetime import datetime


class TestReportUtils(TestCase):
    """Test the report utility functions for sorting and filtering."""

    def setUp(self):
        """Set up test data."""
        self.job = JobListing.objects.create(
            title="Software Engineer",
            detailed_description="We are looking for a skilled software engineer...",
            required_skills=["Python", "Django", "JavaScript"]
        )
        
        # Create test applicants with different scores
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
            analysis_status='analyzed',
            is_shortlisted=False
        )

    def test_get_candidates_for_job_default_sorting(self):
        """Test that get_candidates_for_job returns candidates sorted by overall_score descending by default."""
        candidates = get_candidates_for_job(self.job.id)
        
        # Should return all 3 candidates
        self.assertEqual(len(candidates), 3)
        
        # Should be sorted by overall_score descending (95, 85, 75)
        self.assertEqual(candidates[0].overall_score, 95)
        self.assertEqual(candidates[0].applicant_name, "Bob Johnson")
        self.assertEqual(candidates[2].overall_score, 75)
        self.assertEqual(candidates[2].applicant_name, "Jane Smith")

    def test_get_candidates_for_job_custom_sorting(self):
        """Test custom sorting functionality."""
        candidates = get_candidates_for_job(
            job_id=self.job.id,
            sort_by='applicant_name',
            sort_order='asc'
        )
        
        self.assertEqual(candidates[0].applicant_name, "Bob Johnson")
        self.assertEqual(candidates[1].applicant_name, "Jane Smith")
        self.assertEqual(candidates[2].applicant_name, "John Doe")

    def test_get_candidates_for_job_score_filtering(self):
        """Test score threshold filtering."""
        candidates = get_candidates_for_job(
            job_id=self.job.id,
            score_threshold=80
        )
        
        # Should only return applicants with score >= 80
        self.assertEqual(len(candidates), 2)
        for candidate in candidates:
            self.assertGreaterEqual(candidate.overall_score, 80)

    def test_get_candidates_for_job_sort_and_filter(self):
        """Test combining sorting and filtering."""
        candidates = get_candidates_for_job(
            job_id=self.job.id,
            sort_by='overall_score',
            sort_order='asc',
            score_threshold=80
        )
        
        # Should return only candidates with score >= 80, sorted ascending
        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0].overall_score, 85)  # John Doe
        self.assertEqual(candidates[1].overall_score, 95)  # Bob Johnson

    def test_get_candidates_for_job_max_limit(self):
        """Test that the function respects the 500 candidate limit."""
        # Create more than 500 applicants to test the limit
        for i in range(501):
            Applicant.objects.create(
                job_listing=self.job,
                applicant_name=f"Applicant {i}",
                resume_file=f"resume{i}.pdf",
                content_hash=f"hash_{i:04d}",  # Ensure unique hashes with consistent format
                file_size=100000,
                file_format="PDF",
                overall_score=50 + (i % 50),  # Scores between 50-99
                categorization="Mid-Level",
                quality_grade="C",
                justification_summary=f"Justification for applicant {i}",
                analysis_status='analyzed'
            )

        # Even with 503 total applicants (3 from setup + 501 new), should be limited to 500
        candidates = get_candidates_for_job(self.job.id)
        self.assertLessEqual(len(candidates), 500)

    def test_sort_candidates_by_overall_score(self):
        """Test sorting candidates by overall score."""
        candidates = [self.applicant1, self.applicant2, self.applicant3]
        
        # Test descending sort (default)
        sorted_desc = sort_candidates(candidates, 'overall_score', 'desc')
        self.assertEqual(sorted_desc[0].overall_score, 95)  # Bob Johnson
        self.assertEqual(sorted_desc[2].overall_score, 75)  # Jane Smith
        
        # Test ascending sort
        sorted_asc = sort_candidates(candidates, 'overall_score', 'asc')
        self.assertEqual(sorted_asc[0].overall_score, 75)  # Jane Smith
        self.assertEqual(sorted_asc[2].overall_score, 95)  # Bob Johnson

    def test_sort_candidates_by_name(self):
        """Test sorting candidates by name."""
        candidates = [self.applicant1, self.applicant2, self.applicant3]
        
        sorted_names = sort_candidates(candidates, 'applicant_name', 'asc')
        self.assertEqual(sorted_names[0].applicant_name, "Bob Johnson")
        self.assertEqual(sorted_names[2].applicant_name, "John Doe")

    def test_filter_candidates_by_score(self):
        """Test filtering candidates by score threshold."""
        candidates = [self.applicant1, self.applicant2, self.applicant3]
        
        # Filter for scores >= 80
        filtered = filter_candidates_by_score(candidates, 80)
        self.assertEqual(len(filtered), 2)
        
        for candidate in filtered:
            self.assertGreaterEqual(candidate.overall_score, 80)
    
    def test_filter_candidates_by_score_no_threshold(self):
        """Test filtering with no threshold (should return all)."""
        candidates = [self.applicant1, self.applicant2, self.applicant3]
        
        filtered = filter_candidates_by_score(candidates, 0)
        self.assertEqual(len(filtered), 3)
    
    def test_toggle_shortlist_status(self):
        """Test toggling shortlist status."""
        # Initially, applicant1 is not shortlisted
        self.assertFalse(self.applicant1.is_shortlisted)
        
        # Toggle status
        new_status = toggle_shortlist_status(self.applicant1.id)
        self.assertTrue(new_status)
        
        # Refresh from DB to confirm change
        self.applicant1.refresh_from_db()
        self.assertTrue(self.applicant1.is_shortlisted)
        
        # Toggle again to unshortlist
        new_status = toggle_shortlist_status(self.applicant1.id)
        self.assertFalse(new_status)
        
        self.applicant1.refresh_from_db()
        self.assertFalse(self.applicant1.is_shortlisted)

    def test_toggle_shortlist_status_nonexistent(self):
        """Test toggling shortlist status for non-existent candidate."""
        result = toggle_shortlist_status(99999)  # Non-existent ID
        self.assertFalse(result)  # Should return False

    def test_get_candidates_for_job_with_invalid_job(self):
        """Test get_candidates_for_job with invalid job ID."""
        candidates = get_candidates_for_job(99999)  # Non-existent job
        self.assertEqual(len(candidates), 0)

    def test_get_candidates_for_job_unanalyzed_candidates(self):
        """Test that only analyzed candidates are returned."""
        # Create unanalyzed candidate
        unanalyzed = Applicant.objects.create(
            job_listing=self.job,
            applicant_name="Unanalyzed Applicant",
            resume_file="test_resume4.pdf",
            content_hash="hash4",
            file_size=100000,
            file_format="PDF",
            analysis_status='pending',  # Not analyzed
            overall_score=None  # Score is null
        )
        
        candidates = get_candidates_for_job(self.job.id)
        
        # Should not include the unanalyzed candidate
        candidate_names = [c.applicant_name for c in candidates]
        self.assertNotIn("Unanalyzed Applicant", candidate_names)
        self.assertEqual(len(candidates), 3)  # Only the 3 analyzed ones