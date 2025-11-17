# Research Notes: AI Resume Scoring Engine

**Created**: 2025-11-11
**Feature**: 002-ai-resume-scoring

## Summary

This research document outlines the key decisions and findings for implementing the AI Resume Scoring Engine. It covers architecture patterns, technology choices, and implementation strategies for creating an efficient scoring system using LangGraph and Ollama.

## Decision: LangGraph Map-Reduce Architecture for Bulk Resume Processing
**Rationale**: The system requires processing multiple resumes efficiently, making LangGraph's Map-Reduce pattern ideal for parallel execution of individual resume analyses while maintaining orchestration control. This approach allows us to process many resumes simultaneously while keeping the complexity of state management handled by LangGraph.

**Alternatives considered**:
- Sequential processing: Would be too slow for bulk operations
- Manual threading: Would increase complexity and error potential
- External task queues (Celery): Would add unnecessary dependencies against project constraints

## Decision: Ollama Integration via Service Layer
**Rationale**: Following the constitution's mandate to encapsulate all Ollama interactions within services, we chose to implement a dedicated service layer in `hr_assistant/services/`. This ensures separation of concerns and makes testing easier with mockable interfaces.

**Alternatives considered**:
- Direct API calls from views: Would violate constitution requirements
- Model-level integration: Would tightly couple data and AI logic
- Middleware integration: Would be unnecessarily complex for this use case

## Decision: AIAnalysisResponse Data Contract
**Rationale**: A standardized data contract ensures consistency between the AI processing results and the database storage. Using a Python data class (or Pydantic model) ensures type safety and validation.

**Fields defined**:
- `overall_score` (int 0-100)
- `quality_grade` (str: A, B, C, D, F)
- `categorization` (str: Senior, Mid-Level, Junior, Mismatched)
- `justification_summary` (str)

**Alternatives considered**:
- Dictionary-based approach: Less type-safe and harder to validate
- Multiple separate fields: More complex to manage as a unit
- Custom class without validation: Risk of inconsistent data formats

## Decision: Asynchronous Processing with 202 Response Pattern
**Rationale**: To maintain responsive UI while processing potentially many resumes, the system returns an immediate 202 Accepted response and processes in the background. This aligns with the requirement for responsive UI and handles the potential long-running nature of bulk processing.

**Alternatives considered**:
- Synchronous processing: Would block the UI for potentially long periods
- WebSocket updates: Would add complexity not required by core requirements
- Polling endpoint: Would still require background processing approach

## Decision: Supervisor/Worker Graph Architecture
**Rationale**: The two-tiered graph approach provides clear separation of orchestration and execution concerns. The Supervisor manages the batch operation and final persistence, while individual Workers handle single-resume analysis, allowing for parallel execution without complex state management.

**Alternatives considered**:
- Single monolithic graph: Would be harder to maintain and debug
- Direct database operations in workers: Would violate separation of concerns
- External orchestration: Would add unnecessary complexity

## Best Practices for LangGraph Implementation
- Use state management for passing data between nodes
- Implement error handling at each node level
- Use LangGraph's built-in checkpointing for resilience
- Separate business logic from orchestration logic