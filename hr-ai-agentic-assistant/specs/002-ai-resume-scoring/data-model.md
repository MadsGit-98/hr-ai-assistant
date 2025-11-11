# Data Model: AI Resume Scoring Engine

**Created**: 2025-11-11
**Feature**: 002-ai-resume-scoring

## Entities

### Applicant (Extended)
This extends the existing Applicant model to include scoring information:

- `id`: Integer - Primary key
- `name`: String - Applicant's name
- `email`: String - Applicant's email
- `resume_file`: FileField - Original resume file uploaded
- `parsed_resume_text`: TextField - Parsed text content from resume file
- `overall_score`: IntegerField - Overall score (0-100), nullable until scored
- `quality_grade`: CharField(max_length=1) - Quality grade (A, B, C, D, F), nullable until scored
- `categorization`: CharField(max_length=20) - Categorization (Senior, Mid-Level, Junior, Mismatched), nullable until scored
- `justification_summary`: TextField - AI-generated justification for the scores
- `analysis_date`: DateTimeField - Date when analysis was completed
- `processing_status`: CharField(max_length=20) - Current status: 'pending', 'processing', 'completed', 'error'
- `job_listing`: ForeignKey - Job listing this score is relative to
- `created_at`: DateTimeField - Timestamp of record creation
- `updated_at`: DateTimeField - Timestamp of last update

**Validation Rules:**
- `overall_score` must be between 0 and 100 when present
- `quality_grade` must be one of A, B, C, D, F when present
- `categorization` must be one of Senior, Mid-Level, Junior, Mismatched when present
- `processing_status` must be one of 'pending', 'processing', 'completed', 'error'

**Indexes:**
- Index on (job_listing_id, processing_status) for efficient filtering
- Index on overall_score for sorting operations

### JobListing (Existing, referenced)
- `id`: Integer - Primary key
- `title`: String - Job title
- `requirements`: TextField - Job requirements to compare against
- `skills`: TextField - Required skills
- `experience_level`: String - Expected experience level
- Additional fields as defined in existing model

## Relationships

- One JobListing can have multiple Applicant records (one-to-many)
- Each Applicant record is associated with exactly one JobListing
- The scoring is specific to the JobListing it's associated with

## State Transitions for processing_status

- `pending` → `processing` when scoring is initiated
- `processing` → `completed` when all scoring steps finish successfully
- `processing` → `error` when any scoring step fails
- `completed` → `completed` (no change, final state)
- `error` → `processing` when retry is initiated (optional feature)

## AIAnalysisResponse Contract

This is a data transfer object used internally within the service layer:

- `overall_score`: Integer - Score between 0-100
- `quality_grade`: String - Single character grade (A-F)
- `categorization`: String - One of Senior, Mid-Level, Junior, Mismatched
- `justification_summary`: String - Explanation of the scoring
- `applicant_id`: Integer - Reference to the applicant being scored

## Constraints

- Resume text must be successfully parsed before scoring begins
- A scoring operation is always specific to one JobListing and can involve multiple Applicants
- Once scored (status = 'completed'), further changes to job requirements don't automatically trigger re-scoring (as per clarifications)
- Only one scoring process can run system-wide at a time (as per clarifications)