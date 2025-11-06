from django import forms
from .models import JobListing
import json


class JobListingForm(forms.ModelForm):
    """
    Django form for job listing creation/editing with validation (T015)
    """
    required_skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Enter required skills as a comma-separated list",
        required=False
    )
    # Hidden field for optimistic locking to prevent concurrent editing (T035)
    version = forms.FloatField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = JobListing
        fields = ['title', 'detailed_description', 'required_skills', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'detailed_description': forms.Textarea(attrs={
                'rows': 10, 
                'placeholder': 'Enter job description using markdown formatting...',
                'class': 'form-textarea'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_required_skills(self):
        """
        Convert comma-separated string to JSON array for required_skills field
        """
        skills_input = self.cleaned_data.get('required_skills', '')
        if skills_input.strip():
            # Split by comma and clean up the skills
            skills_list = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
            # Validate max 100 items
            if len(skills_list) > 100:
                raise forms.ValidationError('Number of required skills exceeds maximum of 100 items')
            return skills_list
        return []

    def __init__(self, *args, **kwargs):
        """
        Initialize form with existing skills as comma-separated string if editing
        """
        super().__init__(*args, **kwargs)
        
        # If editing existing job listing, convert JSON skills back to comma-separated string for display
        if self.instance and self.instance.pk and isinstance(self.instance.required_skills, list):
            self.fields['required_skills'].initial = ', '.join(self.instance.required_skills)

    def save(self, commit=True):
        """
        Override save to exclude the version field from saving
        """
        # Remove version from cleaned_data so it doesn't get saved to the model
        self.cleaned_data.pop('version', None)
        return super().save(commit)