// API Configuration
const API_BASE_URL = 'http://localhost:8001/api/v1';

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
async function register(userData) {
    try {
        const result = await apiCall('/auth/register', 'POST', userData);
        showToast(result.message, 'success');
        
        // Set email for verification
        document.getElementById('verify-email').value = userData.email;
        showPage('verify-page');
        
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

async function login(credentials) {
    try {
        const result = await apiCall('/auth/login', 'POST', credentials);
        showToast(result.message, 'success');
        
        // Store token in localStorage
        if (result.access_token) {
            localStorage.setItem('token', result.access_token);
        }
        
        currentUser = result.user;
        localStorage.setItem('currentUser', JSON.stringify(result.user));
        document.getElementById('user-name').textContent = `Welcome, ${result.user.name}`;
        
        // Set role badge
        const roleBadge = document.getElementById('user-role');
        roleBadge.textContent = result.user.role;
        roleBadge.className = `role-badge ${result.user.role.toLowerCase()}`;
        
        showPage('dashboard-page');
        showRoleBasedDashboard(result.user.role);
        
        // Check for pending payment verification
        setTimeout(() => {
            handlePaymentSuccess();
        }, 1000);
        
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

function showRoleBasedDashboard(role) {
    // Hide all dashboards
    document.getElementById('admin-dashboard').classList.add('hidden');
    document.getElementById('teacher-dashboard').classList.add('hidden');
    document.getElementById('student-dashboard').classList.add('hidden');
    
    // Show appropriate dashboard
    if (role === 'Teacher') {
        document.getElementById('teacher-dashboard').classList.remove('hidden');
        loadTeacherData();
    } else if (role === 'student') {
        document.getElementById('student-dashboard').classList.remove('hidden');
        loadStudentData();
    } else {
        // Admin or other roles
        document.getElementById('admin-dashboard').classList.remove('hidden');
        loadUserStats();
    }
}

// Teacher Functions
async function loadTeacherData() {
    await loadTeacherCourses();
    await loadStudentsList();
}

async function loadTeacherCourses() {
    try {
        const result = await apiCall(`/courses/teacher/${currentUser.id}?token=${localStorage.getItem('token')}`);
        const coursesContainer = document.getElementById('teacher-courses');
        
        if (result.courses && result.courses.length > 0) {
            coursesContainer.innerHTML = result.courses.map(course => `
                <div class="course-card">
                    <div class="course-header">
                        <h3 class="course-title">${course.title}</h3>
                        <span class="course-price">$${course.price}</span>
                    </div>
                    <span class="course-category">${course.category}</span>
                    <p class="course-description">${course.description}</p>
                    <div class="course-meta">
                        <span>Duration: ${course.duration}</span>
                        <span>Enrolled: ${course.enrolled_count || 0}</span>
                    </div>
                    <div class="course-actions">
                        <button class="btn btn-edit" onclick="editCourse('${course._id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-success" onclick="addVideo('${course._id}')">
                            <i class="fas fa-video"></i> Add Video
                        </button>
                        <button class="btn btn-delete" onclick="deleteCourse('${course._id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            coursesContainer.innerHTML = '<div class="no-data">No courses created yet</div>';
        }
    } catch (error) {
        showToast('Failed to load courses', 'error');
    }
}

async function loadStudentsList() {
    try {
        const result = await apiCall('/users/students');
        const tbody = document.getElementById('students-tbody');
        
        if (result.students && result.students.length > 0) {
            tbody.innerHTML = result.students.map(student => `
                <tr>
                    <td>${student.name}</td>
                    <td>${student.email}</td>
                    <td>${student.enrolled_courses || 0}</td>
                    <td><span class="status-badge ${student.isActive ? 'status-online' : 'status-offline'}">
                        ${student.isActive ? 'Online' : 'Offline'}
                    </span></td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="no-data">No students found</td></tr>';
        }
    } catch (error) {
        showToast('Failed to load students', 'error');
    }
}

async function createCourse(courseData) {
    try {
        // Create FormData for multipart/form-data
        const formData = new FormData();
        formData.append('token', localStorage.getItem('token') || '');
        formData.append('title', courseData.title);
        formData.append('description', courseData.description);
        formData.append('price', courseData.price);
        formData.append('teacher_id', currentUser.id);
        formData.append('visible', true);
        
        // Add thumbnail if selected
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
        
        console.log('Course creation result:', result);
        
        // Upload videos if any
        if (courseData.videos && courseData.videos.length > 0) {
            showToast('Uploading videos...', 'info');
            console.log('Course ID for videos:', result.id);
            await uploadCourseVideos(result.id, courseData.videos);
        }
        
        // Hide form and reload courses
        document.getElementById('course-form-container').classList.add('hidden');
        document.getElementById('course-form').reset();
        await loadTeacherCourses();
        
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

async function deleteCourse(courseId) {
    if (!confirm('Are you sure you want to delete this course?')) return;
    
    try {
        const result = await apiCall(`/courses/${courseId}`, 'DELETE');
        showToast(result.message, 'success');
        await loadTeacherCourses();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Student Functions
async function loadStudentData() {
    await loadEnrolledCourses();
    await loadAvailableCourses();
}

async function loadEnrolledCourses() {
    try {
        const result = await apiCall(`/courses/student/${currentUser.id}`);
        const coursesContainer = document.getElementById('enrolled-courses');
        
        if (result.enrollments && result.enrollments.length > 0) {
            coursesContainer.innerHTML = result.enrollments.map(enrollment => `
                <div class="course-card">
                    <div class="course-header">
                        <h3 class="course-title">${enrollment.course_title}</h3>
                        <span class="course-price enrolled-badge">Enrolled</span>
                    </div>
                    <div class="course-meta">
                        <span><i class="fas fa-chart-line"></i> Progress: ${enrollment.progress || 0}%</span>
                        <span><i class="fas fa-calendar"></i> ${new Date(enrollment.enrolled_at).toLocaleDateString()}</span>
                    </div>
                    <div class="course-actions">
                        <button class="btn btn-primary" onclick="startCourse('${enrollment.course_id}')">
                            <i class="fas fa-play"></i> Continue Learning
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            coursesContainer.innerHTML = '<div class="no-data">No enrolled courses yet</div>';
        }
    } catch (error) {
        showToast('Failed to load enrolled courses', 'error');
    }
}

async function loadAvailableCourses() {
    try {
        console.log('Loading available courses...');
        const [coursesResult, enrollmentsResult] = await Promise.all([
            apiCall('/courses/all'),
            apiCall(`/courses/student/${currentUser.id}`)
        ]);
        
        console.log('API Response:', coursesResult);
        
        const coursesContainer = document.getElementById('available-courses');
        
        if (coursesResult.courses && coursesResult.courses.length > 0) {
            // Get enrolled course IDs
            const enrolledCourseIds = enrollmentsResult.enrollments ? 
                enrollmentsResult.enrollments.map(e => e.course_id) : [];
            
            // Filter out enrolled courses
            const availableCourses = coursesResult.courses.filter(
                course => !enrolledCourseIds.includes(course._id)
            );
            
            if (availableCourses.length > 0) {
                coursesContainer.innerHTML = availableCourses.map(course => `
                    <div class="course-card">
                        <div class="course-header">
                            <h3 class="course-title">${course.title}</h3>
                            <span class="course-price">₹${course.price}</span>
                        </div>
                        <p class="course-description">${course.description}</p>
                        <div class="course-actions">
                            <button class="btn btn-enroll" onclick="initiatePayment('${course._id}', ${course.price})">
                                <i class="fas fa-credit-card"></i> Buy Now
                            </button>
                            <button class="btn btn-secondary" onclick="manualVerifyPayment()" style="display:none;" id="verify-btn-${course._id}">
                                <i class="fas fa-check"></i> Verify Payment
                            </button>
                        </div>
                    </div>
                `).join('');
            } else {
                coursesContainer.innerHTML = '<div class="no-data">All courses enrolled!</div>';
            }
        } else {
            console.log('No courses found');
            coursesContainer.innerHTML = '<div class="no-data">No courses available</div>';
        }
    } catch (error) {
        console.error('Error loading courses:', error);
        showToast('Failed to load courses: ' + error.message, 'error');
        document.getElementById('available-courses').innerHTML = '<div class="no-data">Error loading courses</div>';
    }
}

async function initiatePayment(courseId, amount) {
    try {
        showLoading();
        
        // Create checkout session
        const formData = new FormData();
        formData.append('token', localStorage.getItem('token'));
        formData.append('course_id', courseId);
        formData.append('student_id', currentUser.id);
        
        const response = await fetch(`${API_BASE_URL}/payment/create-checkout-session`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Checkout session creation failed');
        }
        
        hideLoading();
        
        // Redirect to Stripe Checkout
        window.location.href = result.checkout_url;
        
    } catch (error) {
        hideLoading();
        showToast('Payment initiation failed: ' + error.message, 'error');
    }
}

async function verifySessionPayment(sessionId) {
    try {
        showLoading();
        
        const formData = new FormData();
        formData.append('token', localStorage.getItem('token'));
        formData.append('session_id', sessionId);
        
        const response = await fetch(`${API_BASE_URL}/payment/verify-session`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        hideLoading();
        
        if (response.ok) {
            showToast('Payment successful! Course enrolled.', 'success');
            // Reload both sections to reflect changes
            await Promise.all([
                loadEnrolledCourses(),
                loadAvailableCourses()
            ]);
        } else {
            throw new Error(result.detail || 'Payment verification failed');
        }
        
    } catch (error) {
        hideLoading();
        showToast('Payment verification failed: ' + error.message, 'error');
    }
}

// Handle payment success from URL parameters
function handlePaymentSuccess() {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const paymentStatus = urlParams.get('payment');
    const pendingSessionId = localStorage.getItem('pending_session_id');
    
    if (paymentStatus === 'success' && sessionId) {
        showToast('Payment successful! Verifying enrollment...', 'success');
        if (currentUser) {
            verifySessionPayment(sessionId);
        } else {
            localStorage.setItem('pending_session_id', sessionId);
        }
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (paymentStatus === 'cancelled') {
        showToast('Payment was cancelled', 'warning');
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if ((sessionId || pendingSessionId) && currentUser) {
        const finalSessionId = sessionId || pendingSessionId;
        verifySessionPayment(finalSessionId);
        
        // Clean up
        localStorage.removeItem('pending_session_id');
        if (sessionId) {
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }
}

async function searchCourses(query) {
    if (!query.trim()) {
        await loadAvailableCourses();
        return;
    }
    
    try {
        const result = await apiCall(`/courses/search/${encodeURIComponent(query)}`);
        const coursesContainer = document.getElementById('available-courses');
        
        if (result.courses && result.courses.length > 0) {
            coursesContainer.innerHTML = result.courses.map(course => `
                <div class="course-card">
                    <div class="course-header">
                        <h3 class="course-title">${course.title}</h3>
                        <span class="course-price">$${course.price}</span>
                    </div>
                    <span class="course-category">${course.category}</span>
                    <p class="course-description">${course.description}</p>
                    <div class="course-meta">
                        <span>Duration: ${course.duration}</span>
                        <span>By: ${course.teacher_name}</span>
                    </div>
                    <div class="course-actions">
                        <button class="btn btn-enroll" onclick="enrollCourse('${course._id}')">
                            <i class="fas fa-plus"></i> Enroll
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            coursesContainer.innerHTML = '<div class="no-data">No courses found</div>';
        }
    } catch (error) {
        showToast('Search failed', 'error');
    }
}

async function logout() {
    if (!currentUser) return;
    
    try {
        await apiCall('/auth/logout', 'POST', { user_id: currentUser.id });
        showToast('Logged out successfully', 'success');
        
        currentUser = null;
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        showPage('login-page');
        
        // Clear forms
        document.querySelectorAll('form').forEach(form => form.reset());
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function verifyEmail(email, otp) {
    try {
        const result = await apiCall('/auth/verify-email', 'POST', { email, otp });
        showToast(result.message, 'success');
        
        showPage('login-page');
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

async function loadUserStats() {
    try {
        const stats = await apiCall('/auth/users/stats');
        
        // Update stats cards
        document.getElementById('total-users').textContent = stats.total_users;
        document.getElementById('online-users').textContent = stats.online_users;
        document.getElementById('offline-users').textContent = stats.offline_users;
        
        // Update online users table
        const tbody = document.getElementById('online-users-tbody');
        tbody.innerHTML = '';
        
        if (stats.online_user_details && stats.online_user_details.length > 0) {
            stats.online_user_details.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>${user.role}</td>
                    <td><span class="status-badge status-online">Online</span></td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="no-data">No online users</td></tr>';
        }
        
    } catch (error) {
        showToast('Failed to load user statistics', 'error');
        console.error('Stats loading error:', error);
    }
}

// Form Handlers
function handleRegisterForm(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('register-name').value.trim(),
        email: document.getElementById('register-email').value.trim(),
        role: document.getElementById('register-role').value,
        password: document.getElementById('register-password').value,
        confirm_password: document.getElementById('register-confirm-password').value
    };
    
    // Client-side validation
    if (!formData.name || !formData.email || !formData.role || !formData.password || !formData.confirm_password) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    if (formData.password !== formData.confirm_password) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    if (formData.password.length < 6) {
        showToast('Password must be at least 6 characters long', 'error');
        return;
    }
    
    register(formData);
}

function handleLoginForm(event) {
    event.preventDefault();
    
    const credentials = {
        email: document.getElementById('login-email').value.trim(),
        password: document.getElementById('login-password').value
    };
    
    console.log('Login attempt:', credentials.email);
    
    if (!credentials.email || !credentials.password) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    login(credentials);
}

function handleVerifyForm(event) {
    event.preventDefault();
    
    const email = document.getElementById('verify-email').value.trim();
    const otp = document.getElementById('verify-otp').value.trim();
    
    if (!email || !otp) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    if (otp.length !== 6) {
        showToast('OTP must be 6 digits', 'error');
        return;
    }
    
    verifyEmail(email, otp);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('currentUser');
    
    if (token && userData) {
        try {
            currentUser = JSON.parse(userData);
            document.getElementById('user-name').textContent = `Welcome, ${currentUser.name}`;
            
            const roleBadge = document.getElementById('user-role');
            roleBadge.textContent = currentUser.role;
            roleBadge.className = `role-badge ${currentUser.role.toLowerCase()}`;
            
            showPage('dashboard-page');
            showRoleBasedDashboard(currentUser.role);
        } catch (error) {
            // Clear invalid data
            localStorage.removeItem('token');
            localStorage.removeItem('currentUser');
        }
    }
    
    // Handle payment success on page load
    handlePaymentSuccess();
    
    // Form submissions
    document.getElementById('register-form').addEventListener('submit', handleRegisterForm);
    document.getElementById('login-form').addEventListener('submit', handleLoginForm);
    document.getElementById('verify-form').addEventListener('submit', handleVerifyForm);
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Refresh stats button
    document.getElementById('refresh-stats').addEventListener('click', loadUserStats);
    
    // Teacher Dashboard Events
    document.getElementById('create-course-btn').addEventListener('click', function() {
        document.getElementById('course-form-container').classList.remove('hidden');
    });
    
    document.getElementById('cancel-course').addEventListener('click', function() {
        document.getElementById('course-form-container').classList.add('hidden');
        document.getElementById('course-form').reset();
    });
    
    document.getElementById('course-form').addEventListener('submit', handleCourseForm);
    
    // Video form events
    document.getElementById('cancel-video').addEventListener('click', function() {
        document.getElementById('video-form-container').classList.add('hidden');
        document.getElementById('video-form').reset();
    });
    
    document.getElementById('video-form').addEventListener('submit', handleVideoForm);
    
    // Student Dashboard Events
    document.getElementById('search-btn').addEventListener('click', function() {
        const query = document.getElementById('course-search').value;
        searchCourses(query);
    });
    
    document.getElementById('course-search').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchCourses(e.target.value);
        }
    });
    
    // OTP input formatting
    document.getElementById('verify-otp').addEventListener('input', function(e) {
        // Only allow numbers
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
    });
    
    // Password strength indicator (optional enhancement)
    document.getElementById('register-password').addEventListener('input', function(e) {
        const password = e.target.value;
        const strength = getPasswordStrength(password);
        // You can add visual feedback here
    });
    
    // Auto-refresh stats every 30 seconds when on dashboard
    setInterval(() => {
        if (currentPage === 'dashboard-page' && currentUser) {
            if (currentUser.role === 'Teacher') {
                loadTeacherData();
            } else if (currentUser.role === 'student') {
                loadStudentData();
            } else {
                loadUserStats();
            }
        }
    }, 30000);
});

// Form Handlers
function handleCourseForm(event) {
    event.preventDefault();
    
    const thumbnailFile = document.getElementById('course-thumbnail').files[0];
    const videoFiles = document.getElementById('course-videos').files;
    
    const courseData = {
        title: document.getElementById('course-title').value.trim(),
        description: document.getElementById('course-description').value.trim(),
        price: parseFloat(document.getElementById('course-price').value),
        thumbnail: thumbnailFile || null,
        videos: Array.from(videoFiles)
    };
    
    // Validation
    if (!courseData.title || !courseData.description || courseData.price < 0) {
        showToast('Please fill in all fields correctly', 'error');
        return;
    }
    
    createCourse(courseData);
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

// Upload multiple videos to course
async function uploadCourseVideos(courseId, videoFiles) {
    try {
        for (let i = 0; i < videoFiles.length; i++) {
            const videoFile = videoFiles[i];
            const videoTitle = videoFile.name.replace(/\.[^/.]+$/, ""); // Remove extension
            
            const formData = new FormData();
            formData.append('token', localStorage.getItem('token'));
            formData.append('course_id', courseId);
            formData.append('title', videoTitle);
            formData.append('description', `Video ${i + 1}`);
            formData.append('video_file', videoFile);
            
            const response = await fetch(`${API_BASE_URL}/courses/add-video`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `Failed to upload ${videoFile.name}`);
            }
            
            showToast(`Uploaded: ${videoFile.name}`, 'success');
        }
    } catch (error) {
        showToast(`Video upload error: ${error.message}`, 'error');
    }
}

// Helper Functions
function getPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Error handling for network issues
window.addEventListener('online', function() {
    showToast('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showToast('Connection lost. Please check your internet connection.', 'warning');
});

// Prevent form submission on Enter key in certain inputs
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.tagName !== 'BUTTON' && e.target.type !== 'submit') {
        // Find the submit button in the same form and click it
        const form = e.target.closest('form');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                e.preventDefault();
                submitBtn.click();
            }
        }
    }
});

// Initialize app
console.log('Learning Platform Frontend Initialized');
showToast('Welcome to Learning Platform', 'info');

// Course learning function
function startCourse(courseId) {
    if (!courseId) {
        showToast('Invalid course ID', 'error');
        return;
    }
    
    // Redirect to course player page
    window.location.href = `course-player.html?course_id=${courseId}`;
}

// Manual payment verification
function manualVerifyPayment() {
    const sessionId = prompt('Enter your Stripe session ID (from the URL after payment):');
    if (sessionId && sessionId.startsWith('cs_')) {
        verifySessionPayment(sessionId);
    } else {
        showToast('Invalid session ID format', 'error');
    }
}

// Video upload functions
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
        formData.append('token', localStorage.getItem('token'));
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
        await loadTeacherCourses();
        
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}