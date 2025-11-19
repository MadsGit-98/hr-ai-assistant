"""
End-to-End tests for candidate reporting functionality.
Tests covering the critical user journeys as defined in the specification.
"""
from django.test import TestCase, Client
from django.urls import reverse
from jobs.models import JobListing, Applicant
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class TestCandidateReportingE2E(TestCase):
    """End-to-End tests for candidate reporting and shortlisting functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up the test browser."""
        super().setUpClass()
        
        # Set up Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode for tests
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the WebDriver
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        """Close the test browser."""
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """Set up test data."""
        # Create a test job listing
        self.job = JobListing.objects.create(
            title="Software Engineer",
            detailed_description="We are looking for a skilled software engineer...",
            required_skills=["Python", "Django", "JavaScript"],
            is_active=True
        )
        
        # Create test applicants with different scores
        self.applicant1 = Applicant.objects.create(
            job_listing=self.job,
            applicant_name="John Doe",
            resume_file="test_resume1.pdf",
            content_hash="hash1",
            file_size=100000,
            file_format="PDF",
            overall_score=87,
            categorization="Senior",
            quality_grade="A",
            justification_summary="Excellent experience with Python and Django frameworks. Very skilled in web development, with 8+ years of experience building scalable applications.",
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
            overall_score=72,
            categorization="Mid-Level",
            quality_grade="B",
            justification_summary="Good experience with web development and APIs. 5 years of experience with JavaScript and React.",
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
            justification_summary="Outstanding experience and skills in full-stack development. Expert in Python, Django, and modern JavaScript frameworks.",
            analysis_status='analyzed',
            is_shortlisted=False
        )

    def test_navigate_to_report_and_verify_candidates_displayed(self):
        """Test navigating to the report and verifying that candidates are displayed sorted by default score."""
        # Navigate to the candidate report page
        self.driver.get(f"http://localhost:8000/jobs/{self.job.id}/candidates/")
        
        # Wait for the page to load and candidates to be displayed
        candidates_table = self.wait.until(
            EC.presence_of_element_located((By.ID, "candidates_table_body"))
        )
        
        # Find all candidate rows
        candidate_rows = candidates_table.find_elements(By.TAG_NAME, "tr")
        
        # Verify that all 3 candidates are displayed
        self.assertEqual(len(candidate_rows), 3, "Should display 3 candidate rows")
        
        # Verify that the candidates are sorted by score in descending order (default)
        # The first row should be Bob Johnson (score 95)
        first_candidate_name = candidate_rows[0].find_elements(By.TAG_NAME, "td")[0].text
        first_candidate_score = candidate_rows[0].find_elements(By.TAG_NAME, "td")[1].text
        
        self.assertIn("Bob Johnson", first_candidate_name)
        self.assertIn("95", first_candidate_score)
        
        # The last row should be Jane Smith (score 72)
        last_candidate_name = candidate_rows[2].find_elements(By.TAG_NAME, "td")[0].text
        last_candidate_score = candidate_rows[2].find_elements(By.TAG_NAME, "td")[1].text
        
        self.assertIn("Jane Smith", last_candidate_name)
        self.assertIn("72", last_candidate_score)

    def test_filter_candidates_and_verify_list_shrinks(self):
        """Test interacting with the filter input and verifying the displayed list shrinks correctly."""
        # Navigate to the candidate report page
        self.driver.get(f"http://localhost:8000/jobs/{self.job.id}/candidates/")
        
        # Wait for the page to load
        self.wait.until(
            EC.presence_of_element_located((By.ID, "score_threshold"))
        )
        
        # Find the score threshold input and filter button
        score_threshold_input = self.driver.find_element(By.ID, "score_threshold")
        filter_button = self.driver.find_element(By.ID, "apply_filter")
        
        # Set the threshold to 80 (should filter out Jane Smith with score 72)
        score_threshold_input.clear()
        score_threshold_input.send_keys("80")
        
        # Click the filter button
        filter_button.click()
        
        # Wait for the table to update
        candidates_table = self.wait.until(
            EC.presence_of_element_located((By.ID, "candidates_table_body"))
        )
        
        # Find all candidate rows after filtering
        candidate_rows = candidates_table.find_elements(By.TAG_NAME, "tr")
        
        # Should now have 2 candidates (John Doe with 87 and Bob Johnson with 95)
        self.assertEqual(len(candidate_rows), 2, "Should display 2 candidates after filtering")
        
        # Verify that Jane Smith (the one with score 72) is not in the results
        all_candidate_texts = []
        for row in candidate_rows:
            name = row.find_elements(By.TAG_NAME, "td")[0].text
            all_candidate_texts.append(name)
        
        self.assertIn("Bob Johnson", all_candidate_texts, "Bob Johnson should be in filtered results")
        self.assertIn("John Doe", all_candidate_texts, "John Doe should be in filtered results")
        self.assertNotIn("Jane Smith", all_candidate_texts, "Jane Smith should not be in filtered results")

    def test_click_shortlist_button_and_verify_status_update(self):
        """Test clicking the Shortlist button and verifying the is_shortlisted status visually updates."""
        # Navigate to the candidate report page
        self.driver.get(f"http://localhost:8000/jobs/{self.job.id}/candidates/")
        
        # Wait for the page to load
        self.wait.until(
            EC.presence_of_element_located((By.ID, "candidates_table_body"))
        )
        
        # Find the table body and locate the first candidate row (John Doe)
        candidates_table = self.driver.find_element(By.ID, "candidates_table_body")
        candidate_rows = candidates_table.find_elements(By.TAG_NAME, "tr")
        
        # Find the row for John Doe (who is initially not shortlisted)
        john_doe_row = None
        for row in candidate_rows:
            name_cell = row.find_elements(By.TAG_NAME, "td")[0]
            if "John Doe" in name_cell.text:
                john_doe_row = row
                break
        
        self.assertIsNotNone(john_doe_row, "John Doe row should be found")
        
        # Find the shortlist button in John Doe's row
        shortlist_button = john_doe_row.find_element(By.CLASS_NAME, "toggle-shortlist-btn")
        
        # Verify initial state (should say "Shortlist")
        self.assertEqual(shortlist_button.text, "Shortlist", "Initial button text should be 'Shortlist'")
        
        # Get the button's initial class to check if it has shortlist styling
        initial_classes = shortlist_button.get_attribute("class")
        self.assertIn("bg-gray-100", initial_classes, "Should have gray background initially")
        
        # Click the shortlist button
        shortlist_button.click()
        
        # Wait a bit for the AJAX request to complete
        time.sleep(1)
        
        # Refresh the reference to the button to get the updated state
        updated_shortlist_button = None
        candidate_rows = candidates_table.find_elements(By.TAG_NAME, "tr")
        for row in candidate_rows:
            name_cell = row.find_elements(By.TAG_NAME, "td")[0]
            if "John Doe" in name_cell.text:
                updated_shortlist_button = row.find_element(By.CLASS_NAME, "toggle-shortlist-btn")
                break
        
        # Verify the button text changed to "Unshortlist"
        self.assertEqual(updated_shortlist_button.text, "Unshortlist", "Button text should change to 'Unshortlist'")
        
        # Verify the button styling changed to indicate shortlisted status
        updated_classes = updated_shortlist_button.get_attribute("class")
        self.assertIn("bg-green-100", updated_classes, "Should have green background when shortlisted")
        
        # Verify the candidate is now marked as shortlisted in the database
        self.applicant1.refresh_from_db()
        self.assertTrue(self.applicant1.is_shortlisted, "Candidate should be marked as shortlisted in database")