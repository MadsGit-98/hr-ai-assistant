# AI HR Assistant Constitution

<!-- 
Sync Impact Report:
- Version change: N/A → 1.0.0
- Added sections: All principles (new constitution)
- Templates requiring updates: .specify/templates/plan-template.md ✅, .specify/templates/spec-template.md ✅, .specify/templates/tasks-template.md ✅
- Follow-up TODOs: None
-->

## Core Principles

### Core Technical Stack Mandate
Web Framework MUST be Django (latest stable version). Local LLM Hosting MUST ONLY use Ollama. AI Agent Orchestration MUST use LangGraph for complex workflow logic. Primary Data Store MUST be SQLite3.

### Architectural Integrity
Strictly follow the Django Model-Template-View (MTV) design pattern. Architecture MUST prioritize minimal dependencies, leveraging core Python and Django features first. Abstraction Mandate: All interaction with Ollama and LangGraph MUST be encapsulated within a dedicated service module (e.g., hr_agent/services.py). Views MUST NOT manage LLM state directly.

### Frontend/UX Simplicity
User Interface (UX) MUST be extremely simple and minimal, focusing on the three core flows: Upload, Process, and Report. Design MUST be fully responsive and utilize a mobile-first approach with fluid layouts. Tailwind css must be used for styling.

### Quality & Testing Standards
All Python code MUST adhere to PEP 8. Use standard Django conventions for naming (e.g., Singular PascalCase for Models). Unit Test Mandate: All new features MUST achieve a minimum of 90% line coverage using Python's native unittest module. End-to-End and Integration Testing MUST use Selenium.

### Security & Compliance
The system MUST implement best practices for secure file storage and restricted internal access due to the sensitive nature of PII contained in resumes.

## Development Workflow
All development must follow the defined architectural patterns, with services abstracting external dependencies and strict adherence to Django conventions.

## Quality Gates
Code reviews must verify compliance with all constitution principles. All tests must pass with minimum 90% coverage before merging. Security practices must be validated for any PII handling code.

## Governance
All PRs/reviews must verify compliance with all constitution principles. Any deviation must be documented with justification and approved by the technical lead. The constitution supersedes all other practices.

**Version**: 1.0.0 | **Ratified**: 2025-11-06 | **Last Amended**: 2025-11-06
