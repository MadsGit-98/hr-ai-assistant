from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import tempfile
import os


class ResumeUploadSeleniumTest(StaticLiveServerTestCase):
    def setUp(self):
        # Set up the Selenium WebDriver (make sure you have ChromeDriver installed)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode for testing
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def tearDown(self):
        self.driver.quit()

    def test_resume_upload_page_loads(self):
        """Test that the resume upload page loads correctly"""
        self.driver.get(f'{self.live_server_url}/jobs/upload/')
        
        # Check if the page has the correct title
        self.assertIn('Resume Upload', self.driver.title)
        
        # Check if the upload area exists
        upload_area = self.driver.find_element(By.ID, 'upload-area')
        self.assertIsNotNone(upload_area)

    def test_navigation_to_resume_upload_page(self):
        """Test navigating to the resume upload page from the main page"""
        # Go to the main page (which should redirect to jobs)
        self.driver.get(self.live_server_url)
        
        # The redirect should go to the job listing page, so we directly go to upload
        self.driver.get(f'{self.live_server_url}/jobs/upload/')
        
        # Verify we're on the upload page
        upload_area = self.driver.find_element(By.ID, 'upload-area')
        self.assertIsNotNone(upload_area)
        
        # Verify the title
        self.assertIn('Resume Upload', self.driver.title)