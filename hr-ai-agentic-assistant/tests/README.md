# Selenium Tests for HR AI Assistant

This project includes Selenium tests for end-to-end testing of the user journey as required by the project constitution.

## Prerequisites

To run the Selenium tests, you need to have:

1. **Chrome Browser** installed on your system
2. **ChromeDriver** that matches your Chrome version

### Installing ChromeDriver

Option 1: Use WebDriver Manager (recommended)
```bash
pip install webdriver-manager
```

Option 2: Download manually
- Go to https://chromedriver.chromium.org/
- Download the version that matches your Chrome browser version
- Place it in your PATH or project directory

## Running the Tests

### Install dependencies
```bash
pip install -r requirements.txt
```

If you want automatic driver management:
```bash
pip install webdriver-manager
```

### Run all tests (including Selenium)
```bash
python manage.py test
```

### Run only Selenium tests
```bash
python manage.py test tests.jobs.test_selenium
python manage.py test tests.jobs.test_job_activation_selenium
```

## Test Coverage

The Selenium tests cover the critical user journey for job listing management:

1. **Full CRUD Journey Test** (`test_full_job_listing_crud_journey`):
   - Creating a job listing
   - Viewing job listing details
   - Updating a job listing
   - Deleting a job listing

2. **Activation Functionality Test** (`test_job_activation_functionality`):
   - Creating multiple job listings
   - Testing the single active listing constraint
   - Verifying activation/deactivation works correctly

3. **Validation Test** (`test_job_listing_validation_errors`):
   - Testing form validation with empty submissions
   - Ensuring proper error messages are displayed

## Notes

- The tests run in headless mode by default for CI/CD compatibility
- To see the browser during tests, remove the `--headless` flag in the test setup
- Tests use Django's LiveServerTestCase which automatically handles database transactions
- Each test starts with a clean database state

## Troubleshooting

If you encounter issues:
1. Make sure ChromeDriver is properly installed and accessible
2. Check that your Chrome browser and ChromeDriver versions are compatible
3. Ensure the development server can start on the default port (usually 8081 for tests)