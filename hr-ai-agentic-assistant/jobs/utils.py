import hashlib
from django.core.exceptions import ValidationError
import os


def validate_file_type(file):
    """
    Validates that the uploaded file is either a PDF or DOCX by checking content.
    
    Args:
        file: The uploaded file object
        
    Returns:
        bool: True if file type is valid, False otherwise
    """
    try:
        # Check file extension first as a basic validation
        filename = file.name.lower()
        if filename.endswith('.pdf'):
            return True
        elif filename.endswith('.docx'):
            return True
        else:
            return False
    except Exception as e:
        return False


def validate_file_extension(file):
    """
    Validates file extension is PDF or DOCX.
    
    Args:
        file: The uploaded file object
        
    Returns:
        bool: True if extension is valid, False otherwise
    """
    import os
    filename = file.name
    allowed_extensions = ['.pdf', '.docx']
    
    _, extension = os.path.splitext(filename.lower())
    return extension in allowed_extensions


def calculate_file_hash(file):
    """
    Calculate SHA256 hash of file content for duplicate detection.
    
    Args:
        file: File object to hash
        
    Returns:
        str: SHA256 hash of the file content
    """
    sha256_hash = hashlib.sha256()
    # Process file in chunks to handle large files efficiently
    for chunk in iter(lambda: file.read(4096), b""):
        sha256_hash.update(chunk)
    file.seek(0)  # Reset file pointer
    return sha256_hash.hexdigest()


def extract_applicant_name_from_filename(filename):
    """
    Extract applicant name from the filename using pattern recognition.
    
    Args:
        filename: The original filename of the uploaded file
        
    Returns:
        str: Extracted applicant name, or a default value if extraction fails
    """
    import re
    import os
    
    # Remove extension and get base filename
    base_name = os.path.splitext(filename)[0]
    
    # Common patterns for resume filenames:
    # FirstName_LastName_Resume.pdf
    # LastName, FirstName Resume.pdf
    # FirstName-LastName.pdf
    # etc.
    
    # Pattern 1: Name_Resume (e.g., "John_Doe_Resume.pdf")
    pattern1 = r'^([A-Za-z]+(?:_[A-Za-z]+)?)'
    match = re.match(pattern1, base_name)
    if match:
        name_part = match.group(1).replace('_', ' ')
        return name_part.title()
    
    # Pattern 2: Name-Resume (e.g., "John-Doe.pdf")
    pattern2 = r'^([A-Za-z]+(?:-[A-Za-z]+)?)'
    match = re.match(pattern2, base_name)
    if match:
        name_part = match.group(1).replace('-', ' ')
        return name_part.title()
    
    # Pattern 3: Name, Resume (e.g., "Doe, John.pdf")
    pattern3 = r'^([^,]+),\s*([^,]+)'
    match = re.match(pattern3, base_name)
    if match:
        last_name = match.group(1).strip()
        first_name = match.group(2).strip()
        return f"{first_name} {last_name}".title()
    
    # If no pattern matches, return the base filename as name
    return base_name.replace('_', ' ').replace('-', ' ').title()


def check_duplicate_content(content_hash):
    """
    Check if a file with the same content hash already exists in the database.
    
    Args:
        content_hash: SHA256 hash of the file content
        
    Returns:
        bool: True if duplicate found, False otherwise
    """
    from .models import Applicant  # Import here to avoid circular imports
    return Applicant.objects.filter(content_hash=content_hash).exists()


def check_duplicate_name(applicant_name):
    """
    Check if an applicant with the same name already exists in the database.
    
    Args:
        applicant_name: The extracted applicant name
        
    Returns:
        bool: True if duplicate found, False otherwise
    """
    from .models import Applicant  # Import here to avoid circular imports
    return Applicant.objects.filter(applicant_name=applicant_name).exists()


def validate_file_size(file, max_size=10*1024*1024):  # Default to 10MB
    """
    Validate that the file size is within the allowed limit.
    
    Args:
        file: The uploaded file object
        max_size: Maximum allowed file size in bytes (default 10MB)
        
    Returns:
        bool: True if size is within limit, False otherwise
    """
    return file.size <= max_size