from django.db import models
import json
from django.core.exceptions import ValidationError
import bleach
import markdown


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
