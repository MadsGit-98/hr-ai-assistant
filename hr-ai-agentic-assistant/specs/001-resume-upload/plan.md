# Implementation Plan: Resume Ingestion (Bulk Upload)

**Branch**: `001-resume-upload` | **Date**: Sunday, November 9, 2025 | **Spec**: [specs/001-resume-upload/spec.md](specs/001-resume-upload/spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a bulk resume upload feature that allows hiring managers to upload multiple PDF/DOCX files efficiently, with duplicate detection based on content hash and applicant name, and immediate visual feedback. The feature will include secure file storage, GDPR compliance, and integration with the LangGraph AI analysis pipeline.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django (latest stable), LangGraph, Ollama API client, Tailwind CSS
**Storage**: SQLite3 (primary), file storage for resumes
**Testing**: Python unittest, Selenium for E2E testing
**Target Platform**: Web server (Linux/Windows/Mac), browser-based UI
**Project Type**: Web application (Django MTV pattern)
**Performance Goals**: Handle up to 100 files in under 10 minutes, with responsive UI
**Constraints**: 90% test coverage minimum, PEP 8 compliance, secure PII handling
**Scale/Scope**: Single HR assistant application with focus on 3 core flows (Upload, Process, Report)

### Architecture Components

**Django Application**: Dedicated `jobs` app (as indicated by the existing project structure) for resume ingestion components
**Data Model**: Applicant model with file reference (FileField), content hash (SHA256), applicant_name, and raw text content
**File Storage**: Django's default file storage with secure configuration for uploaded resumes, with file size limits up to 10MB
**UI/UX**: Drag-and-drop interface with visual feedback and duplicate alerts, using Tailwind CSS for responsive design
**Backend Logic**: Synchronous processing with progress feedback for bulk uploads, with asynchronous trigger placeholder for LangGraph AI processing after successful storage

**Resolved unknowns from research**:
- **SHA256 hash calculation**: Use Python's built-in `hashlib` library to calculate SHA256 hash of file content efficiently by processing in chunks
- **Large file upload handling**: Configure Django settings with appropriate size limits (FILE_UPLOAD_MAX_MEMORY_SIZE = 10MB) and process files in chunks
- **Bulk processing without blocking UI**: Implement JavaScript fetch API for AJAX uploads with real-time progress indicators
- **Security for sensitive data**: Validate file types by content (not just extension), store files in secure location, implement access controls, and ensure GDPR compliance

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Core Technical Stack Mandate**: Using Django (latest stable) as required
- ✅ **Architectural Integrity**: Following Django MTV pattern with service encapsulation in dedicated `jobs` app
- ✅ **Frontend/UX Simplicity**: Simple drag-and-drop interface with mobile-first approach using Tailwind CSS  
- ✅ **Quality & Testing Standards**: Planning for 90% unittest coverage as required, with Selenium for E2E testing
- ✅ **Security & Compliance**: Implementing secure file storage, content validation, and GDPR compliance for PII
- ✅ **Code Standards**: Following PEP 8 and Django naming conventions (Singular PascalCase for Models)
- ✅ **Dependency Management**: Leveraging core Python/Django features first, with minimal additional dependencies

## Project Structure

### Documentation (this feature)

```text
specs/001-resume-upload/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
jobs/
├── models.py        # Applicant model with file storage and hash fields
├── views.py         # ApplicantUploadView for handling multi-file POST requests
├── utils.py         # Duplication utility for hash calculation and duplicate detection
├── urls.py          # URL routing for upload endpoints
└── services.py      # Service layer for LangGraph integration (future)
├── templates/
│   └── upload.html  # Drag-and-drop upload interface with feedback
├── static/
│   └── css/
│       └── tailwind.css  # Tailwind CSS for styling
└── tests/
    ├── test_models.py     # Unit tests for Applicant model
    ├── test_views.py      # Unit tests for ApplicantUploadView
    ├── test_utils.py      # Unit tests for duplication utility
    └── test_e2e.py        # Selenium tests for critical user journeys
```

**Structure Decision**: Web application structure selected with dedicated `jobs` Django app for resume ingestion, following Django conventions for models, views, and templates. This approach centralizes all resume-related functionality in a single app while maintaining separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations identified. All implementation approaches comply with the established architectural patterns and technical mandates.

## Summary of Implementation Plan

This implementation plan has completed the following phases for the Resume Ingestion (Bulk Upload) feature:

### Phase 0: Research & Analysis
- Researched SHA256 hash calculation for file content
- Investigated best practices for handling large file uploads in Django
- Determined optimal approach for bulk processing without blocking the UI
- Established security best practices for handling sensitive resume data
- Documented findings in research.md

### Phase 1: Design & Contracts
- Designed the Applicant data model with all required fields and validation rules
- Created API contracts for resume upload and management endpoints
- Developed a comprehensive quickstart guide with implementation steps
- Planned unit tests to achieve 90%+ coverage as required by constitution
- Updated agent context with new technology considerations

### Generated Artifacts
1. **plan.md**: This implementation plan document
2. **research.md**: Comprehensive research findings for all technical unknowns
3. **data-model.md**: Detailed Applicant entity design with fields, validation, and relationships
4. **contracts/openapi.yaml**: API contract specification for resume ingestion endpoints
5. **quickstart.md**: Step-by-step implementation guide with code examples
6. **Agent context**: Updated with new technology stack considerations

The implementation plan is now complete and ready for the development phase, with all architectural decisions made, technical challenges addressed, and compliance with the project constitution verified.