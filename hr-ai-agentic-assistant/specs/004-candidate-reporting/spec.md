# Feature Specification: Candidate Reporting and Shortlisting

**Feature Branch**: `004-candidate-reporting`
**Created**: Tuesday, November 18, 2025
**Status**: Draft
**Input**: User description: "Final Shortlisting and Reporting Feature - We have an Hiring Manager user role. The specific User Story: As a Hiring Manager, I want to view a sortable and filterable Final Report of all analyzed candidates so I can quickly identify the best candidates to interview. Requirements: The report must be displayed in the scoring results page at \"scoring_results.html\" The report MUST display the following data for each candidate: Name, Overall Score, Categorization, Quality Grade, and AI Justification Summary for their score. The report MUST be sortable by Overall Score (default: descending). The manager MUST be able to apply a filter to view only candidates whose Overall Score is above a user-defined threshold (e.g., \"Show candidates scoring 85+\"). The manager MUST have a simple button to shortlist or mark a candidate for interview directly from the report view."

## Clarifications

### Session 2025-11-18

- Q: What are the possible values for candidate "Categorization" and "Quality Grade", and how are they determined? → A: Categorization values: Senior, Mid-Level, Junior, Mismatched. Quality Grade values: A, B, C, D, F. Determined by AI scoring process.
- Q: Is 500 candidates the maximum supported by the system, or just a performance benchmark? → A: Hard limit - System will not process more than 500 candidates.
- Q: What is the maximum length for the AI Justification Summary that needs to be accommodated in the UI? → A: Variable with expand/collapse - Show truncated version with option to expand
- Q: What is the valid range for candidate scores and score thresholds? → A: 0-100 range - Scores and thresholds use a 0-100 percentage-based range
- Q: How is the shortlist status persisted and are there any limits to the number of candidates that can be shortlisted? → A: Persistent in database with no limits - Shortlist status is saved permanently with no upper limit

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Candidate Reports (Priority: P1)

As a Hiring Manager, I want to view a sortable and filterable Final Report of all analyzed candidates so I can quickly identify the best candidates to interview. The report must display Name, Overall Score, Categorization, Quality Grade, and AI Justification Summary.

**Why this priority**: This is the core functionality that enables hiring managers to efficiently review candidate scores and make informed decisions about who to interview.

**Independent Test**: Can be fully tested by loading the scoring results page and verifying that candidate data is displayed in a table format with all required fields visible.

**Acceptance Scenarios**:

1. **Given** a user is on the scoring results page, **When** they view the candidate report, **Then** they see a table with Name, Overall Score, Categorization, Quality Grade, and AI Justification Summary for each candidate
2. **Given** a user is on the scoring results page, **When** the page loads, **Then** the candidates are sorted by Overall Score in descending order by default

---

### User Story 2 - Sort Candidates (Priority: P2)

As a Hiring Manager, I want the candidate report to be sortable by Overall Score so I can quickly see the highest-ranked candidates first.

**Why this priority**: Sorting functionality allows managers to customize how they view candidates to match their needs.

**Independent Test**: Can be tested by clicking sort controls and verifying that the candidate list reorders appropriately.

**Acceptance Scenarios**:

1. **Given** candidate data is displayed in a table, **When** user clicks the Overall Score column header, **Then** the table reorders by that column in ascending order
2. **Given** the table is sorted in ascending order by Overall Score, **When** user clicks the Overall Score column header again, **Then** the table reverses to descending order

---

### User Story 3 - Filter Candidates (Priority: P3)

As a Hiring Manager, I want to apply a filter to view only candidates whose Overall Score is above a user-defined threshold so I can focus on top-tier candidates.

**Why this priority**: Filtering helps hiring managers quickly narrow down large candidate pools to focus on the most qualified applicants.

**Independent Test**: Can be tested by applying filters and verifying that only candidates meeting the threshold are displayed.

**Acceptance Scenarios**:

1. **Given** multiple candidates with different scores are displayed, **When** user sets a score threshold (e.g., 85), **Then** only candidates with scores at or above the threshold remain in the table
2. **Given** a score threshold is set, **When** user updates the threshold value, **Then** the table updates to show only candidates meeting the new threshold

---

### User Story 4 - Shortlist Candidates (Priority: P2)

As a Hiring Manager, I want a simple button to shortlist or mark a candidate for interview directly from the report view so I can quickly identify promising candidates without navigating away.

**Why this priority**: Quick action buttons improve the efficiency of the hiring process by enabling rapid decision-making.

**Independent Test**: Can be tested by clicking shortlist buttons and verifying the candidate status updates appropriately.

**Acceptance Scenarios**:

1. **Given** candidate data is displayed in the report, **When** user clicks the "Shortlist" button for a candidate, **Then** the candidate's status is updated to indicate they've been shortlisted
2. **Given** a candidate has been shortlisted, **When** user clicks the "Unshortlist" button, **Then** the candidate's status is reverted to normal

---

### Edge Cases

- What happens when no candidates meet the filter criteria?
- How does the system handle empty candidate lists?
- What if the AI Justification Summary is too long to display properly in the table?
- How does the system handle simultaneous filter and sort operations?
- What happens if a candidate's score is updated while the manager is viewing the report?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a table of all analyzed candidates on the scoring_results.html page
- **FR-002**: System MUST display the following data for each candidate: Name, Overall Score, Categorization, Quality Grade, and AI Justification Summary
- **FR-003**: System MUST sort candidates by Overall Score in descending order by default when the page loads
- **FR-004**: System MUST allow users to sort the candidate table by clicking on column headers
- **FR-005**: System MUST provide a filter interface that allows users to set a minimum Overall Score threshold
- **FR-006**: System MUST update the displayed candidate list based on the applied score filter
- **FR-007**: System MUST provide a "Shortlist" button for each candidate in the report view
- **FR-008**: System MUST allow users to mark candidates for interview directly from the report view
- **FR-009**: System MUST preserve user's current sorting and filtering when marking candidates for interview
- **FR-010**: System MUST update the candidate's status visually after being shortlisted
- **FR-011**: System MUST enforce a maximum limit of 500 candidates that can be processed and displayed
- **FR-012**: System MUST display truncated AI Justification Summary with expand/collapse functionality to show full content
- **FR-013**: System MUST support candidate scores and score thresholds in the range of 0-100
- **FR-014**: System MUST persist shortlist status in the database with no upper limit on number of shortlisted candidates

### Key Entities *(include if feature involves data)*

- **Candidate**: Represents a job applicant with attributes including Name, Overall Score, Categorization (values: Senior, Mid-Level, Junior, Mismatched), Quality Grade (values: A, B, C, D, F), AI Justification Summary, and Shortlist status
- **Score Threshold Filter**: Represents the user-defined minimum Overall Score value to filter candidates
- **Sorting Parameters**: Represents the current sorting column and direction applied to the candidate list

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Hiring managers can identify top candidates within 30 seconds of loading the scoring results page
- **SC-002**: Users can apply filters and see updated results within 2 seconds for datasets up to the maximum of 500 candidates
- **SC-003**: 95% of hiring managers can successfully shortlist candidates without requiring assistance
- **SC-004**: The candidate report page loads completely within 5 seconds for datasets up to the maximum of 500 candidates
- **SC-005**: Users can sort the candidate list by any column with a response time under 1 second