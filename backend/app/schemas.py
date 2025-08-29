"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransactionTypeEnum(str, Enum):
    """Transaction type enum"""
    CREDIT = "credit"
    DEBIT = "debit"

# Admin Schemas
class AdminRegister(BaseModel):
    """Admin registration schema"""
    name: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class AdminLogin(BaseModel):
    """Admin login schema"""
    name: str
    password: str

class AdminResponse(BaseModel):
    """Admin response schema"""
    id: int
    name: str
    uuid: str
    created_date: datetime
    
    class Config:
        from_attributes = True

# User Schemas
class UserCreate(BaseModel):
    """User creation schema"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    mobile: str = Field(..., pattern="^[0-9]{10}$")
    location: str = Field(..., max_length=100)
    
    @validator('mobile')
    def validate_mobile(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('Mobile number must be exactly 10 digits')
        return v

class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    mobile: Optional[str] = Field(None, pattern="^[0-9]{10}$")
    location: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    uuid: str
    first_name: str
    last_name: str
    mobile: str
    location: str
    is_active: bool
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True

# User Record Schemas
class UserRecordDebit(BaseModel):
    """User debit record schema"""
    bags: int = Field(..., gt=0)
    product_type: str
    kg: float = Field(..., gt=0)
    cut_weight: float = Field(..., ge=0)
    amount_per_kg: float = Field(..., gt=0)

class UserRecordCredit(BaseModel):
    """User credit record schema"""
    credit_amount: float = Field(..., gt=0)
    round_off: float = Field(default=0.0)

class UserRecordCreate(BaseModel):
    """User record creation schema"""
    transaction_type: TransactionTypeEnum
    # Debit fields (optional)
    bags: Optional[int] = None
    product_type: Optional[str] = None
    kg: Optional[float] = None
    cut_weight: Optional[float] = None
    amount_per_kg: Optional[float] = None
    # Credit fields (optional)
    credit_amount: Optional[float] = None
    round_off: Optional[float] = None

class UserRecordResponse(BaseModel):
    """User record response schema"""
    id: int
    user_id: int
    transaction_type: str
    created_date: datetime
    bags: Optional[int]
    product_type: Optional[str]
    kg: Optional[float]
    cut_weight: Optional[float]
    net_weight: Optional[float]
    amount_per_kg: Optional[float]
    rough_amount: Optional[float]
    tax: Optional[float]
    levi: Optional[float]
    net_amount: Optional[float]
    credit_amount: Optional[float]
    round_off: Optional[float]
    
    class Config:
        from_attributes = True

# Client Schemas
class ClientCreate(BaseModel):
    """Client creation schema"""
    name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    location: str = Field(..., max_length=100)
    phone_number: str = Field(..., pattern="^[0-9]{10}$")

class ClientUpdate(BaseModel):
    """Client update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, pattern="^[0-9]{10}$")

class ClientResponse(BaseModel):
    """Client response schema"""
    id: int
    uuid: str
    name: str
    username: str
    location: str
    phone_number: str
    created_date: datetime
    updated_date: datetime
    debit_total: float
    credit_total: float
    profit_loss_total: float
    
    class Config:
        from_attributes = True

# Client Record Schemas
class ClientRecordCreate(BaseModel):
    """Client record creation schema"""
    transaction_type: TransactionTypeEnum
    credit_amount: Optional[float] = None
    debit_amount: Optional[float] = None
    profit_loss: Optional[float] = None

class ClientRecordResponse(BaseModel):
    """Client record response schema"""
    id: int
    client_id: int
    transaction_type: str
    created_date: datetime
    credit_amount: Optional[float]
    debit_amount: Optional[float]
    profit_loss: Optional[float]
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardResponse(BaseModel):
    """Dashboard response schema"""
    admin_name: str
    total_users: int
    active_users: int
    total_clients: int
    users_pending_amount: float
    clients_pending_amount: float
    recent_users: List[UserResponse]
    recent_clients: List[ClientResponse]

# Calculation Schemas
class UserCalculationResponse(BaseModel):
    """User calculation response"""
    user_id: int
    user_name: str
    total_debit: float
    total_credit: float
    sum_deficit: float  # total_debit - total_credit
    status: str  # "Surplus" or "Deficit"

class ClientCalculationResponse(BaseModel):
    """Client calculation response"""
    client_id: int
    client_name: str
    total_debit: float
    total_credit: float
    profit_loss_total: float
    pending_amount: float  # (total_debit - total_credit) ± profit_loss
    status: str  # "Profit" or "Loss"

class PendingAmountResponse(BaseModel):
    """Pending amount response"""
    total_pending: float
    details: List[dict]