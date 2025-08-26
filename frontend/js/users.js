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

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Load users
async function loadUsers() {
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
        // Load users
        const usersResponse = await fetch(`${API_URL}/admin/${adminInfo.uuid}/users`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (usersResponse.status === 401) {
            logout();
            return;
        }
        
        const users = await usersResponse.json();
        
        // Load pending amount
        const pendingResponse = await fetch(`${API_URL}/admin/${adminInfo.uuid}/final_users_pending_amount`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const pendingData = await pendingResponse.json();
        document.getElementById('totalPendingAmount').textContent = formatCurrency(pendingData.total_pending);
        
        // Update users table
        const usersTableBody = document.getElementById('usersTable');
        if (users && users.length > 0) {
            const usersWithCalc = await Promise.all(users.map(async (user) => {
                try {
                    const calcResponse = await fetch(`${API_URL}/admin/${adminInfo.uuid}/user/${user.id}/calculate_record_details`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    const calc = await calcResponse.json();
                    return { ...user, calc };
                } catch {
                    return { ...user, calc: { sum_deficit: 0, status: 'N/A' } };
                }
            }));
            
            usersTableBody.innerHTML = usersWithCalc.map(user => `
                <tr>
                    <td>${user.first_name} ${user.last_name}</td>
                    <td>${user.mobile}</td>
                    <td>${user.location}</td>
                    <td>
                        <span class="text-${user.is_active ? 'success' : 'danger'}">
                            ${user.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>
                        <span class="text-${user.calc.sum_deficit > 0 ? 'warning' : 'success'}">
                            ${formatCurrency(Math.abs(user.calc.sum_deficit))} ${user.calc.status}
                        </span>
                    </td>
                    <td>
                        <button onclick="showTransactionModal(${user.id})" class="btn btn-info btn-sm">Add Transaction</button>
                        <button onclick="viewRecords(${user.id}, '${user.first_name} ${user.last_name}')" class="btn btn-secondary btn-sm">View Records</button>
                        <button onclick="toggleUserStatus(${user.id}, ${user.is_active})" class="btn btn-${user.is_active ? 'warning' : 'success'} btn-sm">
                            ${user.is_active ? 'Disable' : 'Enable'}
                        </button>
                    </td>
                </tr>
            `).join('');
        } else {
            usersTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No users found</td></tr>';
        }
        
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Failed to load users');
    }
}

// Show add user modal
function showAddUserModal() {
    document.getElementById('addUserModal').classList.add('active');
}

// Close add user modal
function closeAddUserModal() {
    document.getElementById('addUserModal').classList.remove('active');
    document.getElementById('addUserForm').reset();
}

// Add new user
document.getElementById('addUserForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const adminInfo = getAdminInfo();
    const token = localStorage.getItem('token');
    
    const userData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        mobile: document.getElementById('mobile').value,
        location: document.getElementById('location').value
    };
    
    try {
        const response = await fetch(`${API_URL}/admin/${adminInfo.uuid}/add_user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            closeAddUserModal();
            loadUsers();
            alert('User added successfully');
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to add user');
        }
    } catch (error) {
        console.error('Error adding user:', error);
        alert('Failed to add user');
    }
});

// Toggle user status
async function toggleUserStatus(userId, currentStatus) {
    const adminInfo = getAdminInfo();
    const token = localStorage.getItem('token');
    const action = currentStatus ? 'disable' : 'enable';
    
    if (!confirm(`Are you sure you want to ${action} this user?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/admin/${adminInfo.uuid}/user/${userId}/${action}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            loadUsers();
            alert(`User ${action}d successfully`);
        } else {
            alert(`Failed to ${action} user`);
        }
    } catch (error) {
        console.error(`Error ${action}ing user:`, error);
        alert(`Failed to ${action} user`);
    }
}

// Show transaction modal
function showTransactionModal(userId) {
    document.getElementById('transactionUserId').value = userId;
    document.getElementById('transactionModal').classList.add('active');
    toggleTransactionFields();
}

// Close transaction modal
function closeTransactionModal() {
    document.getElementById('transactionModal').classList.remove('active');
    document.getElementById('transactionForm').reset();
}

// Toggle transaction fields
function toggleTransactionFields() {
    const type = document.getElementById('transactionType').value;
    document.getElementById('creditFields').style.display = type === 'credit' ? 'block' : 'none';
    document.getElementById('debitFields').style.display = type === 'debit' ? 'block' : 'none';
}

// Add transaction
document.getElementById('transactionForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const adminInfo = getAdminInfo();
    const token = localStorage.getItem('token');
    const userId = document.getElementById('transactionUserId').value;
    const type = document.getElementById('transactionType').value;
    
    let transactionData = {
        transaction_type: type
    };
    
    if (type === 'credit') {
        transactionData.credit_amount = parseFloat(document.getElementById('creditAmount').value);
        transactionData.round_off = parseFloat(document.getElementById('roundOff').value) || 0;
    } else {
        transactionData.bags = parseInt(document.getElementById('bags').value);
        transactionData.product_type = document.getElementById('productType').value;
        transactionData.kg = parseFloat(document.getElementById('kg').value);
        transactionData.cut_weight = parseFloat(document.getElementById('cutWeight').value);
        transactionData.amount_per_kg = parseFloat(document.getElementById('amountPerKg').value);
    }
    
    try {
        const response = await fetch(`${API_URL}/admin/${adminInfo.uuid}/user/${userId}/add_record`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(transactionData)
        });
        
        if (response.ok) {
            closeTransactionModal();
            loadUsers();
            alert('Transaction added successfully');
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to add transaction');
        }
    } catch (error) {
        console.error('Error adding transaction:', error);
        alert('Failed to add transaction');
    }
});

// View user records
async function viewRecords(userId, userName) {
    const adminInfo = getAdminInfo();
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`${API_URL}/admin/${adminInfo.uuid}/user/${userId}/record_details`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        let recordsHTML = `
            <h3>${userName} - Transaction Records</h3>
            
            <div class="card mb-3">
                <div class="card-header">Credit Records (${data.total_credits})</div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Amount</th>
                                <th>Round Off</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        if (data.credit_records && data.credit_records.length > 0) {
            data.credit_records.forEach(record => {
                recordsHTML += `
                    <tr>
                        <td>${new Date(record.date).toLocaleDateString()}</td>
                        <td>${formatCurrency(record.amount)}</td>
                        <td>${formatCurrency(record.round_off || 0)}</td>
                    </tr>
                `;
            });
        } else {
            recordsHTML += '<tr><td colspan="3" class="text-center text-muted">No credit records</td></tr>';
        }
        
        recordsHTML += `
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">Debit Records (${data.total_debits})</div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Product</th>
                                <th>Bags</th>
                                <th>Net Weight</th>
                                <th>Net Amount</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        if (data.debit_records && data.debit_records.length > 0) {
            data.debit_records.forEach(record => {
                recordsHTML += `
                    <tr>
                        <td>${new Date(record.date).toLocaleDateString()}</td>
                        <td>${record.product_type}</td>
                        <td>${record.bags}</td>
                        <td>${record.net_weight} kg</td>
                        <td>${formatCurrency(record.net_amount)}</td>
                    </tr>
                `;
            });
        } else {
            recordsHTML += '<tr><td colspan="5" class="text-center text-muted">No debit records</td></tr>';
        }
        
        recordsHTML += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        document.getElementById('recordsContent').innerHTML = recordsHTML;
        document.getElementById('recordsModal').classList.add('active');
        
    } catch (error) {
        console.error('Error loading records:', error);
        alert('Failed to load records');
    }
}

// Close records modal
function closeRecordsModal() {
    document.getElementById('recordsModal').classList.remove('active');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadUsers);