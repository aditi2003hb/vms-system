"""
CRUD operations and business logic
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from . import models, schemas
from datetime import datetime
import math

def calculate_user_record_debit(record_data: dict) -> dict:
    """Calculate debit transaction values for user record"""
    bags = record_data.get('bags', 0)
    kg = record_data.get('kg', 0)
    cut_weight = record_data.get('cut_weight', 0)
    amount_per_kg = record_data.get('amount_per_kg', 0)
    
    # Calculate net weight: kg - (bags × cut_weight)
    net_weight = kg - (bags * cut_weight)
    
    # Calculate rough amount: net_weight × amount_per_kg
    rough_amount = net_weight * amount_per_kg
    
    # Calculate tax: 1% of rough_amount
    tax = rough_amount * 0.01
    
    # Calculate levi: 5 × bags
    levi = 5 * bags
    
    # Calculate net amount: rough_amount + tax + levi
    net_amount = rough_amount + tax + levi
    
    # Round net amount as per rules (you can adjust rounding logic)
    net_amount = round(net_amount, 2)
    
    return {
        'net_weight': net_weight,
        'rough_amount': rough_amount,
        'tax': tax,
        'levi': levi,
        'net_amount': net_amount
    }

def get_user_sum_deficit(db: Session, user_id: int) -> dict:
    """Calculate sum/deficit for a user"""
    records = db.query(models.UserRecord).filter(models.UserRecord.user_id == user_id).all()
    
    total_debit = sum(r.net_amount for r in records if r.transaction_type == models.TransactionType.DEBIT and r.net_amount)
    total_credit = sum(r.credit_amount for r in records if r.transaction_type == models.TransactionType.CREDIT and r.credit_amount)
    
    sum_deficit = total_debit - total_credit
    status = "Deficit" if sum_deficit > 0 else "Surplus"
    
    return {
        'total_debit': total_debit,
        'total_credit': total_credit,
        'sum_deficit': sum_deficit,
        'status': status
    }

def get_all_users_pending_amount(db: Session, admin_id: int) -> dict:
    """Calculate total pending amount for all users of an admin"""
    users = db.query(models.User).filter(models.User.admin_id == admin_id).all()
    
    total_pending = 0
    details = []
    
    for user in users:
        calc = get_user_sum_deficit(db, user.id)
        if calc['sum_deficit'] > 0:  # Only count deficits as pending
            total_pending += calc['sum_deficit']
            details.append({
                'user_id': user.id,
                'user_name': f"{user.first_name} {user.last_name}",
                'pending_amount': calc['sum_deficit']
            })
    
    return {
        'total_pending': total_pending,
        'details': details
    }

def update_client_totals(db: Session, client_id: int):
    """Update client totals after adding a record"""
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        return
    
    records = db.query(models.ClientRecord).filter(models.ClientRecord.client_id == client_id).all()
    
    client.debit_total = sum(r.debit_amount for r in records if r.debit_amount)
    client.credit_total = sum(r.credit_amount for r in records if r.credit_amount)
    client.profit_loss_total = sum(r.profit_loss for r in records if r.profit_loss)
    
    db.commit()

def get_client_pending_amount(db: Session, client_id: int) -> dict:
    """Calculate pending amount for a client"""
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        return {}
    
    # Pending = (total_debit - total_credit) ± profit_loss_total
    pending = (client.debit_total - client.credit_total) + client.profit_loss_total
    status = "Profit" if client.profit_loss_total > 0 else "Loss" if client.profit_loss_total < 0 else "Neutral"
    
    return {
        'client_id': client.id,
        'client_name': client.name,
        'total_debit': client.debit_total,
        'total_credit': client.credit_total,
        'profit_loss_total': client.profit_loss_total,
        'pending_amount': pending,
        'status': status
    }

def get_all_clients_pending_amount(db: Session, admin_id: int) -> dict:
    """Calculate total pending amount for all clients of an admin"""
    clients = db.query(models.Client).filter(models.Client.admin_id == admin_id).all()
    
    total_pending = 0
    details = []
    
    for client in clients:
        calc = get_client_pending_amount(db, client.id)
        if calc:
            total_pending += calc['pending_amount']
            details.append({
                'client_id': client.id,
                'client_name': client.name,
                'pending_amount': calc['pending_amount'],
                'status': calc['status']
            })
    
    return {
        'total_pending': total_pending,
        'details': details
    }

# Admin CRUD
def create_admin(db: Session, admin_data: schemas.AdminRegister) -> models.Admin:
    """Create a new admin"""
    from .auth import get_password_hash
    
    # Check if admin name already exists
    existing = db.query(models.Admin).filter(models.Admin.name == admin_data.name).first()
    if existing:
        raise ValueError("Admin with this name already exists")
    
    db_admin = models.Admin(
        name=admin_data.name,
        password=get_password_hash(admin_data.password)
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def get_admin_by_uuid(db: Session, admin_uuid: str) -> Optional[models.Admin]:
    """Get admin by UUID"""
    return db.query(models.Admin).filter(models.Admin.uuid == admin_uuid).first()

# User CRUD
def create_user(db: Session, admin_id: int, user_data: schemas.UserCreate) -> models.User:
    """Create a new user"""
    db_user = models.User(
        admin_id=admin_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        mobile=user_data.mobile,
        location=user_data.location
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users_by_admin(db: Session, admin_id: int) -> List[models.User]:
    """Get all users for an admin"""
    return db.query(models.User).filter(models.User.admin_id == admin_id).all()

def get_user_by_id(db: Session, user_id: int, admin_id: int) -> Optional[models.User]:
    """Get user by ID for specific admin"""
    return db.query(models.User).filter(
        models.User.id == user_id,
        models.User.admin_id == admin_id
    ).first()

def get_user_by_uuid(db: Session, user_uuid: str, admin_id: int) -> Optional[models.User]:
    """Get user by UUID for specific admin"""
    return db.query(models.User).filter(
        models.User.uuid == user_uuid,
        models.User.admin_id == admin_id
    ).first()

def update_user_status(db: Session, user_id: int, admin_id: int, is_active: bool) -> Optional[models.User]:
    """Enable or disable a user"""
    user = get_user_by_id(db, user_id, admin_id)
    if user:
        user.is_active = is_active
        user.updated_date = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def add_user_record(db: Session, user_id: int, record_data: schemas.UserRecordCreate) -> models.UserRecord:
    """Add a transaction record for a user"""
    db_record = models.UserRecord(
        user_id=user_id,
        transaction_type=models.TransactionType[record_data.transaction_type.value.upper()]
    )
    
    if record_data.transaction_type == schemas.TransactionTypeEnum.DEBIT:
        # Calculate debit values
        calc_values = calculate_user_record_debit({
            'bags': record_data.bags,
            'kg': record_data.kg,
            'cut_weight': record_data.cut_weight,
            'amount_per_kg': record_data.amount_per_kg
        })
        
        db_record.bags = record_data.bags
        db_record.product_type = record_data.product_type
        db_record.kg = record_data.kg
        db_record.cut_weight = record_data.cut_weight
        db_record.amount_per_kg = record_data.amount_per_kg
        db_record.net_weight = calc_values['net_weight']
        db_record.rough_amount = calc_values['rough_amount']
        db_record.tax = calc_values['tax']
        db_record.levi = calc_values['levi']
        db_record.net_amount = calc_values['net_amount']
    else:
        # Credit transaction
        db_record.credit_amount = record_data.credit_amount
        db_record.round_off = record_data.round_off or 0
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_user_records(db: Session, user_id: int) -> List[models.UserRecord]:
    """Get all records for a user"""
    return db.query(models.UserRecord).filter(models.UserRecord.user_id == user_id).all()

# Client CRUD
def create_client(db: Session, admin_id: int, client_data: schemas.ClientCreate) -> models.Client:
    """Create a new client"""
    # Check if username already exists
    existing = db.query(models.Client).filter(models.Client.username == client_data.username).first()
    if existing:
        raise ValueError("Client with this username already exists")
    
    db_client = models.Client(
        admin_id=admin_id,
        name=client_data.name,
        username=client_data.username,
        location=client_data.location,
        phone_number=client_data.phone_number
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_clients_by_admin(db: Session, admin_id: int) -> List[models.Client]:
    """Get all clients for an admin"""
    return db.query(models.Client).filter(models.Client.admin_id == admin_id).all()

def get_client_by_id(db: Session, client_id: int, admin_id: int) -> Optional[models.Client]:
    """Get client by ID for specific admin"""
    return db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.admin_id == admin_id
    ).first()

def update_client(db: Session, client_id: int, admin_id: int, client_data: schemas.ClientUpdate) -> Optional[models.Client]:
    """Update client information"""
    client = get_client_by_id(db, client_id, admin_id)
    if client:
        if client_data.name:
            client.name = client_data.name
        if client_data.location:
            client.location = client_data.location
        if client_data.phone_number:
            client.phone_number = client_data.phone_number
        
        client.updated_date = datetime.utcnow()
        db.commit()
        db.refresh(client)
    return client

def add_client_record(db: Session, client_id: int, record_data: schemas.ClientRecordCreate) -> models.ClientRecord:
    """Add a transaction record for a client"""
    db_record = models.ClientRecord(
        client_id=client_id,
        transaction_type=models.TransactionType[record_data.transaction_type.value.upper()],
        credit_amount=record_data.credit_amount,
        debit_amount=record_data.debit_amount,
        profit_loss=record_data.profit_loss
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # Update client totals
    update_client_totals(db, client_id)
    
    return db_record

def get_client_records(db: Session, client_id: int) -> List[models.ClientRecord]:
    """Get all records for a client"""
    return db.query(models.ClientRecord).filter(models.ClientRecord.client_id == client_id).all()