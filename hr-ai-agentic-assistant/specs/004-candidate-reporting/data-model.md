# Data Model: Candidate Reporting and Shortlisting

**Feature**: 004-candidate-reporting
**Date**: Tuesday, November 18, 2025

## Entities

### Applicant (Extended)
This extends the existing Applicant model to include shortlisting information:

- `id`: Integer - Primary key (existing)
- `job_listing`: ForeignKey - The job listing this applicant has applied for (existing)
- `applicant_name`: String - Name of the applicant extracted from the resume filename (existing)
- `resume_file`: FileField - Reference to the uploaded resume file (PDF/DOCX) (existing)
- `content_hash`: String - SHA256 hash of the file content for duplicate detection (existing)
- `file_size`: PositiveIntegerField - Size of the uploaded file in bytes (existing)
- `file_format`: String - File format (PDF, DOCX) (existing)
- `upload_date`: DateTimeField - Timestamp of when the resume was uploaded (existing)
- `processing_status`: String - Current status of AI processing (choices: 'pending', 'processing', 'completed', 'error') (existing)
- `analysis_status`: String - Status of the analysis process (choices: 'pending', 'analyzed', 'error') (existing)
- `overall_score`: IntegerField - Overall score (0-100) representing fitness for the job (existing)
- `quality_grade`: String - Quality grade (A, B, C, D, F) reflecting quality of experience (existing)
- `categorization`: String - Categorization (e.g., Senior, Mid-Level, Junior, Mismatched) (existing)
- `justification_summary`: TextField - AI-generated justification for the scores (existing)
- `analysis_timestamp`: DateTimeField - Date and time when the analysis was completed (existing)
- `parsed_resume_text`: TextField - Parsed text content from resume file (existing)
- `ai_analysis_result`: JSONField - JSON data containing the results of AI analysis (existing)
- `is_shortlisted` (BooleanField): NEW FIELD - Flag indicating if the candidate is marked for interview (default: False)

**Validation Rules**:
- `file_format` must be either 'PDF' or 'DOCX' (existing)
- `file_size` must be between 1KB and 10MB (existing)
- `applicant_name`, `resume_file`, `content_hash` must not be null (existing)
- `applicant_name` should match standard name patterns (existing)
- If `job_listing` is provided, it must be active (existing)
- `overall_score` must be between 0 and 100 (existing)
- An applicant must be associated with a valid job listing (existing)

**State Transitions**:
- When `is_shortlisted` is toggled from False to True: The candidate is marked for interview consideration
- When `is_shortlisted` is toggled from True to False: The candidate is unmarked from interview consideration

### JobListing (Existing, referenced)
- `id`: Integer - Primary key (existing)
- `title`: String - Title of the job position (existing)
- `detailed_description`: TextField - Description of the job with markdown content (existing)
- `required_skills`: JSONField - Structured list of required skills/qualities for the position (existing)
- `is_active`: BooleanField - Boolean flag indicating if this is the active listing (existing)
- `created_date`: DateTimeField - Auto-created timestamp (existing)
- `modified_date`: DateTimeField - Auto-updated timestamp (existing)

## Relationships

- One JobListing can have multiple Applicant records (one-to-many) (existing)
- Each Applicant record is associated with exactly one JobListing (existing)

## Database Constraints

- Maximum of 500 applicants per job listing (enforced in application logic)
- Overall score range: 0-100 (enforced by field validation) (existing)
- File format must be 'PDF' or 'DOCX' (existing)
- File size between 1KB and 10MB (existing)
- Content hash must be unique (existing)

## Indexing Strategy

- Index on `content_hash` for fast duplicate detection queries (existing)
- Index on `upload_date` for chronological queries (existing)
- Index on `processing_status` for status-based filtering (existing)
- Index on `applicant_name` for name-based searches (existing)
- Index on `overall_score` for sorting operations (existing)
- Index on `is_shortlisted` for quick filtering of shortlisted candidates (NEW)
- Index on `job_listing` and `processing_status` for efficient filtering (existing)