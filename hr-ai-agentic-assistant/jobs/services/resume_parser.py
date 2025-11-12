"""
Resume parsing and text extraction service
"""
import os
from django.conf import settings
from django.core.files.storage import default_storage
import PyPDF2
import docx
import tempfile


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""


def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX file
    """
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {str(e)}")
        return ""


def parse_resume_text(resume_file):
    """
    Parse the resume file and extract the text content
    """
    file_extension = os.path.splitext(resume_file.name)[1].lower()
    
    # Create a temporary file to work with the uploaded content
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in resume_file.chunks():
            temp_file.write(chunk)
        temp_file_path = temp_file.name
    
    try:
        # Extract text based on file type
        if file_extension == '.pdf':
            text_content = extract_text_from_pdf(temp_file_path)
        elif file_extension == '.docx':
            text_content = extract_text_from_docx(temp_file_path)
        else:
            # For unsupported formats, return empty string
            text_content = ""
            
        return text_content
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def store_parsed_resume_text(applicant, resume_text):
    """
    Store the parsed resume text in the applicant record
    """
    # Update the applicant's parsed resume text field
    applicant.parsed_resume_text = resume_text
    applicant.save()


def process_resume_upload(resume_file, applicant):
    """
    Process a resume upload: parse text and store it
    """
    # Parse the resume text
    parsed_text = parse_resume_text(resume_file)
    
    # Store the parsed text in the applicant record
    store_parsed_resume_text(applicant, parsed_text)
    
    return parsed_text