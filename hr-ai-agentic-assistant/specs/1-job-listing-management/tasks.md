---

description: "Task list template for feature implementation"
---

# Tasks: Job Listing Management

**Input**: Design documents from `/specs/1-job-listing-management/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Django project structure with 'hr_assistant' project
- [ ] T002 [P] Install Django, markdown and bleach dependencies
- [ ] T003 Create 'jobs' Django application
- [ ] T004 Configure project settings to include 'jobs' app
- [ ] T005 [P] Install and configure Tailwind CSS for the project

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T006 Setup JobListing model with required fields in jobs/models.py
- [ ] T006a Add field validation to JobListing model: title max 200 chars in jobs/models.py (depends on T006)
- [ ] T006b Add field validation to JobListing model: detailed_description max 50000 chars in jobs/models.py (depends on T006)
- [ ] T006c Add field validation to JobListing model: required_skills max 100 items in jobs/models.py (depends on T006)
- [ ] T007 [P] Implement single active job listing validation in jobs/models.py
- [ ] T007a [P] Implement single active job listing constraint: deactivate other listings when one is activated in jobs/models.py (depends on T006)
- [ ] T007b [P] Implement auto-activation of first created job listing in jobs/models.py (depends on T006)
- [ ] T008 [P] Configure markdown sanitization using markdown and bleach libraries for detailed_description field in jobs/models.py
- [ ] T009 Create base templates directory structure in jobs/templates/
- [ ] T010 Create base static files directory structure in jobs/static/
- [ ] T011 Configure URL routing framework and include jobs URLs in main urls.py
- [ ] T003a Configure project to operate without authentication as proof-of-concept in settings.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Job Listing (Priority: P1) 🎯 MVP

**Goal**: Enable hiring managers to create new job listings with title, detailed description, and required skills

**Independent Test**: Can be fully tested by creating a new job listing with all required fields and verifying it's saved and can be viewed. Delivers the core value of being able to define what the system will use to evaluate candidates.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

- [ ] T012 [P] [US1] Unit test for JobListing model creation validation in tests/jobs/test_models.py
- [ ] T013 [P] [US1] Unit test for create view functionality in tests/jobs/test_views.py

### Implementation for User Story 1

- [ ] T014 [P] [US1] Create JobListing model with all required fields in jobs/models.py (depends on T006, T007, T008)
- [ ] T015 [US1] Create JobListingForm with validation in jobs/forms.py
- [ ] T016 [US1] Implement JobListingCreateView in jobs/views.py
- [ ] T017 [US1] Create joblisting_form.html template with Tailwind CSS in jobs/templates/jobs/
- [ ] T018 [US1] Add create URL route to jobs/urls.py
- [ ] T019 [US1] Add markdown rendering helper function in jobs/utils.py
- [ ] T020 [US1] Integrate markdown rendering and sanitization in the create view
- [ ] T020a [US1] Implement markdown to HTML conversion with sanitization function in jobs/utils.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Job Listing (Priority: P1)

**Goal**: Enable hiring managers to view existing job listings

**Independent Test**: Can be fully tested by navigating to view an existing job listing and confirming all information displays correctly. Delivers value by allowing managers to review job requirements.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T021 [P] [US2] Unit test for detail view functionality in tests/jobs/test_views.py
- [ ] T022 [P] [US2] Unit test for job listing retrieval in tests/jobs/test_models.py

### Implementation for User Story 2

- [ ] T023 [P] [US2] Implement JobListingDetailView in jobs/views.py
- [ ] T024 [US2] Implement JobListingListView in jobs/views.py
- [ ] T025 [US2] Create joblisting_detail.html template with Tailwind CSS in jobs/templates/jobs/
- [ ] T026 [US2] Create joblisting_list.html template with Tailwind CSS in jobs/templates/jobs/
- [ ] T027 [US2] Add detail and list URL routes to jobs/urls.py
- [ ] T028 [US2] Integrate markdown rendering in the detail view

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Edit Job Listing (Priority: P2)

**Goal**: Enable hiring managers to edit existing job listings

**Independent Test**: Can be fully tested by editing an existing job listing and verifying the changes are saved and reflected when viewing. Delivers value by allowing ongoing management of job requirements.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T029 [P] [US3] Unit test for update view functionality in tests/jobs/test_views.py
- [ ] T030 [P] [US3] Unit test for job listing update validation in tests/jobs/test_models.py

### Implementation for User Story 3

- [ ] T031 [P] [US3] Implement JobListingUpdateView in jobs/views.py
- [ ] T032 [US3] Implement JobListingDeleteView in jobs/views.py
- [ ] T033 [US3] Update joblisting_form.html template to support both create and update operations
- [ ] T034 [US3] Add update and delete URL routes to jobs/urls.py
- [ ] T035 [US3] Implement mechanism to prevent concurrent editing - ensure only one user can edit a job listing at a time using optimistic locking in jobs/views.py
- [ ] T036 [US3] Add activate endpoint to set job listing as active in jobs/views.py
- [ ] T037 [US3] Add activate URL route to jobs/urls.py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T038 [P] Documentation updates in docs/
- [ ] T039 Code cleanup and refactoring
- [ ] T040 Performance optimization across all stories
- [ ] T041 [P] Additional unit tests (if requested) in tests/jobs/
- [ ] T042 Security hardening
- [ ] T043 Run quickstart.md validation
- [ ] T044 [P] Create Selenium E2E tests in tests/jobs/test_e2e.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Unit test for JobListing model creation validation in tests/jobs/test_models.py"
Task: "Unit test for create view functionality in tests/jobs/test_views.py"

# Launch all models for User Story 1 together:
Task: "Create JobListing model with all required fields in jobs/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Add User Story 1 → Test independently → Deploy/Demo (MVP!)
   - Add User Story 2 → Test independently → Deploy/Demo 
   - Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence