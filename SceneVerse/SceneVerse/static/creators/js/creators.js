// Creators Dashboard JavaScript with Sidebar Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-open');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth < 992) {
            if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
                sidebar.classList.remove('mobile-open');
            }
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Project type selection with visual feedback
    const typeOptions = document.querySelectorAll('.type-option');
    typeOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Remove active class from all labels
            document.querySelectorAll('.type-label').forEach(label => {
                label.classList.remove('active');
            });

            // Add active class to selected label
            if (this.checked) {
                this.nextElementSibling.classList.add('active');
            }
        });
    });

    // Project item click handlers
    const projectItems = document.querySelectorAll('.project-item');
    projectItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (!e.target.closest('.project-actions')) {
                const projectTitle = this.querySelector('h5').textContent;
                console.log('Navigating to project:', projectTitle);
                // Add navigation logic here
            }
        });
    });

    // Application status updates
    const statusBadges = document.querySelectorAll('.badge');
    statusBadges.forEach(badge => {
        badge.addEventListener('click', function() {
            if (this.classList.contains('status-pending') ||
                this.classList.contains('status-reviewed')) {
                const currentStatus = this.textContent.trim();
                const newStatus = prompt('Update application status:', currentStatus);
                if (newStatus && newStatus !== currentStatus) {
                    this.textContent = newStatus;
                    updateApplicationStatus(newStatus);
                }
            }
        });
    });

    // Search functionality
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            // Add search logic here
            console.log('Searching for:', searchTerm);
        });
    }

    // Form handling
    const newProjectForm = document.getElementById('newProjectForm');
    if (newProjectForm) {
        newProjectForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add form submission logic
            console.log('Creating new project...');
            this.submit();
            // Get selected project type
            const selectedType = document.querySelector('input[name="projectType"]:checked');
            if (selectedType) {
                console.log('Project type:', selectedType.value);
            }
        });
    }

    // Stats counter animation
    function animateStats() {
        const statNumbers = document.querySelectorAll('.stat-info h3');
        statNumbers.forEach(stat => {
            const target = parseInt(stat.textContent);
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    stat.textContent = target;
                    clearInterval(timer);
                } else {
                    stat.textContent = Math.floor(current);
                }
            }, 30);
        });
    }

    // Initialize stats animation when in viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats();
                observer.unobserve(entry.target);
            }
        });
    });

    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        observer.observe(statsSection);
    }

    // Real-time updates simulation
    function simulateRealTimeUpdates() {
        setInterval(() => {
            // Simulate new message count update
            const messageCount = document.querySelector('.stat-info h3:nth-child(3)');
            if (messageCount && Math.random() > 0.7) {
                const current = parseInt(messageCount.textContent);
                messageCount.textContent = current + 1;

                // Add notification animation
                messageCount.style.animation = 'pulse 0.5s ease-in-out';
                setTimeout(() => {
                    messageCount.style.animation = '';
                }, 500);
            }
        }, 15000);
    }

    simulateRealTimeUpdates();

    // Project type color coding
    function initializeProjectBadges() {
        const projects = document.querySelectorAll('.project-item');
        projects.forEach(project => {
            const badge = project.querySelector('.project-badge');
            if (badge) {
                const type = Array.from(badge.classList).find(cls =>
                    cls !== 'project-badge' && !cls.startsWith('bi-')
                );

                if (type) {
                    // Add specific styling based on project type
                    console.log('Project type detected:', type);
                }
            }
        });
    }

    initializeProjectBadges();

    // Utility function to update application status
    function updateApplicationStatus(status) {
        // This would typically make an API call
        console.log('Updating application status to:', status);

        // Show success notification
        showNotification('Application status updated successfully!', 'success');
    }

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    // Initialize any modals with additional functionality
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            console.log('Modal opening:', this.id);
        });
    });
});

// CSS Animation for notifications and interactions
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }

    .type-label.active {
        animation: pulse 0.3s ease-in-out;
    }

    .sidebar {
        animation: slideIn 0.3s ease-out;
    }

    .stat-card:hover .stat-icon {
        animation: pulse 0.5s ease-in-out;
    }
`;
document.head.appendChild(style);
