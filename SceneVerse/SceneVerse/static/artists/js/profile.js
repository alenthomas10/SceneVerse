// Profile Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeProfilePage();
    loadPortfolioHighlights();
    loadExperienceList();
});

// Initialize profile page
function initializeProfilePage() {
    // Set up event listeners
    document.getElementById('editProfileBtn').addEventListener('click', openEditProfileModal);
    document.getElementById('editCoverBtn').addEventListener('click', editCoverPhoto);
    document.getElementById('editAvatarBtn').addEventListener('click', editAvatar);

    // Set up edit buttons for different sections
    const editButtons = document.querySelectorAll('.btn-edit');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            editSection(section);
        });
    });

    // Initialize skills input
    initializeSkillsInput();
}

// Open edit profile modal
function openEditProfileModal() {
    const modal = new bootstrap.Modal(document.getElementById('editProfileModal'));
    modal.show();
}

// Save profile changes
function saveProfile() {
    const form = document.getElementById('editProfileForm');
    const formData = new FormData(form);

    // Show loading state
    const saveButton = document.querySelector('#editProfileModal .btn.custom-btn');
    const originalText = saveButton.innerHTML;
    saveButton.innerHTML = '<i class="bi-arrow-repeat spinner"></i> Saving...';
    saveButton.disabled = true;

    // Simulate API call
    setTimeout(() => {
        // Update profile information
        document.querySelector('.profile-details h1').textContent =
            `${formData.get('first_name')} ${formData.get('last_name')}`;
        document.querySelector('.profile-title').textContent = formData.get('title');
        document.getElementById('aboutText').textContent = formData.get('about');

        // Update location in about section
        const locationItem = document.querySelector('.detail-item:first-child span');
        locationItem.textContent = formData.get('location');

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
        modal.hide();

        // Reset button
        saveButton.innerHTML = originalText;
        saveButton.disabled = false;

        // Show success message
        showNotification('Profile updated successfully!', 'success');
        this.submit();
    }, 1500);
}

// Share profile


// Edit cover photo
function editCoverPhoto() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                document.querySelector('.cover-image img').src = event.target.result;
                showNotification('Cover photo updated!', 'success');
            };
            reader.readAsDataURL(file);
        }
    };
    input.click();
}

// Edit avatar
// Function to handle the file selection and submission
document.getElementById('fileInput').onchange = function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        const form = document.querySelector('form'); // Get the form

        reader.onload = function(event) {
            const imgSrc = event.target.result;

            // 1. Update avatar images for instant visual feedback
            document.querySelector('.profile-avatar img').src = imgSrc;
            document.querySelector('.user-avatar img').src = imgSrc;

            // 2. Show notification
            showNotification('Profile picture updated!', 'success');

            // 3. Submit the form. The 'fileInput' now contains the File object
            // and will be correctly sent to the server.
            form.submit();
        };

        // Read the file as Data URL (base64 string) to update the UI immediately
        reader.readAsDataURL(file);
    }
};

// Ensure your 'editAvatarBtn' click handler only triggers the file input click:
document.getElementById('editAvatarBtn').addEventListener('click', function() {
    document.getElementById('fileInput').click();
});

// Edit specific section
function editSection(section) {
    switch(section) {
        case 'about':
            openEditProfileModal();
            break;
        case 'skills':
            editSkills();
            break;
        case 'contact':
            editContactInfo();
            break;
        case 'experience':
            addExperience();
            break;
        default:
            console.log('Editing section:', section);
    }
}

// Initialize skills input
function initializeSkillsInput() {
    const skillsInput = document.getElementById('skillsInput');
    const skillsList = document.getElementById('skillsList');

    // Set current skills as initial value
    const currentSkills = Array.from(skillsList.querySelectorAll('.skill-tag'))
        .map(tag => tag.textContent)
        .join(', ');
    skillsInput.value = currentSkills;
}

// Edit skills
function editSkills() {
    openEditProfileModal();

    // Focus on skills input after modal opens
    setTimeout(() => {
        document.getElementById('skillsInput').focus();
    }, 500);
}

// Edit contact information
function editContactInfo() {
     openEditProfileModal();

    setTimeout(() => {
        document.getElementById('phoneInput').focus();
    }, 500);
}

// Add experience
function addExperience() {
    // In a real app, this would open an experience add modal
    showNotification('Experience editing feature coming soon!', 'info');
}

// Load portfolio highlights
function loadPortfolioHighlights() {
    const portfolioContainer = document.getElementById('portfolioHighlights');

    // Simulate loading
    portfolioContainer.innerHTML = `
        <div class="loading-spinner">
            <i class="bi-arrow-repeat"></i>
            <p>Loading portfolio...</p>
        </div>
    `;

    // Simulate API call
    setTimeout(() => {
        const portfolioItems = [
            { id: 1, title: 'Commercial Shoot', type: 'video', thumbnail: '/static/images/portfolio/1.jpg' },
            { id: 2, title: 'Film Scene', type: 'video', thumbnail: '/static/images/portfolio/2.jpg' },
            { id: 3, title: 'Fashion Campaign', type: 'image', thumbnail: '/static/images/portfolio/3.jpg' },
            { id: 4, title: 'Theater Performance', type: 'video', thumbnail: '/static/images/portfolio/4.jpg' }
        ];

        let portfolioHTML = '';
        portfolioItems.forEach(item => {
            portfolioHTML += `
                <div class="portfolio-item">
                    <img src="${item.thumbnail}" alt="${item.title}">
                    <div class="portfolio-overlay">
                        <h6>${item.title}</h6>
                        <small>${item.type === 'video' ? 'Video' : 'Photo'}</small>
                    </div>
                </div>
            `;
        });

        portfolioContainer.innerHTML = portfolioHTML;
    }, 1000);
}

// Load experience list
function loadExperienceList() {
    const experienceContainer = document.getElementById('experienceList');

    // Simulate loading
    experienceContainer.innerHTML = `
        <div class="loading-spinner">
            <i class="bi-arrow-repeat"></i>
            <p>Loading experience...</p>
        </div>
    `;

    // Simulate API call
    setTimeout(() => {
        const experienceItems = [
            {
                id: 1,
                title: 'Lead Actress - "Midnight Shadows"',
                company: 'Silver Screen Productions',
                period: 'Jan 2023 - Mar 2023',
                description: 'Played the lead role in a psychological thriller, working with acclaimed director Michael Chen.'
            },
            {
                id: 2,
                title: 'Supporting Role - "City Lights"',
                company: 'Urban Films',
                period: 'Aug 2022 - Nov 2022',
                description: 'Featured as the best friend character in this romantic comedy series.'
            },
            {
                id: 3,
                title: 'Commercial Model - Spring Collection',
                company: 'Fashion Forward Inc.',
                period: 'Mar 2022 - Apr 2022',
                description: 'Modeled for the national spring advertising campaign across print and digital media.'
            }
        ];

        let experienceHTML = '';
        experienceItems.forEach((item, index) => {
            experienceHTML += `
                <div class="experience-item">
                    <div class="experience-icon">
                        <i class="bi-${index === 0 ? 'star' : 'camera'}"></i>
                    </div>
                    <div class="experience-content">
                        <h5>${item.title}</h5>
                        <div class="experience-meta">
                            <span>${item.company}</span> • <span>${item.period}</span>
                        </div>
                        <p class="experience-description">${item.description}</p>
                    </div>
                </div>
            `;
        });

        experienceContainer.innerHTML = experienceHTML;
    }, 1000);
}


// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Add to page
    document.querySelector('.content-area').insertBefore(notification, document.querySelector('.content-area').firstChild);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Export profile data
function exportProfileData() {
    const profileData = {
        name: document.querySelector('.profile-details h1').textContent,
        title: document.querySelector('.profile-title').textContent,
        about: document.getElementById('aboutText').textContent,
        skills: Array.from(document.querySelectorAll('.skill-tag')).map(tag => tag.textContent),
        location: document.querySelector('.detail-item:first-child span').textContent,
        connections: document.querySelector('.stat-item:first-child .stat-number').textContent,
        projects: document.querySelector('.stat-item:nth-child(2) .stat-number').textContent,
        rating: document.querySelector('.stat-item:last-child .stat-number').textContent
    };

    // In a real app, this would download the data as a JSON file
    console.log('Profile data:', profileData);
    showNotification('Profile data exported successfully!', 'success');
}