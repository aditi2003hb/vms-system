"""
Client management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, auth, database

router = APIRouter(prefix="/api/admin", tags=["Clients"])

@router.post("/{admin_uuid}/add_client", response_model=schemas.ClientResponse)
def add_client(
    admin_uuid: str,
    client_data: schemas.ClientCreate,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Add a new client for the admin"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        client = crud.create_client(db, current_admin.id, client_data)
        return client
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{admin_uuid}/clients", response_model=List[schemas.ClientResponse])
def get_clients(
    admin_uuid: str,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get all clients for the admin"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    clients = crud.get_clients_by_admin(db, current_admin.id)
    return clients

@router.post("/{admin_uuid}/client/{client_id}/add_record", response_model=schemas.ClientRecordResponse)
def add_client_record(
    admin_uuid: str,
    client_id: int,
    record_data: schemas.ClientRecordCreate,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Add a credit/debit record for a client"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    client = crud.get_client_by_id(db, client_id, current_admin.id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Validate required fields based on transaction type
    if record_data.transaction_type == schemas.TransactionTypeEnum.CREDIT:
        if not record_data.credit_amount:
            raise HTTPException(
                status_code=400,
                detail="Credit amount is required for credit transaction"
            )
    elif record_data.transaction_type == schemas.TransactionTypeEnum.DEBIT:
        if not record_data.debit_amount:
            raise HTTPException(
                status_code=400,
                detail="Debit amount is required for debit transaction"
            )
    
    record = crud.add_client_record(db, client_id, record_data)
    return record

@router.put("/{admin_uuid}/client/{client_id}/update", response_model=schemas.ClientResponse)
def update_client(
    admin_uuid: str,
    client_id: int,
    client_data: schemas.ClientUpdate,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Update client information"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    client = crud.update_client(db, client_id, current_admin.id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/{admin_uuid}/client/{client_id}/record_details")
def get_client_record_details(
    admin_uuid: str,
    client_id: int,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get credit/debit/profit/loss list for a client"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    client = crud.get_client_by_id(db, client_id, current_admin.id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    records = crud.get_client_records(db, client_id)
    
    credit_records = []
    debit_records = []
    profit_loss_records = []
    
    for record in records:
        record_dict = {
            "id": record.id,
            "date": record.created_date,
            "transaction_type": record.transaction_type.value
        }
        
        if record.credit_amount:
            record_dict["amount"] = record.credit_amount
            credit_records.append(record_dict)
        
        if record.debit_amount:
            record_dict["amount"] = record.debit_amount
            debit_records.append(record_dict)
        
        if record.profit_loss is not None:
            profit_loss_records.append({
                "id": record.id,
                "date": record.created_date,
                "amount": record.profit_loss,
                "type": "Profit" if record.profit_loss > 0 else "Loss"
            })
    
    return {
        "client_id": client_id,
        "client_name": client.name,
        "credit_records": credit_records,
        "debit_records": debit_records,
        "profit_loss_records": profit_loss_records,
        "total_credits": len(credit_records),
        "total_debits": len(debit_records),
        "total_profit_loss_entries": len(profit_loss_records)
    }

@router.get("/{admin_uuid}/client/{client_id}/calculate_record_details", response_model=schemas.ClientCalculationResponse)
def calculate_client_record_details(
    admin_uuid: str,
    client_id: int,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Calculate total profit/loss and pending amount for a client"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    client = crud.get_client_by_id(db, client_id, current_admin.id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    calc = crud.get_client_pending_amount(db, client_id)
    return schemas.ClientCalculationResponse(**calc)

@router.get("/{admin_uuid}/client_panel_names")
def get_client_panel_names(
    admin_uuid: str,
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get client names for sidebar panel"""
    if current_admin.uuid != admin_uuid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    clients = crud.get_clients_by_admin(db, current_admin.id)
    return [
        {
            "id": client.id,
            "uuid": client.uuid,
            "name": client.name,
            "username": client.username,
            "pending_amount": crud.get_client_pending_amount(db, client.id).get('pending_amount', 0)
        }
        for client in clients
    ]