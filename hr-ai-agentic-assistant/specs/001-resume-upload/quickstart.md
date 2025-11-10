# Quickstart: Resume Ingestion (Bulk Upload)

**Feature**: Resume Ingestion (Bulk Upload)
**Date**: Sunday, November 9, 2025
**Status**: Complete

## Project Setup

### Prerequisites
- Python 3.11+
- pip package manager

### Initial Project Setup
1. Ensure the jobs app is created in your Django project:
   ```bash
   python manage.py startapp jobs
   ```

2. Install required packages:
   ```bash
   pip install python-docx PyPDF2
   ```

3. Install Tailwind CSS following the official Django integration guide

## Feature Implementation Guide

### File Structure
```
jobs/
├── models.py            # Applicant model
├── views.py             # Upload view
├── utils.py             # File processing utilities
├── urls.py              # URL routing
├── templates/
│   └── upload.html      # Bulk upload interface
└── static/
    └── css/
        └── tailwind.css
```

### Key Implementation Steps

1. **Create the Applicant model** with file storage and content hash fields:
   - Use FileField for resume_file
   - Implement SHA256 content_hash for duplicate detection
   - Add fields for applicant_name, raw_text_content, file_size, file_format
   - Include processing_status field with choices: pending, processing, completed, error

2. **Implement the upload utility functions** in utils.py:
   - calculate_file_hash() function to compute SHA256 of file content
   - check_duplicate_content() function to detect existing content hashes
   - check_duplicate_name() function to detect existing applicant names

3. **Implement the upload view** with multi-file handling:
   - Handle multiple file uploads via POST requests
   - Validate file types (PDF, DOCX) and sizes (max 10MB)
   - Compute content hash for each file
   - Check for duplicates before saving
   - Return appropriate status for each file (success, duplicate, error)

4. **Create templates** with drag-and-drop interface and Tailwind CSS styling

5. **Write unit tests** to achieve 90% coverage for all components

6. **Write Selenium tests** for critical user journeys

### Configuration

Add 'jobs' to your INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    # ... other apps
    'jobs',
]
```

Configure file upload settings in settings.py:
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

Include the resume upload URLs in your main urls.py:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/applicants/', include('jobs.urls')),
]
```

### Running the Application

1. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

3. Access the upload interface at the configured URL (e.g., `http://127.0.0.1:8000/api/applicants/upload/`)