# Data Model: Resume Ingestion (Bulk Upload)

**Feature**: Resume Ingestion (Bulk Upload) | **Date**: Sunday, November 9, 2025

## Entity: Applicant

Represents an applicant with their resume data and metadata.

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| id | AutoField (Primary Key) | NOT NULL | Unique identifier for the applicant record |
| applicant_name | CharField(255) | NOT NULL | Name of the applicant extracted from the resume filename |
| resume_file | FileField | NOT NULL | Reference to the uploaded resume file (PDF/DOCX) |
| content_hash | CharField(64) | NOT NULL, UNIQUE | SHA256 hash of the file content for duplicate detection |
| file_size | PositiveIntegerField | NOT NULL | Size of the uploaded file in bytes |
| file_format | CharField(10) | NOT NULL | File format (PDF, DOCX) |
| upload_date | DateTimeField | NOT NULL, auto_now_add=True | Timestamp of when the resume was uploaded |
| processing_status | CharField(20) | NOT NULL, default='pending' | Current status of AI processing ('pending', 'processing', 'completed', 'error') |
| ai_analysis_result | JSONField | NULL | JSON data containing the results of AI analysis |

### Validation Rules

1. **File Format Validation**: `file_format` must be either 'PDF' or 'DOCX'
2. **File Size Validation**: `file_size` must be between 1KB and 10MB (10485760 bytes)
3. **Content Hash Uniqueness**: `content_hash` must be unique across all Applicant records
4. **Required Fields**: `applicant_name`, `resume_file`, `content_hash` must not be null
5. **Name Format**: `applicant_name` should match standard name patterns extracted from the filename using pattern recognition (e.g., "FirstName_LastName_Resume.pdf")

### State Transitions

```
'pending' → 'processing' → 'completed'
      ↓
    'error' (retry possible)
```

- `pending`: File uploaded, waiting for AI analysis
- `processing`: AI analysis in progress
- `completed`: AI analysis completed successfully
- `error`: AI analysis failed, can be retried

### Relationships

This entity is intended to be standalone for the initial implementation but may have future relationships with:
- Job Applications (many-to-many relationship in future features)
- Job Listings (many-to-many relationship in future features)

## Database Indexes

1. **content_hash**: B-tree index for fast duplicate detection queries
2. **upload_date**: B-tree index for chronological queries
3. **processing_status**: B-tree index for status-based filtering
4. **applicant_name**: B-tree index for name-based searches

## Migration Strategy

The Applicant model will be created through Django migrations as part of the `jobs` app. The migration will include:

1. Creation of the Applicant table with all required fields
2. Addition of necessary database indexes
3. Setting up unique constraint on content_hash
4. Initial data validation checks

## GDPR Compliance Considerations

- **Right to Access**: API endpoints for data access requests
- **Right to Rectification**: Ability to update applicant information
- **Right to Erasure**: Deletion of applicant records and files
- **Retention Policy**: Automated cleanup of unprocessed files after 30 days
- **Data Portability**: Export functionality for applicant data