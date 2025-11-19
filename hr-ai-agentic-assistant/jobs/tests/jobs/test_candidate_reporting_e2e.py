"""
End-to-End tests for candidate reporting functionality.
Tests covering the critical user journeys as defined in the specification.
"""
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from jobs.models import JobListing, Applicant
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class TestCandidateReportingE2E(StaticLiveServerTestCase):
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
            analysis_status='analyzed'
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
            justification_summary="Outstanding experience and skills in full-stack development. Expert in Python, Django, and modern JavaScript frameworks.",
            analysis_status='analyzed'
        )

    def test_navigate_to_report_and_verify_candidates_displayed(self):
        """Test navigating to the report and verifying that candidates are displayed sorted by default score."""
        # Navigate to the candidate report page using the live server URL
        url = f"{self.live_server_url}/jobs/{self.job.id}/candidates/"
        self.driver.get(url)

        # Wait for the page to fully load by checking for the main heading
        try:
            heading = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Candidate Report')]"))
            )
            self.assertIn("Candidate Report", heading.text)
        except:
            # If the heading never loads, print page source for debugging
            print("Page title:", self.driver.title)
            print("Page source:", self.driver.page_source[:1000])  # First 1000 chars
            raise

        # Wait for the table body element to be present
        candidates_table = self.wait.until(
            EC.presence_of_element_located((By.ID, "candidates_table_body"))
        )

        # Wait for data to load by checking for the change from "Loading candidates..." to actual data
        # Initially, the loading message should be present
        loading_text = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Loading candidates...')]"))
        )
        self.assertIn("Loading candidates...", loading_text.text)

        # Now wait for the loading message to be replaced by actual data
        # We'll wait up to 15 seconds for the API call to complete and data to load
        WebDriverWait(self.driver, 15).until(
            lambda driver: "Loading candidates..." not in driver.page_source or
                           len(driver.find_elements(By.CSS_SELECTOR, "#candidates_table_body tr:not([style*='display: none'])")) > 1
        )

        # Get the candidate rows after data has loaded
        import time
        time.sleep(1)  # Brief pause to ensure DOM has updated
        candidate_rows = candidates_table.find_elements(By.TAG_NAME, "tr")

        # Verify we got all 3 candidates (should replace the loading row)
        self.assertEqual(len(candidate_rows), 3, f"Expected 3 candidate rows, got {len(candidate_rows)}: {[r.text for r in candidate_rows]}")

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
        # Navigate to the candidate report page using the live server URL
        url = f"{self.live_server_url}/jobs/{self.job.id}/candidates/"
        self.driver.get(url)

        # Wait for the page to fully load by checking for the main heading
        heading = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Candidate Report')]"))
        )
        self.assertIn("Candidate Report", heading.text)

        # Wait for the table body element to be present
        candidates_table = self.wait.until(
            EC.presence_of_element_located((By.ID, "candidates_table_body"))
        )

        # Wait for data to load by checking for the change from "Loading candidates..." to actual data
        # We'll wait up to 15 seconds for the API call to complete and data to load
        WebDriverWait(self.driver, 15).until(
            lambda driver: "Loading candidates..." not in driver.page_source or
                           len(driver.find_elements(By.CSS_SELECTOR, "#candidates_table_body tr:not([style*='display: none'])")) > 1
        )

        # Get the candidate rows after data has loaded
        import time
        time.sleep(1)  # Brief pause to ensure DOM has updated
        candidate_rows = candidates_table.find_elements(By.TAG_NAME, "tr")

        # Verify all 3 candidates are initially loaded
        self.assertEqual(len(candidate_rows), 3, f"Expected 3 candidate rows initially, got {len(candidate_rows)}: {[r.text for r in candidate_rows]}")

        # Wait for the score threshold input to become available
        score_threshold_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "score_threshold"))
        )

        # Find the filter button
        filter_button = self.driver.find_element(By.ID, "apply_filter")

        # Set the threshold to 80 (should filter out Jane Smith with score 72)
        score_threshold_input.clear()
        score_threshold_input.send_keys("80")

        # Click the filter button
        filter_button.click()

        # After clicking filter, wait for loading state and then filtered results
        # Wait for the table to update - it might temporarily show loading again
        WebDriverWait(self.driver, 10).until(
            lambda driver: "Loading candidates..." not in driver.page_source or
                           len(driver.find_elements(By.CSS_SELECTOR, "#candidates_table_body tr:not([style*='display: none'])")) in [2, 3]  # 2 after filter, 3 initially
        )

        # Get the candidate rows after filtering
        time.sleep(1)  # Brief pause to ensure DOM has updated after filter
        candidate_rows = candidates_table.find_elements(By.TAG_NAME, "tr")

        # Should now have 2 candidates (John Doe with 87 and Bob Johnson with 95)
        self.assertEqual(len(candidate_rows), 2, f"Should display 2 candidates after filtering, but got {len(candidate_rows)}. Rows: {[r.text for r in candidate_rows]}")

        # Verify that Jane Smith (the one with score 72) is not in the results
        all_candidate_texts = []
        for row in candidate_rows:
            name = row.find_elements(By.TAG_NAME, "td")[0].text
            all_candidate_texts.append(name)

        self.assertIn("Bob Johnson", all_candidate_texts, "Bob Johnson should be in filtered results")
        self.assertIn("John Doe", all_candidate_texts, "John Doe should be in filtered results")
        self.assertNotIn("Jane Smith", all_candidate_texts, "Jane Smith should not be in filtered results")