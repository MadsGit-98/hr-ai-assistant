from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from .models import JobListing
from .forms import JobListingForm
from . import utils


class JobListingCreateView(CreateView):
    """
    Implement JobListingCreateView for T016
    """
    model = JobListing
    form_class = JobListingForm
    template_name = 'jobs/joblisting_form.html'
    success_url = reverse_lazy('joblisting_list')

    def form_valid(self, form):
        """
        Add success message on successful creation
        """
        messages.success(self.request, 'Job listing created successfully!')
        return super().form_valid(form)


class JobListingDetailView(DetailView):
    """
    Implement JobListingDetailView for T023
    """
    model = JobListing
    template_name = 'jobs/joblisting_detail.html'

    def get_context_data(self, **kwargs):
        """
        Add rendered description to context
        """
        context = super().get_context_data(**kwargs)
        context['rendered_description'] = self.object.get_rendered_description()
        return context


class JobListingListView(ListView):
    """
    Implement JobListingListView for T024
    """
    model = JobListing
    template_name = 'jobs/joblisting_list.html'
    context_object_name = 'job_listings'


class JobListingUpdateView(UpdateView):
    """
    Implement JobListingUpdateView for T031
    """
    model = JobListing
    form_class = JobListingForm
    template_name = 'jobs/joblisting_form.html'
    success_url = reverse_lazy('joblisting_list')

    def get_form_kwargs(self):
        """
        Add version field to form to support optimistic locking for T035
        """
        kwargs = super().get_form_kwargs()
        # Add the current version to form initial data if it's an update
        if self.object:
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['version'] = self.object.modified_date.timestamp()
        return kwargs

    def form_valid(self, form):
        """
        Add success message on successful update and implement concurrency check for T035
        """
        # For a proof-of-concept, we'll implement a simple optimistic locking mechanism
        # Check if the object has been modified since it was loaded by comparing timestamps
        original_version = self.request.POST.get('version')
        if original_version:
            # Convert string timestamp back to float
            original_version = float(original_version)
            # Get current version from database
            current_obj = JobListing.objects.get(pk=self.object.pk)
            current_version = current_obj.modified_date.timestamp()
            
            # If versions don't match, another user has modified the record
            if original_version != current_version:
                form.add_error(None, "Another user has modified this job listing. Please refresh and try again.")
                return self.form_invalid(form)
        
        # Proceed with saving if no conflict
        messages.success(self.request, 'Job listing updated successfully!')
        return super().form_valid(form)


class JobListingDeleteView(DeleteView):
    """
    Implement JobListingDeleteView for T032
    """
    model = JobListing
    template_name = 'jobs/joblisting_confirm_delete.html'
    success_url = reverse_lazy('joblisting_list')

    def delete(self, request, *args, **kwargs):
        """
        Add success message on successful deletion
        """
        messages.success(request, 'Job listing deleted successfully!')
        return super().delete(request, *args, **kwargs)


def activate_job_listing(request, pk):
    """
    Add activate endpoint to set job listing as active for T036
    """
    job_listing = get_object_or_404(JobListing, pk=pk)
    # The model's save method handles deactivating other listings
    job_listing.is_active = True
    job_listing.save()
    messages.success(request, f'"{job_listing.title}" is now the active job listing!')
    return redirect('joblisting_list')