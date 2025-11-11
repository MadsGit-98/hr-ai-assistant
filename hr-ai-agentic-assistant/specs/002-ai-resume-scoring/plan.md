# Implementation Plan: AI Resume Scoring Engine

**Branch**: `002-ai-resume-scoring` | **Date**: 2025-11-11 | **Spec**: [link to spec]
**Input**: Feature specification from `/specs/002-ai-resume-scoring/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of an AI-powered resume scoring engine that processes uploaded resumes against active job listings. The system uses LangGraph orchestration with Ollama LLM to generate three distinct metrics for each resume: Overall Score (0-100), Categorization (Senior/Mid-Level/Junior/Mismatched), and Quality Grade (A, B, C, D, F). The solution follows a Map-Reduce pattern in LangGraph for efficient bulk processing of resumes with a Supervisor Main Graph for orchestration and Worker Sub-Graphs for parallel execution of single-resume analysis.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django (latest stable), LangGraph, Ollama API client, Tailwind CSS
**Storage**: SQLite3 (primary), file storage for resumes
**Testing**: Python unittest, Selenium for E2E testing
**Target Platform**: Web server (Linux/Windows/Mac), browser-based UI
**Project Type**: Web application (Django MTV pattern)
**Performance Goals**: Resume processing under 30 seconds per resume, responsive UI with mobile support
**Constraints**: 90% test coverage minimum, PEP 8 compliance, secure PII handling
**Scale/Scope**: Single HR assistant application with focus on 3 core flows (Upload, Process, Report)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Django Framework: Using Django as required
- ✅ Ollama LLM Hosting: System will use Ollama as required
- ✅ LangGraph Orchestration: System will use LangGraph for complex workflow logic as required
- ✅ SQLite3 Data Store: Using SQLite3 as primary data store as required
- ✅ Service Encapsulation: All interaction with Ollama and LangGraph encapsulated within hr_assistant/services as required
- ✅ MTV Pattern: Following Django MTV design pattern as required
- ✅ Minimal Dependencies: Leveraging core Python/Django first as required
- ✅ Services in Subdirectory: All service modules in hr_assistant/services directory as required
- ✅ Views Don't Manage LLM State: LLM state managed in services, not views as required
- ✅ PEP 8 Compliance: Code will adhere to PEP 8 as required
- ✅ 90% Test Coverage: Unit tests using Python unittest to achieve 90% coverage as required
- ✅ Secure PII Handling: Basic protection with HTTPS and database storage per clarifications

## Project Structure

### Documentation (this feature)

```text
specs/002-ai-resume-scoring/
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
├── models/
│   ├── __init__.py
│   └── applicant.py            # Extended with scoring fields
├── services/
│   ├── __init__.py
│   ├── ai_analysis.py          # Main AI analysis service with LangGraph orchestration
│   └── resume_scoring.py       # Resume scoring interface
├── views/
│   ├── __init__.py
│   └── scoring_views.py        # Handles UI interactions for resume scoring
├── urls.py
└── settings.py

tests/
├── unit/
│   ├── test_ai_analysis.py     # Unit tests for AI analysis service
│   ├── test_resume_scoring.py  # Unit tests for scoring service
│   └── test_contracts.py       # Unit tests for data contracts
├── integration/
│   └── test_scoring_pipeline.py # Integration tests for end-to-end scoring
└── contract/
    └── test_api_contracts.py    # API contract tests

media/
└── resumes/                     # Directory for uploaded resume files
```

**Structure Decision**: Using Django project with services subdirectory structure. All AI and Ollama interactions are encapsulated in the hr_assistant/services directory as mandated by the constitution. The models, views, and other components follow Django MTV pattern with appropriate separation of concerns.

## Phase 0: Research & Analysis

### 1. Architectural Foundation and Contracts

#### Service Layer Integration
The system implements a dedicated Python module `hr_assistant/services` as the single point of entry for the AI Engine, achieving maximum decoupling from Django views and models.

#### Contract Definition (Data Schemas)
The AIAnalysisResponse data contract is defined using a Python data class with required fields:
- `overall_score` (int 0-100)
- `quality_grade` (str: A, B, C, D, F)
- `categorization` (str: Senior, Mid-Level, Junior, Mismatched)
- `justification_summary` (str)

#### Model Field Updates
The Applicant model will be extended with fields matching the AIAnalysisResponse contract to store results:
- `overall_score` (IntegerField)
- `quality_grade` (CharField)
- `categorization` (CharField)
- `justification_summary` (TextField)
- `analysis_date` (DateTimeField)
- `processing_status` (CharField for tracking: 'pending', 'processing', 'completed', 'error')

### 2. LangGraph Engine Construction (Map-Reduce Primitives)

#### Graph Structure
The system implements a two-tiered graph structure:
- Supervisor Main Graph for orchestration
- Worker Sub-Graph for parallel execution of single-resume analysis

#### State Definition
The Supervisor Graph state includes:
- `applicant_id_list` (list of applicant IDs to process)
- `job_criteria` (requirements to compare against)
- `results` (accumulated results from worker graphs)
- `status` (current processing state)

#### Worker Sub-Graph (Map Primitive)
The worker sub-graph handles analysis of a single resume with the following sequential nodes:

1. **Data Retrieval Node**: Retrieves pre-parsed raw resume text from Applicant model instance in SQLite3 database, placing it and job_criteria into worker's state for LLM calls.

2. **Scoring & Grading Node**: Calls Ollama to calculate the overall_score and quality_grade simultaneously based on job criteria.

3. **Categorization Node**: Calls Ollama to assign the categorization (Senior/Mid-Level/Junior/Mismatched).

4. **Justification Node**: Calls Ollama to generate the concise justification_summary.

5. **Worker Output**: Returns validated AIAnalysisResponse contract.

#### Supervisor Main Graph (Reduce Primitive)
The supervisor graph manages the batch operation:

1. **Batch Iteration Setup (Map/Send)**: Initializes state to trigger LangGraph's native Map primitive, using Send mechanism to invoke the Worker Sub-Graph for each individual applicant ID from input list.

2. **Result Merge**: LangGraph's built-in state management automatically merges output from all parallel Worker executions into a unified list once all workers complete.

3. **Final Edge**: Defines the Bulk Persistence Node for database updates.

### 3. Persistence and Asynchronous Handling

#### Bulk Persistence Node
A specialized LangGraph node responsible for:
- Taking the list of final, validated results from the Supervisor Graph
- Updating corresponding Applicant records in SQLite3 database via efficient Django ORM bulk update operation

#### Asynchronous Trigger
Implementation of lightweight asynchronous solution using Django's background task capabilities to execute the Supervisor Graph process after resume ingestion. The Django View returns immediate 202 Accepted response while task runs in the background.

### 4. Testing and Quality Assurance

#### Unit Testing Plan (unittest)
Test cases to achieve 90% coverage for:
- AIAnalysisResponse contract definition (schema validation)
- Bulk Persistence Node (ensuring correct data saving)
- Service Layer (hr_assistant/services) to test the logic of the Graph process
- Mocking the Ollama response to test business logic without external API calls

#### Integration Testing
High-level integration test that uses mocked Ollama response to ensure full data pipeline: Upload -> Trigger -> Supervisor Graph -> Worker Graphs -> Bulk Persistence -> Database Update.

## Phase 1: Design Artifacts

### 1. Data Model (data-model.md)
- Define Applicant model extensions with scoring fields
- Specify database constraints and indexes for efficient querying
- Detail state transitions (pending -> processing -> completed/error)

### 2. API Contracts (contracts/)
- Define endpoints for initiating bulk scoring
- Specify data contracts for the AIAnalysisResponse
- Document error handling and status responses

### 3. Implementation Quickstart (quickstart.md)
- Guide for setting up Ollama with required models
- Steps for configuring the LangGraph workflow
- Testing and validation procedures

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (None) | (None) | (None) |

All constitution requirements have been verified and incorporated into the design.