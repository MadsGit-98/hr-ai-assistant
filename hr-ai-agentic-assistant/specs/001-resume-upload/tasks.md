# Tasks: Resume Ingestion (Bulk Upload)

**Feature**: Resume Ingestion (Bulk Upload)
**Date**: Sunday, November 9, 2025
**Status**: To Do

## Dependencies & Execution Order

- **User Story 1 [P1]**: Bulk Resume Upload - Base dependency for all other stories
- **User Story 2 [P1]**: Visual Feedback During Upload - Dependent on US1
- **User Story 3 [P2]**: Duplicate Detection and Alert - Dependent on US1

## Parallel Execution Examples

**Per User Story:**
- **US1**: Can work on Applicant model (jobs/models.py) in parallel with upload view (jobs/views.py)
- **US2**: Can work on frontend template while backend API response is being developed
- **US3**: Can develop duplicate detection utilities while visual feedback UI is being implemented

## Implementation Strategy

- **MVP Scope**: User Story 1 (Bulk Resume Upload) with minimal visual feedback
- **Incremental Delivery**: Each user story should be deployable independently
- **Test Driven**: Each component should have associated tests to achieve 90%+ coverage

---

## Phase 1: Foundational Components

- [X] T001 Configure Django media settings for file storage (max 10MB limit)
- [X] T002 Implement file validation utilities for PDF/DOCX format checking in jobs/utils.py
- [X] T003 Create base directory structure: jobs/templates, jobs/static/css if not present

## Phase 2: User Story 1 - Bulk Resume Upload (P1)

**Goal**: Enable Hiring Manager to securely upload multiple applicant resumes in bulk

**Independent Test**: Can be fully tested by uploading multiple resume files via drag-and-drop or file selection and confirming they are accepted by the system.

### Implementation Tasks

- [X] T004 [P] [US1] Create Applicant model with required fields per data-model.md in jobs/models.py
- [X] T005 [P] [US1] Implement Applicant model validation rules per data-model.md in jobs/models.py
- [X] T006 [P] [US1] Create database migration for Applicant model (makemigrations)
- [X] T007 [P] [US1] Implement calculate_file_hash utility function in jobs/utils.py using hashlib
- [X] T008 [US1] Create ApplicantUploadView in jobs/views.py to handle multi-file POST requests
- [X] T009 [US1] Implement file type validation (PDF/DOCX) in upload view
- [X] T010 [US1] Implement file size validation (max 10MB) in upload view
- [X] T011 [US1] Configure upload endpoint in jobs/urls.py
- [X] T012 [US1] Test file upload functionality with valid PDF and DOCX files
- [X] T013 [US1] Test rejection of invalid file formats

## Phase 3: User Story 2 - Visual Feedback During Upload (P1)

**Goal**: Provide immediate visual feedback after uploading resumes so user can confirm files were processed correctly

**Independent Test**: Can be tested by uploading files and verifying that visual feedback (file names, status messages, progress indicators) is provided during the upload process.

### Implementation Tasks

- [X] T014 [P] [US2] Create upload.html template with drag-and-drop interface in jobs/templates/
- [X] T015 [P] [US2] Implement JavaScript for drag-and-drop file handling
- [X] T016 [US2] Add visual feedback for file queue display
- [X] T017 [US2] Implement JavaScript for AJAX file uploads using fetch API
- [X] T018 [US2] Add progress indicators for individual files during upload
- [X] T019 [US2] Display success/error status for each uploaded file
- [X] T020 [US2] Style the upload interface with Tailwind CSS for responsive design
- [X] T021 [US2] Test visual feedback during successful file uploads
- [X] T022 [US2] Test visual feedback for failed file uploads

## Phase 4: User Story 3 - Duplicate Detection and Alert (P2)

**Goal**: Check for duplicate resumes based on applicant name and file content to avoid processing the same candidate multiple times

**Independent Test**: Can be tested by uploading the same resume file twice or different files with same applicant name, and verifying the system detects and alerts about duplicates.

### Implementation Tasks

- [X] T023 [P] [US3] Implement check_duplicate_content utility in jobs/utils.py
- [X] T024 [P] [US3] Implement check_duplicate_name utility in jobs/utils.py
- [X] T025 [US3] Integrate duplicate detection in upload view before saving
- [X] T026 [US3] Modify upload response to include duplicate status information
- [X] T027 [US3] Update frontend to display duplicate alerts
- [X] T028 [US3] Implement logic to handle duplicate detection options (skip, replace, keep both)
- [X] T029 [US3] Test duplicate detection based on content hash
- [X] T030 [US3] Test duplicate detection based on applicant name
- [X] T031 [US3] Test duplicate handling options (skip, replace, keep both)

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T039 Implement GDPR compliance features for applicant data management
- [X] T040 Add database indexes to Applicant model per data-model.md
- [X] T041 Create comprehensive unit tests for all models (target 90% coverage)
- [X] T042 Create comprehensive unit tests for all views (target 90% coverage)
- [X] T043 Create comprehensive unit tests for all utilities (target 90% coverage)
- [X] T044 Create Selenium tests for critical user journeys (US1, US2, US3)
- [X] T045 Implement proper error handling and user-friendly error messages
- [X] T046 Add logging for file upload operations and duplicate detection
- [X] T047 Implement secure file storage location with restricted access
- [X] T048 Create documentation for the API endpoints based on OpenAPI contract
- [X] T049 Run final test suite and ensure 90%+ coverage across all components
- [X] T050 Perform final integration testing of all user stories together
- [X] T051 Create performance test to validate processing 50 files within 5 minutes
- [X] T052 Create test to validate 95% duplicate detection accuracy rate
- [X] T053 Implement load testing for maximum file size (10MB) and batch limits (100 files)