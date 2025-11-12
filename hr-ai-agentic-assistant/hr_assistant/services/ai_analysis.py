"""
LangGraph implementation for AI Resume Scoring Engine with Map-Reduce pattern
"""
from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
from langchain_ollama import ChatOllama
from .contracts import GraphState, AIAnalysisResponse
import os
import django

# Setup Django environment once at module level
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_assistant.settings')
django.setup()

# Import Django models after setting up Django
from jobs.models import Applicant


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
    results = state.get("results", [])
    error_count = state.get("error_count", 0)
    
    if current_idx < len(state.get("applicant_id_list", [])):
        applicant_id = state["applicant_id_list"][current_idx]
        
        try:
            # Retrieve applicant and their resume text
            applicant = Applicant.objects.get(id=applicant_id)
            resume_text = applicant.parsed_resume_text or str(applicant.resume_file)  # Fallback to file path if parsed text not available
            
            # Update resume_texts in state
            resume_texts = state.get("resume_texts", {})
            resume_texts[applicant_id] = resume_text
            state["resume_texts"] = resume_texts
            
        except Exception as e:
            print(f"Error retrieving data for applicant {applicant_id}: {str(e)}")
            error_count += 1
    
    state["current_index"] = current_idx + 1
    state["error_count"] = error_count
    
    return state


def scoring_grading_node(state: GraphState) -> GraphState:
    """
    Worker node: Calls Ollama to calculate overall_score and quality_grade
    """
    current_idx = state.get("current_index", 0)
    applicant_id_list = state.get("applicant_id_list", [])
    
    if current_idx <= len(applicant_id_list):
        current_idx = max(0, current_idx - 1)  # Adjust for the increment in previous node
        
        if current_idx < len(applicant_id_list):
            applicant_id = applicant_id_list[current_idx]
            state_resume_text = state["resume_texts"].get(applicant_id, "")
            state_job_requirements = state.get("job_requirements", "")
            
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
                prompt = scoring_prompt.format(job_requirements= state_job_requirements, resume_texts = state_resume_text)
                response = llm.invoke(prompt)
                response_text = response.content
                
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
                
                # Store in temporary state for next node
                temp_state = state.copy()
                temp_state["current_overall_score"] = overall_score
                temp_state["current_quality_grade"] = quality_grade
                
                return temp_state
            except Exception as e:
                print(f"Error in scoring_grading_node for applicant {applicant_id}: {str(e)}")
                # Return default values in case of error
                temp_state = state.copy()
                temp_state["current_overall_score"] = 0
                temp_state["current_quality_grade"] = "F"
                
                return temp_state
    
    return state


def categorization_node(state: GraphState) -> GraphState:
    """
    Worker node: Calls Ollama to assign categorization
    """
    current_idx = state.get("current_index", 0)
    applicant_id_list = state.get("applicant_id_list", [])
    
    if current_idx <= len(applicant_id_list):
        current_idx = max(0, current_idx - 1)  # Adjust for the increment in previous node
        
        if current_idx < len(applicant_id_list):
            applicant_id = applicant_id_list[current_idx]
            state_resume_text = state["resume_texts"].get(applicant_id, "")
            state_job_requirements = state.get("job_requirements", "")
            
            # Prepare the prompt for categorization
            categorization_prompt = """
            Based on the following resume and job requirements, categorize the candidate:
            
            Job Requirements: {job_requirements}
            
            Resume: {resume_text}
            
            Categorize as one of: Senior, Mid-Level, Junior, or Mismatched
            
            Respond with only the category name.
            """
            
            try:
                prompt = categorization_prompt.format(job_requirements =state_job_requirements, resume_text = state_resume_text)
                response = llm.invoke(prompt)
                response_categorization = response.content.strip()
                
                # Validate the category
                valid_categories = ["Senior", "Mid-Level", "Junior", "Mismatched"]
                if categorization not in valid_categories:
                    # Use Ollama again to get a valid category
                    validation_prompt = """
                    The category {categorization} is not valid. Choose one of: Senior, Mid-Level, Junior, or Mismatched
                    Based on this resume: {resume_text}
                    
                    Respond with only the valid category name.
                    """
                    prompt = validation_prompt.format(categorization=response_categorization, resume_text= state_resume_text)
                    response = llm.invoke(prompt)
                    categorization = response.content.strip()
                
                # Store in temporary state for next node
                temp_state = state.copy()
                temp_state["current_categorization"] = categorization
                
                return temp_state
            except Exception as e:
                print(f"Error in categorization_node for applicant {applicant_id}: {str(e)}")
                # Return default value in case of error
                temp_state = state.copy()
                temp_state["current_categorization"] = "Mismatched"
                
                return temp_state
    
    return state


def justification_node(state: GraphState) -> GraphState:
    """
    Worker node: Calls Ollama to generate justification_summary
    """
    current_idx = state.get("current_index", 0)
    applicant_id_list = state.get("applicant_id_list", [])
    
    if current_idx <= len(applicant_id_list):
        current_idx = max(0, current_idx - 1)  # Adjust for previous increment
        
        if current_idx < len(applicant_id_list):
            applicant_id = applicant_id_list[current_idx]
            state_resume_text = state["resume_texts"].get(applicant_id, "")
            state_job_requirements = state.get("job_requirements", "")
            state_overall_score = state.get("current_overall_score", 0)
            state_quality_grade = state.get("current_quality_grade", "F")
            state_categorization = state.get("current_categorization", "Mismatched")
            
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
                prompt = justification_prompt.format(job_requirements = state_job_requirements, resume_text= state_resume_text, overall_score=state_overall_score, quality_grade=state_quality_grade, categorization=state_categorization)
                response = llm.invoke(prompt)
                justification = response.content.strip()
                
                # Create the AIAnalysisResponse object
                analysis_result = AIAnalysisResponse(
                    overall_score=state.get("current_overall_score", 0),
                    quality_grade=state.get("current_quality_grade", "F"),
                    categorization=state.get("current_categorization", "Mismatched"),
                    justification_summary=justification,
                    applicant_id=applicant_id
                )
                
                # Add to results
                results = state.get("results", [])
                results.append(analysis_result)
                
                temp_state = state.copy()
                temp_state["results"] = results
                
                return temp_state
            except Exception as e:
                print(f"Error in justification_node for applicant {applicant_id}: {str(e)}")
                # Create a result with default values in case of error
                analysis_result = AIAnalysisResponse(
                    overall_score=state.get("current_overall_score", 0),
                    quality_grade=state.get("current_quality_grade", "F"),
                    categorization=state.get("current_categorization", "Mismatched"),
                    justification_summary=f"Error processing: {str(e)}",
                    applicant_id=applicant_id
                )
                
                # Add to results
                results = state.get("results", [])
                results.append(analysis_result)
                
                temp_state = state.copy()
                temp_state["results"] = results
                
                return temp_state
    
    return state


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
    worker_graph.add_edge("data_retrieval", "scoring_grading")
    worker_graph.add_edge("scoring_grading", "categorization")
    worker_graph.add_edge("categorization", "justification")
    
    # Set entry point
    worker_graph.set_entry_point("data_retrieval")
    
    return worker_graph.compile()


def worker_node(state: GraphState) -> GraphState:
    """
    Single node that runs the worker graph for one applicant
    """
    # Get the current applicant to process
    current_idx = state.get("current_index", 0)
    applicant_id_list = state.get("applicant_id_list", [])
    
    if current_idx < len(applicant_id_list):
        # Create a temporary state for this single applicant
        applicant_id = applicant_id_list[current_idx]
        
        # Create a temporary state for this specific applicant
        worker_state = state.copy()
        worker_state["applicant_id_list"] = [applicant_id]
        worker_state["current_index"] = 0  # Each worker processes its own applicant from start
        
        # Run the worker process
        worker_graph = create_worker_graph()
        result_state = worker_graph.invoke(worker_state)
        
        # Extract the results from the worker run
        worker_results = result_state.get("results", [])
        
        # Merge the results back to the main state
        results = state.get("results", [])
        results.extend(worker_results)
        
        new_state = state.copy()
        new_state["results"] = results
        new_state["current_index"] = current_idx + 1  # Move to next applicant in main list
        
        return new_state
    
    return state


def create_supervisor_graph():
    """
    Create the Supervisor Main Graph with Map-Reduce pattern using Send for parallel execution
    """
    
    def dispatch_workers(state: GraphState):
        """
        Supervisor node that uses Send to dispatch parallel worker tasks for each applicant
        """
        applicant_ids = state.get("applicant_id_list", [])
        
        # Create a list of Send objects to dispatch work to multiple worker nodes
        sends = []
        for applicant_id in applicant_ids:
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
                "job_requirements": state.get("job_requirements", "")
            }
            
            # Use Send to dispatch to the worker_node with specific parameters
            sends.append(Send("worker_node", worker_state))
        
        # Return the sends to trigger parallel execution
        return {"__pregel_send": sends}

    def process_results(state: GraphState) -> GraphState:
        """
        Collect and process results from all workers before persistence
        """
        # This would collect results from all parallel workers
        # In our current setup, we're handling results collection in the worker node
        return state

    # Create the supervisor graph
    supervisor_graph = StateGraph(GraphState)
    
    # Add nodes
    supervisor_graph.add_node("dispatch_workers", dispatch_workers)
    supervisor_graph.add_node("worker_node", worker_node)
    supervisor_graph.add_node("process_results", process_results)
    supervisor_graph.add_node("bulk_persistence", bulk_persistence_node)
    
    # Set entry point
    supervisor_graph.add_edge(START, "dispatch_workers")
    
    # Add the worker node that will be called via Send
    # The dispatch_workers node handles the parallel dispatch using SEND
    
    # Add edges from worker to results processing and then to persistence
    supervisor_graph.add_edge("worker_node", "process_results")
    supervisor_graph.add_edge("process_results", "bulk_persistence")
    supervisor_graph.add_edge("bulk_persistence", END)
    
    return supervisor_graph.compile()


def bulk_persistence_node(state: GraphState) -> GraphState:
    """
    Bulk Persistence Node: Updates Applicant records in SQLite3 database via Django ORM
    """
    results = state.get("results", [])
    error_count = 0
    
    # Prepare bulk update data
    for result in results:
        try:
            # Update the applicant record with the analysis results
            applicant = Applicant.objects.get(id=result.applicant_id)
            applicant.overall_score = result.overall_score
            applicant.quality_grade = result.quality_grade
            applicant.categorization = result.categorization
            applicant.justification_summary = result.justification_summary
            applicant.processing_status = 'completed'
            applicant.save()
        except Exception as e:
            print(f"Error updating applicant {result.applicant_id}: {str(e)}")
            error_count += 1
    
    # Update state with final status
    final_state = state.copy()
    final_state["status"] = "completed"
    final_state["error_count"] = state.get("error_count", 0) + error_count
    
    return final_state