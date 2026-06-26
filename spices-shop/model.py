from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from database import Base
from datetime import datetime

# Customer Model
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Required
    phone = Column(String)  # Required
    first_name = Column(String)  # Required
    last_name = Column(String)  # Required
    address = Column(Text)  # Required
    city = Column(String)  # Required
    state = Column(String)  # Required
    
    # Optional account stuff
    password = Column(String, nullable=True)  # NULL if guest
    has_account = Column(Boolean, default=False)  # FALSE if guest
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

# Order Model (we'll expand this later)
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    customer_id = Column(Integer)  # Link to customer
    total_amount = Column(Float)
    status = Column(String, default="pending")  # pending, paid, delivered
    created_at = Column(DateTime, default=datetime.utcnow)