"""
Test cases for JobListing model (T012, T022, T030)
"""
import unittest
from django.test import TestCase
from jobs.models import JobListing


class TestJobListingModel(TestCase):
    
    def test_job_listing_creation(self):
        """T012: Test JobListing model creation validation"""
        job = JobListing.objects.create(
            title="Software Engineer",
            detailed_description="Job requiring Python and Django skills",
            required_skills=["Python", "Django", "SQL"]
        )
        self.assertEqual(job.title, "Software Engineer")
        self.assertEqual(job.required_skills, ["Python", "Django", "SQL"])
        self.assertFalse(job.is_active)  # Default value
    
    def test_job_listing_with_active_status(self):
        """Test creating an active job listing"""
        job = JobListing.objects.create(
            title="Active Job",
            detailed_description="Active job description",
            required_skills=["Skill1", "Skill2"],
            is_active=True
        )
        self.assertTrue(job.is_active)
    
    def test_single_active_listing_constraint(self):
        """T022, T030: Test that only one job listing can be active at a time"""
        # Create first active job listing
        job1 = JobListing.objects.create(
            title="First Job",
            detailed_description="First job description",
            required_skills=["Skill1"],
            is_active=True
        )
        
        # Create second active job listing
        job2 = JobListing.objects.create(
            title="Second Job", 
            detailed_description="Second job description",
            required_skills=["Skill2"],
            is_active=True  # This should deactivate job1
        )
        
        # Refresh from database
        job1.refresh_from_db()
        job2.refresh_from_db()
        
        # Only job2 should be active, job1 should be inactive
        self.assertFalse(job1.is_active)
        self.assertTrue(job2.is_active)
    
    def test_title_max_length(self):
        """T006a: Test title max character limit"""
        long_title = "A" * 201  # 201 characters, exceeding the 200 limit
        job = JobListing(
            title=long_title,
            detailed_description="Test description",
            required_skills=["Skill1"]
        )
        
        # This should raise a validation error when saved
        # Django validates max_length during save
        with self.assertRaises(Exception):
            job.full_clean()  # This calls field validation
    
    def test_description_max_length(self):
        """T006b: Test detailed_description max character limit"""
        long_description = "A" * 50001  # 50001 characters, exceeding the 50000 limit
        job = JobListing(
            title="Test Job",
            detailed_description=long_description,
            required_skills=["Skill1"]
        )
        
        # This should raise a validation error during clean
        with self.assertRaises(Exception):
            job.full_clean()
    
    def test_skills_max_count(self):
        """T006c: Test required_skills max item limit"""
        too_many_skills = [f"Skill{i}" for i in range(101)]  # 101 skills, exceeding the 100 limit
        job = JobListing(
            title="Test Job",
            detailed_description="Test description",
            required_skills=too_many_skills
        )
        
        # This should raise a validation error during clean
        with self.assertRaises(Exception):
            job.full_clean()
    
    def test_markdown_rendering(self):
        """Test that markdown is properly rendered to HTML"""
        markdown_content = "**Bold text** and *italic text*"
        job = JobListing.objects.create(
            title="Markdown Test",
            detailed_description=markdown_content,
            required_skills=["Markdown"]
        )
        
        rendered = job.get_rendered_description()
        self.assertIn("<strong>Bold text</strong>", rendered)
        self.assertIn("<em>italic text</em>", rendered)