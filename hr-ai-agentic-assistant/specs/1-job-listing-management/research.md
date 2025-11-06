# Research: Job Listing Management

**Feature**: Job Listing Management
**Date**: 2025-11-06
**Status**: Complete

## Decision: Data Storage for Required Skills

**Rationale**: For storing a structured list of required skills in SQLite3, Django's JSONField is the most appropriate solution. It allows for structured storage of the skill list while maintaining the ability to query if needed in the future. For a proof-of-concept without authentication, this provides both the structure needed for the AI to process the skills list and the flexibility for future enhancements.

**Alternatives considered**:
- Django's CharField with delimiter-separated values (e.g., comma-separated): Simple but makes querying difficult
- Separate Skill model with many-to-many relationship: More complex but would be more appropriate for a production system
- Django's ArrayField: Would require PostgreSQL, not compatible with SQLite3 mandate

## Decision: Single Active Job Listing Validation

**Rationale**: Implementing the single active job listing constraint requires a custom model validation and potentially a database constraint. The recommended approach is to override the model's save method to deactivate other job listings when a new one is activated. This ensures only one listing can be active at a time while maintaining data integrity.

**Alternatives considered**:
- Database-level constraint: More complex to implement in SQLite3
- Application-level validation only: Could result in data inconsistency if multiple listings are activated outside the normal application flow

## Decision: Markdown Support in Detailed Description

**Rationale**: To support markdown in the detailed_description field while maintaining security, we'll use the `markdown` Python library combined with `bleach` for sanitization. This approach is consistent with the constitution's security requirements by preventing XSS while allowing rich text formatting.

**Alternatives considered**:
- Pure HTML field: High XSS risk
- Plain text only: Doesn't meet requirement for markdown support
- Third-party WYSIWYG editor: Would add unnecessary dependencies, violating the minimal dependency principle