// JavaScript for candidate reporting and shortlisting functionality
let currentSortBy = 'overall_score';
let currentSortOrder = 'desc';
let currentScoreThreshold = 0;
let currentJobId = null;
let candidateData = [];

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Extract job ID from URL path if present
    // Only extract if the URL pattern is /jobs/{job_id}/...
    const pathParts = window.location.pathname.split('/');
    const jobIdIndex = pathParts.indexOf('jobs');
    if (jobIdIndex !== -1 && pathParts.length > jobIdIndex + 1) {
        const potentialJobId = pathParts[jobIdIndex + 1];
        // Only use as job ID if it's a valid number (not a page name like 'scoring-results' or 'scoring_results')
        if (potentialJobId && /^\d+$/.test(potentialJobId)) {
            currentJobId = potentialJobId;
        }
    }

    // Also check if there's a job_id in the query parameters, but only use it if it's numeric
    const urlParams = new URLSearchParams(window.location.search);
    const urlJobId = urlParams.get('job_id');
    if (urlJobId && /^\d+$/.test(urlJobId)) {
        currentJobId = urlJobId;
    }

    // Set up event listeners
    document.getElementById('apply_filter').addEventListener('click', applyFilter);
    
    // Check if sort order select exists and set up listener
    const sortOrderSelect = document.getElementById('sort_order');
    if (sortOrderSelect) {
        sortOrderSelect.addEventListener('change', function() {
            currentSortOrder = this.value;
            // Re-sort the current data
            sortAndRenderCandidates();
        });
    }
    
    // Load initial data
    loadCandidateData();
});

// Load candidate data from the backend
async function loadCandidateData() {
    try {
        // Build query parameters
        const params = new URLSearchParams({
            'sort_by': currentSortBy,
            'sort_order': currentSortOrder,
            'score_threshold': currentScoreThreshold
        });
        
        // If we have a job ID, add it to the query
        if (currentJobId) {
            params.append('job_id', currentJobId);
        }
        
        // Make API call to get candidates
        const response = await fetch(`/jobs/api/candidates/?${params}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        candidateData = data.candidates || [];
        
        // Render the data
        renderCandidateTable();
    } catch (error) {
        console.error('Error loading candidate data:', error);
        showErrorMessage('Failed to load candidate data. Please try again.');
    }
}

// Render candidates in the table
function renderCandidateTable() {
    const tableBody = document.getElementById('candidates_table_body');
    const emptyState = document.getElementById('empty_state');
    
    if (!candidateData || candidateData.length === 0) {
        // Show empty state
        tableBody.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }
    
    // Hide empty state
    emptyState.classList.add('hidden');
    
    // Generate table rows
    let tableHTML = '';
    candidateData.forEach(candidate => {
        // Format the AI justification summary with expand/collapse functionality
        const truncatedJustification = candidate.justification_summary && candidate.justification_summary.length > 150 
            ? candidate.justification_summary.substring(0, 150) + '...' 
            : candidate.justification_summary;
            
        tableHTML += `
            <tr class="bg-white hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${candidate.applicant_name || 'N/A'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${candidate.overall_score || 'N/A'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${candidate.categorization || 'N/A'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${candidate.quality_grade || 'N/A'}
                </td>
                <td class="px-6 py-4 text-sm text-gray-500">
                    <div class="justification-container" data-full-text="${candidate.justification_summary || ''}">
                        <span class="truncated-text">${truncatedJustification || 'N/A'}</span>
                        ${candidate.justification_summary && candidate.justification_summary.length > 150 
                          ? `<button class="text-blue-600 hover:text-blue-900 ml-2 expand-btn" 
                             data-candidate-id="${candidate.id}">Show more</button>` 
                          : ''}
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <button 
                        class="toggle-shortlist-btn ${candidate.is_shortlisted ? 'bg-green-100 text-green-800 hover:bg-green-200' : 'bg-gray-100 text-gray-800 hover:bg-gray-200'} px-3 py-1 rounded-md text-sm font-medium"
                        data-candidate-id="${candidate.id}"
                        data-is-shortlisted="${candidate.is_shortlisted}"
                    >
                        ${candidate.is_shortlisted ? 'Unshortlist' : 'Shortlist'}
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = tableHTML;
    
    // Add event listeners for expand/collapse buttons
    document.querySelectorAll('.expand-btn').forEach(button => {
        button.addEventListener('click', function() {
            const container = this.closest('.justification-container');
            const truncatedText = container.querySelector('.truncated-text');
            const fullText = container.dataset.fullText;
            const isExpanded = this.textContent === 'Show less';
            
            if (isExpanded) {
                // Collapse: show truncated version
                truncatedText.textContent = fullText.substring(0, 150) + '...';
                this.textContent = 'Show more';
            } else {
                // Expand: show full version
                truncatedText.textContent = fullText;
                this.textContent = 'Show less';
            }
        });
    });
    
    // Add event listeners for shortlist buttons
    document.querySelectorAll('.toggle-shortlist-btn').forEach(button => {
        button.addEventListener('click', function() {
            const candidateId = this.dataset.candidateId;
            const currentStatus = this.dataset.isShortlisted === 'True';
            toggleShortlistStatus(candidateId, currentStatus, this);
        });
    });
    
    // Update sort indicators
    updateSortIndicators();
}

// Toggle shortlist status via API
async function toggleShortlistStatus(candidateId, currentStatus, buttonElement) {
    try {
        // Temporarily disable the button to prevent double clicks
        buttonElement.disabled = true;
        buttonElement.classList.add('opacity-50', 'cursor-not-allowed');

        const response = await fetch(`/jobs/api/candidates/${candidateId}/toggle-shortlist/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Find the candidate in our data and update the status
        const candidateIndex = candidateData.findIndex(candidate => candidate.id == candidateId);
        if (candidateIndex !== -1) {
            candidateData[candidateIndex].is_shortlisted = data.is_shortlisted;

            // Update the button text and class
            if (data.is_shortlisted) {
                buttonElement.textContent = 'Unshortlist';
                buttonElement.classList.remove('bg-gray-100', 'text-gray-800', 'hover:bg-gray-200');
                buttonElement.classList.add('bg-green-100', 'text-green-800', 'hover:bg-green-200');
            } else {
                buttonElement.textContent = 'Shortlist';
                buttonElement.classList.remove('bg-green-100', 'text-green-800', 'hover:bg-green-200');
                buttonElement.classList.add('bg-gray-100', 'text-gray-800', 'hover:bg-gray-200');
            }

            buttonElement.dataset.isShortlisted = data.is_shortlisted;
        }
    } catch (error) {
        console.error('Error toggling shortlist status:', error);
        // Provide more specific error information
        if (error.message.includes('404')) {
            alert('Candidate not found. Please refresh the page and try again.');
        } else {
            alert('Failed to update shortlist status. Please try again.');
        }
    } finally {
        // Re-enable the button
        buttonElement.disabled = false;
        buttonElement.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

// Apply the score filter
function applyFilter() {
    const scoreInput = document.getElementById('score_threshold');
    const newThreshold = parseInt(scoreInput.value) || 0;
    
    // Validate the threshold is within range
    if (newThreshold < 0 || newThreshold > 100) {
        alert('Score threshold must be between 0 and 100');
        return;
    }
    
    currentScoreThreshold = newThreshold;
    loadCandidateData(); // Reload with new filter
}

// Sort the table by a specific column
function sortTable(sortBy) {
    // Update sort indicators
    if (currentSortBy === sortBy) {
        // If clicking the same column, toggle sort order
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        // If clicking a different column, reset to descending
        currentSortBy = sortBy;
        currentSortOrder = 'desc';
    }
    
    // Update sort indicators
    updateSortIndicators();
    
    // Reload data with new sort parameters
    loadCandidateData();
}

// Sort and render candidates based on current settings (without API call)
function sortAndRenderCandidates() {
    // Sort the current data in memory
    candidateData.sort((a, b) => {
        let valueA, valueB;
        
        switch(currentSortBy) {
            case 'overall_score':
                valueA = a.overall_score || 0;
                valueB = b.overall_score || 0;
                break;
            case 'applicant_name':
                valueA = (a.applicant_name || '').toLowerCase();
                valueB = (b.applicant_name || '').toLowerCase();
                break;
            case 'categorization':
                valueA = (a.categorization || '').toLowerCase();
                valueB = (b.categorization || '').toLowerCase();
                break;
            case 'quality_grade':
                valueA = (a.quality_grade || '').toLowerCase();
                valueB = (b.quality_grade || '').toLowerCase();
                break;
            default:
                valueA = 0;
                valueB = 0;
        }
        
        // Handle comparison based on data type
        let comparison;
        if (typeof valueA === 'number' && typeof valueB === 'number') {
            comparison = valueA - valueB;
        } else {
            comparison = valueA.toString().localeCompare(valueB.toString());
        }
        
        return currentSortOrder === 'asc' ? comparison : -comparison;
    });
    
    // Render the sorted data
    renderCandidateTable();
}

// Update the sort indicators in the table header
function updateSortIndicators() {
    // Reset all indicators
    document.querySelectorAll('[id^="sort_indicator_"]').forEach(indicator => {
        indicator.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />';
    });
    
    // Update the active indicator
    const activeIndicator = document.getElementById(`sort_indicator_${currentSortBy === 'overall_score' ? 'score' : currentSortBy}`);
    if (activeIndicator) {
        if (currentSortOrder === 'asc') {
            // Up arrow for ascending
            activeIndicator.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />';
        } else {
            // Down arrow for descending
            activeIndicator.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />';
        }
    }
}

// Helper function to get CSRF token
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length, cookie.length);
        }
    }
    return '';
}

// Show error message
function showErrorMessage(message) {
    // Create error element if it doesn't exist
    let errorElement = document.getElementById('error-message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.id = 'error-message';
        errorElement.className = 'error-message bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4';
        errorElement.style.display = 'none';
        
        const container = document.querySelector('.container');
        container.insertBefore(errorElement, container.firstChild);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}