// API Base URL
const API_URL = 'http://localhost:8000/api';

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Get admin info
function getAdminInfo() {
    const adminInfo = localStorage.getItem('adminInfo');
    return adminInfo ? JSON.parse(adminInfo) : null;
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('adminInfo');
    window.location.href = 'login.html';
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Load dashboard data
async function loadDashboard() {
    if (!checkAuth()) return;
    
    const adminInfo = getAdminInfo();
    const token = localStorage.getItem('token');
    
    if (!adminInfo) {
        logout();
        return;
    }
    
    // Display admin name
    document.getElementById('adminName').textContent = `Welcome, ${adminInfo.name}`;
    
    try {
        const response = await fetch(`${API_URL}/dashboard/${adminInfo.uuid}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load dashboard');
        }
        
        const data = await response.json();
        
        // Update stats
        document.getElementById('totalUsers').textContent = data.total_users;
        document.getElementById('activeUsers').textContent = data.active_users;
        document.getElementById('totalClients').textContent = data.total_clients;
        document.getElementById('usersPending').textContent = formatCurrency(data.users_pending_amount);
        document.getElementById('clientsPending').textContent = formatCurrency(data.clients_pending_amount);
        
        // Update recent users table
        const usersTableBody = document.getElementById('recentUsersTable');
        if (data.recent_users && data.recent_users.length > 0) {
            usersTableBody.innerHTML = data.recent_users.map(user => `
                <tr>
                    <td>${user.first_name} ${user.last_name}</td>
                    <td>${user.mobile}</td>
                    <td>${user.location}</td>
                    <td>
                        <span class="text-${user.is_active ? 'success' : 'danger'}">
                            ${user.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>${formatDate(user.created_date)}</td>
                </tr>
            `).join('');
        } else {
            usersTableBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No users found</td></tr>';
        }
        
        // Update recent clients table
        const clientsTableBody = document.getElementById('recentClientsTable');
        if (data.recent_clients && data.recent_clients.length > 0) {
            clientsTableBody.innerHTML = data.recent_clients.map(client => `
                <tr>
                    <td>${client.name}</td>
                    <td>${client.username}</td>
                    <td>${client.location}</td>
                    <td>${client.phone_number}</td>
                    <td>${formatDate(client.created_date)}</td>
                </tr>
            `).join('');
        } else {
            clientsTableBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No clients found</td></tr>';
        }
        
    } catch (error) {
        console.error('Dashboard error:', error);
        alert('Failed to load dashboard data');
    }
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', loadDashboard);

// Refresh dashboard every 30 seconds
setInterval(loadDashboard, 30000);