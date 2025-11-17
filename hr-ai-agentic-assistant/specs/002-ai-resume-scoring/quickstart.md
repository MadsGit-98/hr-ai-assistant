# Quickstart: AI Resume Scoring Engine

**Created**: 2025-11-11
**Feature**: 002-ai-resume-scoring

## Overview

This guide explains how to set up and use the AI Resume Scoring Engine to analyze resumes against job listings and generate objective, data-driven scores.

## Prerequisites

- Python 3.11+
- Django (latest stable)
- Ollama running locally with a suitable model (e.g., llama2 or better)
- SQLite3 (or your configured database)
- Existing resume uploads in the system

## Setup Ollama

1. Install Ollama from https://ollama.ai
2. Pull a suitable model for resume analysis:
   ```bash
   ollama pull llama2
   ```
3. Start the Ollama service:
   ```bash
   ollama serve
   ```

## Configuration

1. Ensure the services are properly configured in `hr_assistant/settings.py`
2. Verify database settings for SQLite3
3. Make sure the Applicant model includes scoring fields (migrate if needed)

## Implementation Steps

### 1. Extend the Applicant Model
- Add scoring fields: `overall_score`, `quality_grade`, `categorization`, `justification_summary`, `analysis_date`, `processing_status`
- Run migrations to update the database schema

### 2. Implement the AI Analysis Service
- Create `hr_assistant/services/ai_analysis.py` with LangGraph workflow
- Implement the Supervisor Main Graph and Worker Sub-Graph
- Create the AIAnalysisResponse data contract

### 3. Update the Views
- Create scoring views that return 202 responses for asynchronous processing
- Implement status checking endpoints
- Create endpoints to retrieve scored applicants

### 4. Testing
- Write unit tests achieving 90%+ coverage
- Test the full pipeline with mocked Ollama responses
- Validate data contracts and error handling

## Usage

1. Ensure Ollama is running and accessible
2. Navigate to the job listings page
3. Select an active job listing
4. Initiate the resume scoring process via the API:
   ```bash
   POST /api/job-listings/{job_id}/score-resumes/
   ```
5. Monitor the scoring status:
   ```bash
   GET /api/job-listings/{job_id}/scoring-status/
   ```
6. Retrieve the scored applicants:
   ```bash
   GET /api/job-listings/{job_id}/scored-applicants/
   ```

## API Endpoints

- `POST /api/job-listings/{job_id}/score-resumes/` - Initiate bulk scoring
- `GET /api/job-listings/{job_id}/scoring-status/` - Check scoring status
- `GET /api/job-listings/{job_id}/scored-applicants/` - Get scored applicants

## Troubleshooting

- If Ollama is not responding, check that the service is running and accessible
- If scoring fails, check the processing_status field on Applicant records
- For performance issues with large applicant sets, consider processing in smaller batches