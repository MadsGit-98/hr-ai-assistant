"""
LangGraph implementation for AI Resume Scoring Engine with Map-Reduce pattern
"""
from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
from langchain_ollama import ChatOllama
from .contracts import GraphState, AIAnalysisResponse
import os
import django
import logging

# Setup Django environment once at module level
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_assistant.settings')
django.setup()

# Import Django models after setting up Django
from jobs.models import Applicant

# Import logger for node-level logging
ai_logger = logging.getLogger('ai_processing')

# Initialize the Ollama model
llm = ChatOllama(
    model="llama2",  # Default model, can be configured
    temperature=0.1,
)

def data_retrieval_node(state: GraphState) -> GraphState:
    """
    Worker node: Retrieves pre-parsed raw resume text from Applicant model
    """
    current_idx = state.get("current_index", 0)
    error_count = state.get("error_count", 0)

    ai_logger.info(f"[Data Retrieval Node] Starting data retrieval for index {current_idx}")

    if current_idx < len(state.get("applicant_id_list", [])):
        applicant_id = state["applicant_id_list"][current_idx]
        ai_logger.info(f"[Data Retrieval Node] Retrieving data for applicant {applicant_id}")

        try:
            # Retrieve applicant and their resume text
            applicant = Applicant.objects.get(id=applicant_id)
            resume_text = applicant.parsed_resume_text or str(applicant.resume_file)  # Fallback to file path if parsed text not available

            # Update resume_texts in state
            resume_texts = state.get("resume_texts", {})
            resume_texts[applicant_id] = resume_text
            state["resume_texts"] = resume_texts

            ai_logger.info(f"[Data Retrieval Node] Successfully retrieved data for applicant {applicant_id}, resume length: {len(resume_text) if resume_text else 0}")

        except Exception as e:
            ai_logger.error(f"[Data Retrieval Node] Error retrieving data for applicant {applicant_id}: {str(e)}")
            error_count += 1

    state["current_index"] = current_idx + 1
    state["error_count"] = error_count

    ai_logger.info(f"[Data Retrieval Node] Completed, next index: {state['current_index']}, error count: {state['error_count']}")
    return state


def scoring_grading_node(state: GraphState) -> GraphState:
    """
    Worker node: Calls Ollama to calculate overall_score and quality_grade
    """
    current_idx = state.get("current_index", 0)
    applicant_id_list = state.get("applicant_id_list", [])

    ai_logger.info(f"[Scoring Grading Node] Starting scoring and grading for index {current_idx}")

    if current_idx <= len(applicant_id_list):
        current_idx = max(0, current_idx - 1)  # Adjust for the increment in previous node

        if current_idx < len(applicant_id_list):
            applicant_id = applicant_id_list[current_idx]
            state_resume_text = state["resume_texts"].get(applicant_id, "")
            state_job_requirements = state.get("job_requirements", "")

            ai_logger.info(f"[Scoring Grading Node] Processing applicant {applicant_id}, resume length: {len(state_resume_text)}, job requirements length: {len(state_job_requirements)}")

            # Prepare the prompt for scoring and grading
            scoring_prompt = """
            Analyze the following resume against these job requirements:

            Job Requirements: {job_requirements}

            Resume: {resume_text}

            Based on how well the resume matches the job requirements, provide:
            1. An overall score from 0-100 (where 100 is perfect match)
            2. A quality grade (A, B, C, D, or F)

            Respond in the following format:
            Overall Score: [number]
            Quality Grade: [letter]
            """

            try:
                prompt = scoring_prompt.format(job_requirements=state_job_requirements, resume_text=state_resume_text)
                ai_logger.info(f"[Scoring Grading Node] Sending request to LLM for applicant {applicant_id}")
                response = llm.invoke(prompt)
                response_text = response.content

                ai_logger.info(f"[Scoring Grading Node] LLM response received for applicant {applicant_id}: {response_text[:100]}...")

                # Parse the response to extract score and grade
                lines = response_text.split("\n")
                overall_score = 0
                quality_grade = "F"

                for line in lines:
                    if "Overall Score:" in line:
                        try:
                            overall_score = int(line.split(":")[1].strip())
                        except:
                            overall_score = 0
                    elif "Quality Grade:" in line:
                        quality_grade = line.split(":")[1].strip()

                ai_logger.info(f"[Scoring Grading Node] Parsed score: {overall_score}, grade: {quality_grade} for applicant {applicant_id}")

                # Check if current_analysis_response exists in state before accessing it
                if "current_analysis_response" not in state:
                    # Initialize if not present
                    state["current_analysis_response"] = AIAnalysisResponse(
                        overall_score=0,
                        quality_grade="F",
                        categorization="Mismatched",
                        justification_summary="",
                        applicant_id=applicant_id
                    )

                # Store results in the current analysis response 
                state["current_analysis_response"].overall_score = overall_score
                state["current_analysis_response"].quality_grade = quality_grade
                return state
            except Exception as e:
                ai_logger.error(f"[Scoring Grading Node] Error in scoring_grading_node for applicant {applicant_id}: {str(e)}")

                # Check if current_analysis_response exists in state before accessing it
                if "current_analysis_response" not in state:
                    # Initialize if not present
                    state["current_analysis_response"] = AIAnalysisResponse(
                        overall_score=0,
                        quality_grade="F",
                        categorization="Mismatched",
                        justification_summary="",
                        applicant_id=applicant_id
                    )

                # Store results in the current analysis response 
                state["current_analysis_response"].overall_score = 0
                state["current_analysis_response"].quality_grade = "F"
                return state

    ai_logger.info(f"[Scoring Grading Node] Completed without processing applicant")
    return state


def categorization_node(state: GraphState) -> GraphState:
    """
    Worker node: Calls Ollama to assign categorization
    """
    current_idx = state.get("current_index", 0)
    applicant_id_list = state.get("applicant_id_list", [])

    ai_logger.info(f"[Categorization Node] Starting categorization for index {current_idx}")

    if current_idx <= len(applicant_id_list):
        current_idx = max(0, current_idx - 1)  # Adjust for the increment in previous node

        if current_idx < len(applicant_id_list):
            applicant_id = applicant_id_list[current_idx]
            state_resume_text = state["resume_texts"].get(applicant_id, "")
            state_job_requirements = state.get("job_requirements", "")

            ai_logger.info(f"[Categorization Node] Processing applicant {applicant_id}, resume length: {len(state_resume_text)}, job requirements length: {len(state_job_requirements)}")

            # Prepare the prompt for categorization
            categorization_prompt = """
            Based on the following resume and job requirements, categorize the candidate:

            Job Requirements: {job_requirements}

            Resume: {resume_text}

            Categorize as one of: Senior, Mid-Level, Junior, or Mismatched

            Respond with only the category name.
            """

            try:
                prompt = categorization_prompt.format(job_requirements=state_job_requirements, resume_text=state_resume_text)
                ai_logger.info(f"[Categorization Node] Sending request to LLM for applicant {applicant_id}")
                response = llm.invoke(prompt)
                response_categorization = response.content.strip()

                ai_logger.info(f"[Categorization Node] Initial LLM response for applicant {applicant_id}: '{response_categorization}'")

                # Validate the category
                valid_categories = ["Senior", "Mid-Level", "Junior", "Mismatched"]
                if response_categorization not in valid_categories:
                    # Use Ollama again to get a valid category
                    validation_prompt = """
                    The category {categorization} is not valid. Choose one of: Senior, Mid-Level, Junior, or Mismatched
                    Based on this resume: {resume_text}

                    Respond with only the valid category name.
                    """
                    ai_logger.info(f"[Categorization Node] Invalid category '{response_categorization}', requesting validation for applicant {applicant_id}")
                    prompt = validation_prompt.format(categorization=response_categorization, resume_text=state_resume_text)
                    response = llm.invoke(prompt)
                    categorization = response.content.strip()
                    ai_logger.info(f"[Categorization Node] Validated category for applicant {applicant_id}: '{categorization}'")
                else:
                    categorization = response_categorization
                    ai_logger.info(f"[Categorization Node] Valid category for applicant {applicant_id}: '{categorization}'")

                # Check if current_analysis_response exists in state before accessing it
                if "current_analysis_response" not in state:
                    # Initialize if not present
                    state["current_analysis_response"] = AIAnalysisResponse(
                        overall_score=0,
                        quality_grade="F",
                        categorization="Mismatched",
                        justification_summary="",
                        applicant_id=applicant_id
                    )

                # Store results in the current analysis response 
                state["current_analysis_response"].categorization = categorization

                return state
            except Exception as e:
                ai_logger.error(f"[Categorization Node] Error in categorization_node for applicant {applicant_id}: {str(e)}")

                # Check if current_analysis_response exists in state before accessing it
                if "current_analysis_response" not in state:
                    # Initialize if not present
                    state["current_analysis_response"] = AIAnalysisResponse(
                        overall_score=0,
                        quality_grade="F",
                        categorization="Mismatched",
                        justification_summary="",
                        applicant_id=applicant_id
                    )

                # Store results in the current analysis response 
                state["current_analysis_response"].categorization = "Mismatched"

                return state

    ai_logger.info(f"[Categorization Node] Completed without processing applicant")
    return state


def justification_node(state: GraphState):
    """
    Worker node: Calls Ollama to generate justification_summary
    """
    current_idx = state.get("current_index", 0)
    applicant_id_list = state.get("applicant_id_list", [])

    ai_logger.info(f"[Justification Node] Starting justification for index {current_idx}")

    if current_idx <= len(applicant_id_list):
        current_idx = max(0, current_idx - 1)  # Adjust for previous increment

        if current_idx < len(applicant_id_list):
            applicant_id = applicant_id_list[current_idx]
            state_resume_text = state["resume_texts"].get(applicant_id, "")
            state_job_requirements = state.get("job_requirements", "")
            state_overall_score = state["current_analysis_response"].overall_score
            state_quality_grade = state["current_analysis_response"].quality_grade
            state_categorization = state["current_analysis_response"].categorization

            ai_logger.info(f"[Justification Node] Processing applicant {applicant_id}, resume length: {len(state_resume_text)}, score: {state_overall_score}, grade: {state_quality_grade}, category: {state_categorization}")

            # Prepare the prompt for justification
            justification_prompt = """
            Provide a brief justification for the scores given to this candidate:

            Job Requirements: {job_requirements}

            Resume: {resume_text}

            Overall Score: {overall_score}
            Quality Grade: {quality_grade}
            Categorization: {categorization}

            Explain in 1-2 sentences why these scores were given, mentioning specific strengths or weaknesses.
            """

            try:
                prompt = justification_prompt.format(job_requirements=state_job_requirements, resume_text=state_resume_text, overall_score=state_overall_score, quality_grade=state_quality_grade, categorization=state_categorization)
                ai_logger.info(f"[Justification Node] Sending justification request to LLM for applicant {applicant_id}")
                response = llm.invoke(prompt)
                justification = response.content.strip()

                ai_logger.info(f"[Justification Node] Received justification for applicant {applicant_id}: '{justification[:100]}...'")

                # Create the AIAnalysisResponse object if not already created 
                if "current_analysis_response" not in state:
                    # Initialize if not present
                    state["current_analysis_response"] = AIAnalysisResponse(
                        overall_score=0,
                        quality_grade="F",
                        categorization="Mismatched",
                        justification_summary="",
                        applicant_id=applicant_id
                    )

                # Store in the currently available AIAnalysisResponse object in the graph's state
                state["current_analysis_response"].justification_summary = justification

                ai_logger.info(f"Merging Analysis Response For Applicant: {applicant_id}")
                return {"results": [state["current_analysis_response"]]}
            except Exception as e:
                ai_logger.error(f"[Justification Node] Error in justification_node for applicant {applicant_id}: {str(e)}")

                # Check if current_analysis_response exists in state before accessing it
                if "current_analysis_response" not in state:
                    # Initialize if not present
                    state["current_analysis_response"] = AIAnalysisResponse(
                        overall_score=0,
                        quality_grade="F",
                        categorization="Mismatched",
                        justification_summary="",
                        applicant_id=applicant_id
                    )

                # Store results in the current analysis response 
                state["current_analysis_response"].justification_summary = f"Error processing: {str(e)}"

                return {"results": [state["current_analysis_response"]]}

    ai_logger.info(f"[Justification Node] Completed without processing applicant")
    state["current_analysis_response"].justification_summary = "[Justification Node] Completed without processing applicant"
    return {"results": [state["current_analysis_response"]]}


def create_worker_graph():
    """
    Create the Worker Sub-Graph with sequential nodes for single-resume analysis
    """
    worker_graph = StateGraph(GraphState)
    
    # Add nodes to the worker graph
    worker_graph.add_node("data_retrieval", data_retrieval_node)
    worker_graph.add_node("scoring_grading", scoring_grading_node)
    worker_graph.add_node("categorization", categorization_node)
    worker_graph.add_node("justification", justification_node)
    
    # Define the flow for a single resume
    worker_graph.add_edge(START, "data_retrieval")
    worker_graph.add_edge("data_retrieval", "scoring_grading")
    worker_graph.add_edge("scoring_grading", "categorization")
    worker_graph.add_edge("categorization", "justification")
    worker_graph.add_edge("justification", END)
    
    return worker_graph.compile()

def create_supervisor_graph():
    """
    Create the Supervisor Main Graph with Map-Reduce pattern using Send for parallel execution
    """

    def continue_to_process(state: GraphState):
        """
        Dispatch applicants, Create sends objects for parallel processing and decide whether to merge the results if finished.
        """
        applicant_ids = state.get("applicant_id_list", [])

        # If there are actual applicants 
        if applicant_ids:
            # Create a list of Send objects to dispatch work to multiple worker nodes
            sends = []
            for applicant_id in applicant_ids:
                ai_logger.info(f"[Dispatch Workers Node] Creating worker for applicant {applicant_id}")
                current_analysis_response = AIAnalysisResponse(overall_score=0, quality_grade="F", categorization="Mismatched", justification_summary="", applicant_id=applicant_id)
                # Create a specific state for this applicant to be processed
                worker_state = {
                    "applicant_id_list": [applicant_id],
                    "job_criteria": state.get("job_criteria", {}),
                    "results": [],
                    "status": "processing",
                    "current_index": 0,  # Each individual worker starts at index 0 for its single applicant
                    "error_count": 0,
                    "total_count": 1,
                    "resume_texts": state.get("resume_texts", {}),
                    "job_requirements": state.get("job_requirements", ""),
                    "current_analysis_response": current_analysis_response
                }

                # Use Send to dispatch to the worker_node with specific parameters
                sends.append(Send("WorkerSubGraph", worker_state))

            ai_logger.info(f"[Dispatch Workers Node] Created {len(sends)} worker dispatches")
            # Return the sends to trigger parallel execution
            return sends
        else: 
            return "bulk_persistence"

    def bulk_persistence_node(state: GraphState):
        """
        Bulk Persistence Node: Updates Applicant records in SQLite3 database via Django ORM
        """
        results = state.get("results", [])
        error_count = 0

        ai_logger.info(f"[Bulk Persistence Node] Starting bulk persistence for {len(results)} results")

        # Prepare bulk update data
        for i, result in enumerate(results):
            ai_logger.info(f"[Bulk Persistence Node] Processing result {i+1}/{len(results)} for applicant {result.applicant_id}")
            try:
                # Update the applicant record with the analysis results
                applicant = Applicant.objects.get(id=result.applicant_id)
                ai_logger.info(f"[Bulk Persistence Node] Updating applicant {result.applicant_id} with score: {result.overall_score}, grade: {result.quality_grade}, category: {result.categorization}")

                applicant.overall_score = result.overall_score
                applicant.quality_grade = result.quality_grade
                applicant.categorization = result.categorization
                applicant.justification_summary = result.justification_summary
                applicant.processing_status = 'completed'
                applicant.save()

                ai_logger.info(f"[Bulk Persistence Node] Successfully updated applicant {result.applicant_id}")
            except Exception as e:
                ai_logger.error(f"[Bulk Persistence Node] Error updating applicant {result.applicant_id}: {str(e)}")
                error_count += 1

        # Update state with final status
        state["status"] = "completed"
        new_state_error_count = state.get("error_count", 0) + error_count

        ai_logger.info(f"[Bulk Persistence Node] Completed bulk persistence, errors: {error_count}, final status: {state['status']}")

        return {"status": "completed", "error_count": new_state_error_count}
        
    # Create the supervisor graph
    supervisor_graph = StateGraph(GraphState)
    # Compiled worker subgraph
    worker_subgraph = create_worker_graph()
    
    # Add Nodes
    supervisor_graph.add_node("WorkerSubGraph", worker_subgraph)
    supervisor_graph.add_node("bulk_persistence", bulk_persistence_node)

    # Add Edges 
    supervisor_graph.add_conditional_edges(START, continue_to_process)
    supervisor_graph.add_edge("WorkerSubGraph", "bulk_persistence")
    supervisor_graph.add_edge("bulk_persistence", END)

    return supervisor_graph.compile()