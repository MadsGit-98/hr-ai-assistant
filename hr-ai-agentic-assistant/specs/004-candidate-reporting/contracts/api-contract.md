# API Contract: Candidate Reporting and Shortlisting

**Feature**: 004-candidate-reporting
**Date**: Tuesday, November 18, 2025

## Overview

This document defines the API contracts for the candidate reporting and shortlisting feature. The API enables the display, sorting, filtering, and shortlisting of candidates.

## Endpoints

### GET /scoring_results/

**Description**: Retrieves the candidate report page with all analyzed candidates for the active job.

**Query Parameters**:
- `sort_by` (optional, string): Column to sort by. Default: "overall_score"
  - Valid values: "name", "overall_score", "categorization", "quality_grade"
- `sort_order` (optional, string): Sort direction. Default: "desc"
  - Valid values: "asc", "desc"
- `score_threshold` (optional, integer): Minimum score threshold for filtering. Default: 0
  - Valid range: 0-100

**Response**:
- Status: 200 OK
- Content-Type: text/html
- Body: HTML page containing the candidate report table with filtering and sorting controls

**Error Responses**:
- 404: Job not found
- 500: Internal server error

### GET /jobs/{job_id}/candidates/

**Description**: Retrieves the candidate report page for a specific job with all analyzed candidates.

**Path Parameters**:
- `job_id` (integer): ID of the job listing

**Query Parameters**:
- `sort_by` (optional, string): Column to sort by. Default: "overall_score"
  - Valid values: "name", "overall_score", "categorization", "quality_grade"
- `sort_order` (optional, string): Sort direction. Default: "desc"
  - Valid values: "asc", "desc"
- `score_threshold` (optional, integer): Minimum score threshold for filtering. Default: 0
  - Valid range: 0-100

**Response**:
- Status: 200 OK
- Content-Type: text/html
- Body: HTML page containing the candidate report table with filtering and sorting controls

**Error Responses**:
- 404: Job not found
- 500: Internal server error

### POST /api/candidates/{candidate_id}/toggle-shortlist/

**Description**: Toggles the shortlist status of a specific candidate.

**Path Parameters**:
- `candidate_id` (integer): ID of the candidate

**Request Body**:
- Content-Type: application/json
- Example: `{}`
- No required fields in the body

**Response**:
- Status: 200 OK
- Content-Type: application/json
- Body:
  ```json
  {
    "candidate_id": 123,
    "is_shortlisted": true,
    "message": "Candidate shortlist status updated successfully"
  }
  ```

**Error Responses**:
- 400: Invalid candidate ID
- 404: Candidate not found
- 500: Internal server error

## Request/Response Formats

### Candidate Data Format
```json
{
  "id": 123,
  "name": "John Doe",
  "overall_score": 87.5,
  "categorization": "Senior",
  "quality_grade": "A",
  "ai_justification_summary": "Candidate has excellent experience with the required skills...",
  "is_shortlisted": false,
  "job_id": 42
}
```

### Filtered Candidates List Format
```json
{
  "candidates": [
    {
      "id": 123,
      "name": "John Doe",
      "overall_score": 87.5,
      "categorization": "Senior",
      "quality_grade": "A",
      "ai_justification_summary": "Candidate has excellent experience with the required skills...",
      "is_shortlisted": false,
      "job_id": 42
    }
  ],
  "total_count": 25,
  "filtered_count": 15,
  "filters_applied": {
    "score_threshold": 80
  },
  "sorting_applied": {
    "sort_by": "overall_score",
    "sort_order": "desc"
  }
}
```

## Validations

### Request Validations:
1. Score threshold must be between 0 and 100
2. Sort by field must be one of the allowed values
3. Sort order must be either "asc" or "desc"
4. Candidate ID must be a positive integer

### Response Validations:
1. All required fields in candidate data must be present
2. Overall score must be between 0 and 100
3. Categorization must be one of: "Senior", "Mid-Level", "Junior", "Mismatched"
4. Quality grade must be one of: "A", "B", "C", "D", "F"
5. The number of candidates returned must not exceed the 500 candidate limit

## Security Considerations

1. All endpoints require authentication for hiring managers
2. Candidates can only be accessed by users with appropriate permissions for the corresponding job
3. The API enforces the maximum limit of 500 candidates
4. All inputs are validated to prevent injection attacks

## Performance Requirements

1. The report page should load within 5 seconds for up to 500 candidates
2. Filtering should return results within 2 seconds for up to 500 candidates
3. Sorting should return results within 1 second
4. The shortlist toggle should respond within 500ms