"""
Selenium tests specifically for job listing activation functionality
"""
import unittest
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from jobs.models import JobListing


class JobActivationSeleniumTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Set up Chrome options for headless testing (can be modified for debugging)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Remove this line if you want to see the browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the WebDriver with automatic driver management
        service = Service(ChromeDriverManager().install())
        cls.selenium = webdriver.Chrome(service=service, options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Clean up any existing job listings before each test
        JobListing.objects.all().delete()

    def test_job_activation_functionality(self):
        """
        Test the job activation feature - ensuring only one job can be active at a time
        """
        selenium = self.selenium

        # Create first job listing
        selenium.get(f'{self.live_server_url}/jobs/')

        title_input = WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        description_input = selenium.find_element(By.NAME, "detailed_description")
        skills_input = selenium.find_element(By.NAME, "required_skills")
        submit_button = selenium.find_element(By.XPATH, "//button[@type='submit']")

        title_input.send_keys("First Job")
        description_input.send_keys("Description for first job")
        skills_input.send_keys("Python, Django")

        submit_button.click()

        # Wait for redirect back to jobs list
        WebDriverWait(selenium, 10).until(
            EC.url_contains("/jobs/")
        )

        # Wait a bit for the database to process the insert
        import time
        time.sleep(1)

        # Verify first job was created
        self.assertTrue(
            JobListing.objects.filter(title="First Job").exists(),
            "First job should exist in the database"
        )
        
        # Create second job listing
        create_link = WebDriverWait(selenium, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "+ New Job Listing"))
        )
        create_link.click()

        title_input = WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        description_input = selenium.find_element(By.NAME, "detailed_description")
        skills_input = selenium.find_element(By.NAME, "required_skills")
        submit_button = selenium.find_element(By.XPATH, "//button[@type='submit']")

        title_input.send_keys("Second Job")
        description_input.send_keys("Description for second job")
        skills_input.send_keys("Java, Spring")

        submit_button.click()

        # Wait for redirect back to jobs list
        WebDriverWait(selenium, 10).until(
            EC.url_contains("/jobs/")
        )

        # Wait for database transaction to complete
        time.sleep(1)

        # Verify that both jobs exist in the database
        self.assertTrue(
            JobListing.objects.filter(title="First Job").exists(),
            "First job should exist in the database"
        )
        self.assertTrue(
            JobListing.objects.filter(title="Second Job").exists(),
            "Second job should exist in the database"
        )

        # Verify only one job is active - the first job should be active by default
        # (as the model auto-activates the first created)
        first_job = JobListing.objects.get(title="First Job")
        second_job = JobListing.objects.get(title="Second Job")

        self.assertTrue(first_job.is_active, "First job should be active by default")
        self.assertFalse(second_job.is_active, "Second job should not be active by default")

        # Test activating the second job, which should deactivate the first
        activate_url = f"{self.live_server_url}/jobs/{second_job.pk}/activate/"
        selenium.get(activate_url)

        # Wait for redirect back to jobs list
        WebDriverWait(selenium, 10).until(
            EC.url_contains("/jobs/")
        )

        # Wait for database update to complete
        time.sleep(1)

        # Refresh from database
        first_job.refresh_from_db()
        second_job.refresh_from_db()

        self.assertTrue(second_job.is_active, "Second job should be active after activation")
        self.assertFalse(first_job.is_active, "First job should be inactive after second job activation")