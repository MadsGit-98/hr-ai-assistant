# Quickstart Guide: Candidate Reporting and Shortlisting

**Feature**: 004-candidate-reporting
**Date**: Tuesday, November 18, 2025

## Overview

This guide provides instructions for setting up and running the candidate reporting and shortlisting feature. This feature allows hiring managers to view a sortable and filterable report of analyzed candidates and mark them for interviews.

## Prerequisites

- Python 3.11+
- Django (latest stable version)
- Ollama for local LLM hosting
- Node.js (for Tailwind CSS processing)

## Setup Instructions

### 1. Clone and Navigate to Repository
```bash
cd F:\Python Web App Projects\HR AI Assistive Agent\hr-ai-assistant\hr-ai-agentic-assistant
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install and Start Ollama
```bash
# Download and install Ollama from https://ollama.ai
# Start the Ollama server
ollama serve
```

### 4. Apply Database Migrations
```bash
# Apply migrations to update the Applicant model with the is_shortlisted field
python manage.py makemigrations
python manage.py migrate
```

### 5. Install and Build Frontend Assets
```bash
# Navigate to the static directory and build Tailwind CSS
cd static
npm install
npm run build
```

### 6. Load Sample Data (Optional)
```bash
# If you want to test with sample data
python manage.py loaddata sample_candidates.json
```

## Running the Application

### 1. Start the Django Development Server
```bash
python manage.py runserver
```

### 2. Access the Feature
- Navigate to `http://127.0.0.1:8000/scoring_results/` or `http://127.0.0.1:8000/jobs/<job_id>/candidates/`
- You will see a table of candidates with their evaluation details
- Use the filter controls to set a minimum score threshold
- Click on column headers to sort the results
- Use the "Shortlist" buttons to mark candidates for interviews

## Key Features

### Candidate Report View
- Displays all analyzed candidates for a specific job
- Shows Name, Overall Score, Categorization, Quality Grade, and AI Justification Summary
- Default sorting by Overall Score in descending order

### Filtering
- Filter candidates by minimum Overall Score using the input field
- Results update immediately after applying the filter

### Sorting
- Click on any column header to sort by that column
- Click again to toggle between ascending and descending order

### Shortlisting
- Click the "Shortlist" button to mark a candidate for interview
- Click "Unshortlist" to remove the mark
- Status updates without page refresh

## API Endpoints

### GET /scoring_results/ or /jobs/<job_id>/candidates/
- Returns the candidate report page
- Query Parameters:
  - `sort_by`: Column to sort by (default: 'overall_score')
  - `sort_order`: Ascending/descending (default: 'desc')
  - `score_threshold`: Minimum score threshold for filtering (default: 0)

### POST /api/candidates/<id>/toggle-shortlist/
- Toggles the is_shortlisted status of a candidate
- Returns: Updated is_shortlisted status

## Testing the Feature

### Running Unit Tests
```bash
python manage.py test tests.unit.test_candidate_reporting
```

### Running Integration Tests
```bash
python manage.py test tests.integration.test_candidate_report_view
```

### Running E2E Tests
```bash
python manage.py test tests.e2e.test_candidate_reporting_e2e
```

## Troubleshooting

### Common Issues

1. **Database Migration Errors**: Run `python manage.py migrate` to ensure all database changes are applied.

2. **Ollama Not Responding**: Verify that Ollama is running with `ollama serve`.

3. **Missing CSS Styling**: Run the Tailwind build command again: `npm run build` in the static directory.

4. **500 Candidates Limit Not Enforced**: Check that the filter logic in `hr_assistant/services/report_utils.py` is properly limiting results.

## Next Steps

After successfully setting up the feature, you can:
- Analyze more candidate resumes
- Fine-tune the AI evaluation criteria
- Add more filtering options
- Implement additional reporting features