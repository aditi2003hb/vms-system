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

// Load clients
async function loadClients() {
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
        // Load clients
        const clientsResponse = await fetch(`${API_URL}/admin/${adminInfo.uuid}/clients`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (clientsResponse.status === 401) {
            logout();
            return;
        }
        
        const clients = await clientsResponse.json();
        
        // Load pending amount
        const pendingResponse = await fetch(`${API_URL}/admin/${adminInfo.uuid}/final_clients_pending_amount`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const pendingData = await pendingResponse.json();
        document.getElementById('totalPendingAmount').textContent = formatCurrency(pendingData.total_pending);
        
        // Update clients table
        const clientsTableBody = document.getElementById('clientsTable');
        if (clients && clients.length > 0) {
            const clientsWithCalc = await Promise.all(clients.map(async (client) => {
                try {
                    const calcResponse = await fetch(`${API_URL}/admin/${adminInfo.uuid}/client/${client.id}/calculate_record_details`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    const calc = await calcResponse.json();
                    return { ...client, calc };
                } catch {
                    return { ...client, calc: { pending_amount: 0, profit_loss_total: 0, status: 'N/A' } };
                }
            }));
            
            clientsTableBody.innerHTML = clientsWithCalc.map(client => `
                <tr>
                    <td>${client.name}</td>
                    <td>${client.username}</td>
                    <td>${client.location}</td>
                    <td>${client.phone_number}</td>
                    <td>
                        <span class="text-${client.calc.profit_loss_total > 0 ? 'success' : client.calc.profit_loss_total < 0 ? 'danger' : 'muted'}">
                            ${formatCurrency(Math.abs(client.calc.profit_loss_total))} ${client.calc.status}
                        </span>
                    </td>
                    <td>
                        <span class="text-warning">
                            ${formatCurrency(Math.abs(client.calc.pending_amount))}
                        </span>
                    </td>
                    <td>
                        <button onclick="showTransactionModal(${client.id})" class="btn btn-info btn-sm">Add Transaction</button>
                        <button onclick="viewRecords(${client.id}, '${client.name}')" class="btn btn-secondary btn-sm">View Records</button>
                        <button onclick="showUpdateModal(${client.id}, '${client.name}', '${client.location}', '${client.phone_number}')" class="btn btn-warning btn-sm">Update</button>
                    </td>
                </tr>
            `).join('');
        } else {
            clientsTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No clients found</td></tr>';
        }
        
    } catch (error) {
        console.error('Error loading clients:', error);
        alert('Failed to load clients');
    }
}

// Show add client modal
function showAddClientModal() {
    document.getElementById('addClientModal').classList.add('active');
}

// Close add client modal
function closeAddClientModal() {
    document.getElementById('addClientModal').classList.remove('active');
    document.getElementById('addClientForm').reset();
}

// Add new client
document.getElementById('addClientForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const adminInfo = getAdminInfo();
    const token = localStorage.getItem('token');
    
    const clientData = {
        name: document.getElementById('clientName').value,
        username: document.getElementById('clientUsername').value,
        location: document.getElementById('clientLocation').value,
        phone_number: document.getElementById('clientPhone').value
    };
    
    try {
        const response = await fetch(`${API_URL}/admin/${adminInfo.uuid}/add_client`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(clientData)
        });
        
        if (response.ok) {
            closeAddClientModal();
            loadClients();
            alert('Client added successfully');
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to add client');
        }
    } catch (error) {
        console.error('Error adding client:', error);
        alert('Failed to add client');
    }
});

// Show update modal
function showUpdateModal(clientId, name, location, phone) {
    document.getElementById('updateClientId').value = clientId;
    document.getElementById('updateClientName').value = name;
    document.getElementById('updateClientLocation').value = location;
    document.getElementById('updateClientPhone').value = phone;
    document.getElementById('updateClientModal').classList.add('active');
}

// Close update client modal
function closeUpdateClientModal() {
    document.getElementById('updateClientModal').classList.remove('active');
    document.getElementById('updateClientForm').reset();
}

// Update client
document.getElementById('updateClientForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const adminInfo = getAdminInfo();
    const token = localStorage.getItem('token');
    const clientId = document.getElementById('updateClientId').value;
    
    const updateData = {
        name: document.getElementById('updateClientName').value,
        location: document.getElementById('updateClientLocation').value,
        phone_number: document.getElementById('updateClientPhone').value
    };
    
    try {
        const response = await fetch(`${API_URL}/admin/${adminInfo.uuid}/client/${clientId}/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(updateData)
        });
        
        if (response.ok) {
            closeUpdateClientModal();
            loadClients();
            alert('Client updated successfully');
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to update client');
        }
    } catch (error) {
        console.error('Error updating client:', error);
        alert('Failed to update client');
    }
});

// Show transaction modal
function showTransactionModal(clientId) {
    document.getElementById('transactionClientId').value = clientId;
    document.getElementById('transactionModal').classList.add('active');
}

// Close transaction modal
function closeTransactionModal() {
    document.getElementById('transactionModal').classList.remove('active');
    document.getElementById('transactionForm').reset();
}

// Add transaction
document.getElementById('transactionForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const adminInfo = getAdminInfo();
    const token = localStorage.getItem('token');
    const clientId = document.getElementById('transactionClientId').value;
    const type = document.getElementById('transactionType').value;
    const amount = parseFloat(document.getElementById('transactionAmount').value);
    const profitLoss = parseFloat(document.getElementById('profitLoss').value) || null;
    
    const transactionData = {
        transaction_type: type,
        [type === 'credit' ? 'credit_amount' : 'debit_amount']: amount,
        profit_loss: profitLoss
    };
    
    try {
        const response = await fetch(`${API_URL}/admin/${adminInfo.uuid}/client/${clientId}/add_record`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(transactionData)
        });
        
        if (response.ok) {
            closeTransactionModal();
            loadClients();
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

// View client records
async function viewRecords(clientId, clientName) {
    const adminInfo = getAdminInfo();
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`${API_URL}/admin/${adminInfo.uuid}/client/${clientId}/record_details`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        let recordsHTML = `
            <h3>${clientName} - Transaction Records</h3>
            
            <div class="card mb-3">
                <div class="card-header">Credit Records (${data.total_credits})</div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Amount</th>
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
                    </tr>
                `;
            });
        } else {
            recordsHTML += '<tr><td colspan="2" class="text-center text-muted">No credit records</td></tr>';
        }
        
        recordsHTML += `
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card mb-3">
                <div class="card-header">Debit Records (${data.total_debits})</div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        if (data.debit_records && data.debit_records.length > 0) {
            data.debit_records.forEach(record => {
                recordsHTML += `
                    <tr>
                        <td>${new Date(record.date).toLocaleDateString()}</td>
                        <td>${formatCurrency(record.amount)}</td>
                    </tr>
                `;
            });
        } else {
            recordsHTML += '<tr><td colspan="2" class="text-center text-muted">No debit records</td></tr>';
        }
        
        recordsHTML += `
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">Profit/Loss Records (${data.total_profit_loss_entries})</div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        if (data.profit_loss_records && data.profit_loss_records.length > 0) {
            data.profit_loss_records.forEach(record => {
                recordsHTML += `
                    <tr>
                        <td>${new Date(record.date).toLocaleDateString()}</td>
                        <td class="text-${record.type === 'Profit' ? 'success' : 'danger'}">${record.type}</td>
                        <td>${formatCurrency(Math.abs(record.amount))}</td>
                    </tr>
                `;
            });
        } else {
            recordsHTML += '<tr><td colspan="3" class="text-center text-muted">No profit/loss records</td></tr>';
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
document.addEventListener('DOMContentLoaded', loadClients);