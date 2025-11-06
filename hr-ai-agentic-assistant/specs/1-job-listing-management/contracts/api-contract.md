# API Contract: Job Listing Management

**Feature**: Job Listing Management
**Date**: 2025-11-06
**Version**: 1.0

## Endpoints

### GET /jobs/
Retrieve a list of all job listings.

**Response**:
```json
{
  "job_listings": [
    {
      "id": 1,
      "title": "Software Engineer",
      "is_active": true,
      "created_date": "2025-11-06T10:00:00Z",
      "modified_date": "2025-11-06T10:00:00Z"
    }
  ]
}
```

### GET /jobs/{id}/
Retrieve a specific job listing by ID.

**Response**:
```json
{
  "id": 1,
  "title": "Software Engineer",
  "detailed_description": "**Job Description**\n\nWe are looking for a skilled software engineer...",
  "required_skills": ["Python", "Django", "SQL", "Git"],
  "is_active": true,
  "created_date": "2025-11-06T10:00:00Z",
  "modified_date": "2025-11-06T10:00:00Z"
}
```

### POST /jobs/
Create a new job listing.

**Request Body**:
```json
{
  "title": "Software Engineer",
  "detailed_description": "**Job Description**\n\nWe are looking for a skilled software engineer...",
  "required_skills": ["Python", "Django", "SQL", "Git"],
  "is_active": true
}
```

**Response**:
```json
{
  "id": 2,
  "title": "Software Engineer",
  "detailed_description": "**Job Description**\n\nWe are looking for a skilled software engineer...",
  "required_skills": ["Python", "Django", "SQL", "Git"],
  "is_active": true,
  "created_date": "2025-11-06T11:00:00Z",
  "modified_date": "2025-11-06T11:00:00Z"
}
```

### PUT /jobs/{id}/
Update an existing job listing.

**Request Body**:
```json
{
  "id": 1,
  "title": "Senior Software Engineer",
  "detailed_description": "**Updated Job Description**\n\nWe are looking for a senior software engineer...",
  "required_skills": ["Python", "Django", "SQL", "Git", "Leadership"],
  "is_active": true
}
```

**Response**:
```json
{
  "id": 1,
  "title": "Senior Software Engineer",
  "detailed_description": "**Updated Job Description**\n\nWe are looking for a senior software engineer...",
  "required_skills": ["Python", "Django", "SQL", "Git", "Leadership"],
  "is_active": true,
  "created_date": "2025-11-06T10:00:00Z",
  "modified_date": "2025-11-06T12:00:00Z"
}
```

### DELETE /jobs/{id}/
Delete a job listing.

**Response**: 204 No Content

### POST /jobs/{id}/activate/
Set a specific job listing as active (and deactivate all others).

**Response**:
```json
{
  "id": 1,
  "title": "Software Engineer",
  "detailed_description": "**Job Description**\n\nWe are looking for a skilled software engineer...",
  "required_skills": ["Python", "Django", "SQL", "Git"],
  "is_active": true,
  "created_date": "2025-11-06T10:00:00Z",
  "modified_date": "2025-11-06T13:00:00Z"
}
```