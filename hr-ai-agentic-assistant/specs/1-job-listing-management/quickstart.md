# Quickstart: Job Listing Management

**Feature**: Job Listing Management
**Date**: 2025-11-06
**Status**: Complete

## Project Setup

### Prerequisites
- Python 3.11+
- pip package manager

### Initial Project Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Django:
   ```bash
   pip install django
   pip install markdown
   pip install bleach
   ```

3. Create the Django project:
   ```bash
   django-admin startproject hr_assistant
   cd hr_assistant
   ```

4. Create the jobs app:
   ```bash
   python manage.py startapp jobs
   ```

5. Install Tailwind CSS following the official Django integration guide

## Feature Implementation Guide

### File Structure
```
jobs/
├── models.py            # JobListing model
├── views.py             # CRUD views
├── forms.py             # Job listing forms
├── urls.py              # URL routing
├── templates/
│   └── jobs/
│       ├── joblisting_form.html
│       ├── joblisting_detail.html
│       └── joblisting_list.html
└── static/
    └── css/
        └── tailwind.css
```

### Key Implementation Steps

1. **Create the JobListing model** with the required fields and validation
   - Use JSONField for required_skills
   - Implement custom validation for single active listing constraint
   - Add markdown sanitization for detailed_description

2. **Implement the four required CBVs**:
   - JobListingCreateView
   - JobListingDetailView
   - JobListingUpdateView
   - JobListingDeleteView
   - Include custom logic for active listing management

3. **Create Django forms** with proper validation and Tailwind CSS classes

4. **Implement templates** with responsive design using Tailwind CSS

5. **Write unit tests** to achieve 90% coverage

6. **Write Selenium tests** for the critical user journey

### Configuration

Add 'jobs' to your INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    # ... other apps
    'jobs',
]
```

Include the job listing URLs in your main urls.py:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('jobs/', include('jobs.urls')),
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

3. Access the application at `http://127.0.0.1:8000/jobs/`