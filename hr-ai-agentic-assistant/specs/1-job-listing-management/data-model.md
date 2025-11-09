# Data Model: Job Listing Management

**Feature**: Job Listing Management
**Date**: 2025-11-06
**Status**: Complete

## Entities

### JobListing

The JobListing entity represents a single job position with all required information for applicant scoring.

**Fields**:
- `id` (AutoField, Primary Key): Unique identifier for the job listing
- `title` (CharField, max_length=200): Title of the job position (from spec limits)
- `detailed_description` (TextField): Description of the job with markdown content
- `required_skills` (JSONField): Structured list of required skills/qualities for the position
- `is_active` (BooleanField, default=False): Boolean flag indicating if this is the active listing
- `created_date` (DateTimeField, auto_now_add=True): Timestamp when the listing was created
- `modified_date` (DateTimeField, auto_now=True): Timestamp when the listing was last modified

**Validation Rules**:
1. `title` is required and must not exceed 200 characters
2. Only one JobListing can have `is_active` set to True at any time
3. `required_skills` must be a valid JSON array of strings
4. `detailed_description` supports markdown content but must be sanitized to prevent XSS

**Relationships**:
- No relationships with other entities in this proof-of-concept version

**State Transitions**:
- When a JobListing is set to `is_active=True`, all other JobListings must be set to `is_active=False`
- JobListings can transition between active/inactive states based on user action