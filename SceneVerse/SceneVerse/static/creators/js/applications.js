// Applications Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Basic application interactions

    // View application details
    const viewApplicationButtons = document.querySelectorAll('.application-actions .custom-border-btn');
    viewApplicationButtons.forEach(button => {
        button.addEventListener('click', function() {
            // In a real implementation, this would fetch application details
            // For now, we'll just show a modal
            const applicationModal = new bootstrap.Modal(document.getElementById('applicationDetailModal'));
            applicationModal.show();
        });
    });

    // View profile buttons
    const viewProfileButtons = document.querySelectorAll('.application-actions .custom-btn');
    viewProfileButtons.forEach(button => {
        button.addEventListener('click', function() {
            // In a real implementation, this would navigate to the artist's profile
            alert('This would navigate to the artist profile page in a real implementation.');
        });
    });

    // Bulk actions functionality
    const bulkActionsBtn = document.getElementById('bulkActionsBtn');
    if (bulkActionsBtn) {
        // Simple checkbox selection for demonstration
        // In a real implementation, this would handle actual bulk operations
        bulkActionsBtn.addEventListener('click', function() {
            // This would typically show a dropdown with bulk action options
            // For now, we'll just log the selected applications
            const selectedApplications = document.querySelectorAll('.application-select input:checked');
            console.log(`${selectedApplications.length} applications selected for bulk action`);
        });
    }

    // Filter form submission
    const filterForm = document.querySelector('.filter-card form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // In a real implementation, this would submit the filter criteria
            // and refresh the applications list
            console.log('Filter form submitted');
            // Simulate loading
            const applicationsList = document.querySelector('.applications-list');
            if (applicationsList) {
                applicationsList.style.opacity = '0.7';
                setTimeout(() => {
                    applicationsList.style.opacity = '1';
                }, 500);
            }
        });
    }
});