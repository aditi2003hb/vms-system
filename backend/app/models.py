"""
SQLAlchemy database models for VMS
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from .database import Base

class TransactionType(enum.Enum):
    """Transaction type enumeration"""
    CREDIT = "credit"
    DEBIT = "debit"

class Admin(Base):
    """Admin model"""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Hashed password
    uuid = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="admin", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="admin", cascade="all, delete-orphan")

class User(Base):
    """User (Buyer) model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    uuid = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    mobile = Column(String(10), nullable=False)
    location = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    admin = relationship("Admin", back_populates="users")
    records = relationship("UserRecord", back_populates="user", cascade="all, delete-orphan")

class UserRecord(Base):
    """User transaction records"""
    __tablename__ = "user_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Debit transaction fields
    bags = Column(Integer, nullable=True)
    product_type = Column(String, nullable=True)
    kg = Column(Float, nullable=True)
    cut_weight = Column(Float, nullable=True)
    net_weight = Column(Float, nullable=True)
    amount_per_kg = Column(Float, nullable=True)
    rough_amount = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    levi = Column(Float, nullable=True)
    net_amount = Column(Float, nullable=True)
    
    # Credit transaction fields
    credit_amount = Column(Float, nullable=True)
    round_off = Column(Float, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="records")

class Client(Base):
    """Client (Vendor/Seller) model"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    uuid = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    location = Column(String)
    phone_number = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    debit_total = Column(Float, default=0.0)
    credit_total = Column(Float, default=0.0)
    profit_loss_total = Column(Float, default=0.0)
    
    # Relationships
    admin = relationship("Admin", back_populates="clients")
    records = relationship("ClientRecord", back_populates="client", cascade="all, delete-orphan")

class ClientRecord(Base):
    """Client transaction records"""
    __tablename__ = "client_records"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    credit_amount = Column(Float, nullable=True)
    debit_amount = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="records")