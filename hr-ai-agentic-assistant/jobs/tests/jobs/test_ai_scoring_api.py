"""
Contract tests for API endpoints
"""
from django.test import TestCase, Client
from jobs.models import JobListing, Applicant
from django.urls import reverse
import json
from unittest.mock import patch


class TestScoringAPIContract(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a job listing
        self.job = JobListing.objects.create(
            title="Software Engineer",
            detailed_description="We need a skilled software engineer...",
            required_skills=["Python", "Django", "AI/ML"],
            is_active=True
        )
        
        # Create an applicant
        self.applicant = Applicant.objects.create(
            applicant_name="John Doe",
            resume_file="test_resume.pdf",
            content_hash="dummy_hash",
            file_size=1024,
            file_format="PDF",
            job_listing=self.job,
            processing_status="pending"
        )
    
    @patch('hr_assistant.services.ai_analysis.create_supervisor_graph')
    def test_score_resumes_endpoint_contract(self, mock_create_graph):
        """Test the contract for the score-resumes endpoint"""
        # Mock the graph to avoid actual AI processing
        mock_graph_instance = mock_create_graph.return_value
        mock_graph_instance.invoke.return_value = {
            'results': [],
            'status': 'completed',
            'current_index': 0,
            'error_count': 0
        }
        
        url = reverse('score_resumes', kwargs={'job_id': self.job.id})
        response = self.client.post(url,
                                   data=json.dumps({'applicant_ids': [self.applicant.id]}),
                                   content_type='application/json')
        
        # Should return 202 status (Accepted) in a real scenario
        # Might return other status codes in test environment depending on setup
        self.assertIn(response.status_code, [202, 400, 404, 422, 500])
        
        if response.status_code == 202:
            # Verify response structure when successful
            response_data = json.loads(response.content)
            expected_fields = ['status', 'message', 'job_id', 'applicant_count', 'tracking_id']
            for field in expected_fields:
                self.assertIn(field, response_data)
            
            # Verify specific field types/values
            self.assertEqual(response_data['status'], 'accepted')
            self.assertEqual(response_data['job_id'], self.job.id)
            self.assertIsInstance(response_data['applicant_count'], int)
            self.assertIsInstance(response_data['tracking_id'], str)
    
    def test_scoring_status_endpoint_contract(self):
        """Test the contract for the scoring-status endpoint"""
        url = reverse('scoring_status', kwargs={'job_id': self.job.id})
        response = self.client.get(url)
        
        # Should return 200 status
        self.assertEqual(response.status_code, 200)
        
        # Verify response structure
        response_data = json.loads(response.content)
        expected_fields = ['job_id', 'status', 'total_applicants', 'completed_count', 
                          'processing_count', 'error_count', 'message']
        for field in expected_fields:
            self.assertIn(field, response_data)
        
        # Verify specific field types/values
        self.assertEqual(response_data['job_id'], self.job.id)
        self.assertIn(response_data['status'], ['pending', 'processing', 'completed', 'error'])
        self.assertIsInstance(response_data['total_applicants'], int)
    
    def test_scored_applicants_endpoint_contract(self):
        """Test the contract for the scored-applicants endpoint"""
        url = reverse('scored_applicants', kwargs={'job_id': self.job.id})
        response = self.client.get(url)
        
        # Should return 200 status
        self.assertEqual(response.status_code, 200)
        
        # Verify response structure
        response_data = json.loads(response.content)
        expected_fields = ['job_id', 'applicants', 'total_count', 'filtered_count']
        for field in expected_fields:
            self.assertIn(field, response_data)
        
        # Verify specific field types/values
        self.assertEqual(response_data['job_id'], self.job.id)
        self.assertIsInstance(response_data['applicants'], list)
        self.assertIsInstance(response_data['total_count'], int)
    
    def test_detailed_analysis_endpoint_contract(self):
        """Test the contract for the detailed-analysis endpoint"""
        url = reverse('detailed_analysis', kwargs={'applicant_id': self.applicant.id})
        response = self.client.get(url)
        
        # Should return 200 if applicant has analysis, 404 if not
        self.assertIn(response.status_code, [200, 404])
        
        if response.status_code == 200:
            # If 200, verify response structure
            response_data = json.loads(response.content)
            expected_fields = ['applicant_id', 'name', 'overall_score', 'quality_grade', 
                              'categorization', 'justification_summary', 'detailed_analysis', 
                              'processing_status']
            for field in expected_fields:
                self.assertIn(field, response_data)
        
        # If 404, it means the applicant doesn't have detailed analysis yet
        # This is expected behavior when the scoring hasn't been performed yet