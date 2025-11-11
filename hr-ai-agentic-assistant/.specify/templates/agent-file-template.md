# AI HR Assistant - System Context

## Core Principles

### Core Technical Stack Mandate
Web Framework MUST be Django (latest stable version). Local LLM Hosting MUST ONLY use Ollama. AI Agent Orchestration MUST use LangGraph for complex workflow logic. Primary Data Store MUST be SQLite3.

### Architectural Integrity
Strictly follow the Django Model-Template-View (MTV) design pattern. Architecture MUST prioritize minimal dependencies, leveraging core Python and Django features first. Abstraction Mandate: All interaction with Ollama and LangGraph MUST be encapsulated within dedicated service modules within the hr_assistant/services subdirectory. Views MUST NOT manage LLM state directly. All service modules MUST be located in the hr_assistant/services directory.

### Frontend/UX Simplicity
User Interface (UX) MUST be extremely simple and minimal, focusing on the three core flows: Upload, Process, and Report. Design MUST be fully responsive and utilize a mobile-first approach with fluid layouts. Tailwind css must be used for styling.

### Quality & Testing Standards
All Python code MUST adhere to PEP 8. Use standard Django conventions for naming (e.g., Singular PascalCase for Models). Unit Test Mandate: All new features MUST achieve a minimum of 90% line coverage using Python's native unittest module. End-to-End and Integration Testing MUST use Selenium.

### Security & Compliance
The system MUST implement best practices for secure file storage and restricted internal access due to the sensitive nature of PII contained in resumes.

## Current Feature Context

### AI Resume Scoring Engine
Feature: Implementation of an AI-powered resume scoring system that processes uploaded resumes against job listings using LangGraph and Ollama.

#### Architecture
- Service Layer Integration: All AI and Ollama interactions encapsulated in hr_assistant/services/
- Supervisor/Worker Graph Architecture: Two-tiered LangGraph structure for efficient bulk processing
- Data Contract: AIAnalysisResponse with overall_score, quality_grade, categorization, and justification_summary
- Asynchronous Processing: 202 response pattern for responsive UI during bulk operations

#### Technical Implementation
- Map-Reduce Pattern: Using LangGraph's native primitives for parallel resume analysis
- State Management: Supervisor graph state includes applicant_id_list, job_criteria, results, and status
- Worker Nodes: Sequential execution of Data Retrieval, Scoring & Grading, Categorization, and Justification
- Bulk Persistence: Efficient Django ORM bulk update after processing completion

#### Data Model Extensions
- Applicant model extended with scoring fields: overall_score, quality_grade, categorization, justification_summary
- Processing status tracking: pending, processing, completed, error
- Job-specific scoring: Each score is relative to a specific job listing

#### API Endpoints
- POST /api/job-listings/{job_id}/score-resumes/ - Initiate bulk scoring
- GET /api/job-listings/{job_id}/scoring-status/ - Check processing status
- GET /api/job-listings/{job_id}/scored-applicants/ - Retrieve scored results