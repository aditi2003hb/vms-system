# Vendor Management System (VMS)

A comprehensive Multi-Admin Platform for Managing Vendors, Buyers, and Transaction Records with Automated Calculations.

## 🚀 Features

- **Multi-Admin Support**: Each admin has their own UUID-based authentication
- **User Management**: Manage buyers with credit/debit transactions
- **Client Management**: Manage vendors/sellers with profit/loss tracking
- **Automated Calculations**: 
  - Sum/Deficit for Users
  - Profit/Loss for Clients
  - Pending Amounts with real-time updates
- **Dark Theme UI**: Professional navy blue and grey interface
- **Secure Authentication**: JWT-based authentication with password protection

## 📁 Project Structure

```
vms-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── database.py      # Database configuration
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # Authentication utilities
│   │   ├── crud.py          # CRUD operations
│   │   └── routers/         # API endpoints
│   │       ├── admin.py
│   │       ├── users.py
│   │       └── clients.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html           # Landing page
│   ├── login.html           # Login/Register page
│   ├── dashboard.html       # Admin dashboard
│   ├── users.html           # Users management
│   ├── clients.html         # Clients management
│   ├── css/
│   │   └── style.css        # Dark theme styles
│   └── js/
│       ├── auth.js          # Authentication logic
│       ├── dashboard.js     # Dashboard functionality
│       ├── users.js         # Users management logic
│       └── clients.js       # Clients management logic
└── README.md
```

## 🛠 Tech Stack

- **Backend**: Python 3.8+, FastAPI, SQLAlchemy, Pydantic
- **Database**: SQLite (can be easily switched to PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Authentication**: JWT tokens with bcrypt password hashing

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge)

## 🔧 Installation & Setup

### Step 1: Clone or Create Project Directory

```bash
# If you have the project files, navigate to the project directory
cd vms-system

# Or create a new directory
mkdir vms-system
cd vms-system
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Environment Configuration

Create or verify the `.env` file in the backend directory:

```bash
# backend/.env
DATABASE_URL=sqlite:///./vms_database.db
SECRET_KEY=your-super-secret-key-change-this-in-production-2024
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Step 4: Start the Backend Server

```bash
# From the backend directory
cd backend

# Run with Uvicorn (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run with Hypercorn (production)
hypercorn app.main:app --bind 0.0.0.0:8000
```

The backend API will be available at:
- API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Step 5: Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd vms-system/frontend

# For development, you can use Python's built-in server
python -m http.server 3000

# Or use any static file server like Live Server in VS Code
```

The frontend will be available at:
- `http://localhost:3000`

## 📝 Complete Setup Commands (Quick Start)

### For Windows:

```bash
# Terminal 1 - Backend
cd vms-system\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd vms-system\frontend
python -m http.server 3000
```

### For macOS/Linux:

```bash
# Terminal 1 - Backend
cd vms-system/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd vms-system/frontend
python3 -m http.server 3000
```

## 🚀 Usage Guide

### 1. Initial Setup
1. Open browser and go to `http://localhost:3000`
2. Click "Register Admin" to create your first admin account
3. **Important**: Save the generated UUID - you'll need it for login!

### 2. Admin Login
1. Use your admin name, UUID, and password to login
2. You'll be redirected to the dashboard

### 3. Managing Users (Buyers)
1. Navigate to "Users Management"
2. Click "Add New User" to register buyers
3. Add credit/debit transactions for each user
4. View calculated sum/deficit automatically

### 4. Managing Clients (Vendors)
1. Navigate to "Clients Management"
2. Click "Add New Client" to register vendors
3. Record transactions with profit/loss tracking
4. View pending amounts and profit/loss calculations

### 5. Dashboard Overview
- View total users and clients
- See pending amounts for both users and clients
- Quick access to recent additions

## 📊 Calculation Logic

### For Users (Buyers):
- **Net Weight** = kg - (bags × cut_weight)
- **Rough Amount** = net_weight × amount_per_kg
- **Tax** = 1% of rough_amount
- **Levi** = 5 × bags
- **Net Amount** = rough_amount + tax + levi
- **Sum/Deficit** = Total Debit - Total Credit

### For Clients (Vendors):
- **Pending Amount** = (total_debit - total_credit) ± profit_loss
- Tracks profit (+) and loss (-) separately

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token authentication
- Admin isolation (each admin sees only their data)
- Session management with token expiry

## 🐛 Troubleshooting

### Backend Issues:

1. **Port already in use**:
   ```bash
   # Change port in the command
   uvicorn app.main:app --reload --port 8001
   ```

2. **Database errors**:
   ```bash
   # Delete the database file and restart
   rm vms_database.db
   # Restart the server
   ```

3. **Import errors**:
   ```bash
   # Ensure virtual environment is activated
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

### Frontend Issues:

1. **CORS errors**:
   - Ensure backend is running on port 8000
   - Check that frontend API_URL is correct in JS files

2. **Login issues**:
   - Verify UUID is copied correctly
   - Check browser console for errors

## 📱 API Endpoints

### Admin Endpoints:
- `POST /api/register_admin` - Register new admin
- `POST /api/login_admin` - Admin login
- `GET /api/dashboard/{admin_uuid}` - Dashboard data

### User Endpoints:
- `POST /api/admin/{admin_uuid}/add_user` - Add user
- `GET /api/admin/{admin_uuid}/users` - List users
- `POST /api/admin/{admin_uuid}/user/{user_id}/add_record` - Add transaction
- `GET /api/admin/{admin_uuid}/user/{user_id}/calculate_record_details` - Get calculations

### Client Endpoints:
- `POST /api/admin/{admin_uuid}/add_client` - Add client
- `GET /api/admin/{admin_uuid}/clients` - List clients
- `POST /api/admin/{admin_uuid}/client/{client_id}/add_record` - Add transaction
- `GET /api/admin/{admin_uuid}/client/{client_id}/calculate_record_details` - Get calculations

## 🔄 Database Migration (Optional)

To use PostgreSQL instead of SQLite:

1. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/vms_db
   ```

## 📈 Future Enhancements

- [ ] Export reports to PDF/Excel
- [ ] Email notifications
- [ ] Advanced filtering and search
- [ ] Bulk transaction import
- [ ] Mobile responsive improvements
- [ ] Real-time updates with WebSockets

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Support

For issues or questions, please check the troubleshooting section or review the API documentation at `/docs` endpoint.

---

**Note**: Remember to change the SECRET_KEY in production and use HTTPS for secure deployments.