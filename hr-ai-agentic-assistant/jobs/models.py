from django.db import models
from django.core.exceptions import ValidationError
import bleach
import markdown
import hashlib


class JobListing(models.Model):
    """
    Represents a single job position with all required information for applicant scoring.
    """
    title = models.CharField(
        max_length=200,  # T006a: Title max 200 chars
        help_text="Title of the job position"
    )
    detailed_description = models.TextField(
        help_text="Description of the job with markdown content"
    )
    required_skills = models.JSONField(
        default=list,
        help_text="Structured list of required skills/qualities for the position"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Boolean flag indicating if this is the active listing"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Custom validation to enforce constraints:
        - Title is required and max 200 chars (already handled by field definition)
        - detailed_description max 50000 chars (T006b)
        - required_skills max 100 items (T006c)
        - Only one JobListing can be active at a time (T007, T007a)
        """
        # T006b: Validate detailed_description max length
        if len(self.detailed_description) > 50000:
            raise ValidationError({'detailed_description': 'Description exceeds maximum length of 50000 characters'})
        
        # T006c: Validate required_skills max items
        if isinstance(self.required_skills, list) and len(self.required_skills) > 100:
            raise ValidationError({'required_skills': 'Number of required skills exceeds maximum of 100 items'})
        
        # T007, T007a: Ensure only one active job listing at a time
        if self.is_active:
            # Deactivate other job listings when this one is activated
            JobListing.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)

    def save(self, *args, **kwargs):
        """
        Override save to implement auto-activation of first created job listing (T007b)
        and ensure only one active listing constraint (T007, T007a)
        """
        # Check if this is the first job listing being created (T007b)
        if not self.pk and JobListing.objects.count() == 0:
            self.is_active = True
        elif self.is_active:
            # Ensure only one listing is active at a time (T007, T007a)
            JobListing.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        
        super().save(*args, **kwargs)

    def get_rendered_description(self):
        """
        Return the detailed_description rendered from markdown to HTML with sanitization (T008)
        """
        if self.detailed_description:
            # Convert markdown to HTML
            html = markdown.markdown(self.detailed_description, extensions=['extra', 'codehilite'])
            # Sanitize HTML to prevent XSS while allowing safe elements
            allowed_tags = [
                'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'blockquote', 'code', 'pre', 'hr', 'a', 'img'
            ]
            allowed_attributes = {
                'a': ['href', 'title'],
                'img': ['src', 'alt', 'title'],
                'p': ['class'],
                'code': ['class'],
                'pre': ['class']
            }
            return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
        return ''

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Job Listing"
        verbose_name_plural = "Job Listings"


class Applicant(models.Model):
    """
    Represents an applicant with their resume data and metadata.
    """
    job_listing = models.ForeignKey(
        JobListing,
        on_delete=models.CASCADE,
        related_name='applicants',
        help_text="The job listing this applicant has applied for",
        null=True,  # Temporarily allow null for existing records
        blank=True  # Allow blank in forms
    )
    applicant_name = models.CharField(
        max_length=255,
        help_text="Name of the applicant extracted from the resume filename"
    )
    resume_file = models.FileField(
        upload_to='resumes/',
        help_text="Reference to the uploaded resume file (PDF/DOCX)"
    )
    content_hash = models.CharField(
        max_length=64,  # SHA256 hash is 64 hex characters
        unique=True,
        help_text="SHA256 hash of the file content for duplicate detection"
    )
    file_size = models.PositiveIntegerField(
        help_text="Size of the uploaded file in bytes"
    )
    file_format = models.CharField(
        max_length=10,
        help_text="File format (PDF, DOCX)"
    )
    upload_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of when the resume was uploaded"
    )
    processing_status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('error', 'Error')
        ],
        help_text="Current status of AI processing"
    )
    analysis_status = models.CharField(
        max_length=15,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('analyzed', 'Analyzed'),
            ('error', 'Error')
        ],
        help_text="Status of the analysis process"
    )
    # Fields for AI analysis results
    overall_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Overall score (0-100) representing fitness for the job"
    )
    quality_grade = models.CharField(
        max_length=1,
        null=True,
        blank=True,
        help_text="Quality grade (A, B, C, D, F) reflecting quality of experience"
    )
    categorization = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Categorization (e.g., Senior, Mid-Level, Junior, Mismatched)"
    )
    justification_summary = models.TextField(
        null=True,
        blank=True,
        help_text="AI-generated justification for the scores"
    )
    analysis_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the analysis was completed"
    )
    ai_analysis_result = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON data containing the results of AI analysis"
    )

    def clean(self):
        """
        Custom validation to enforce the following rules:
        1. File Format Validation: file_format must be either 'PDF' or 'DOCX'
        2. File Size Validation: file_size must be between 1KB and 10MB (10485760 bytes)
        3. Required Fields: applicant_name, resume_file, content_hash must not be null
        4. Name Format: applicant_name should match standard name patterns extracted from the filename using pattern recognition (e.g., "FirstName_LastName_Resume.pdf")
        5. Job Listing Validation: job_listing must be active
        """
        # 1. File Format Validation: file_format must be either 'PDF' or 'DOCX'
        if self.file_format.upper() not in ['PDF', 'DOCX']:
            raise ValidationError({'file_format': 'File format must be either PDF or DOCX'})

        # 2. File Size Validation: file_size must be between 1KB and 10MB (10485760 bytes)
        if not (1024 <= self.file_size <= 10 * 1024 * 1024):  # 1KB to 10MB
            raise ValidationError({'file_size': 'File size must be between 1KB and 10MB'})

        # 3. Required Fields: applicant_name, resume_file, content_hash must not be null
        if not self.applicant_name:
            raise ValidationError({'applicant_name': 'Applicant name is required'})
        if not self.resume_file:
            raise ValidationError({'resume_file': 'Resume file is required'})
        if not self.content_hash:
            raise ValidationError({'content_hash': 'Content hash is required'})

        # 4. Name Format: applicant_name should match standard name patterns
        import re
        name_pattern = r'^[A-Za-z\s\'-]+$'  # Allow letters, spaces, apostrophes, and hyphens
        if not re.match(name_pattern, self.applicant_name):
            raise ValidationError({'applicant_name': 'Applicant name contains invalid characters'})

        # 5. Job Listing Validation: if job_listing is provided, it must be active
        if self.job_listing and not self.job_listing.is_active:
            raise ValidationError({'job_listing': 'Cannot add applicant to an inactive job listing'})

    def __str__(self):
        return f"{self.applicant_name} - {self.resume_file.name}"

    class Meta:
        verbose_name = "Applicant"
        verbose_name_plural = "Applicants"
        # Database Indexes (from data-model.md):
        # 1. content_hash: B-tree index for fast duplicate detection queries
        # 2. upload_date: B-tree index for chronological queries
        # 3. processing_status: B-tree index for status-based filtering
        # 4. applicant_name: B-tree index for name-based searches
        # 5. overall_score: B-tree index for sorting operations
        # 6. (job_listing_id, processing_status): B-tree index for efficient filtering
        indexes = [
            models.Index(fields=['content_hash']),
            models.Index(fields=['upload_date']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['applicant_name']),
            models.Index(fields=['overall_score']),
            models.Index(fields=['job_listing', 'processing_status']),
        ]
