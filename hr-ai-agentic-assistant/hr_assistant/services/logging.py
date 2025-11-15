"""
Error handling and logging infrastructure for AI processing
"""
import logging
from typing import Dict, Any
from django.conf import settings
import traceback
from functools import wraps


# Configure logging for AI processing
ai_logger = logging.getLogger('ai_processing')
ai_logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
import os
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir, exist_ok=True)

# Create a file handler for AI processing logs
if not ai_logger.handlers:
    file_handler = logging.FileHandler(os.path.join(logs_dir, 'ai_processing.log'))
    file_handler.setLevel(logging.INFO)
    
    # Create a console handler for debugging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    ai_logger.addHandler(file_handler)
    ai_logger.addHandler(console_handler)


class AIProcessingError(Exception):
    """
    Custom exception for AI processing errors
    """
    def __init__(self, message: str, applicant_id: int = None, error_code: str = None):
        self.message = message
        self.applicant_id = applicant_id
        self.error_code = error_code
        super().__init__(self.message)


def log_ai_error(error: Exception, applicant_id: int = None, context: str = None):
    """
    Log AI processing errors with appropriate context
    """
    error_msg = f"AI Processing Error"
    if context:
        error_msg += f" in {context}"
    if applicant_id:
        error_msg += f" for applicant {applicant_id}"
    error_msg += f": {str(error)}"
    
    ai_logger.error(error_msg)
    ai_logger.error(f"Traceback: {traceback.format_exc()}")


def handle_ai_errors(applicant_id: int = None, context: str = None):
    """
    Decorator for handling AI processing errors
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AIProcessingError:
                # Re-raise custom AI processing errors
                raise
            except Exception as e:
                # Log the error
                log_ai_error(e, applicant_id, context or func.__name__)
                
                # Raise a custom AI processing error
                raise AIProcessingError(
                    f"AI processing failed: {str(e)}",
                    applicant_id=applicant_id,
                    error_code="AI_PROCESSING_ERROR"
                )
        return wrapper
    return decorator


def validate_ollama_connection():
    """
    Validate that Ollama is accessible and responding
    """
    try:
        import ollama
        # Test the connection by making a simple request
        response = ollama.chat(
            model='llama2',
            messages=[{'role': 'user', 'content': 'test'}],
            options={'num_predict': 5}
        )
        return True
    except Exception as e:
        ai_logger.error(f"Ollama connection test failed: {str(e)}")
        return False


def log_ai_processing_start(applicant_id: int, job_id: int = None):
    """
    Log the start of AI processing for an applicant
    """
    msg = f"Starting AI processing for applicant {applicant_id}"
    if job_id:
        msg += f" for job {job_id}"
    ai_logger.info(msg)


def log_ai_processing_complete(applicant_id: int, results: Dict[str, Any] = None):
    """
    Log the completion of AI processing for an applicant
    """
    msg = f"Completed AI processing for applicant {applicant_id}"
    if results:
        msg += f" - Score: {results.get('overall_score', 'N/A')}, Grade: {results.get('quality_grade', 'N/A')}"
    ai_logger.info(msg)


def log_resume_analysis(applicant_id: int, analysis_data: Dict[str, Any]):
    """
    Log detailed resume analysis results
    """
    msg = f"Resume analysis for applicant {applicant_id}: {analysis_data}"
    ai_logger.info(msg)