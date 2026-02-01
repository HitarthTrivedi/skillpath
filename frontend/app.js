// Configuration
const API_BASE_URL = 'http://localhost:5000/api/v1';

// State Management
const AppState = {
    currentUser: null,
    currentPage: 'onboarding',
    roadmap: null,
    progressData: null,
    profileData: null
};

// Utility Functions
function showLoading() {
    document.getElementById('loading-overlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('active');
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function showStatusMessage(elementId, message, type = 'success') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `status-message active ${type}`;

    setTimeout(() => {
        element.classList.remove('active');
    }, 5000);
}

// Navigation
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const targetPage = link.dataset.page;

            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Show target page
            pages.forEach(page => page.classList.remove('active'));
            document.getElementById(`${targetPage}-page`).classList.add('active');

            AppState.currentPage = targetPage;

            // Load page data
            loadPageData(targetPage);
        });
    });
}

function loadPageData(page) {
    if (!AppState.currentUser) return;

    switch (page) {
        case 'roadmap':
            loadRoadmap();
            break;
        case 'progress':
            loadProgress();
            break;
        case 'profile':
            loadProfile();
            break;
    }
}

// Onboarding
function initOnboarding() {
    const form = document.getElementById('onboarding-form');
    // Ensure we start at step 1
    let currentStep = 1;
    const totalSteps = 4;

    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const submitBtn = document.getElementById('submit-btn');

    // Multi-step visibility logic
    function updateStepVisibility() {
        // Safe check for elements
        const steps = document.querySelectorAll('.form-step');
        if (!steps.length) return;

        steps.forEach(step => step.classList.remove('active'));

        const currentStepEl = document.querySelector(`.form-step[data-step="${currentStep}"]`);
        if (currentStepEl) currentStepEl.classList.add('active');

        document.querySelectorAll('.step-dot').forEach(dot => {
            const step = parseInt(dot.dataset.step);
            if (step <= currentStep) dot.classList.add('active');
            else dot.classList.remove('active');
        });

        if (prevBtn) prevBtn.style.display = currentStep > 1 ? 'inline-flex' : 'none';

        if (currentStep === totalSteps) {
            if (nextBtn) nextBtn.style.display = 'none';
            if (submitBtn) submitBtn.style.display = 'inline-flex';
        } else {
            if (nextBtn) nextBtn.style.display = 'inline-flex';
            if (submitBtn) submitBtn.style.display = 'none';
        }
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            // Debug: console.log('Next button clicked');
            const currentStepEl = document.querySelector(`.form-step[data-step="${currentStep}"]`);
            if (!currentStepEl) return;

            const inputs = currentStepEl.querySelectorAll('input, select, textarea');
            let isValid = true;
            let firstInvalid = null;

            inputs.forEach(input => {
                // Ignore hidden inputs (like photo base64) unless explicitly required
                if (input.type === 'hidden') return;

                // Reset error state
                input.classList.remove('error');

                if (!input.checkValidity()) {
                    input.reportValidity();
                    input.classList.add('error');
                    isValid = false;
                    if (!firstInvalid) firstInvalid = input;
                }
            });

            if (isValid) {
                if (currentStep < totalSteps) {
                    currentStep++;
                    updateStepVisibility();
                }
            } else {
                // Focus the first invalid field
                if (firstInvalid) firstInvalid.focus();
                showToast('Please fill in all required fields.', 'error');
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentStep > 1) {
                currentStep--;
                updateStepVisibility();
            }
        });
    }

    // --- Interaction Logic (Moved inside to ensure elements exist) ---

    // Photo Upload
    const photoInput = document.getElementById('profile-photo-input');
    const photoPreview = document.getElementById('profile-preview');
    const photoBase64 = document.getElementById('profile-photo-base64');

    if (photoInput && photoPreview && photoBase64) {
        photoInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                if (!file.type.startsWith('image/')) {
                    showToast('Please upload a valid image file', 'error');
                    return;
                }

                // Validate file size (e.g., < 2MB)
                if (file.size > 2 * 1024 * 1024) {
                    showToast('Image is too large (max 2MB)', 'error');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function (e) {
                    // Update DOM explicitly
                    photoPreview.innerHTML = ''; // Clear text
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.alt = "Profile Preview";
                    // Apply inline styles to be absolutely sure
                    img.style.width = '100%';
                    img.style.height = '100%';
                    img.style.objectFit = 'cover';
                    img.style.borderRadius = '50%';

                    photoPreview.appendChild(img);

                    photoBase64.value = e.target.result;
                };
                reader.onerror = function () {
                    showToast('Error reading file', 'error');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Relocation Toggle
    const relocationToggle = document.getElementById('relocation-toggle');
    const relocationInputGroup = document.getElementById('relocation-input-group');
    const relocationStatus = document.getElementById('relocation-status');
    const relocationGoal = document.getElementById('relocation-goal');

    if (relocationToggle && relocationInputGroup && relocationStatus) {
        relocationToggle.addEventListener('change', () => {
            if (relocationToggle.checked) {
                relocationInputGroup.style.display = 'block';
                relocationStatus.textContent = 'Yes';
                if (relocationGoal) relocationGoal.required = true;
            } else {
                relocationInputGroup.style.display = 'none';
                relocationStatus.textContent = 'No';
                if (relocationGoal) relocationGoal.required = false;
            }
        });
    }

    // Planning Horizon Slider
    const horizonSlider = document.getElementById('planning-horizon');
    const horizonValue = document.getElementById('horizon-value');

    if (horizonSlider && horizonValue) {
        horizonSlider.addEventListener('input', () => {
            const val = horizonSlider.value;
            horizonValue.textContent = `${val} Year${val > 1 ? 's' : ''}`;
        });
    }
    // --- End Interaction Logic ---

    // Initialize
    updateStepVisibility();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        showLoading();

        try {
            const formData = new FormData(form);
            const data = {
                name: formData.get('name'),
                email: formData.get('email'),
                major: formData.get('major'),
                university: formData.get('university'),
                gpa: parseFloat(formData.get('gpa')) || null,
                career_aspirations: formData.get('career_aspirations'),
                target_industries: formData.get('target_industries').split(',').map(s => s.trim()),
                current_skills: formData.get('current_skills').split(',').map(s => s.trim()),
                experience_level: formData.get('experience_level'),
                preferred_learning: formData.get('preferred_learning'),
                preferred_content_types: formData.get('preferred_content_types') ? formData.get('preferred_content_types').split(',').map(s => s.trim()) : [],
                time_commitment: formData.get('time_commitment'),

                // New Fields
                profile_photo: document.getElementById('profile-photo-base64').value || null,
                relocation_goal: relocationToggle.checked ? formData.get('relocation_goal') : null,
                extracurricular_interests: formData.get('extracurricular_interests') ? formData.get('extracurricular_interests').split(',').map(s => s.trim()) : [],
                planning_horizon_years: parseInt(horizonSlider.value)
            };

            // Using years directly, no specific timeline conversion needed for API beyond this
            const timeline = parseInt(horizonSlider.value) * 12; // Convert years to months for internal consistency if needed

            // Register user
            const registerResponse = await fetch(`${API_BASE_URL}/users/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: data.email,
                    name: data.name
                })
            });

            if (!registerResponse.ok && registerResponse.status !== 409) {
                throw new Error('Failed to register user');
            }

            const registerData = await registerResponse.json();
            const userId = registerData.user?.id || (await getUserIdByEmail(data.email));

            // Complete onboarding
            const onboardResponse = await fetch(`${API_BASE_URL}/users/onboard`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    ...data
                })
            });

            if (!onboardResponse.ok) {
                throw new Error('Failed to complete onboarding');
            }

            const onboardData = await onboardResponse.json();
            AppState.currentUser = { id: userId, ...data };

            // Generate growth path
            const roadmapResponse = await fetch(`${API_BASE_URL}/growth-path/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    timeline_months: timeline
                })
            });

            if (!roadmapResponse.ok) {
                throw new Error('Failed to generate growth path');
            }

            hideLoading();
            showToast('Growth path generated successfully! 🎉', 'success');
            showStatusMessage('onboarding-status', 'Success! Navigate to "My Roadmap" to see your personalized path.', 'success');

            // Switch to roadmap view
            setTimeout(() => {
                document.querySelector('[data-page="roadmap"]').click();
            }, 2000);

        } catch (error) {
            hideLoading();
            console.error('Onboarding error:', error);
            showToast('Error during onboarding. Please try again.', 'error');
            showStatusMessage('onboarding-status', error.message, 'error');
        }
    });
}

async function getUserIdByEmail(email) {
    // Helper to get user ID when already registered
    return 1; // Simplified for demo
}

// Roadmap Display
async function loadRoadmap() {
    if (!AppState.currentUser) {
        document.getElementById('roadmap-content').innerHTML =
            '<p class="empty-state">Please complete onboarding first</p>';
        return;
    }

    showLoading();

    try {
        // Load profile for analysis
        const profileResponse = await fetch(`${API_BASE_URL}/users/${AppState.currentUser.id}/profile`);
        const profileData = await profileResponse.json();

        // Display analysis
        if (profileData.profile && profileData.profile.analysis) {
            displayAnalysis(profileData.profile.analysis);
        }

        // Load roadmap
        const roadmapResponse = await fetch(`${API_BASE_URL}/growth-path/${AppState.currentUser.id}`);

        if (!roadmapResponse.ok) {
            document.getElementById('roadmap-content').innerHTML =
                '<p class="empty-state">No roadmap found. Please complete onboarding.</p>';
            hideLoading();
            return;
        }

        const roadmapData = await roadmapResponse.json();
        AppState.roadmap = roadmapData.enriched_roadmap;

        displayRoadmap(AppState.roadmap);
        hideLoading();

    } catch (error) {
        console.error('Error loading roadmap:', error);
        showToast('Error loading roadmap', 'error');
        hideLoading();
    }
}

function displayAnalysis(analysis) {
    const container = document.getElementById('profile-analysis');

    const html = `
        <h2>Your Profile Analysis</h2>
        <div class="analysis-grid">
            <div class="analysis-card">
                <h3>💪 Strengths</h3>
                <ul>
                    ${analysis.strengths.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
            <div class="analysis-card">
                <h3>🎯 Areas to Develop</h3>
                <ul>
                    ${analysis.gaps.map(g => `<li>${g}</li>`).join('')}
                </ul>
            </div>
            <div class="analysis-card">
                <h3>🚀 Career Paths</h3>
                <ul>
                    ${analysis.career_paths.map(c => `<li>${c}</li>`).join('')}
                </ul>
            </div>
            <div class="analysis-card">
                <h3>📚 Learning Tips</h3>
                <ul>
                    ${analysis.learning_tips.map(t => `<li>${t}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function displayRoadmap(roadmap) {
    const container = document.getElementById('roadmap-content');

    if (!roadmap || !roadmap.phases) {
        container.innerHTML = '<p class="empty-state">No roadmap data available</p>';
        return;
    }

    const html = roadmap.phases.map(phase => `
        <div class="phase-card">
            <div class="phase-header">
                <div>
                    <h2>${phase.title}</h2>
                    <span class="phase-badge">Phase ${phase.phase}</span>
                </div>
            </div>
            <p class="phase-focus">Focus: ${phase.focus}</p>

            ${renderPhaseItems('Courses 📚', phase.courses, 'course')}
            ${renderPhaseItems('Projects 💻', phase.projects, 'project')}
            ${renderPhaseItems('Certificates 🏆', phase.certificates, 'certificate')}
            ${renderPhaseItems('Internships 💼', phase.internships, 'internship')}
            ${renderPhaseItems('Tests 📝', phase.tests, 'test')}
        </div>
    `).join('');

    container.innerHTML = html;
}

function renderPhaseItems(title, items, type) {
    if (!items || items.length === 0) return '';

    return `
        <h3>${title}</h3>
        <div class="items-grid">
            ${items.map(item => renderItem(item, type)).join('')}
        </div>
    `;
}

function renderItem(item, type) {
    const progress = item.progress || { status: 'not_started' };

    let details = '';
    if (type === 'course') {
        details = `
            <div class="item-details">
                📍 ${item.platform} | ⏱️ ${item.duration || 'Self-paced'}
            </div>
        `;
    } else if (type === 'test') {
        details = `
            <div class="item-details">
                🎯 Target: ${item.target_score} | 📅 ${item.timing}
            </div>
        `;
    } else if (type === 'internship') {
        details = `
            <div class="item-details">
                📅 ${item.when} | 🏢 ${item.companies?.join(', ') || 'Various companies'}
            </div>
        `;
    } else if (type === 'certificate') {
        details = `
            <div class="item-details">
                🏫 ${item.provider} | 📅 ${item.timing}
            </div>
        `;
    } else if (type === 'project') {
        details = `
            <div class="item-details">
                🛠️ Skills: ${item.skills_demonstrated?.join(', ') || 'Multiple skills'}
            </div>
        `;
    }

    return `
        <div class="item-card" data-item-id="${item.id}">
            <div class="item-header">
                <div class="item-type">${type}</div>
            </div>
            <div class="item-name">${item.name || item.type}</div>
            ${details}
            ${item.description ? `<div class="item-details">${item.description}</div>` : ''}
            <div class="item-rationale">
                💡 ${item.rationale}
            </div>
            <div class="item-progress">
                <span class="status-badge status-${progress.status}">
                    ${progress.status.replace('_', ' ')}
                </span>
                ${progress.status === 'completed' && progress.encouragement_message ?
            `<div class="encouragement-message">${progress.encouragement_message}</div>` : ''}
            </div>
        </div>
    `;
}

// Progress Tracking
async function loadProgress() {
    if (!AppState.currentUser) {
        document.getElementById('progress-tasks').innerHTML =
            '<p class="empty-state">Please complete onboarding first</p>';
        return;
    }

    showLoading();

    try {
        // Load summary
        const summaryResponse = await fetch(`${API_BASE_URL}/progress/${AppState.currentUser.id}/summary`);
        const summary = await summaryResponse.json();
        displayProgressSummary(summary);

        // Load tasks
        const tasksResponse = await fetch(`${API_BASE_URL}/progress/${AppState.currentUser.id}/tasks`);
        const tasksData = await tasksResponse.json();
        AppState.progressData = tasksData.tasks;

        displayTasks(AppState.progressData);
        hideLoading();

    } catch (error) {
        console.error('Error loading progress:', error);
        showToast('Error loading progress', 'error');
        hideLoading();
    }
}

function displayProgressSummary(summary) {
    const container = document.getElementById('progress-summary');

    const percentage = summary.total > 0
        ? Math.round((summary.completed / summary.total) * 100)
        : 0;

    const html = `
        <div class="progress-stat">
            <div class="progress-stat-value">${summary.total}</div>
            <div class="progress-stat-label">Total Tasks</div>
        </div>
        <div class="progress-stat">
            <div class="progress-stat-value">${summary.completed}</div>
            <div class="progress-stat-label">Completed</div>
        </div>
        <div class="progress-stat">
            <div class="progress-stat-value">${summary.in_progress}</div>
            <div class="progress-stat-label">In Progress</div>
        </div>
        <div class="progress-stat">
            <div class="progress-stat-value">${percentage}%</div>
            <div class="progress-stat-label">Completion Rate</div>
        </div>
    `;

    container.innerHTML = html;
}

function displayTasks(tasks, filter = 'all') {
    const container = document.getElementById('progress-tasks');

    let filteredTasks = tasks;
    if (filter !== 'all') {
        filteredTasks = tasks.filter(t => t.item_type === filter);
    }

    if (filteredTasks.length === 0) {
        container.innerHTML = '<p class="empty-state">No tasks found</p>';
        return;
    }

    const html = filteredTasks.map(task => `
        <div class="task-card">
            <div class="task-info">
                <div class="task-name">${task.item_name}</div>
                <div class="task-meta">
                    <span class="item-type">${task.item_type}</span>
                    <span class="status-badge status-${task.status}">${task.status.replace('_', ' ')}</span>
                    ${task.completion_date ? `<span>✓ ${new Date(task.completion_date).toLocaleDateString()}</span>` : ''}
                </div>
                ${task.encouragement_message ?
            `<div class="encouragement-message">${task.encouragement_message}</div>` : ''}
            </div>
            <div class="task-actions">
                ${task.status !== 'completed' ? `
                    <button class="btn btn-secondary" onclick="updateTaskStatus('${task.item_id}', 'in_progress')">
                        ▶ Start
                    </button>
                    <button class="btn btn-success" onclick="updateTaskStatus('${task.item_id}', 'completed')">
                        ✓ Complete
                    </button>
                ` : '<span style="color: var(--success-color); font-weight: bold;">✓ Completed</span>'}
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}

async function updateTaskStatus(itemId, status) {
    if (!AppState.currentUser) return;

    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/progress/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: AppState.currentUser.id,
                item_id: itemId,
                status: status
            })
        });

        if (!response.ok) {
            throw new Error('Failed to update progress');
        }

        const data = await response.json();
        hideLoading();

        if (status === 'completed') {
            showToast('🎉 Great job! Task completed!', 'success');
            if (data.progress.encouragement_message) {
                setTimeout(() => {
                    showToast(data.progress.encouragement_message, 'info');
                }, 1000);
            }
        } else {
            showToast('Task status updated', 'success');
        }

        // Reload progress
        await loadProgress();

    } catch (error) {
        console.error('Error updating task:', error);
        showToast('Error updating task', 'error');
        hideLoading();
    }
}

// Progress Filters
function initProgressFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;
            if (AppState.progressData) {
                displayTasks(AppState.progressData, filter);
            }
        });
    });
}

// Profile Builder
async function loadProfile() {
    if (!AppState.currentUser) {
        return;
    }

    showLoading();

    try {
        // Load resume
        const resumeResponse = await fetch(`${API_BASE_URL}/profile/${AppState.currentUser.id}/resume`);
        const resumeData = await resumeResponse.json();

        // Populate editor fields
        if (resumeData.resume && resumeData.resume.header) {
            const h = resumeData.resume.header;
            if (document.getElementById('res-phone')) document.getElementById('res-phone').value = h.phone || '';
            if (document.getElementById('res-linkedin')) document.getElementById('res-linkedin').value = h.linkedin || '';
            if (document.getElementById('res-github')) document.getElementById('res-github').value = h.github || '';
            if (document.getElementById('res-portfolio')) document.getElementById('res-portfolio').value = h.portfolio || '';
        }

        displayResume(resumeData.resume);

        // Load LinkedIn
        const linkedinResponse = await fetch(`${API_BASE_URL}/profile/${AppState.currentUser.id}/linkedin`);
        const linkedinData = await linkedinResponse.json();
        displayLinkedIn(linkedinData);

        hideLoading();

    } catch (error) {
        console.error('Error loading profile:', error);
        showToast('Error loading profile', 'error');
        hideLoading();
    }
}

function displayResume(resume) {
    const container = document.getElementById('resume-content');

    if (!resume || !resume.header) {
        container.innerHTML = '<p class="empty-state">Loading resume data...</p>';
        return;
    }

    const h = resume.header;
    const contactParts = [];
    if (h.email) contactParts.push(h.email);
    if (h.phone) contactParts.push(h.phone);
    if (h.location) contactParts.push(h.location);
    if (h.linkedin) contactParts.push(`<a href="${h.linkedin}" target="_blank">LinkedIn</a>`);
    if (h.github) contactParts.push(`<a href="${h.github}" target="_blank">GitHub</a>`);
    if (h.portfolio) contactParts.push(`<a href="${h.portfolio}" target="_blank">Portfolio</a>`);

    let html = `
        <div class="resume-header">
            <div class="resume-name">${h.name}</div>
            <div class="resume-contact">
                ${contactParts.join(' | ')}
            </div>
        </div>
    `;

    // Education
    if (resume.education) {
        html += `
            <div class="resume-section-title">Education</div>
            <div class="resume-entry">
                <div class="resume-entry-header">
                    <span>${resume.education.university}</span>
                    <span>${resume.education.graduation_year}</span>
                </div>
                <div class="resume-entry-subheader">
                    <span>${resume.education.major}</span>
                </div>
                ${resume.education.gpa ? `<div>GPA: ${resume.education.gpa}</div>` : ''}
            </div>
        `;
    }

    // Skills
    if (resume.skills && resume.skills.length > 0) {
        html += `
            <div class="resume-section-title">Skills</div>
            <div>${resume.skills.join(', ')}</div>
        `;
    }

    // Experience
    if (resume.experience && resume.experience.length > 0) {
        html += `<div class="resume-section-title">Experience</div>`;
        resume.experience.forEach(exp => {
            html += `
                <div class="resume-entry">
                    <div class="resume-entry-header">
                        <span>${exp.title}</span>
                        <span>${exp.date}</span>
                    </div>
                     <ul class="resume-list">
                        ${exp.bullets.map(b => `<li>${b}</li>`).join('')}
                    </ul>
                </div>
            `;
        });
    }

    // Projects
    if (resume.projects && resume.projects.length > 0) {
        html += `<div class="resume-section-title">Projects</div>`;
        resume.projects.forEach(proj => {
            html += `
                <div class="resume-entry">
                    <div class="resume-entry-header">
                        <span>${proj.name}</span>
                        <span>${proj.date}</span>
                    </div>
                     <ul class="resume-list">
                        ${proj.bullets.map(b => `<li>${b}</li>`).join('')}
                    </ul>
                </div>
            `;
        });
    }

    // Certifications
    if (resume.certifications && resume.certifications.length > 0) {
        html += `<div class="resume-section-title">Certifications</div>`;
        resume.certifications.forEach(cert => {
            html += `
                <div class="resume-entry">
                    <div class="resume-entry-header">
                        <span>${cert.name}</span>
                        <span>${cert.date}</span>
                    </div>
                </div>
            `;
        });
    }

    container.innerHTML = html;
}

function displayLinkedIn(data) {
    const container = document.getElementById('linkedin-content');

    if (!data || (!data.post_ideas && !data.profile_summary && !data.skills_to_add)) {
        container.innerHTML = '<p class="empty-state">No LinkedIn suggestions available yet</p>';
        return;
    }

    let html = '';

    // Profile Summary
    if (data.profile_summary) {
        html += `
            <div class="linkedin-section">
                <h3>Profile Summary</h3>
                <div style="background: white; padding: 1.5rem; border-radius: 0.75rem; border-left: 4px solid #0077b5;">
                    ${data.profile_summary}
                </div>
            </div>
        `;
    }

    // Post Ideas
    if (data.post_ideas && data.post_ideas.length > 0) {
        html += `
            <div class="linkedin-section">
                <h3>Post Ideas</h3>
                ${data.post_ideas.map(post => `
                    <div class="post-idea-card">
                        <div class="post-idea-topic">${post.topic}</div>
                        <div class="post-idea-draft">${post.draft}</div>
                        <div class="post-hashtags">
                            ${post.hashtags.map(tag => `#${tag}`).join(' ')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Skills to Add
    if (data.skills_to_add && data.skills_to_add.length > 0) {
        html += `
            <div class="linkedin-section">
                <h3>Skills to Add to Profile</h3>
                <div class="skills-list">
                    ${data.skills_to_add.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

// Profile Tabs
function initProfileTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;

            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });

    // Resume Details Form
    const resumeForm = document.getElementById('resume-details-form');
    if (resumeForm) {
        resumeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!AppState.currentUser) return;

            showLoading();
            try {
                const response = await fetch(`${API_BASE_URL}/profile/details`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: AppState.currentUser.id,
                        phone_number: document.getElementById('res-phone').value,
                        linkedin_url: document.getElementById('res-linkedin').value,
                        github_url: document.getElementById('res-github').value,
                        portfolio_url: document.getElementById('res-portfolio').value
                    })
                });

                if (response.ok) {
                    showToast('Contact details saved!', 'success');
                    loadProfile(); // Reload to update resume
                }
            } catch (err) {
                console.error(err);
                showToast('Failed to save details', 'error');
            } finally {
                hideLoading();
            }
        });
    }
}

// Profile Actions
function initProfileActions() {
    document.getElementById('refresh-profile').addEventListener('click', async () => {
        if (!AppState.currentUser) return;

        showLoading();

        try {
            const response = await fetch(`${API_BASE_URL}/profile/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: AppState.currentUser.id })
            });

            if (!response.ok) {
                throw new Error('Failed to refresh profile');
            }

            hideLoading();
            showToast('Profile refreshed successfully!', 'success');
            await loadProfile();

        } catch (error) {
            console.error('Error refreshing profile:', error);
            showToast('Error refreshing profile', 'error');
            hideLoading();
        }
    });

    document.getElementById('download-resume').addEventListener('click', async () => {
        if (!AppState.currentUser) return;

        try {
            const response = await fetch(`${API_BASE_URL}/profile/${AppState.currentUser.id}/resume`);
            const data = await response.json();

            const blob = new Blob([JSON.stringify(data.resume, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'resume.json';
            a.click();
            URL.revokeObjectURL(url);

            showToast('Resume downloaded!', 'success');

        } catch (error) {
            console.error('Error downloading resume:', error);
            showToast('Error downloading resume', 'error');
        }
    });
}

// Roadmap Actions
function initRoadmapActions() {
    document.getElementById('refresh-roadmap').addEventListener('click', async () => {
        if (!AppState.currentUser) return;

        const confirmed = confirm('This will regenerate your growth path. Continue?');
        if (!confirmed) return;

        showLoading();

        try {
            const response = await fetch(`${API_BASE_URL}/growth-path/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: AppState.currentUser.id,
                    timeline_months: 12
                })
            });

            if (!response.ok) {
                throw new Error('Failed to regenerate roadmap');
            }

            hideLoading();
            showToast('Roadmap regenerated successfully!', 'success');
            await loadRoadmap();

        } catch (error) {
            console.error('Error regenerating roadmap:', error);
            showToast('Error regenerating roadmap', 'error');
            hideLoading();
        }
    });
}

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initOnboarding();
    initProgressFilters();
    initProfileTabs();
    initProfileActions();
    initRoadmapActions();

    console.log('🚀 AI-Powered Student Growth Planner initialized!');
});

// Make updateTaskStatus available globally
window.updateTaskStatus = updateTaskStatus;