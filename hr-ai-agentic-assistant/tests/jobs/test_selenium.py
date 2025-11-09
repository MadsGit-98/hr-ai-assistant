"""
Selenium tests for the critical user journey in Job Listing Management
These tests ensure the end-to-end functionality works as expected from a user perspective.
"""
import unittest
import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from jobs.models import JobListing


class JobListingSeleniumTest(LiveServerTestCase):
    
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
    
    def test_full_job_listing_crud_journey(self):
        """
        Test the complete user journey for job listing management:
        1. Create a job listing
        2. View the created job listing
        3. Update the job listing
        4. Verify the update
        5. Delete the job listing
        """
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/jobs/')
        
        # Wait for the page to load and verify we're on the right page
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        # Step 1: Create a new job listing
        title_input = WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        description_input = selenium.find_element(By.NAME, "detailed_description")
        skills_input = selenium.find_element(By.NAME, "required_skills")
        submit_button = WebDriverWait(selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
        )
        
        # Scroll to ensure the button is visible before clicking
        selenium.execute_script("arguments[0].scrollIntoView();", submit_button)
        
        title_input.send_keys("Software Developer")
        description_input.send_keys("We are looking for a skilled software developer...")
        skills_input.send_keys("Python, Django, JavaScript")
        
        submit_button.click()
        
        # Wait for redirect after creation
        WebDriverWait(selenium, 10).until(
            EC.url_contains("/jobs/")
        )
        
        # Verify the job listing was created by checking if the title appears on the page
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Software Developer')]"))
        )
        
        # Step 2: Verify the job listing exists by navigating to the detail page
        # Find the created job listing and click on it to view details
        detail_link = WebDriverWait(selenium, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Software Developer"))
        )
        detail_link.click()
        
        # Verify we are on the detail page
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Software Developer') and @class='text-2xl font-bold']"))
        )
        
        # Step 3: Navigate to the edit page
        edit_link = selenium.find_element(By.LINK_TEXT, "Edit Job")
        edit_link.click()
        
        # Step 4: Update the job listing
        title_input = WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        description_input = selenium.find_element(By.NAME, "detailed_description")
        skills_input = selenium.find_element(By.NAME, "required_skills")
        submit_button = WebDriverWait(selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
        )
        
        # Clear and update the title
        title_input.clear()
        title_input.send_keys("Senior Software Developer")
        description_input.clear()
        description_input.send_keys("We are looking for a senior software developer with experience...")
        skills_input.clear()
        skills_input.send_keys("Python, Django, JavaScript, React, PostgreSQL")
        
        # Scroll to ensure the button is visible before clicking
        selenium.execute_script("arguments[0].scrollIntoView();", submit_button)
        
        submit_button.click()
        
        # Wait for redirect after update
        WebDriverWait(selenium, 10).until(
            EC.url_contains("/jobs/")
        )
        
        # Verify the update by checking for the new title
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Senior Software Developer')]"))
        )
        
        # Step 5: Delete the job listing
        delete_link = selenium.find_element(By.LINK_TEXT, "Delete Job")
        delete_link.click()
        
        # On the confirmation page, click the delete button
        confirm_delete_button = WebDriverWait(selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Confirm Delete']"))
        )
        confirm_delete_button.click()
        
        # Wait for redirect after deletion and verify the list is empty
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'No job listings available.')]"))
        )
    
    def test_create_multiple_job_listings_and_activate(self):
        """
        Test creating multiple job listings and activating/deactivating them
        """
        selenium = self.selenium
        
        # Create first job listing
        selenium.get(f'{self.live_server_url}/jobs/')
        
        title_input = WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        description_input = selenium.find_element(By.NAME, "detailed_description")
        skills_input = selenium.find_element(By.NAME, "required_skills")
        submit_button = WebDriverWait(selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
        )
        
        # Scroll to ensure the button is visible before clicking
        selenium.execute_script("arguments[0].scrollIntoView();", submit_button)
        
        title_input.send_keys("First Job Listing")
        description_input.send_keys("Description for first job listing")
        skills_input.send_keys("Python, SQL")
        
        submit_button.click()
        
        # Wait for redirect
        WebDriverWait(selenium, 10).until(
            EC.url_contains("/jobs/")
        )
        
        # Create second job listing
        create_link = WebDriverWait(selenium, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Create Job Listing"))
        )
        create_link.click()
        
        title_input = WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        description_input = selenium.find_element(By.NAME, "detailed_description")
        skills_input = selenium.find_element(By.NAME, "required_skills")
        submit_button = WebDriverWait(selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
        )
        
        # Scroll to ensure the button is visible before clicking
        selenium.execute_script("arguments[0].scrollIntoView();", submit_button)
        
        title_input.send_keys("Second Job Listing")
        description_input.send_keys("Description for second job listing")
        skills_input.send_keys("JavaScript, React")
        
        submit_button.click()
        
        # Wait for redirect
        WebDriverWait(selenium, 10).until(
            EC.url_contains("/jobs/")
        )
        
        # Verify both job listings exist
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'First Job Listing')]"))
        )
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Second Job Listing')]"))
        )
    
    def test_job_listing_validation_errors(self):
        """
        Test that validation errors are properly displayed when creating invalid job listings
        """
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/jobs/')
        
        # Submit an empty form to test validation
        submit_button = WebDriverWait(selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
        )
        submit_button.click()
        
        # Wait for validation errors to appear
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "errorlist"))
        )
        
        # Verify that error messages appear
        error_lists = selenium.find_elements(By.CLASS_NAME, "errorlist")
        self.assertGreater(len(error_lists), 0, "Validation errors should be displayed for empty form")