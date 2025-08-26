"""
User management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, auth, database

router = APIRouter(prefix="/api/admin", tags=["Users"])

@router.post("/{admin_uuid}/add_user", response_model=schemas.UserResponse)
def add_user(
    admin_uuid: str,
    user_data: schemas.UserCreate,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Add a new user for the admin"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = crud.create_user(db, current_admin.id, user_data)
    return user

@router.get("/{admin_uuid}/users", response_model=List[schemas.UserResponse])
def get_users(
    admin_uuid: str,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get all users for the admin"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    users = crud.get_users_by_admin(db, current_admin.id)
    return users

@router.put("/{admin_uuid}/user/{user_id}/enable", response_model=schemas.UserResponse)
def enable_user(
    admin_uuid: str,
    user_id: int,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Enable a user"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = crud.update_user_status(db, user_id, current_admin.id, True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{admin_uuid}/user/{user_id}/disable", response_model=schemas.UserResponse)
def disable_user(
    admin_uuid: str,
    user_id: int,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Disable a user"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = crud.update_user_status(db, user_id, current_admin.id, False)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{admin_uuid}/user_panel_names")
def get_user_panel_names(
    admin_uuid: str,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get user names for sidebar panel"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    users = crud.get_users_by_admin(db, current_admin.id)
    return [
        {
            "id": user.id,
            "uuid": user.uuid,
            "name": f"{user.first_name} {user.last_name}",
            "is_active": user.is_active
        }
        for user in users
    ]

@router.get("/{admin_uuid}/user/{user_uuid}/records", response_model=List[schemas.UserRecordResponse])
def get_user_records_by_uuid(
    admin_uuid: str,
    user_uuid: str,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get records for a user by UUID"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = crud.get_user_by_uuid(db, user_uuid, current_admin.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    records = crud.get_user_records(db, user.id)
    return records

@router.post("/{admin_uuid}/user/{user_id}/add_record", response_model=schemas.UserRecordResponse)
def add_user_record(
    admin_uuid: str,
    user_id: int,
    record_data: schemas.UserRecordCreate,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Add a credit/debit transaction for a user"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = crud.get_user_by_id(db, user_id, current_admin.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate required fields based on transaction type
    if record_data.transaction_type == schemas.TransactionTypeEnum.DEBIT:
        if not all([record_data.bags, record_data.product_type, record_data.kg, 
                    record_data.cut_weight is not None, record_data.amount_per_kg]):
            raise HTTPException(
                status_code=400, 
                detail="All debit fields are required for debit transaction"
            )
    elif record_data.transaction_type == schemas.TransactionTypeEnum.CREDIT:
        if not record_data.credit_amount:
            raise HTTPException(
                status_code=400,
                detail="Credit amount is required for credit transaction"
            )
    
    record = crud.add_user_record(db, user_id, record_data)
    return record

@router.get("/{admin_uuid}/user/{user_id}/record_details")
def get_user_record_details(
    admin_uuid: str,
    user_id: int,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get credit/debit list for a user"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = crud.get_user_by_id(db, user_id, current_admin.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    records = crud.get_user_records(db, user_id)
    
    credit_records = []
    debit_records = []
    
    for record in records:
        if record.transaction_type == models.TransactionType.CREDIT:
            credit_records.append({
                "id": record.id,
                "date": record.created_date,
                "amount": record.credit_amount,
                "round_off": record.round_off
            })
        else:
            debit_records.append({
                "id": record.id,
                "date": record.created_date,
                "bags": record.bags,
                "product_type": record.product_type,
                "kg": record.kg,
                "cut_weight": record.cut_weight,
                "net_weight": record.net_weight,
                "amount_per_kg": record.amount_per_kg,
                "rough_amount": record.rough_amount,
                "tax": record.tax,
                "levi": record.levi,
                "net_amount": record.net_amount
            })
    
    return {
        "user_id": user_id,
        "user_name": f"{user.first_name} {user.last_name}",
        "credit_records": credit_records,
        "debit_records": debit_records,
        "total_credits": len(credit_records),
        "total_debits": len(debit_records)
    }

@router.get("/{admin_uuid}/user/{user_id}/calculate_record_details", response_model=schemas.UserCalculationResponse)
def calculate_user_record_details(
    admin_uuid: str,
    user_id: int,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Calculate sum/deficit for a user"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = crud.get_user_by_id(db, user_id, current_admin.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    calc = crud.get_user_sum_deficit(db, user_id)
    
    return schemas.UserCalculationResponse(
        user_id=user_id,
        user_name=f"{user.first_name} {user.last_name}",
        **calc
    )