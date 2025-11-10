# Research: Resume Ingestion (Bulk Upload)

**Feature**: Resume Ingestion (Bulk Upload) | **Date**: Sunday, November 9, 2025

## Research Summary

This research document addresses the unknowns identified in the technical context for the Resume Ingestion feature, focusing on file handling, security, and performance considerations.

## 1. SHA256 Hash Calculation for File Content

**Decision**: Use Python's built-in `hashlib` library to calculate SHA256 hash of file content.

**Rationale**: 
- `hashlib` is part of Python's standard library, requiring no additional dependencies
- SHA256 is cryptographically secure and appropriate for duplicate detection
- Efficient for the typical file sizes expected (up to 10MB per resume)
- Can process files in chunks to handle larger files without memory issues

**Implementation approach**:
```python
import hashlib

def calculate_file_hash(file):
    """Calculate SHA256 hash of file content."""
    sha256_hash = hashlib.sha256()
    # Process file in chunks to handle large files efficiently
    for chunk in iter(lambda: file.read(4096), b""):
        sha256_hash.update(chunk)
    file.seek(0)  # Reset file pointer
    return sha256_hash.hexdigest()
```

**Alternatives considered**:
- MD5: Faster but less secure; not recommended for any security-sensitive applications
- SHA1: Faster than SHA256 but has known vulnerabilities
- Third-party libraries: Would add unnecessary dependencies when standard library suffices

## 2. Best Practices for Handling Large File Uploads in Django

**Decision**: Configure Django settings for secure file uploads with size limits and implement chunked processing.

**Rationale**:
- Django has built-in support for file uploads but requires proper configuration for security
- Need to set appropriate size limits to prevent abuse while allowing the requested 10MB per file
- Chunked processing prevents memory issues with large files

**Implementation approach**:
```python
# In Django settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_TEMP_DIR = '/path/to/temp/upload/dir'

# In views, use chunked processing to handle large files efficiently
```

**Alternatives considered**:
- Streaming uploads: More complex to implement, not necessary for this use case
- External storage services: Overkill for initial implementation, can be added later if needed

## 3. Optimal Approach for Bulk File Processing Without Blocking UI

**Decision**: Implement asynchronous processing with JavaScript feedback using Django's file upload handlers.

**Rationale**:
- Users need feedback during processing of up to 100 files
- Asynchronous processing prevents blocking the UI during potentially lengthy operations
- Django provides built-in upload handlers for progress tracking
- JavaScript can provide real-time feedback to the user

**Implementation approach**:
- Use JavaScript fetch API for AJAX file uploads
- Implement progress indicators for each file
- Process files sequentially or in small batches to manage server resources
- Update UI in real-time to show progress status

**Alternatives considered**:
- WebSockets: More complex setup, not necessary for this use case
- Server-sent events: Good alternative, but AJAX with progress tracking sufficient for now

## 4. Security Best Practices for Handling Sensitive Resume Data

**Decision**: Implement file type validation, secure storage, and GDPR compliance measures.

**Rationale**:
- Resumes contain PII requiring protection under GDPR
- Need to validate file types to prevent malicious uploads
- Secure storage configuration prevents unauthorized access
- GDPR compliance requires proper data handling practices

**Implementation approach**:
- Validate file types by content (not just extension) to prevent attacks
- Store files in a directory not directly accessible via web server
- Implement proper access controls and authentication
- Add GDPR-compliant data retention and deletion policies
- Use Django's built-in file security measures

**Security measures**:
- MIME type validation on upload
- File extension validation
- Virus scanning (future enhancement consideration)
- Access logging for data audit trail
- Secure file storage location with restricted permissions

**Alternatives considered**:
- Content inspection: More thorough but resource-intensive, may be added later
- Client-side validation only: Insufficient security, server-side validation required

## 5. Duplicate Detection Strategy

**Decision**: Combine content hash (SHA256) and applicant name for comprehensive duplicate detection.

**Rationale**:
- Using both content hash and name provides two layers of duplicate detection
- Content hash catches exact duplicates regardless of filenames
- Name matching catches cases where the same person's resume is modified
- Users can choose to skip, replace, or keep both when duplicates detected

**Implementation approach**:
- Calculate SHA256 hash of file content for content-based duplicate detection
- Extract applicant name from filename or file metadata for name-based detection
- Query database for existing hashes and names before saving
- Present options to user when duplicates found

## 6. Performance Optimization for Bulk Processing

**Decision**: Process files in small batches with progress tracking and timeout handling.

**Rationale**:
- Processing 100 files can take significant time (up to 10 minutes as specified)
- Need to prevent timeouts and provide user feedback
- Small batches help manage server resources and allow for error recovery

**Implementation approach**:
- Process files in batches of 5-10 for better resource management
- Implement timeout handling for individual files
- Track progress for each file in the batch
- Provide overall batch progress indicator