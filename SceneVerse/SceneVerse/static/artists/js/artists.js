// Artists Dashboard JavaScript
let currentUser = {
    id: 1,
    name: "Sarah Actor",
    avatar: "/static/images/avatars/artist-avatar.jpg",
    role: "artist"
};

let selectedMedia = [];
let currentConversation = null;

document.addEventListener('DOMContentLoaded', function () {
    initializeDashboard();

    // Only load components if their containers exist
    if (document.getElementById('feedPosts')) loadFeedPosts();
    if (document.getElementById('recommendedProjects')) loadRecommendedProjects();
    if (document.getElementById('activeCasting')) loadActiveCasting();
    if (document.getElementById('networkSuggestions')) loadNetworkSuggestions();

    // Always load conversations if message panel exists or for notifications
    if (document.getElementById('conversationsList') || document.getElementById('messagesPanel')) {
        loadConversations();
    }
});

function initializeDashboard() {
    // Mobile sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('mobile-open');
        });
    }

    // Global search functionality
    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('input', debounce(function (e) {
            performGlobalSearch(e.target.value);
        }, 300));
    }

    // Message search
    const messageSearch = document.getElementById('messageSearch');
    if (messageSearch) {
        messageSearch.addEventListener('input', debounce(function (e) {
            searchConversations(e.target.value);
        }, 300));
    }

    // Notification button
    const notificationBtn = document.getElementById('notificationBtn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', function () {
            showNotifications();
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (event) {
        if (window.innerWidth < 992) {
            if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
                sidebar.classList.remove('mobile-open');
            }
        }
    });
}

// Feed Posts Management
async function loadFeedPosts() {
    if (!document.getElementById('feedPosts')) return;
    try {
        // Simulate API call - replace with actual Django endpoint
        const response = await fetch('/api/artists/feed/');
        const data = await response.json();

        if (data.success) {
            renderFeedPosts(data.posts);
        } else {
            throw new Error(data.message || 'Failed to load feed');
        }
    } catch (error) {
        console.error('Error loading feed:', error);
        showError('Failed to load feed posts');
    }
}

function renderFeedPosts(posts) {
    const feedContainer = document.getElementById('feedPosts');

    if (posts.length === 0) {
        feedContainer.innerHTML = `
            <div class="content-card text-center py-5">
                <i class="bi-newspaper" style="font-size: 3rem; color: rgba(255,255,255,0.3);"></i>
                <h4 class="mt-3">No posts yet</h4>
                <p class="text-muted">Be the first to share something with the community!</p>
                <button class="btn custom-btn mt-2" data-bs-toggle="modal" data-bs-target="#createPostModal">
                    Create First Post
                </button>
            </div>
        `;
        return;
    }

    feedContainer.innerHTML = posts.map(post => `
        <div class="feed-post" data-post-id="${post.id}">
            <div class="post-header">
                <div class="post-author">
                    <div class="user-avatar-sm">
                        <img src="${post.author.avatar}" alt="${post.author.name}">
                    </div>
                    <div class="author-info">
                        <h6>${post.author.name}</h6>
                        <span class="post-time">${formatTimeAgo(post.created_at)} • ${getVisibilityIcon(post.visibility)}</span>
                    </div>
                </div>
                <div class="post-options">
                    <button class="btn btn-sm custom-border-btn" onclick="togglePostOptions(${post.id})">
                        <i class="bi-three-dots"></i>
                    </button>
                </div>
            </div>

            <div class="post-content">
                <p class="post-caption">${post.caption}</p>

                ${post.media && post.media.length > 0 ? renderPostMedia(post.media) : ''}

                ${post.achievement ? `
                    <div class="achievement-badge">
                        <i class="bi-award"></i>
                        <span>${post.achievement}</span>
                    </div>
                ` : ''}
            </div>

            <div class="post-actions">
                <button class="post-action ${post.liked ? 'active' : ''}" onclick="likePost(${post.id})">
                    <i class="bi-heart${post.liked ? '-fill' : ''}"></i>
                    <span>${post.likes_count}</span>
                </button>
                <button class="post-action" onclick="focusComment(${post.id})">
                    <i class="bi-chat"></i>
                    <span>${post.comments_count}</span>
                </button>
                <button class="post-action" onclick="sharePost(${post.id})">
                    <i class="bi-share"></i>
                    <span>Share</span>
                </button>
                <button class="post-action" onclick="savePost(${post.id})">
                    <i class="bi-bookmark${post.saved ? '-fill' : ''}"></i>
                    <span>Save</span>
                </button>
            </div>

            <div class="post-comments" id="comments-${post.id}">
                <!-- Comments will be loaded here when expanded -->
            </div>
        </div>
    `).join('');
}

function renderPostMedia(media) {
    if (media.length === 1) {
        const item = media[0];
        if (item.type === 'image') {
            return `<div class="post-media"><img src="${item.url}" alt="Post image"></div>`;
        } else {
            return `<div class="post-media"><video controls><source src="${item.url}" type="video/mp4"></video></div>`;
        }
    } else {
        return `
            <div class="post-media">
                <div class="media-grid grid-${Math.min(media.length, 3)}">
                    ${media.slice(0, 4).map((item, index) => `
                        <img src="${item.url}" alt="Post image ${index + 1}"
                             ${media.length > 4 && index === 3 ? `style="position: relative;"><div class="media-overlay">+${media.length - 3}</div>` : ''}>
                    `).join('')}
                </div>
            </div>
        `;
    }
}

// Post Creation
function openCreatePostModal(type = null) {
    const modal = new bootstrap.Modal(document.getElementById('createPostModal'));
    modal.show();

    if (type) {
        setTimeout(() => {
            if (type === 'image') {
                triggerMediaUpload('image');
            } else if (type === 'video') {
                triggerMediaUpload('video');
            } else if (type === 'achievement') {
                addAchievement();
            }
        }, 500);
    }
}

function triggerMediaUpload(type) {
    const inputId = type === 'image' ? 'imageUpload' : 'videoUpload';
    document.getElementById(inputId).click();
}

function handleMediaUpload(input, type) {
    const files = Array.from(input.files);
    selectedMedia = [...selectedMedia, ...files.map(file => ({
        file: file,
        type: type,
        url: URL.createObjectURL(file)
    }))];

    updateMediaPreview();
}

function updateMediaPreview() {
    const preview = document.getElementById('mediaPreview');

    if (selectedMedia.length === 0) {
        preview.style.display = 'none';
        preview.classList.remove('has-media');
        return;
    }

    preview.style.display = 'block';
    preview.classList.add('has-media');

    preview.innerHTML = selectedMedia.map((media, index) => `
        <div class="media-preview-item">
            ${media.type === 'image'
            ? `<img src="${media.url}" alt="Preview ${index + 1}">`
            : `<video controls><source src="${media.url}" type="video/mp4"></video>`
        }
            <button type="button" class="remove-media" onclick="removeMedia(${index})">
                <i class="bi-x"></i>
            </button>
        </div>
    `).join('');
}

function removeMedia(index) {
    selectedMedia.splice(index, 1);
    updateMediaPreview();
}

function addAchievement() {
    const achievement = prompt('Enter your achievement:');
    if (achievement) {
        // Store achievement for post creation
        document.querySelector('.post-caption').value += `\n\n🎉 Achievement: ${achievement}`;
    }
}

async function createPost() {
    const form = document.getElementById('createPostForm');
    const formData = new FormData(form);

    const postData = {
        caption: formData.get('caption'),
        visibility: formData.get('visibility'),
        media: selectedMedia,
        type: 'post'
    };

    try {
        // Create FormData for file upload
        const uploadData = new FormData();
        uploadData.append('caption', postData.caption);
        uploadData.append('visibility', postData.visibility);
        uploadData.append('type', postData.type);

        selectedMedia.forEach((media, index) => {
            uploadData.append(`media_${index}`, media.file);
        });

        const response = await fetch('/api/artists/posts/create/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: uploadData
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Post created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createPostModal')).hide();
            form.reset();
            selectedMedia = [];
            updateMediaPreview();
            loadFeedPosts(); // Reload feed
        } else {
            throw new Error(data.message || 'Failed to create post');
        }
    } catch (error) {
        console.error('Error creating post:', error);
        showError('Failed to create post: ' + error.message);
    }
}

// Projects and Casting Calls
async function loadRecommendedProjects() {
    try {
        const response = await fetch('/api/artists/projects/recommended/');
        const data = await response.json();

        if (data.success) {
            renderRecommendedProjects(data.projects);
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

function renderRecommendedProjects(projects) {
    const container = document.getElementById('recommendedProjects');

    container.innerHTML = projects.map(project => `
        <div class="project-item">
            <div class="project-info">
                <h6>${project.title}</h6>
                <p class="project-meta">${project.creator_name} • ${project.type}</p>
                <div class="project-tags">
                    ${project.roles.map(role => `<span class="role-tag">${role}</span>`).join('')}
                </div>
            </div>
            <div class="project-actions">
                <button class="btn btn-sm custom-btn" onclick="applyToProject(${project.id})">Apply</button>
            </div>
        </div>
    `).join('');
}

async function loadActiveCasting() {
    try {
        const response = await fetch('/api/artists/casting/active/');
        const data = await response.json();

        if (data.success) {
            renderActiveCasting(data.casting_calls);
        }
    } catch (error) {
        console.error('Error loading casting calls:', error);
    }
}

function renderActiveCasting(castingCalls) {
    const container = document.getElementById('activeCasting');

    container.innerHTML = castingCalls.map(casting => `
        <div class="casting-item">
            <div class="casting-info">
                <h6>${casting.role}</h6>
                <p class="casting-meta">${casting.project_title} • ${casting.deadline}</p>
                <div class="casting-details">
                    <span class="detail">${casting.location}</span>
                    <span class="detail">${casting.payment}</span>
                </div>
            </div>
            <div class="casting-actions">
                <button class="btn btn-sm custom-border-btn" onclick="viewCasting(${casting.id})">View</button>
            </div>
        </div>
    `).join('');
}

function applyToProject(projectId) {
    // Load project details and open application modal
    fetch(`/api/projects/${projectId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('applyProjectId').value = projectId;
                document.getElementById('projectTitle').textContent = data.project.title;
                document.getElementById('projectCreator').textContent = `by ${data.project.creator_name}`;

                const modal = new bootstrap.Modal(document.getElementById('applyProjectModal'));
                modal.show();

                loadPortfolioForApplication();
            }
        })
        .catch(error => {
            console.error('Error loading project:', error);
            showError('Failed to load project details');
        });
}

async function submitApplication() {
    const form = document.getElementById('applyProjectForm');
    const formData = new FormData(form);

    const applicationData = {
        project_id: formData.get('project_id'),
        applied_role: formData.get('applied_role'),
        message: formData.get('message'),
        portfolio_items: Array.from(document.querySelectorAll('#portfolioSelection input:checked')).map(input => input.value)
    };

    try {
        const response = await fetch('/api/artists/applications/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(applicationData)
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Application submitted successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('applyProjectModal')).hide();
            form.reset();
            updateApplicationsCount();
        } else {
            throw new Error(data.message || 'Failed to submit application');
        }
    } catch (error) {
        console.error('Error submitting application:', error);
        showError('Failed to submit application: ' + error.message);
    }
}

// Network and Connections
async function loadNetworkSuggestions() {
    try {
        const response = await fetch('/api/artists/network/suggestions/');
        const data = await response.json();

        if (data.success) {
            renderNetworkSuggestions(data.suggestions);
        }
    } catch (error) {
        console.error('Error loading suggestions:', error);
    }
}

function renderNetworkSuggestions(suggestions) {
    const container = document.getElementById('networkSuggestions');

    container.innerHTML = suggestions.map(user => `
        <div class="suggestion-item">
            <div class="user-avatar-sm">
                <img src="${user.avatar}" alt="${user.name}">
            </div>
            <div class="suggestion-info">
                <h6>${user.name}</h6>
                <p class="suggestion-meta">${user.role} • ${user.mutual_connections} mutual connections</p>
            </div>
            <div class="suggestion-actions">
                <button class="btn btn-sm custom-border-btn" onclick="connectUser(${user.id})">Connect</button>
            </div>
        </div>
    `).join('');
}

// Messaging System
function openMessages() {
    document.getElementById('messagesPanel').classList.add('open');
}

function closeMessages() {
    document.getElementById('messagesPanel').classList.remove('open');
    document.getElementById('chatWindow').style.display = 'none';
    currentConversation = null;
}

async function loadConversations() {
    try {
        const response = await fetch('/api/artists/messages/conversations/');
        const data = await response.json();

        if (data.success) {
            renderConversations(data.conversations);
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

function renderConversations(conversations) {
    const container = document.getElementById('conversationsList');

    container.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${conv.unread ? 'unread' : ''}" onclick="openChat(${conv.id}, ${conv.other_user.id})">
            <div class="user-avatar-sm">
                <img src="${conv.other_user.avatar}" alt="${conv.other_user.name}">
            </div>
            <div class="conversation-info">
                <h6>${conv.other_user.name}</h6>
                <p class="last-message">${conv.last_message}</p>
                <span class="message-time">${formatTimeAgo(conv.updated_at)}</span>
            </div>
            ${conv.unread ? '<span class="unread-badge"></span>' : ''}
        </div>
    `).join('');
}

function openChat(conversationId, userId) {
    currentConversation = conversationId;

    // Show chat window
    document.getElementById('chatWindow').style.display = 'flex';

    // Load chat messages
    loadChatMessages(conversationId);

    // Mark as read
    markConversationAsRead(conversationId);
}

async function loadChatMessages(conversationId) {
    try {
        const response = await fetch(`/api/artists/messages/conversations/${conversationId}/`);
        const data = await response.json();

        if (data.success) {
            renderChatMessages(data.messages);
        }
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function renderChatMessages(messages) {
    const container = document.getElementById('chatMessages');

    container.innerHTML = messages.map(msg => `
        <div class="message ${msg.sender_id === currentUser.id ? 'sent' : 'received'}">
            <div class="message-text">${msg.content}</div>
            <div class="message-time">${formatTime(msg.created_at)}</div>
        </div>
    `).join('');

    container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const content = input.value.trim();

    if (!content || !currentConversation) return;

    try {
        const response = await fetch('/api/artists/messages/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                conversation_id: currentConversation,
                content: content
            })
        });

        const data = await response.json();

        if (data.success) {
            input.value = '';
            loadChatMessages(currentConversation);
        } else {
            throw new Error(data.message || 'Failed to send message');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Failed to send message');
    }
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}

function formatTime(dateString) {
    return new Date(dateString).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getVisibilityIcon(visibility) {
    const icons = {
        'public': '🌍',
        'network': '👥',
        'private': '🔒'
    };
    return icons[visibility] || '🌍';
}

function getCSRFToken() {
    // CSRF token retrieval for Django
    const name = 'csrftoken';
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

    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function showError(message) {
    showNotification(message, 'danger');
}

// Quick Action Functions
function findProjects() {
    window.location.href = '/artists/projects/';
}

function updateApplicationsCount() {
    // Update applications count badge
    const countElement = document.getElementById('applicationsCount');
    const currentCount = parseInt(countElement.textContent) || 0;
    countElement.textContent = currentCount + 1;

    // Update stats
    const statsElement = document.getElementById('applicationsStat');
    statsElement.textContent = currentCount + 1;
}

// Initialize real-time updates for messages
function initializeRealTimeUpdates() {
    // Simulate real-time message updates
    setInterval(() => {
        if (currentConversation) {
            loadChatMessages(currentConversation);
        }
        loadConversations();
    }, 10000); // Update every 10 seconds
}

// Start real-time updates
initializeRealTimeUpdates();