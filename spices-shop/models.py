from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# Customer Model
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    password = Column(String, nullable=True)
    has_account = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: one customer has many orders
    orders = relationship("Order", back_populates="customer")

# Order Model
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    # Order details
    subtotal = Column(Float)
    delivery_fee = Column(Float, default=3000)  # Default delivery fee
    total_amount = Column(Float)
    
    # Status
    status = Column(String, default="pending")  # pending, paid, processing, shipped, delivered, cancelled
    payment_status = Column(String, default="unpaid")  # unpaid, paid, failed
    
    # Payment info (for later)
    payment_reference = Column(String, nullable=True)
    
    # Delivery info
    delivery_name = Column(String, nullable=True)
    delivery_address = Column(Text)
    delivery_phone = Column(String)
    delivery_city = Column(String)
    delivery_state = Column(String)
    delivery_note = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: one order has many items
    items = relationship("OrderItem", back_populates="order")
    customer = relationship("Customer", back_populates="orders")

# Order Items Model (what products they bought)
class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer)
    product_name = Column(String)  # Save name in case product changes later
    quantity = Column(Integer)
    price_at_time = Column(Float)  # Price when they bought it
    subtotal = Column(Float)
    
    # Relationship
    order = relationship("Order", back_populates="items")


# Product model (inventory)
class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            'stock_quantity >= 0',
            name='stock_quantity_non_negative'
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String, nullable=True)
    price = Column(Float, default=0.0)
    image = Column(String, nullable=True)
    stock_quantity = Column(Integer, default=100)
    low_stock_threshold = Column(Integer, default=10)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'image': self.image,
            'stock_quantity': self.stock_quantity,
            'low_stock_threshold': self.low_stock_threshold
        }


# Stock change audit log
class StockLog(Base):
    __tablename__ = "stock_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, nullable=True)
    change_type = Column(String, nullable=False)
    quantity_change = Column(Integer, nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    note = Column(String, nullable=True)