# Tasks: Candidate Reporting and Shortlisting

**Input**: Design documents from `/specs/004-candidat-reporting/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Verify all dependencies from requirements.txt are installed for reporting feature
- [ ] T002 [P] Configure Tailwind CSS for responsive tables and components needed for candidate reporting
- [ ] T003 Verify Django project structure is ready with hr_assistant and jobs apps

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [x] T004 Update Applicant model with is_shortlisted field in jobs/models.py
- [x] T005 Create database migration for is_shortlisted field in jobs/migrations/
- [x] T006 [P] Create report utility module in hr_assistant/services/report_utils.py
- [x] T007 Create scoring results HTML template in templates/scoring_results.html
- [x] T008 [P] Create reporting JavaScript file in static/js/reporting.js
- [x] T009 Create Tailwind CSS for responsive table in static/css/tailwind.css

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Candidate Reports (Priority: P1) 🎯 MVP

**Goal**: As a Hiring Manager, I want to view a sortable and filterable Final Report of all analyzed candidates so I can quickly identify the best candidates to interview. The report must display Name, Overall Score, Categorization, Quality Grade, and AI Justification Summary.

**Independent Test**: Can be fully tested by loading the scoring results page and verifying that candidate data is displayed in a table format with all required fields visible.

### Implementation for User Story 1

- [x] T010 [P] [US1] Create CandidateReportView class-based view in jobs/views.py
- [x] T011 [US1] Implement GET endpoint for /scoring_results/ in jobs/urls.py and views.py
- [x] T012 [US1] Fetch all analyzed applicants from database in views.py (max 500 per spec)
- [x] T013 [US1] Implement default sorting by Overall Score descending in report_utils.py
- [x] T014 [US1] Pass required candidate data to template: Name, Overall Score, Categorization, Quality Grade, and Justification Summary
- [x] T015 [US1] Create HTML table structure in scoring_results.html with all required fields
- [x] T016 [US1] Implement responsive table with Tailwind CSS classes in scoring_results.html
- [x] T017 [US1] Add AI Justification Summary with expand/collapse functionality in scoring_results.html and reporting.js

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Sort Candidates (Priority: P2)

**Goal**: As a Hiring Manager, I want the candidate report to be sortable by Overall Score so I can quickly see the highest-ranked candidates first.

**Independent Test**: Can be tested by clicking sort controls and verifying that the candidate list reorders appropriately.

### Implementation for User Story 2

- [x] T018 [P] [US2] Implement query parameter parsing for sorting in CandidateReportView
- [x] T019 [US2] Add sorting logic by multiple columns in report_utils.py
- [x] T020 [US2] Implement toggle between ascending/descending in report_utils.py
- [x] T021 [US2] Add column header click handlers in scoring_results.html and reporting.js
- [x] T022 [US2] Update URL with sort parameters when clicking headers
- [x] T023 [US2] Add visual indicators for sort direction in scoring_results.html
- [x] T024 [US2] Optimize sorting performance to meet 1-second response time requirement (SC-005)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Filter Candidates (Priority: P3)

**Goal**: As a Hiring Manager, I want to apply a filter to view only candidates whose Overall Score is above a user-defined threshold so I can focus on top-tier candidates.

**Independent Test**: Can be tested by applying filters and verifying that only candidates meeting the threshold are displayed.

### Implementation for User Story 3

- [x] T025 [P] [US3] Implement score threshold query parameter parsing in CandidateReportView
- [x] T026 [US3] Add in-memory filtering logic in report_utils.py
- [x] T027 [US3] Create filter input UI in scoring_results.html
- [x] T028 [US3] Add filter button and event handlers in reporting.js
- [x] T029 [US3] Update URL with filter parameters
- [x] T030 [US3] Handle case when no candidates meet filter criteria (empty state)
- [x] T031 [US3] Optimize filtering performance to meet 2-second response time requirement with up to 500 candidates (SC-002)

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Shortlist Candidates (Priority: P2)

**Goal**: As a Hiring Manager, I want a simple button to shortlist or mark a candidate for interview directly from the report view so I can quickly identify promising candidates without navigating away.

**Independent Test**: Can be tested by clicking shortlist buttons and verifying the candidate status updates appropriately.

### Implementation for User Story 4

- [x] T032 [P] [US4] Create shortlist toggle endpoint in jobs/views.py
- [x] T033 [US4] Add POST endpoint for /api/candidates/<id>/toggle-shortlist/ in jobs/urls.py
- [x] T034 [US4] Implement logic to toggle is_shortlisted status in views.py
- [x] T035 [US4] Add shortlist/unshortlist buttons to each candidate row in scoring_results.html
- [x] T036 [US4] Implement AJAX request handling in reporting.js
- [x] T037 [US4] Update UI to reflect shortlist status without page refresh
- [x] T038 [US4] Preserve current sorting and filtering when toggling shortlist (FR-009)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T039 [P] Documentation updates in docs/
- [x] T040 Code cleanup and refactoring
- [x] T041 Performance optimization across all stories (ensure page loads under 5 seconds with 500 candidates)
- [x] T042 [P] Unit tests for report_utils.py functions
- [x] T043 Security hardening (ensure proper authentication)
- [x] T044 Run quickstart.md validation
- [x] T045 Handle edge cases: empty lists, simultaneous filter/sort operations, long AI summaries
- [x] T046 Verify all functional requirements (FR-001 through FR-014) are met

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all components for User Story 1 together:
Task: "Create CandidateReportView class-based view in jobs/views.py"
Task: "Implement GET endpoint for /scoring_results/ in jobs/urls.py and views.py"
Task: "Create HTML table structure in scoring_results.html with all required fields"
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
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
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