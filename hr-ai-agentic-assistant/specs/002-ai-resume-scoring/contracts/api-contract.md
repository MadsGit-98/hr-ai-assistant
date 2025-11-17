# API Contract: Resume Scoring Endpoints

**Created**: 2025-11-11
**Feature**: 002-ai-resume-scoring

## Endpoint: Initiate Bulk Resume Scoring

### POST /api/job-listings/{job_id}/score-resumes/

Initiates the bulk scoring process for all applicants associated with a job listing.

**Path Parameters:**
- `job_id` (integer): The ID of the job listing to score resumes against

**Request Body:**
```json
{
  "applicant_ids": [1, 2, 3, ...]  // Optional: specific applicant IDs to score; if omitted, scores all applicants for the job
}
```

**Request Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>` (as per existing auth implementation)

**Response:**
- `202 ACCEPTED`: Scoring process initiated successfully
```json
{
  "status": "accepted",
  "message": "Resume scoring process initiated",
  "job_id": 123,
  "applicant_count": 25,
  "tracking_id": "uuid-string-for-potential-future-status-check"
}
```

- `400 BAD REQUEST`: Invalid request parameters
```json
{
  "error": "Invalid input",
  "details": ["applicant_ids must be an array of integers", ...]
}
```

- `404 NOT FOUND`: Job listing does not exist
```json
{
  "error": "Job listing not found"
}
```

- `423 LOCKED`: Another scoring process is already running system-wide (as per clarification)
```json
{
  "error": "Another scoring process is currently running. Please wait for it to complete."
}
```

## Endpoint: Get Scoring Status

### GET /api/job-listings/{job_id}/scoring-status/

Retrieves the current status of the scoring process for a job listing.

**Path Parameters:**
- `job_id` (integer): The ID of the job listing

**Request Headers:**
- `Authorization: Bearer <token>` (as per existing auth implementation)

**Response:**
- `200 OK`: Status retrieved successfully
```json
{
  "job_id": 123,
  "status": "processing",  // Enum: pending, processing, completed, error
  "total_applicants": 25,
  "completed_count": 5,
  "error_count": 0,
  "message": "Processing 5 of 25 applicants"
}
```

## Endpoint: Get Scored Applicants

### GET /api/job-listings/{job_id}/scored-applicants/

Retrieves the applicants with their scores for a specific job listing.

**Path Parameters:**
- `job_id` (integer): The ID of the job listing

**Query Parameters:**
- `status` (string, optional): Filter by processing status (pending, processing, completed, error)
- `limit` (integer, optional): Number of results to return (default: 50, max: 100)
- `offset` (integer, optional): Number of results to skip (for pagination)

**Request Headers:**
- `Authorization: Bearer <token>` (as per existing auth implementation)

**Response:**
- `200 OK`: Applicants retrieved successfully
```json
{
  "job_id": 123,
  "applicants": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "overall_score": 85,
      "quality_grade": "A",
      "categorization": "Senior",
      "justification_summary": "Strong experience in relevant technologies with 8+ years...",
      "processing_status": "completed",
      "analysis_date": "2025-11-11T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "overall_score": 72,
      "quality_grade": "B",
      "categorization": "Mid-Level",
      "justification_summary": "Good experience but lacks some advanced skills...",
      "processing_status": "completed",
      "analysis_date": "2025-11-11T10:32:00Z"
    }
  ],
  "total_count": 25,
  "filtered_count": 25
}
```

## AIAnalysisResponse Contract

This is the internal data structure representing the result of AI analysis:

```json
{
  "overall_score": 85,
  "quality_grade": "A",
  "categorization": "Senior",
  "justification_summary": "Strong experience in relevant technologies with 8+ years...",
  "applicant_id": 1
}
```

**Field Constraints:**
- `overall_score`: Integer between 0 and 100
- `quality_grade`: Single character from A, B, C, D, F
- `categorization`: String from Senior, Mid-Level, Junior, Mismatched
- `justification_summary`: String with explanation of the scoring
- `applicant_id`: Integer referencing the applicant being scored