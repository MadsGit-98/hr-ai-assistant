# HR AI Assistant

A Django-based assistant for HR teams that supports bulk resume uploads, duplicate detection, and an AI-powered resume scoring engine. This repository contains the application code, AI orchestration components, and a comprehensive test suite (including Selenium end-to-end tests).

Table of contents
- Project overview
- Key features
- Architecture & tech stack
- Requirements
- Quick start (local development)
- Configuration & environment variables
- Running the test suite (including Selenium)
- API endpoints (overview)
- File upload limits & policies
- AI scoring engine — how it works
- Troubleshooting
- Contributing
- License & contact

---

Project overview
----------------
HR AI Assistant helps HR teams manage job listings and candidate resumes. The system provides:

- Bulk resume upload (PDF, DOCX) with progress feedback and duplicate detection.
- An AI-based resume scoring engine that analyzes resumes against job requirements and produces:
  - Overall numeric score (0–100)
  - Proficiency categorization (Senior / Mid-Level / Junior / Mismatched)
  - Quality grade (A–F)
- REST API endpoints to upload resumes, trigger scoring, check scoring status, and retrieve scored applicants.
- Background processing for long-running AI analysis and status tracking.
- A comprehensive test suite: unit tests, integration tests, and Selenium end-to-end tests.

Key features
------------
- Resume Upload
  - Bulk upload via drag-and-drop or file picker
  - Accepts PDF and DOCX
  - Duplicate detection using SHA256 content hash + applicant name matching
  - Per-file visual progress and upload status
  - Secure file validation and storage

- AI Resume Scoring
  - Uses LangGraph orchestration + LLM (example: Ollama) for scoring
  - Map-reduce style parallel processing for large batches
  - Produces numeric score, category, and letter grade
  - Stores detailed per-applicant analysis and explanations
  - Background processing with status endpoints

- Job Listing Management
  - CRUD operations for job listings
  - Activation semantics (tests validate single active listing behavior)

- Testing
  - Unit tests, integration tests, and Selenium UI tests covering critical journeys

Architecture & tech stack
-------------------------
- Framework: Django (REST endpoints commonly implemented with Django REST Framework)
- AI orchestration: LangGraph + configurable LLM adapter (Ollama shown as example)
- Background processing: Django management commands or async/background workers (scoring runs asynchronously)
- Frontend: Minimal UI for uploads and job listings (Selenium covers UI behaviour)
- Storage: Local MEDIA storage by default; configurable for S3 or other providers
- Testing: Django test runner / pytest, Selenium + ChromeDriver for browser tests

Requirements
------------
- Python 3.10+
- pip
- Chrome Browser (for Selenium tests)
- ChromeDriver matching the installed Chrome version (or use webdriver-manager)
- Recommended for AI backend: Docker (to run Ollama or other LLM local instances)

Quick start (local development)
-------------------------------
1. Clone the repository
   ```bash
   git clone https://github.com/MadsGit-98/hr-ai-assistant.git
   cd hr-ai-assistant
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # macOS / Linux
   .venv\Scripts\activate       # Windows (PowerShell)
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations and create a superuser
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Start the development server
   ```bash
   python manage.py runserver
   ```
   Visit: http://127.0.0.1:8000/ and the admin at /admin

Configuration & environment variables
-------------------------------------
Adjust settings in `settings.py` or use environment-specific settings. Recommended core settings:

```python
# File upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB per file
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure jobs app is added
INSTALLED_APPS += ['jobs']
```

AI / orchestration environment variables (examples — adapt to your runtime):
- OLLAMA_URL — URL of the Ollama instance (if used)
- LANGGRAPH_CONFIG — path or JSON config for LangGraph flows
- CELERY/BG_WORKER_URL — if using Celery or other background worker

Running the test suite
----------------------
Prerequisites for Selenium tests:
- Chrome Browser installed
- ChromeDriver compatible with Chrome version (or use webdriver-manager for automatic installs)

Install webdriver-manager (recommended)
```bash
pip install webdriver-manager
```

Run all tests:
```bash
python manage.py test
```

Run only Selenium tests (examples):
```bash
python manage.py test jobs.tests.jobs.test_selenium
python manage.py test jobs.tests.jobs.test_job_activation_selenium
python manage.py test jobs.tests.jobs.test_resume_selenium
```

AI scoring tests (examples):
```bash
# Run all AI-related tests (pattern)
python manage.py test jobs.tests.jobs.test_ai_

# Run specific AI tests
python manage.py test jobs.tests.jobs.test_ai_contracts
python manage.py test jobs.tests.jobs.test_ai_scoring_integration
python manage.py test jobs.tests.jobs.test_ai_scoring_api
```

API endpoints (overview)
-----------------------
Replace {job_id} and {applicant_id} with real IDs.

- POST /api/applicants/upload/
  - Upload one or more PDF/DOCX files (multipart/form-data)
  - Returns per-file upload status and created applicant references

- POST /api/job-listings/{job_id}/score-resumes/
  - Initiates scoring for resumes attached to an active job
  - Returns 202 Accepted with a task reference if processing starts asynchronously

- GET /api/job-listings/{job_id}/scoring-status/
  - Returns overall progress and per-applicant processing states

- GET /api/job-listings/{job_id}/scored-applicants/
  - Lists scored applicants with overall_score, category, quality_grade; supports filtering & sorting

- GET /api/applicants/{applicant_id}/detailed-analysis/
  - Detailed AI analysis for the applicant (explanations and evidence)

File upload limits & policies
----------------------------
- Default max file size: 10 MB per file (configurable)
- Default max batch size: 100 files per upload session (configurable)
- Accepted formats: PDF, DOCX only
- Duplicate detection: SHA256 content hash + applicant name matching
- Storage: Files written to MEDIA_ROOT; for production use secure external storage (S3, etc.)

AI scoring engine — how it works
-------------------------------
1. Upload: Resumes are stored and marked pending.
2. Initiation: A scoring job is triggered via API/admin. The endpoint returns 202 and scheduling metadata.
3. Map phase: Each resume is processed with an LLM prompt (extracts key attributes, skills, experience, and a relevance signal).
4. Reduce phase: Aggregate results to compute final metrics:
   - Overall Score (0–100)
   - Category (Senior / Mid-Level / Junior / Mismatched)
   - Quality Grade (A–F)
   The system also stores the detailed analysis that justifies these scores.
5. Results: Results are available through the scored-applicants endpoint and detailed-analysis for each applicant.

Notes on prompts and orchestration
- LangGraph flows are used to orchestrate map/reduce steps; replace LangGraph/Ollama configuration as needed.
- The scoring pipeline is modular so you can swap LLM backends or modify the scoring heuristics.

Troubleshooting
---------------
- ChromeDriver errors: Ensure your ChromeDriver matches Chrome version. Using webdriver-manager avoids manual driver management.
- File upload errors: Confirm `FILE_UPLOAD_MAX_MEMORY_SIZE` and `DATA_UPLOAD_MAX_MEMORY_SIZE` settings.
- Media directory errors: Ensure `MEDIA_ROOT` exists and the process has write permissions.
- AI backend unreachable: Verify AI backend URL(s) and that the service is running.
- Tests failing in CI: Selenium tests run in headless mode by default — confirm required browser binaries and drivers are available in CI.

Contributing
------------
Contributions are welcome. When submitting PRs:
- Make sure tests pass locally
- Add tests for new features or bug fixes
- Keep commits focused and describe changes clearly in PR descriptions
- Follow existing code style and patterns

Suggested development workflow
1. Fork the repo / create a branch
2. Implement feature or fix
3. Add or update tests
4. Run test suite locally
5. Open a PR with a clear description and testing instructions

License & contact
-----------------
Specify the project license here (e.g., MIT). Update as appropriate.

Repository: https://github.com/MadsGit-98/hr-ai-assistant
