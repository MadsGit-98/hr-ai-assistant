# Tests for HR AI Assistant

This project includes tests for both job listing management and resume upload features. The tests cover end-to-end user journeys as required by the project constitution.

## Prerequisites

To run the tests, you need to have:

1. **Chrome Browser** installed on your system (for Selenium tests)
2. **ChromeDriver** that matches your Chrome version (for Selenium tests)

### Installing ChromeDriver

Option 1: Use WebDriver Manager (recommended for Selenium tests)
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

If you want automatic driver management for Selenium:
```bash
pip install webdriver-manager
```

### Run all tests (including both job listing and resume upload tests)
```bash
python manage.py test
```

### Run only Selenium tests
```bash
python manage.py test jobs.tests.jobs.test_selenium
python manage.py test jobs.tests.jobs.test_job_activation_selenium
python manage.py test jobs.tests.jobs.test_resume_selenium
```

### Run AI Resume Scoring Engine tests
```bash
# Run all AI scoring tests
python manage.py test jobs.tests.jobs.test_ai_

# Run specific AI tests
python manage.py test jobs.tests.jobs.test_ai_contracts
python manage.py test jobs.tests.jobs.test_ai_scoring_integration
python manage.py test jobs.tests.jobs.test_ai_scoring_api
```

## Features

The HR AI Assistant includes several core features for HR management:

### Resume Upload Feature

1. **Bulk Upload**: Upload multiple resumes at once via drag-and-drop or file selection
2. **Format Support**: Accepts PDF and DOCX file formats
3. **Duplicate Detection**: Checks for duplicates based on content hash and applicant name
4. **Visual Feedback**: Provides immediate status feedback during upload process
5. **GDPR Compliance**: Implements data protection measures for applicant information
6. **Secure Storage**: Validates file types and stores files securely

### AI Resume Scoring Engine

The HR AI Assistant includes an advanced AI-powered resume scoring engine that automatically analyzes and scores resumes against job requirements.

#### Features

1. **Automated Scoring**: Generates three distinct metrics for each resume:
   - Overall Score (0-100): A single metric representing fitness for the job
   - Categorization: Assigning the candidate to a proficiency tier (e.g., "Senior," "Mid-Level," "Junior," or "Mismatched")
   - Quality Grade (A, B, C, D, F): A letter grade reflecting the quality and relevance of experience
2. **AI-Powered Analysis**: Uses LangGraph orchestration with Ollama LLM for intelligent scoring
3. **Map-Reduce Processing**: Implements parallel processing for efficient bulk resume analysis
4. **Status Tracking**: Shows "Processing..." status during analysis with notifications when complete
5. **Detailed Analysis**: Provides detailed explanations for how each score was determined
6. **Filtering and Sorting**: Allows filtering and sorting candidates based on their scores and categories
7. **Batch Processing**: Initiates processing of all uploaded resumes against an active job listing

#### How to Use

1. Navigate to the job listings page and select an active job listing
2. Initiate the resume scoring process via the API endpoint: `/api/job-listings/{job_id}/score-resumes/`
3. The system returns a 202 status code and processes in the background
4. Check the processing status at: `/api/job-listings/{job_id}/scoring-status/`
5. Retrieve scored applicants at: `/api/job-listings/{job_id}/scored-applicants/`
6. View detailed analysis for individual applicants via the detailed analysis endpoint
7. Filter and sort results by scores, categories, and grades as needed

### How to Use

1. Navigate to the resume upload page at `/api/applicants/upload/`
2. Select multiple PDF or DOCX files via file browser or drag and drop them into the upload area
3. The system will validate file types and sizes automatically
4. During upload, you'll see progress status for each file
5. The system will detect and alert you to any duplicates based on content hash or applicant name
6. After successful upload, files are stored securely and ready for AI analysis

### Technical Details

- **Maximum file size**: 10MB per file
- **Maximum batch size**: 100 files per upload session
- **Duplicate detection**: Uses SHA256 content hash calculation and applicant name matching
- **Storage**: Secure file storage outside the web root with proper access controls
- **Processing status**: Tracks each file's processing state (pending, processing, completed, error)

### Configuration Requirements

Make sure the following settings are in your `settings.py`:

```python
# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Add 'jobs' app to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'jobs',
]
```

## Test Coverage

The tests cover critical user journeys for all features:

### Job Listing Management Tests

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

### Resume Upload Feature Tests

1. **Resume Upload View Tests** (`test_resume_views.py`):
   - Testing valid PDF/DOCX file uploads
   - Testing invalid file type rejection
   - Testing large file rejection
   - Testing duplicate detection by content hash
   - Testing duplicate detection by applicant name

2. **Resume Model Tests** (`test_resume_models.py`):
   - Validation of file format (PDF/DOCX)
   - Validation of file size (1KB-10MB)
   - Validation of applicant name format
   - Content hash uniqueness constraints

3. **Resume Utility Tests** (`test_resume_utils.py`):
   - File type validation
   - File size validation
   - SHA256 hash calculation
   - Duplicate detection logic

4. **Resume Selenium Tests** (`test_resume_selenium.py`):
   - End-to-end testing of the drag-and-drop interface
   - Testing bulk upload functionality
   - Visual feedback verification
   - Duplicate detection UI alerts

### AI Resume Scoring Engine Tests

1. **AI Analysis Contract Tests** (`test_ai_contracts.py`):
   - Validate the AIAnalysisResponse data contract
   - Test overall score range (0-100)
   - Test quality grade format (A, B, C, D, F)
   - Test categorization values (Senior, Mid-Level, Junior, Mismatched)

2. **AI Scoring Integration Tests** (`test_ai_scoring_integration.py`):
   - Test the full scoring pipeline including API endpoints
   - Verify scoring initiation process returns correct status codes
   - Test scoring status endpoint functionality
   - Validate detailed analysis endpoint responses
   - Test applicant scoring with various scenarios

3. **AI Scoring API Contract Tests** (`test_ai_scoring_api.py`):
   - Validate API contract for score-resumes endpoint
   - Test scoring-status endpoint response structure
   - Verify scored-applicants endpoint contract
   - Test detailed-analysis endpoint contract
   - Ensure proper error responses for invalid requests

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
4. Verify that file upload settings in settings.py match the resume upload requirements
5. Check that the media directory has proper write permissions