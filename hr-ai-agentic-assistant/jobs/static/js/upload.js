// Elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const fileSelectionPanel = document.getElementById('file-selection-panel');
const fileList = document.getElementById('file-list');
const fileCount = document.getElementById('file-count');
const uploadBtn = document.getElementById('upload-btn');
const clearAllBtn = document.getElementById('clear-all-btn');
const progressSection = document.getElementById('progress-section');
const progressContainer = document.getElementById('progress-container');

// Selected files array
let selectedFiles = [];

// Event Listeners
browseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelection);
uploadBtn.addEventListener('click', uploadFiles);
clearAllBtn.addEventListener('click', clearAllFiles);

// Drag and drop functionality
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('border-blue-500', 'bg-blue-50');
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('border-blue-500', 'bg-blue-50');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('border-blue-500', 'bg-blue-50');
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
});

// Handle file selection
function handleFileSelection(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

// Add files to the selection
function addFiles(files) {
    // Filter for PDF and DOCX files
    const validFiles = files.filter(file => 
        file.type === 'application/pdf' || 
        file.name.toLowerCase().endsWith('.pdf') ||
        file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
        file.name.toLowerCase().endsWith('.docx')
    );
    
    // Add files to selectedFiles array (without duplicates)
    validFiles.forEach(file => {
        if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            selectedFiles.push(file);
        }
    });
    
    // Update UI
    updateFileList();
}

// Update file list UI
function updateFileList() {
    fileList.innerHTML = '';
    
    if (selectedFiles.length === 0) {
        fileSelectionPanel.classList.add('hidden');
        uploadBtn.disabled = true;
        return;
    }
    
    fileSelectionPanel.classList.remove('hidden');
    uploadBtn.disabled = false;
    
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'flex items-center justify-between p-3 bg-gray-50 rounded border';
        
        fileItem.innerHTML = `
            <div class="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                </svg>
                <div>
                    <div class="font-medium text-sm truncate max-w-xs">\${file.name}</div>
                    <div class="text-xs text-gray-500">\${formatFileSize(file.size)}</div>
                </div>
            </div>
            <button type="button" data-index="\${index}" class="remove-file text-red-600 hover:text-red-800">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            </button>
        `;
        
        fileList.appendChild(fileItem);
    });
    
    // Add event listeners to remove buttons
    document.querySelectorAll('.remove-file').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.currentTarget.getAttribute('data-index'));
            selectedFiles.splice(index, 1);
            updateFileList();
        });
    });
    
    // Update file count
    fileCount.textContent = `Selected: \${selectedFiles.length} file(s)`;
}

// Clear all files
function clearAllFiles() {
    selectedFiles = [];
    updateFileList();
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Upload files
function uploadFiles() {
    if (selectedFiles.length === 0) return;
    
    // Show progress section
    progressSection.classList.remove('hidden');
    
    // Disable upload button during upload
    uploadBtn.disabled = true;
    
    // Prepare form data
    const formData = new FormData();
    selectedFiles.forEach((file, index) => {
        formData.append('resume_files', file);
    });
    
    // Create progress items for each file
    const fileProgress = {};
    selectedFiles.forEach((file, index) => {
        const progressId = \`progress-\${index}\`;
        fileProgress[file.name] = progressId;
        
        const progressItem = document.createElement('div');
        progressItem.id = progressId;
        progressItem.className = 'p-3 bg-gray-50 rounded border';
        progressItem.innerHTML = \`
            <div class="flex justify-between mb-1">
                <span class="text-sm font-medium">\${file.name}</span>
                <span class="text-sm" id="status-\${index}">Uploading...</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full" id="progress-bar-\${index}" style="width: 0%"></div>
            </div>
            <div id="message-\${index}" class="mt-2 text-sm text-gray-600"></div>
        `;
        
        progressContainer.appendChild(progressItem);
    });
    
    // Perform upload with fetch
    fetch('{% url "applicant_upload" %}', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            data.results.forEach((result, index) => {
                const statusSpan = document.getElementById(\`status-\${index}\`);
                const progressBar = document.getElementById(\`progress-bar-\${index}\`);
                const messageDiv = document.getElementById(\`message-\${index}\`);
                
                // Update status and progress bar based on result
                if (result.status === 'success') {
                    statusSpan.textContent = '✓ Completed';
                    statusSpan.className = 'text-sm text-green-600';
                    progressBar.style.width = '100%';
                    messageDiv.textContent = result.message;
                    messageDiv.className = 'mt-2 text-sm text-green-600';
                } else if (result.status === 'duplicate') {
                    statusSpan.textContent = '⚠ Duplicate';
                    statusSpan.className = 'text-sm text-yellow-600';
                    progressBar.style.width = '100%';
                    
                    // Show duplicate information
                    let message = result.message || 'Duplicate detected';
                    if (result.duplicates && result.duplicates.length > 0) {
                        result.duplicates.forEach(dup => {
                            message += \`<br><span class="text-yellow-700">• \${dup.message}</span>\`;
                        });
                    }
                    messageDiv.innerHTML = message;
                    messageDiv.className = 'mt-2 text-sm text-yellow-600';
                } else {
                    statusSpan.textContent = '✗ Failed';
                    statusSpan.className = 'text-sm text-red-600';
                    progressBar.style.width = '100%';
                    messageDiv.textContent = result.message;
                    messageDiv.className = 'mt-2 text-sm text-red-600';
                }
            });
        } else {
            // Handle overall failure
            data.results.forEach((result, index) => {
                const statusSpan = document.getElementById(\`status-\${index}\`);
                const progressBar = document.getElementById(\`progress-bar-\${index}\`);
                const messageDiv = document.getElementById(\`message-\${index}\`);
                
                statusSpan.textContent = '✗ Failed';
                statusSpan.className = 'text-sm text-red-600';
                progressBar.style.width = '100%';
                messageDiv.textContent = result.message || 'Upload failed';
                messageDiv.className = 'mt-2 text-sm text-red-600';
            });
        }
        
        // Re-enable upload button after completion
        uploadBtn.disabled = false;
    })
    .catch(error => {
        console.error('Upload error:', error);
        
        // Update all progress items to show error
        selectedFiles.forEach((file, index) => {
            const statusSpan = document.getElementById(\`status-\${index}\`);
            const progressBar = document.getElementById(\`progress-bar-\${index}\`);
            const messageDiv = document.getElementById(\`message-\${index}\`);
            
            statusSpan.textContent = '✗ Error';
            statusSpan.className = 'text-sm text-red-600';
            progressBar.style.width = '100%';
            messageDiv.textContent = 'An error occurred during upload';
            messageDiv.className = 'mt-2 text-sm text-red-600';
        });
        
        // Re-enable upload button after error
        uploadBtn.disabled = false;
    });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}