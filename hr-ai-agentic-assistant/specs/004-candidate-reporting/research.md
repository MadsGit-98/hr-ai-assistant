# Research Findings: Candidate Reporting and Shortlisting

**Feature**: 004-candidate-reporting
**Date**: Tuesday, November 18, 2025

## Research Summary

This research document captures the key decisions, rationales, and alternatives considered for implementing the candidate reporting and shortlisting feature.

## Decision: Sorting Implementation Approach

**What was chosen**: In-memory sorting using Python after initial data retrieval
**Rationale**: Given SQLite limitations and the need to handle up to 500 candidates, in-memory sorting provides full control over custom sorting logic while staying within SQLite constraints. This approach allows for complex sorting logic that might be difficult to implement directly with SQL, particularly when considering multiple criteria or custom sorting algorithms.
**Alternatives considered**:
- Database-level sorting with multiple queries: Limited by SQLite's capabilities and would require complex queries
- Client-side JavaScript sorting: Would require all data to be sent to the client, which could be slow for up to 500 candidates
- Pagination with server-side sorting: Would complicate the UI and doesn't align with the requirement to display all candidates at once

## Decision: Filtering Implementation Approach

**What was chosen**: Score threshold filtering with query parameters from the request, applied in-memory on the server side
**Rationale**: This approach provides flexibility in filtering logic while maintaining performance. Applying the filter in-memory after data retrieval allows for complex filter criteria without requiring multiple database queries.
**Alternatives considered**:
- Database-level filtering with dynamic queries: Could work, but might be less flexible for complex filtering criteria
- Client-side filtering: Would require all data to be sent to the client, potentially causing performance issues
- Separate API endpoint for filtering: Would over-complicate the architecture and increase network requests

## Decision: UI Expand/Collapse for AI Justification Summary

**What was chosen**: Tailwind CSS implementation with JavaScript for expand/collapse functionality
**Rationale**: This approach provides a clean, responsive UI that works well with the project's Tailwind CSS requirement. It allows long AI Justification Summaries to be accessible without cluttering the table.
**Alternatives considered**:
- Tooltip display: Would limit the amount of text that could be viewed at once
- Modal popup: Would interrupt the user's workflow
- Truncation without expand option: Would hide important information from the user

## Decision: Data Model Changes

**What was chosen**: Add boolean `is_shortlisted` field to existing Applicant model
**Rationale**: This maintains data integrity by keeping all relevant candidate information in one place. The boolean field requires minimal storage space and provides clear, fast querying capabilities.
**Alternatives considered**:
- Separate shortlist table with relationships: Would require joins for queries, potentially slowing performance
- JSON field storing multiple status types: Would be harder to query and maintain
- Text field for status instead of boolean: Would be overkill for a simple yes/no status

## Decision: View Architecture

**What was chosen**: Django Class-Based View (CBV) for the candidate report page
**Rationale**: CBVs provide a clean, reusable structure that follows Django best practices. They are easier to maintain and extend than function-based views, and they naturally support the various HTTP methods needed for this feature.
**Alternatives considered**:
- Function-Based View (FBV): Would work but doesn't provide the same level of organization and reusability
- Generic CBVs with multiple mixins: Might be overkill for this specific use case
- API View with React frontend: Would violate the project's requirement for simple UX with server-rendered templates

## Decision: AJAX Implementation for Shortlist Toggle

**What was chosen**: Lightweight AJAX POST request to toggle shortlist status
**Rationale**: Provides a responsive user experience without requiring a full page refresh. This maintains the user's place in the list and preserves current sorting/filtering settings.
**Alternatives considered**:
- Full page POST and redirect: Would lose the current sort/filter state and be slower
- WebSockets for real-time updates: Would be over-engineering for this simple use case
- Separate API endpoints for each action: Would increase complexity without significant benefit