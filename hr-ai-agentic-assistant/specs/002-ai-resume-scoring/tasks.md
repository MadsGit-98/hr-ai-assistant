# Tasks: AI Resume Scoring Engine

**Input**: Design documents from `/specs/002-ai-resume-scoring/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The feature specification requires 90% test coverage, so we will include comprehensive unit and integration tests throughout.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Django project**: `hr_assistant/` for main Django app
- **Services**: `hr_assistant/services/` for service layer
- **Models**: `jobs/models.py` for Django models (Applicant model already exists)
- **Views**: `jobs/views.py` for Django views
- **Tests**: `tests/` for all test files

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create services directory in hr_assistant/services/ per constitution requirements
- [ ] T002 Install LangGraph and Ollama dependencies in requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Foundational tasks for the AI Resume Scoring Engine:

- [ ] T003 Setup LangGraph configuration and state management in hr_assistant/services/
- [ ] T004 [P] Configure Ollama integration and test connection
- [ ] T005 [P] Update Applicant model to extend scoring fields if needed in jobs/models.py
- [ ] T006 [P] Implement resume text parsing and storage functionality in jobs/services/resume_parser.py
- [ ] T007 Configure error handling and logging infrastructure for AI processing
- [ ] T008 Setup API routing for new scoring endpoints in hr_assistant/urls.py and jobs/urls.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Score Resumes for Active Job Listing (Priority: P1) 🎯 MVP

**Goal**: Implement core functionality to select a job listing and initiate processing of all uploaded resumes against it to generate objective, data-driven candidate scores.

**Independent Test**: The system successfully takes an active job listing and associated resumes, runs the AI analysis, and produces a scoring report with the three required metrics for each resume.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Contract test for POST /api/job-listings/{job_id}/score-resumes/ in tests/contract/test_scoring_api.py
- [ ] T010 [P] [US1] Contract test for GET /api/job-listings/{job_id}/scoring-status/ in tests/contract/test_scoring_api.py
- [ ] T011 [P] [US1] Unit test for AIAnalysisResponse contract in tests/unit/test_contracts.py
- [ ] T012 [P] [US1] Integration test for full scoring pipeline in tests/integration/test_scoring_pipeline.py

### Implementation for User Story 1

- [ ] T013 [P] [US1] Implement AIAnalysisResponse data contract in hr_assistant/services/contracts.py
- [ ] T014 [US1] Create LangGraph state definition for Supervisor graph in hr_assistant/services/ai_analysis.py
- [ ] T015 [US1] Create Worker Sub-Graph with Data Retrieval Node in hr_assistant/services/ai_analysis.py
- [ ] T016 [US1] Create Worker Sub-Graph with Scoring & Grading Node in hr_assistant/services/ai_analysis.py
- [ ] T017 [US1] Create Worker Sub-Graph with Categorization Node in hr_assistant/services/ai_analysis.py
- [ ] T018 [US1] Create Worker Sub-Graph with Justification Node in hr_assistant/services/ai_analysis.py
- [ ] T019 [US1] Create Supervisor Main Graph with Batch Iteration in hr_assistant/services/ai_analysis.py
- [ ] T020 [US1] Create Bulk Persistence Node in hr_assistant/services/ai_analysis.py
- [ ] T021 [US1] Implement resume scoring service interface in hr_assistant/services/resume_scoring.py
- [ ] T022 [US1] Implement scoring view to return 202 response in jobs/views.py
- [ ] T023 [US1] Implement status checking endpoint in jobs/views.py
- [ ] T024 [US1] Add validation and error handling for resume scoring
- [ ] T025 [US1] Add logging for scoring operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Detailed Resume Analysis (Priority: P2)

**Goal**: Implement functionality to view the detailed analysis that led to each resume's scores so that the hiring manager can understand the AI's reasoning and make more informed hiring decisions.

**Independent Test**: For each resume, the system can display the factors that contributed to the Overall Score, Categorization, and Quality Grade.

### Tests for User Story 2 ⚠️

- [ ] T026 [P] [US2] Contract test for GET /api/job-listings/{job_id}/scored-applicants/ in tests/contract/test_scoring_api.py
- [ ] T027 [P] [US2] Unit test for detailed analysis retrieval in tests/unit/test_analysis_details.py
- [ ] T028 [US2] Integration test for detailed analysis display in tests/integration/test_analysis_details.py

### Implementation for User Story 2

- [ ] T029 [P] [US2] Enhance Applicant model to properly store/extract detailed analysis from ai_analysis_result field in jobs/models.py
- [ ] T030 [US2] Implement detailed analysis endpoint in jobs/views.py
- [ ] T031 [US2] Add detailed analysis functionality to resume scoring service in hr_assistant/services/resume_scoring.py
- [ ] T032 [US2] Enhance AI analysis service to return detailed explanations in hr_assistant/services/ai_analysis.py
- [ ] T033 [US2] Add validation and error handling for detailed analysis
- [ ] T034 [US2] Add logging for detailed analysis operations

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Filter and Sort Candidates by Scores (Priority: P3)

**Goal**: Implement functionality to filter and sort candidates based on their scores and categories so that the hiring manager can quickly identify the most promising candidates for further review.

**Independent Test**: The system allows filtering by score ranges, categories, and grades, with results displayed in a sortable table.

### Tests for User Story 3 ⚠️

- [ ] T035 [P] [US3] Contract test for filtering and sorting query parameters in tests/contract/test_scoring_api.py
- [ ] T036 [P] [US3] Unit test for filtering functionality in tests/unit/test_filtering.py
- [ ] T037 [P] [US3] Integration test for sorting functionality in tests/integration/test_sorting.py

### Implementation for User Story 3

- [ ] T038 [P] [US3] Add database indexes for efficient filtering and sorting if needed in jobs/models.py
- [ ] T039 [US3] Update scored applicants endpoint to support filtering and sorting in jobs/views.py
- [ ] T040 [US3] Enhance resume scoring service to support filtering and sorting in hr_assistant/services/resume_scoring.py
- [ ] T041 [US3] Add validation and error handling for filtering and sorting
- [ ] T042 [US3] Add logging for filtering and sorting operations

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T043 [P] Documentation updates in docs/ and specs/ directories
- [ ] T044 Code cleanup and refactoring
- [ ] T045 Performance optimization across all stories
- [ ] T046 [P] Additional unit tests to reach 90% coverage in tests/unit/
- [ ] T047 Security hardening for PII handling
- [ ] T048 Run quickstart.md validation
- [ ] T049 Add Ollama integration tests with mocked responses
- [ ] T050 Final integration testing across all user stories

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds upon US1 components
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds upon US1/US2 components

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
# Launch all tests for User Story 1 together:
T009 [P] [US1] Contract test for POST /api/job-listings/{job_id}/score-resumes/ in tests/contract/test_scoring_api.py
T010 [P] [US1] Contract test for GET /api/job-listings/{job_id}/scoring-status/ in tests/contract/test_scoring_api.py
T011 [P] [US1] Unit test for AIAnalysisResponse contract in tests/unit/test_contracts.py
T012 [P] [US1] Integration test for full scoring pipeline in tests/integration/test_scoring_pipeline.py

# Launch all services for User Story 1 together:
T013 [P] [US1] Implement AIAnalysisResponse data contract in hr_assistant/services/contracts.py
T014 [US1] Create LangGraph state definition for Supervisor graph in hr_assistant/services/ai_analysis.py
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

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

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