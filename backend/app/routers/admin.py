"""
Admin API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from .. import crud, models, schemas, auth, database

router = APIRouter(prefix="/api", tags=["Admin"])

@router.post("/register_admin", response_model=schemas.AdminResponse)
def register_admin(
    admin_data: schemas.AdminRegister,
    db: Session = Depends(database.get_db)
):
    """Register a new admin"""
    try:
        admin = crud.create_admin(db, admin_data)
        return admin
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login_admin")
def login_admin(
    login_data: schemas.AdminLogin,
    db: Session = Depends(database.get_db)
):
    """Login admin with name, UUID, and password"""
    admin = auth.authenticate_admin(
        db, 
        login_data.name, 
        login_data.uuid,
        login_data.password
    )
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": admin.uuid}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "name": admin.name,
            "uuid": admin.uuid,
            "created_date": admin.created_date
        }
    }

@router.get("/dashboard/{admin_uuid}", response_model=schemas.DashboardResponse)
def get_dashboard(
    admin_uuid: str,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get admin dashboard overview"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get users and clients
    users = crud.get_users_by_admin(db, current_admin.id)
    clients = crud.get_clients_by_admin(db, current_admin.id)
    
    # Calculate pending amounts
    users_pending = crud.get_all_users_pending_amount(db, current_admin.id)
    clients_pending = crud.get_all_clients_pending_amount(db, current_admin.id)
    
    # Get recent users and clients (last 5)
    recent_users = sorted(users, key=lambda x: x.created_date, reverse=True)[:5]
    recent_clients = sorted(clients, key=lambda x: x.created_date, reverse=True)[:5]
    
    return schemas.DashboardResponse(
        admin_name=current_admin.name,
        total_users=len(users),
        active_users=len([u for u in users if u.is_active]),
        total_clients=len(clients),
        users_pending_amount=users_pending['total_pending'],
        clients_pending_amount=clients_pending['total_pending'],
        recent_users=recent_users,
        recent_clients=recent_clients
    )

@router.get("/admin/{admin_uuid}/final_users_pending_amount", response_model=schemas.PendingAmountResponse)
def get_final_users_pending_amount(
    admin_uuid: str,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get total pending amount for all users"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = crud.get_all_users_pending_amount(db, current_admin.id)
    return schemas.PendingAmountResponse(**result)

@router.get("/admin/{admin_uuid}/final_clients_pending_amount", response_model=schemas.PendingAmountResponse)
def get_final_clients_pending_amount(
    admin_uuid: str,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get total pending amount for all clients"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = crud.get_all_clients_pending_amount(db, current_admin.id)
    return schemas.PendingAmountResponse(**result)