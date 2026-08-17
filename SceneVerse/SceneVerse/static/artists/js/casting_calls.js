// Casting Calls JavaScript - Minimal Implementation

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    initializeCastingPage();
});

function initializeCastingPage() {
    // Set up modal event listeners
    setupModalListeners();

    // Set up filter functionality
    setupFilters();

}

function setupModalListeners() {
    const applyModal = document.getElementById('applyCastingModal');
    if (applyModal) {
        applyModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const castingId = button.getAttribute('data-casting-id');
            const castingTitle = button.getAttribute('data-casting-title');
            const castingType = button.getAttribute('data-casting-type');

            document.getElementById('applyCastingId').value = castingId;
            document.getElementById('castingTitle').textContent = castingTitle;
            document.getElementById('castingType').textContent = castingType;
        });
    }
}

function setupFilters() {
    const roleFilter = document.getElementById('roleTypeFilter');
    const locationFilter = document.getElementById('locationFilter');

    if (roleFilter) {
        roleFilter.addEventListener('change', filterCastingCalls);
    }

    if (locationFilter) {
        locationFilter.addEventListener('change', filterCastingCalls);
    }
}

function filterCastingCalls() {
    const roleValue = document.getElementById('roleTypeFilter').value;
    const locationValue = document.getElementById('locationFilter').value;

    // In a real application, this would make an API call
    // For now, we'll just log the filter values
    console.log('Filtering by role:', roleValue, 'and location:', locationValue);

    // Show a loading state
    showLoadingState();

    // Simulate API call delay
    setTimeout(() => {
        hideLoadingState();
        // In a real app, you would update the UI with filtered results
    }, 500);
}

function showLoadingState() {
    // Add loading indicator if needed
    console.log('Loading filtered results...');
}

function hideLoadingState() {
    // Remove loading indicator if needed
    console.log('Results loaded');
}

function saveCastingCall(castingId) {
    // Toggle save state
    const saveBtn = event.currentTarget;
    const icon = saveBtn.querySelector('i');

    if (icon.classList.contains('bi-bookmark')) {
        icon.classList.remove('bi-bookmark');
        icon.classList.add('bi-bookmark-fill');
        saveBtn.style.color = 'var(--primary-color)';
        showSaveSuccess('Casting call saved to your favorites');
    } else {
        icon.classList.remove('bi-bookmark-fill');
        icon.classList.add('bi-bookmark');
        saveBtn.style.color = '';
        showSaveSuccess('Casting call removed from favorites');
    }

    // In a real app, you would make an API call here
    console.log('Toggled save for casting call:', castingId);
}

function showSaveSuccess(message) {
    // Simple feedback for save action
    console.log(message);
}

function submitCastingApplication() {
    const form = document.getElementById('applyCastingForm');
    const formData = new FormData(form);

    // Basic validation
    const message = formData.get('message');

    if (!message.trim()) {
        showToast('Please add a message to the casting director.', 'error');
        return;
    }

    const mediaInput = document.getElementById('mediaInput');
    if (!mediaInput || mediaInput.files.length === 0) {
        showToast('Please attach at least one photo or video.', 'error');
        return;
    }

    // Show loading state
    const submitBtn = document.getElementById('submitApplicationBtn');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<i class="bi-arrow-repeat spinner"></i> Applying...';
    submitBtn.disabled = true;

    // Simulate API call
    setTimeout(() => {
        // Reset button
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;

        // Show success message
        showToast('Application sent successfully!', 'success');

        // Close modal
        const modalElement = document.getElementById('applyCastingModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) modal.hide();

        // Reset and submit form
        form.submit();
        form.reset();
    }, 1500);
}

// Removed showApplicationSuccess in favor of global showToast

// Functions from the original template that might be needed
function openMessages() {
    // Implementation for opening messages panel
    console.log('Opening messages panel');
}

function previewMedia(input) {
    // Media Preview Logic
    const mediaPreview = document.getElementById('mediaPreview');
    const files = Array.from(input.files);

    if (mediaPreview) {
        console.log('Previewing media files:', files);
        mediaPreview.innerHTML = ''; // Clear previous previews

        if (files.length === 0) {
            mediaPreview.innerHTML = '<p class="text-muted small col-12">No media selected</p>';
            return;
        }

        files.forEach(file => {
            const col = document.createElement('div');
            col.className = 'col-4 col-md-3 position-relative';

            const reader = new FileReader();
            reader.onload = function (e) {
                if (file.type.startsWith('image/')) {
                    col.innerHTML = `
                        <div class="ratio ratio-1x1">
                            <img src="${e.target.result}" class="rounded border border-secondary" style="object-fit: cover;">
                        </div>
                    `;
                } else if (file.type.startsWith('video/')) {
                    col.innerHTML = `
                        <div class="ratio ratio-1x1 bg-dark rounded border border-secondary">
                            <video src="${e.target.result}" class="w-100 h-100 object-fit-cover" controls></video> 
                        </div>
                    `;
                }
                mediaPreview.appendChild(col);
            };
            reader.readAsDataURL(file);
        });
    } else {
        console.error('Media preview container not found');
    }
}

function findProjects() {
    window.location.href = '/artists/projects/';
}