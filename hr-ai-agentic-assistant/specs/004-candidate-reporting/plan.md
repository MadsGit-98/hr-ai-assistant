# Implementation Plan: Candidate Reporting and Shortlisting

**Branch**: `004-candidate-reporting` | **Date**: Tuesday, November 18, 2025 | **Spec**: [link to spec.md](./spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of the sortable and filterable candidate reporting system with shortlisting functionality. This includes updating the Applicant model to support shortlisting, creating a dedicated Django Class-Based View for the candidate report, implementing server-side filtering and sorting logic in a utility module, and building a responsive UI with expandable AI justification summaries and shortlist toggle buttons.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django (latest stable), LangGraph, Ollama API client, Tailwind CSS
**Storage**: SQLite3 (primary), file storage for resumes
**Testing**: Python unittest, Selenium for E2E testing
**Target Platform**: Web server (Linux/Windows/Mac), browser-based UI
**Project Type**: Web application (Django MTV pattern)
**Performance Goals**: Page loads under 5 seconds for up to 500 candidates, responsive UI with mobile support
**Constraints**: 90% test coverage minimum, PEP 8 compliance, secure PII handling
**Scale/Scope**: Single HR assistant application with focus on 3 core flows (Upload, Process, Report)

## Constitution Check

### GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.

- [X] Web Framework is Django (latest stable version) - Confirmed
- [X] Local LLM Hosting uses Ollama - Confirmed
- [X] AI Agent Orchestration uses LangGraph - Confirmed
- [X] Primary Data Store is SQLite3 - Confirmed
- [X] Architecture follows Django MTV pattern - Confirmed
- [X] Service modules are located in hr_assistant/services - Confirmed
- [X] UI is simple and minimal - Confirmed
- [X] Design is fully responsive with Tailwind CSS - Confirmed
- [X] Code adheres to PEP 8 - Will ensure during implementation
- [X] Unit tests achieve 90% coverage - Confirmed requirement
- [X] Security best practices for PII - Will ensure during implementation

All gates passed.

## Project Structure

### Documentation (this feature)

```text
specs/004-candidate-reporting/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
hr_assistant/
├── services/            # All service modules MUST be located here
│   └── report_utils.py  # Contains report filtering, sorting logic
├── urls.py
└── settings.py

jobs/                    # Main application app containing models, views, etc.
├── models.py            # Contains Applicant and JobListing models (updated with is_shortlisted field)
├── views.py             # Contains Django views including CandidateReportView
├── urls.py
└── apps.py

templates/
└── scoring_results.html # Updated template with reporting features

static/
├── css/
│   └── tailwind.css     # Tailwind styles
└── js/
    └── reporting.js     # JavaScript for client-side interactions

tests/
├── unit/
│   └── test_candidate_reporting.py  # Unit tests for reporting logic
├── integration/
│   └── test_candidate_report_view.py  # Integration tests
└── contract/
    └── test_api_contracts.py  # API contract tests
```

**Structure Decision**: Django project with services subdirectory. The models and views are contained in the jobs app as per the existing application structure, with services in the hr_assistant directory following the constitution's mandate. The implementation will add a boolean field to the Applicant model in models.py, create/update views in views.py for the candidate report, and place all reporting logic in the services directory as per the constitution.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | (none) | (none) |

## Phase 0: Outline & Research

### Research Findings

#### Decision: Sorting Implementation Approach
**Rationale**: Given SQLite limitations and the need to handle up to 500 candidates, in-memory sorting will be implemented using Python after initial data retrieval. This approach provides full control over custom sorting logic while staying within SQLite constraints.
**Alternatives considered**: Database-level sorting with multiple queries, client-side JavaScript sorting, pagination with server-side sorting.

#### Decision: Filtering Implementation Approach
**Rationale**: Score threshold filtering will be implemented using query parameters from the request. The filtering will be applied in-memory on the server side after data retrieval to work within SQLite constraints while maintaining responsive UI.
**Alternatives considered**: Database-level filtering with dynamic queries, client-side filtering, separate API endpoint for filtering.

#### Decision: UI Expand/Collapse for AI Justification Summary
**Rationale**: A Tailwind CSS implementation with JavaScript will handle the expand/collapse functionality for long AI Justification Summaries, ensuring they don't clutter the table while remaining accessible.
**Alternatives considered**: Tooltip display, modal popup, truncation without expand option.

## Phase 1: Design & Contracts

### Data Model Updates

The following updates will be made to the database schema:

1. **Applicant Model** (in `jobs/models.py`):
   - Add `is_shortlisted` BooleanField (default=False) to track shortlist status

2. **JobListing Model** (in `jobs/models.py`):
   - No changes needed - already exists and maintains relationship with applicants for filtering candidates by active job

### API Contract

1. **Candidate Report View** (`/scoring_results/` or `/jobs/<job_id>/candidates/`):
   - GET: Returns the candidate report page with all candidates for a job
   - Query Parameters:
     - `sort_by`: Column to sort by (default: 'overall_score')
     - `sort_order`: Ascending/descending (default: 'desc')
     - `score_threshold`: Minimum score threshold for filtering (default: 0)

2. **Shortlist Toggle Endpoint** (`/api/candidates/<id>/toggle-shortlist/`):
   - POST: Toggles the is_shortlisted status of a candidate
   - Returns: Updated is_shortlisted status

### Quickstart for New Developers

1. **Setup**:
   ```bash
   # Navigate to project root
   cd hr-ai-assistant

   # Install dependencies
   pip install -r requirements.txt

   # Run migrations to update Applicant model in jobs app
   python manage.py makemigrations jobs
   python manage.py migrate
   ```

2. **Running the Application**:
   ```bash
   # Start Ollama server
   ollama serve
   
   # In a separate terminal, start the Django application
   python manage.py runserver
   ```

3. **Accessing the Feature**:
   - Navigate to `/scoring_results/` or `/jobs/<job_id>/candidates/` to view the candidate report
   - Use the filter input and sort controls to manipulate the candidate list
   - Click "Shortlist" buttons to mark candidates for interview

## Implementation Strategy

### 1. Architectural Strategy: Reporting Components

#### Model Update (SQLite3):
The Applicant model in `jobs/models.py` will be modified to include an `is_shortlisted` boolean field to track shortlist status. This field will be used to persistently store whether a candidate has been marked for an interview.

#### View Implementation:
A Django Class-Based View (CBV) `CandidateReportView` will be created to retrieve all analyzed candidates associated with the active job and render the main report page. This view will handle query parameters for sorting and filtering.

#### Helper Utilities:
A dedicated Python utility module (`hr_assistant/services/report_utils.py`) will handle the complex query execution and in-memory data processing (sorting and filtering), which is required due to SQLite constraints.

### 2. Reporting Logic and Data Processing

#### Initial Data Retrieval:
The view will execute a database query to efficiently fetch all Applicant records associated with the active JobListing where AI analysis results are present (overall_score is not null) up to the maximum of 500 candidates.

#### Sorting Implementation:
Sorting by Overall Score will be achieved in-memory using Python after data retrieval. The default behavior will be descending order, with the ability to toggle to ascending.

#### Filtering Implementation:
Score threshold filtering will be implemented using query parameters from the request. The filter will be applied to the dataset after retrieval and before rendering, using in-memory processing.

#### Shortlist Action:
A lightweight approach using a dedicated Django View will handle AJAX POST requests to toggle the `is_shortlisted` status on a single applicant record.

### 3. Frontend and User Experience (UX)

#### Responsive Table Design:
The report table will use responsive HTML/CSS with Tailwind CSS to ensure usability on mobile devices. Information may be stacked at smaller breakpoints for better readability.

#### Filter Input:
A simple number input field and "Filter" button will update the report URL query parameters to apply the user-defined score threshold.

#### Sorting Interaction:
Clicking the table header (for the Score column) will update the URL query parameters to switch between ascending/descending sort states.

#### Action Button:
The "Shortlist/Mark for Interview" button will be included within each row, using minimal JavaScript to send AJAX requests to toggle the `is_shortlisted` status.

### 4. Testing and Quality Assurance

#### Unit Testing Plan:
Unittest test cases will achieve 90% coverage for:
- Report utility functions to confirm correct in-memory sorting and threshold filtering logic
- View logic to ensure it correctly handles URL query parameters for sorting and filtering
- Logic for toggling the `is_shortlisted` status

#### E2E Testing Plan:
Selenium test cases will cover:
- Navigating to the report and verifying that candidates are displayed sorted by default score
- Interacting with the filter input (e.g., filtering for 85+) and verifying the displayed list shrinks correctly
- Clicking the Shortlist button and verifying the `is_shortlisted` status visually updates on the page