// API Base URL
const API_URL = 'http://localhost:8000/api';

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const formTitle = document.getElementById('formTitle');
const toggleForm = document.getElementById('toggleForm');
const toggleFormBack = document.getElementById('toggleFormBack');
const alertContainer = document.getElementById('alertContainer');

// Check for register parameter in URL
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('register') === 'true') {
    showRegisterForm();
}

// Toggle between login and register forms
toggleForm?.addEventListener('click', (e) => {
    e.preventDefault();
    showRegisterForm();
});

toggleFormBack?.addEventListener('click', (e) => {
    e.preventDefault();
    showLoginForm();
});

function showRegisterForm() {
    loginForm.style.display = 'none';
    registerForm.style.display = 'block';
    formTitle.textContent = 'Admin Registration';
    clearAlerts();
}

function showLoginForm() {
    loginForm.style.display = 'block';
    registerForm.style.display = 'none';
    formTitle.textContent = 'Admin Login';
    clearAlerts();
}

// Show alert message
function showAlert(message, type = 'danger') {
    alertContainer.innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;
}

function clearAlerts() {
    alertContainer.innerHTML = '';
}

// Handle Registration
registerForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlerts();
    
    const name = document.getElementById('registerName').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validate passwords match
    if (password !== confirmPassword) {
        showAlert('Passwords do not match!');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/register_admin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show success message
            registerForm.style.display = 'none';
            showAlert('Registration successful! You can now login with your credentials.', 'success');
            
            // Clear form and switch to login
            registerForm.reset();
            setTimeout(() => {
                showLoginForm();
            }, 2000);
        } else {
            showAlert(data.detail || 'Registration failed');
        }
    } catch (error) {
        showAlert('Network error. Please try again.');
        console.error('Registration error:', error);
    }
});

// Handle Login
loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlerts();
    
    const name = document.getElementById('loginName').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/login_admin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token and admin info
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('adminInfo', JSON.stringify(data.admin));
            
            // Redirect to dashboard
            window.location.href = 'dashboard.html';
        } else {
            showAlert(data.detail || 'Invalid credentials');
        }
    } catch (error) {
        showAlert('Network error. Please try again.');
        console.error('Login error:', error);
    }
});

// Check if user is already logged in
function checkAuth() {
    const token = localStorage.getItem('token');
    if (token && window.location.pathname.includes('login.html')) {
        window.location.href = 'dashboard.html';
    }
}

// Run auth check on page load
checkAuth();