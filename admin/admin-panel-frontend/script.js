// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Global state
let currentUser = null;
let currentPage = 'login-page';

// Utility Functions
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    document.getElementById(pageId).classList.add('active');
    currentPage = pageId;
}

// API Functions
async function apiCall(endpoint, method = 'GET', data = null) {
    showLoading();
    
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        console.log(`API Call: ${method} ${url}`);
        
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            config.body = JSON.stringify(data);
            console.log('Request data:', data);
        }
        
        const response = await fetch(url, config);
        console.log('Response status:', response.status);
        
        const result = await response.json();
        console.log('Response data:', result);
        
        if (!response.ok) {
            throw new Error(result.detail || 'Something went wrong');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    } finally {
        hideLoading();
    }
}

// Authentication Functions
async function login(credentials) {
    try {
        const result = await apiCall('/auth/login', 'POST', credentials);
        showToast(result.message || 'Login successful', 'success');
        
        // Store token in localStorage
        if (result.access_token) {
            localStorage.setItem('admin_token', result.access_token);
        }
        
        currentUser = result.user || { name: 'Admin', role: 'admin' };
        localStorage.setItem('admin_user', JSON.stringify(currentUser));
        
        document.getElementById('user-name').textContent = `Welcome, ${currentUser.name}`;
        
        showPage('dashboard-page');
        loadCourses();
        
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

async function logout() {
    try {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_user');
        currentUser = null;
        showPage('login-page');
        
        // Clear forms
        document.querySelectorAll('form').forEach(form => form.reset());
        
        showToast('Logged out successfully', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Course Functions
async function loadCourses() {
    try {
        const token = localStorage.getItem('admin_token');
        const response = await fetch(`${API_BASE_URL}/courses/list?token=${token}`);
        const result = await response.json();
        
        const coursesContainer = document.getElementById('courses-grid');
        
        if (result.courses && result.courses.length > 0) {
            coursesContainer.innerHTML = result.courses.map(course => `
                <div class="course-card">
                    <div class="course-header">
                        <h3 class="course-title">${course.title}</h3>
                        <span class="course-price">$${course.price}</span>
                    </div>
                    <p class="course-description">${course.description}</p>
                    <div class="course-meta">
                        <span>Teacher: ${course.teacher_name || 'N/A'}</span>
                        <span>Enrolled: ${course.enrolled_count || 0}</span>
                    </div>
                    <div class="course-actions">
                        <button class="btn btn-success" onclick="addVideo('${course.id}')">
                            <i class="fas fa-video"></i> Add Video
                        </button>
                        <button class="btn btn-edit" onclick="editCourse('${course.id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-delete" onclick="deleteCourse('${course.id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            coursesContainer.innerHTML = '<div class="no-data">No courses found</div>';
        }
    } catch (error) {
        showToast('Failed to load courses', 'error');
        console.error('Error loading courses:', error);
    }
}

async function createCourse(courseData) {
    try {
        const formData = new FormData();
        formData.append('token', localStorage.getItem('admin_token'));
        formData.append('title', courseData.title);
        formData.append('description', courseData.description);
        formData.append('price', courseData.price);
        formData.append('teacher_id', courseData.teacherId);
        formData.append('visible', true);
        
        if (courseData.thumbnail) {
            formData.append('thumbnail', courseData.thumbnail);
        }
        
        const response = await fetch(`${API_BASE_URL}/courses/create`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Course creation failed');
        }
        
        showToast('Course created successfully', 'success');
        
        // Hide form and reload courses
        document.getElementById('course-form-container').classList.add('hidden');
        document.getElementById('course-form').reset();
        await loadCourses();
        
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

async function updateCourse(courseId, courseData) {
    try {
        const formData = new FormData();
        formData.append('token', localStorage.getItem('admin_token'));
        formData.append('course_id', courseId);
        formData.append('title', courseData.title);
        formData.append('description', courseData.description);
        formData.append('price', courseData.price);
        formData.append('teacher_id', courseData.teacherId);
        formData.append('visible', true);
        
        if (courseData.thumbnail) {
            formData.append('thumbnail', courseData.thumbnail);
        }
        
        const response = await fetch(`${API_BASE_URL}/courses/update`, {
            method: 'PUT',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Course update failed');
        }
        
        showToast('Course updated successfully', 'success');
        
        // Reset form and reload courses
        resetCourseForm();
        await loadCourses();
        
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

function resetCourseForm() {
    document.getElementById('course-form-container').classList.add('hidden');
    document.getElementById('course-form').reset();
    delete document.getElementById('course-form').dataset.courseId;
    
    // Reset form title and button
    document.querySelector('#course-form-container h2').textContent = 'Create New Course';
    document.querySelector('#course-form button[type="submit"]').innerHTML = 'Create Course';
}

async function deleteCourse(courseId) {
    if (!confirm('Are you sure you want to delete this course?')) return;
    
    try {
        const token = localStorage.getItem('admin_token');
        const response = await fetch(`${API_BASE_URL}/courses/delete?token=${token}&course_id=${courseId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Course deleted successfully', 'success');
            await loadCourses();
        } else {
            throw new Error(result.detail || 'Delete failed');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Video Functions
function addVideo(courseId) {
    console.log('Adding video to course:', courseId);
    if (!courseId || courseId === 'undefined') {
        showToast('Invalid course ID', 'error');
        return;
    }
    document.getElementById('video-course-id').value = courseId;
    document.getElementById('video-form-container').classList.remove('hidden');
}

async function uploadVideo(videoData) {
    try {
        showLoading();
        
        const formData = new FormData();
        formData.append('token', localStorage.getItem('admin_token'));
        formData.append('course_id', videoData.courseId);
        formData.append('title', videoData.title);
        formData.append('description', videoData.description);
        formData.append('video_file', videoData.videoFile);
        
        const response = await fetch(`${API_BASE_URL}/courses/add-video`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Video upload failed');
        }
        
        showToast('Video uploaded successfully', 'success');
        
        // Hide form and reload courses
        document.getElementById('video-form-container').classList.add('hidden');
        document.getElementById('video-form').reset();
        await loadCourses();
        
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

// Form Handlers
function handleLoginForm(event) {
    event.preventDefault();
    
    const credentials = {
        email: document.getElementById('login-email').value.trim(),
        password: document.getElementById('login-password').value
    };
    
    if (!credentials.email || !credentials.password) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    login(credentials);
}

function handleCourseForm(event) {
    event.preventDefault();
    
    const thumbnailFile = document.getElementById('course-thumbnail').files[0];
    const courseId = document.getElementById('course-form').dataset.courseId;
    
    const courseData = {
        title: document.getElementById('course-title').value.trim(),
        description: document.getElementById('course-description').value.trim(),
        price: parseFloat(document.getElementById('course-price').value),
        teacherId: document.getElementById('teacher-id').value.trim(),
        thumbnail: thumbnailFile || null
    };
    
    // Validation
    if (!courseData.title || !courseData.description || courseData.price < 0 || !courseData.teacherId) {
        showToast('Please fill in all fields correctly', 'error');
        return;
    }
    
    if (courseId) {
        updateCourse(courseId, courseData);
    } else {
        createCourse(courseData);
    }
}

function handleVideoForm(event) {
    event.preventDefault();
    
    const videoFile = document.getElementById('video-file').files[0];
    
    const videoData = {
        courseId: document.getElementById('video-course-id').value,
        title: document.getElementById('video-title').value.trim(),
        description: document.getElementById('video-description').value.trim(),
        videoFile: videoFile
    };
    
    // Validation
    if (!videoData.title || !videoData.description || !videoData.videoFile) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    uploadVideo(videoData);
}

// Placeholder functions
function editCourse(courseId) {
    // Load course data and show edit form
    loadCourseForEdit(courseId);
}

async function loadCourseForEdit(courseId) {
    try {
        // Find course in current courses list
        const token = localStorage.getItem('admin_token');
        const response = await fetch(`${API_BASE_URL}/courses/list?token=${token}`);
        const result = await response.json();
        
        const course = result.courses.find(c => c.id === courseId);
        if (!course) {
            showToast('Course not found', 'error');
            return;
        }
        
        // Populate edit form
        document.getElementById('course-title').value = course.title;
        document.getElementById('course-description').value = course.description;
        document.getElementById('course-price').value = course.price;
        document.getElementById('teacher-id').value = course.teacher_id || '';
        
        // Store course ID for update
        document.getElementById('course-form').dataset.courseId = courseId;
        
        // Change form title and button text
        document.querySelector('#course-form-container h2').textContent = 'Edit Course';
        document.querySelector('#course-form button[type="submit"]').innerHTML = '<i class="fas fa-save"></i> Update Course';
        
        // Show form
        document.getElementById('course-form-container').classList.remove('hidden');
        
    } catch (error) {
        showToast('Failed to load course data', 'error');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const token = localStorage.getItem('admin_token');
    const userData = localStorage.getItem('admin_user');
    
    if (token && userData) {
        try {
            currentUser = JSON.parse(userData);
            document.getElementById('user-name').textContent = `Welcome, ${currentUser.name}`;
            showPage('dashboard-page');
            loadCourses();
        } catch (error) {
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_user');
        }
    }
    
    // Form submissions
    document.getElementById('login-form').addEventListener('submit', handleLoginForm);
    document.getElementById('course-form').addEventListener('submit', handleCourseForm);
    document.getElementById('video-form').addEventListener('submit', handleVideoForm);
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Course form events
    document.getElementById('create-course-btn').addEventListener('click', function() {
        document.getElementById('course-form-container').classList.remove('hidden');
    });
    
    document.getElementById('cancel-course').addEventListener('click', function() {
        resetCourseForm();
    });
    
    // Video form events
    document.getElementById('cancel-video').addEventListener('click', function() {
        document.getElementById('video-form-container').classList.add('hidden');
        document.getElementById('video-form').reset();
    });
});

// Initialize app
console.log('Admin Panel Frontend Initialized');
showToast('Welcome to Admin Panel', 'info');