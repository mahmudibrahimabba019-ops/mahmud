from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from typing import List
import random
import string
import secrets
import uuid
import httpx
import os
import hmac
import hashlib
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables (including ADMIN_PASSWORD)
load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "halari_admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "spices2024")
admin_tokens = set()

# Create database tables
Base.metadata.create_all(bind=engine)

# SQLite compatibility check: ensure is_active column exists for existing products table
# PostgreSQL creates this column correctly via create_all() when the Product table is first created.
database_url = os.getenv("DATABASE_URL", "sqlite:///./halari_spices.db")
if database_url.startswith("sqlite"):
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check if is_active column exists
            result = conn.execute(text("PRAGMA table_info(products)")).fetchall()
            column_names = [row[1] for row in result]  # Column name is at index 1
            if 'is_active' not in column_names:
                # Add the column with default value True for existing rows
                conn.execute(text("ALTER TABLE products ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL"))
                conn.commit()
                print("[STARTUP] Added is_active column to products table with default=True")
    except Exception as e:
        print(f"[STARTUP] SQLite compatibility check error (non-critical): {e}")

app = FastAPI(
    title="Halari House of Seasoning",
    description="Welcome to Halari House of Seasoning - Your premier destination for authentic Nigerian spices, herbs, and specialty yaji blends. Bringing flavor to your kitchen!"
)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allowed origins — add your production domain when you deploy
allowed_origins = [
    "http://127.0.0.1:3000",      # local frontend dev server
    "http://localhost:3000",       # local alternative
    "http://127.0.0.1:8001",      # local direct access
    "https://halari-frontend.onrender.com",
    "https://halariseasonings.com",
    "https://www.halariseasonings.com",
]

# Read production domain from environment if set
production_url = os.getenv("FRONTEND_URL")
if production_url:
    allowed_origins.append(production_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Token", "Authorization"],
)

# Serve images from the dedicated images folder at /images
app.mount("/images", StaticFiles(directory="images"), name="images")

# ============ PYDANTIC MODELS (Request/Response) ============

# Customer creation (for guest checkout)
class CustomerCreate(BaseModel):
    email: str
    phone: str
    first_name: str
    last_name: str
    address: str
    city: str
    state: str
    password: str = None  # Optional - if they want account

# Customer response (what we send back)
class CustomerResponse(BaseModel):
    id: int
    email: str
    phone: str
    first_name: str
    last_name: str
    address: str
    city: str
    state: str
    has_account: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ============ ORDER MODELS ============

class OrderItemCreate(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price_at_time: float
    subtotal: float

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]
    subtotal: float
    delivery_fee: float = 3000
    total_amount: float
    delivery_address: str
    delivery_phone: str
    delivery_city: str
    delivery_state: str
    delivery_note: str = None
    payment_reference: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    subtotal: float
    delivery_fee: float
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime
    items: List[dict] = []
    
    class Config:
        from_attributes = True

# Simple response (extended for customers and orders)
class MessageResponse(BaseModel):
    message: str
    customer_id: int = None
    order_id: int = None
    order_number: str = None
    payment_reference: Optional[str] = None

# ============ ADMIN MODELS ============

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    message: str
    logged_in: bool
    token: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: str
    payment_status: str = None

class PaymentReferenceUpdate(BaseModel):
    payment_reference: str

# Your 42 products with images
PRODUCTS = [
    # ============ SPICES (28) ============
    {"id": 1, "name": "All spice", "category": "spices", "price": 8000, "image": "ALL SPICE.jpeg"},
    {"id": 2, "name": "Black pepper", "category": "spices", "price": 4000, "image": "BLACK PEPPER.jpeg"},
    {"id": 3, "name": "Black Peppercorn", "category": "spices", "price": 2000, "image": "BLACK PEPPERCORN.jpeg"},
    {"id": 4, "name": "Cardamom", "category": "spices", "price": 7000, "image": "CARDAMOM.jpeg"},
    {"id": 5, "name": "Cayenne Pepper", "category": "spices", "price": 3500, "image": "CAYENNE PEPPER.jpeg"},
    {"id": 6, "name": "Chia Seeds", "category": "SUPERFOODS", "price": 2000, "image": "CHIA SEEDS.jpeg"},
    {"id": 7, "name": "Chili flakes", "category": "spices", "price": 3000, "image": "CHILI FLAKES.jpeg"},
    {"id": 8, "name": "Chili pepper", "category": "spices", "price": 1500, "image": "CHILLI PEPPER.jpeg"},
    {"id": 9, "name": "Cinnamon powder", "category": "spices", "price": 6000, "image": "CINNAMON POWDER.jpeg"},
    {"id": 10, "name": "Cinnamon sticks", "category": "spices", "price": 3000, "image": "CINNAMON STICKS.jpeg"},
    {"id": 11, "name": "Cloves", "category": "spices", "price": 3000, "image": "CLOVES.jpeg"},
    {"id": 12, "name": "Coriander powder", "category": "spices", "price": 2000, "image": "CORIANDER.jpeg"},
    {"id": 13, "name": "Cumin seeds", "category": "spices", "price": 3000, "image": "CUMIN SEEDS.jpeg"},
    {"id": 14, "name": "Fennel seeds", "category": "spices", "price": 2000, "image": "FENNEL.jpeg"},
    {"id": 15, "name": "Fenugreek", "category": "spices", "price": 1500, "image": "FENUGREEK.jpeg"},
    {"id": 16, "name": "Flax seeds", "category": "SUPERFOODS", "price": 2500, "image": "FLAX SEEDS.jpeg"},
    {"id": 17, "name": "Garlic powder", "category": "spices", "price": 2500, "image": "GARLIC POWDER.jpeg"},
    {"id": 18, "name": "Ginger powder", "category": "spices", "price": 2000, "image": "GINGER POWDER.jpeg"},
    {"id": 19, "name": "Negro pepper", "category": "spices", "price": 2000, "image": "NEGRO PEPPER.jpeg"},
    {"id": 20, "name": "Nutmeg", "category": "spices", "price": 4000, "image": "NUTMEG.jpeg"},
    {"id": 21, "name": "Paprika", "category": "spices", "price": 3000, "image": "PAPRIKA.jpeg"},
    {"id": 22, "name": "Saffron", "category": "spices", "price": 3500, "image": "SAFFRON.jpeg"},
    {"id": 23, "name": "Seasalt", "category": "SEASONING BASE", "price": 1500, "image": "SEASALT.jpeg"},
    {"id": 24, "name": "Sesame seeds", "category": "SUPERFOODS", "price": 3000, "image": "SESAME SEEDS.jpeg"},
    {"id": 25, "name": "Star anise", "category": "spices", "price": 1500, "image": "STAR ANISE.jpeg"},
    {"id": 26, "name": "Turmeric", "category": "spices", "price": 2500, "image": "TURMERIC.jpeg"},
    {"id": 27, "name": "White pepper", "category": "spices", "price": 6500, "image": "WHITE PEPPER.jpeg"},
    {"id": 28, "name": "White peppercorn", "category": "spices", "price": 3500, "image": "WHITE PEPPERCORN.jpeg"},

    # ============ HERBS (8) ============
    {"id": 29, "name": "Basil", "category": "herbs", "price": 2000, "image": "BASIL.jpeg"},
    {"id": 30, "name": "Bayleaf", "category": "herbs", "price": 1500, "image": "BAYLEAF.jpeg"},
    {"id": 31, "name": "Lemongrass", "category": "herbs", "price": 1200, "image": "LEMONGRASS.jpeg"},
    {"id": 32, "name": "Mint", "category": "herbs", "price": 1500, "image": "MINT.jpeg"},
    {"id": 33, "name": "Oregano", "category": "herbs", "price": 2500, "image": "OREGANO.jpeg"},
    {"id": 34, "name": "Parsley", "category": "herbs", "price": 1500, "image": "PARSLEY.jpeg"},
    {"id": 35, "name": "Rosemary", "category": "herbs", "price": 2500, "image": "ROSEMARY.jpeg"},
    {"id": 36, "name": "Thyme", "category": "herbs", "price": 2500, "image": "THYME.jpeg"},

    # ============ YAJI (6) ============
    {"id": 37, "name": "150g All spice Yaji", "category": "yaji", "price": 2500, "image": "ALL SPICE YAJI.jpeg"},
    {"id": 38, "name": "150g Daddawa Yaji", "category": "yaji", "price": 2500, "image": "DADDAWA YAJI.jpeg"},
    {"id": 39, "name": "150g Garlic Yaji", "category": "yaji", "price": 3000, "image": "GARLIC YAJI.jpeg"},
    {"id": 40, "name": "400g All spice Yaji", "category": "yaji", "price": 6500, "image": "ALL SPICE YAJI.jpeg"},
    {"id": 41, "name": "400g Daddawa Yaji", "category": "yaji", "price": 6500, "image": "DADDAWA YAJI.jpeg"},
    {"id": 42, "name": "400g Garlic Yaji", "category": "yaji", "price": 7000, "image": "GARLIC YAJI.jpeg"}
]

@app.get("/")
def home():
    return {
        "company": "Halari House of Seasoning",
        "message": "Welcome to Halari House of Seasoning",
        "description": "Your premier destination for authentic Nigerian spices, herbs, and specialty yaji blends. Bringing flavor to your kitchen!",
        "total_products": len(PRODUCTS)
    }

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    """Return active products list augmented with stock info from the database when available."""
    products_with_stock = []
    for p in PRODUCTS:
        # Check if product is active
        prod_db = db.query(models.Product).filter(models.Product.id == p.get('id')).first()
        is_active = prod_db.is_active if prod_db else True  # Default to True for products not yet in DB
        
        # Skip inactive products for customers
        if not is_active:
            continue
            
        prod = dict(p)
        prod['stock_quantity'] = prod_db.stock_quantity if prod_db else 100
        prod['low_stock_threshold'] = prod_db.low_stock_threshold if prod_db else 10
        prod['is_active'] = is_active
        products_with_stock.append(prod)
    return products_with_stock

@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    for product in PRODUCTS:
        if product["id"] == product_id:
            prod_db = db.query(models.Product).filter(models.Product.id == product_id).first()
            is_active = prod_db.is_active if prod_db else True  # Default to True
            
            # Return 404 if product is inactive (hidden from customers)
            if not is_active:
                raise HTTPException(status_code=404, detail="Product not found")
            
            prod = dict(product)
            prod['stock_quantity'] = prod_db.stock_quantity if prod_db else 100
            prod['low_stock_threshold'] = prod_db.low_stock_threshold if prod_db else 10
            prod['is_active'] = is_active
            return prod
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/products/category/{category}")
def get_products_by_category(category: str, db: Session = Depends(get_db)):
    category_products = []
    for p in PRODUCTS:
        if p["category"] == category:
            prod_db = db.query(models.Product).filter(models.Product.id == p.get('id')).first()
            is_active = prod_db.is_active if prod_db else True  # Default to True
            
            # Skip inactive products for customers
            if not is_active:
                continue
            
            category_products.append(p)
    return category_products


# ============ CUSTOMER ENDPOINTS ============

@app.post("/customers/guest", response_model=MessageResponse)
@limiter.limit("10/minute")
def create_guest_customer(request: Request, customer: CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer (guest checkout - no password required)
    """
    # Check if customer already exists with this email
    existing_customer = db.query(models.Customer).filter(
        models.Customer.email == customer.email
    ).first()
    
    if existing_customer:
        return MessageResponse(
            message="Welcome back! Using your existing account.",
            customer_id=existing_customer.id
        )
    
    # Create new customer (guest - no password)
    db_customer = models.Customer(
        email=customer.email,
        phone=customer.phone,
        first_name=customer.first_name,
        last_name=customer.last_name,
        address=customer.address,
        city=customer.city,
        state=customer.state,
        password=None,  # No password for guest
        has_account=False  # Guest account
    )
    
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    return MessageResponse(
        message="Customer created successfully! You can now proceed to payment.",
        customer_id=db_customer.id
    )

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Get customer details by ID
    """
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer

@app.get("/customers/email/{email}", response_model=CustomerResponse)
def get_customer_by_email(email: str, db: Session = Depends(get_db)):
    """
    Find customer by email
    """
    customer = db.query(models.Customer).filter(
        models.Customer.email == email
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer


# ============ ORDER ENDPOINTS ============

def generate_order_number():
    """Generate unique order number like HHS-2024-1234"""
    year = datetime.now().year
    random_num = random.randint(1000, 9999)
    return f"HHS-{year}-{random_num}"


@app.post("/orders/create", response_model=MessageResponse)
@limiter.limit("10/minute")
def create_order(request: Request, order: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order from cart
    """
    print(f"[DEBUG] Received payment_reference: {repr(order.payment_reference)}")
    print(f"[DEBUG] Order received - customer_id: {order.customer_id}, items: {len(order.items)}, total: {order.total_amount}")
    # Check if customer exists
    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate unique order number
    order_number = generate_order_number()
    payment_ref = f"HHS-{uuid.uuid4().hex[:12].upper()}"
    # Check stock availability for each item before creating order
    for item in order.items:
        prod_db = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        available = prod_db.stock_quantity if prod_db else 100
        if available < item.quantity:
            raise HTTPException(status_code=400, detail=f"Sorry, only {available} units of {item.product_name} available")

    # Recalculate prices server-side from database
    calculated_subtotal = 0.0
    validated_items = []

    for item in order.items:
        prod_db = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()
        if not prod_db:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )
        real_price = prod_db.price
        real_subtotal = real_price * item.quantity
        calculated_subtotal += real_subtotal
        validated_items.append({
            "product_id": item.product_id,
            "product_name": prod_db.name,
            "quantity": item.quantity,
            "price_at_time": real_price,
            "subtotal": real_subtotal
        })

    delivery_fee = 3000.0
    calculated_total = calculated_subtotal + delivery_fee

    if abs(calculated_total - order.total_amount) > 1.0:
        print(f"[SECURITY] Price mismatch: frontend={order.total_amount}, server={calculated_total}")
        raise HTTPException(
            status_code=400,
            detail=f"Order total mismatch. Expected ₦{calculated_total}, got ₦{order.total_amount}. Please refresh and try again."
        )

    # Create the order
    db_order = models.Order(
        order_number=order_number,
        customer_id=order.customer_id,
        subtotal=calculated_subtotal,
        delivery_fee=delivery_fee,
        total_amount=calculated_total,
        status="pending",
        payment_status="unpaid",
        payment_reference=payment_ref,
        delivery_name=f"{order.first_name or ''} {order.last_name or ''}".strip() or None,
        delivery_first_name=order.first_name,
        delivery_last_name=order.last_name,
        delivery_email=order.email,
        delivery_address=order.delivery_address,
        delivery_phone=order.delivery_phone,
        delivery_city=order.delivery_city,
        delivery_state=order.delivery_state,
        delivery_note=order.delivery_note
    )
    
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add order items
    for item in validated_items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item["product_id"],
            product_name=item["product_name"],
            quantity=item["quantity"],
            price_at_time=item["price_at_time"],
            subtotal=item["subtotal"]
        )
        db.add(db_item)
    
    db.commit()
    
    return MessageResponse(
        message="Order created successfully!",
        order_id=db_order.id,
        order_number=db_order.order_number,
        payment_reference=payment_ref
    )


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get order details by ID
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get order items
    items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
    
    # Convert items to dict
    items_list = []
    for item in items:
        items_list.append({
            "product_id": item.product_id,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "price": item.price_at_time,
            "subtotal": item.subtotal
        })
    
    # Create response
    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_id": order.customer_id,
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "total_amount": order.total_amount,
        "status": order.status,
        "payment_status": order.payment_status,
        "created_at": order.created_at,
        "items": items_list
    }


@app.get("/orders/customer/{customer_id}")
def get_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    """
    Get all orders for a customer
    """
    orders = db.query(models.Order).filter(
        models.Order.customer_id == customer_id
    ).order_by(models.Order.created_at.desc()).all()
    
    return orders


@app.patch("/orders/{order_id}/payment-reference")
def update_payment_reference(order_id: int, update: PaymentReferenceUpdate, db: Session = Depends(get_db)):
    """
    Update the payment reference for an order after Paystack returns it.
    Called from the frontend after Paystack popup closes with the real reference.
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.payment_status != "unpaid":
        raise HTTPException(
            status_code=400,
            detail="Cannot update reference: order is already paid or failed"
        )

    existing = db.query(models.Order).filter(
        models.Order.payment_reference == update.payment_reference,
        models.Order.id != order_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="This payment reference is already attached to another order"
        )

    order.payment_reference = update.payment_reference
    db.commit()

    return {"message": "Payment reference updated"}


# ============ ADMIN ENDPOINTS ============

@app.post("/admin/login", response_model=AdminResponse)
@limiter.limit("5/minute")
def admin_login(request: Request, login: AdminLogin):
    """
    Simple admin login
    """
    if login.username == ADMIN_USERNAME and login.password == os.getenv('ADMIN_PASSWORD', 'spices2024'):
        token = secrets.token_hex(32)
        admin_tokens.add(token)
        return AdminResponse(
            message="Login successful! Welcome to Halari House admin.",
            logged_in=True,
            token=token
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/admin/logout")
def admin_logout(request: Request):
    token = request.headers.get("X-Admin-Token")
    if token in admin_tokens:
        admin_tokens.discard(token)
    return {"message": "Logged out successfully"}


def verify_admin_token(request: Request):
    token = request.headers.get("X-Admin-Token")
    if not token or token not in admin_tokens:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized — admin login required"
        )
    return token


# ============ ADMIN PRODUCTS ENDPOINTS ============

@app.get("/admin/products")
def admin_get_all_products(db: Session = Depends(get_db), token: str = Depends(verify_admin_token)):
    """Return ALL products (including inactive/hidden) with stock info. Admin only."""
    products_with_stock = []
    for p in PRODUCTS:
        prod = dict(p)
        prod_db = db.query(models.Product).filter(models.Product.id == p.get('id')).first()
        prod['stock_quantity'] = prod_db.stock_quantity if prod_db else 100
        prod['low_stock_threshold'] = prod_db.low_stock_threshold if prod_db else 10
        prod['is_active'] = prod_db.is_active if prod_db else True
        products_with_stock.append(prod)
    return products_with_stock


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


def update_env_var(key: str, value: str, env_path: str = ".env"):
    """Replace or add a key in a .env file at env_path."""
    try:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []

        key_found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                key_found = True
                break

        if not key_found:
            # Ensure newline at end
            if lines and not lines[-1].endswith('\n'):
                lines[-1] = lines[-1] + '\n'
            lines.append(f"{key}={value}\n")

        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print('Failed to update .env:', e)
        return False


@app.post('/admin/change-password')
def admin_change_password(payload: ChangePasswordRequest, token: str = Depends(verify_admin_token)):
    """Allow admin to change their password (updates .env)."""
    stored = os.getenv('ADMIN_PASSWORD', 'spices2024')
    if payload.current_password != stored:
        raise HTTPException(status_code=401, detail='Current password is incorrect')
    if not payload.new_password or len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail='New password must be at least 6 characters')

    ok = update_env_var('ADMIN_PASSWORD', payload.new_password)
    if not ok:
        raise HTTPException(status_code=500, detail='Failed to update password file')

    # Update runtime env so subsequent checks use new password immediately
    os.environ['ADMIN_PASSWORD'] = payload.new_password
    return { 'message': 'Password updated successfully!' }


@app.get("/admin")
def admin_home(token: str = Depends(verify_admin_token)):
    """
    Admin home - lists all available admin endpoints
    """
    return {
        "admin_endpoints": {
            "login": "POST /admin/login - Login as admin",
            "dashboard": "GET /admin/summary - View dashboard summary",
            "all_orders": "GET /admin/orders - View all orders",
            "order_details": "GET /admin/orders/{id} - View specific order",
            "update_order": "PUT /admin/orders/{id}/status - Update order status",
            "all_customers": "GET /admin/customers - View all customers"
        }
    }


@app.get("/admin/summary")
def admin_summary(db: Session = Depends(get_db), token: str = Depends(verify_admin_token)):
    """
    Get summary dashboard data for admin
    """
    from datetime import date
    
    today = date.today()
    
    # Get today's orders
    today_orders = db.query(models.Order).filter(
        models.Order.created_at >= str(today)
    ).all()
    
    # Calculate today's sales
    today_sales = sum(order.total_amount for order in today_orders)
    
    # Get total customers
    total_customers = db.query(models.Customer).count()
    
    # Get pending orders
    pending_orders = db.query(models.Order).filter(
        models.Order.status == "pending"
    ).count()
    
    # Get 5 most recent orders
    recent = db.query(models.Order).order_by(
        models.Order.created_at.desc()
    ).limit(5).all()
    
    recent_orders_list = []
    for order in recent:
        # Get customer name
        customer = db.query(models.Customer).filter(
            models.Customer.id == order.customer_id
        ).first()
        
        customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown"
        
        recent_orders_list.append({
            "order_number": order.order_number,
            "created_at": str(order.created_at),
            "customer": customer_name,
            "total": order.total_amount,
            "status": order.status,
            "payment_status": order.payment_status
        })
    
    return {
        "total_orders_today": len(today_orders),
        "total_sales_today": today_sales,
        "total_customers": total_customers,
        "pending_orders": pending_orders,
        "recent_orders": recent_orders_list
    }


@app.post("/admin/products/{product_id}/stock")
def update_product_stock(product_id: int, payload: dict, db: Session = Depends(get_db), token: str = Depends(verify_admin_token)):
    """Update stock for a product. Payload: { "delta": 10 } or { "set": 50 }"""
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        # Create product entry using PRODUCTS list if available
        p = next((x for x in PRODUCTS if x.get('id') == product_id), None)
        if p:
            prod = models.Product(id=p['id'], name=p.get('name'), category=p.get('category'), price=p.get('price', 0), image=p.get('image'))
            db.add(prod)
            db.commit()
            db.refresh(prod)
        else:
            raise HTTPException(status_code=404, detail='Product not found')

    old_qty = prod.stock_quantity

    if 'set' in payload:
        # Explicitly allow zero; reject negative set values
        try:
            new_qty = int(payload.get('set', prod.stock_quantity))
        except Exception:
            raise HTTPException(status_code=400, detail='Invalid set value')
        if new_qty < 0:
            raise HTTPException(status_code=400, detail='Stock must be >= 0')
    elif 'delta' in payload:
        delta = int(payload.get('delta', 0))
        # Apply delta but never allow negative final stock; clamp to 0
        new_qty = max(0, old_qty + delta)
    else:
        new_qty = old_qty

    prod.stock_quantity = new_qty

    db.add(prod)

    log = models.StockLog(
        product_id=prod.id,
        order_id=None,
        change_type="manual_increase" if new_qty > old_qty else "manual_decrease",
        quantity_change=new_qty - old_qty,
        quantity_before=old_qty,
        quantity_after=new_qty,
        note="Manual admin adjustment"
    )
    db.add(log)

    db.commit()
    return { 'message': 'Stock updated', 'product_id': prod.id, 'stock_quantity': prod.stock_quantity }


@app.patch("/admin/products/{product_id}/toggle-active")
def toggle_product_active(product_id: int, db: Session = Depends(get_db), token: str = Depends(verify_admin_token)):
    """Toggle a product's is_active status (hide/show from storefront). Admin only."""
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        # Create product entry using PRODUCTS list if available
        p = next((x for x in PRODUCTS if x.get('id') == product_id), None)
        if p:
            prod = models.Product(
                id=p['id'],
                name=p.get('name'),
                category=p.get('category'),
                price=p.get('price', 0),
                image=p.get('image'),
                is_active=True  # Default to active when first created
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)
        else:
            raise HTTPException(status_code=404, detail='Product not found')

    # Toggle the state
    old_state = prod.is_active
    prod.is_active = not prod.is_active
    db.commit()

    return {
        'message': f"Product {'hidden' if not prod.is_active else 'shown'} successfully",
        'product_id': prod.id,
        'product_name': prod.name,
        'is_active': prod.is_active,
        'previous_state': old_state
    }


@app.get('/admin/low-stock')
def get_low_stock(db: Session = Depends(get_db), token: str = Depends(verify_admin_token)):
    prods = db.query(models.Product).filter(models.Product.stock_quantity < models.Product.low_stock_threshold).all()
    return [p.to_dict() for p in prods]


@app.get("/admin/orders")
def admin_get_all_orders(
    from_date: str = None,
    to_date: str = None,
    today: bool = False,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """
    Get all orders (admin only)
    """
    query = db.query(models.Order)

    # Handle today shortcut
    if today:
        today_date = date.today()
        start = datetime.combine(today_date, datetime.min.time())
        end = datetime.combine(today_date, datetime.max.time())
        query = query.filter(models.Order.created_at >= start, models.Order.created_at <= end)
    else:
        # Handle from/to date range if provided (YYYY-MM-DD)
        try:
            if from_date:
                start = datetime.strptime(from_date, '%Y-%m-%d')
                query = query.filter(models.Order.created_at >= start)
            if to_date:
                # include the entire to_date by setting time to end of day
                end = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(models.Order.created_at < end)
        except Exception:
            raise HTTPException(status_code=400, detail='Invalid date format. Use YYYY-MM-DD')

    orders = query.order_by(models.Order.created_at.desc()).all()
    
    orders_list = []
    for order in orders:
        # Get customer name
        customer = db.query(models.Customer).filter(
            models.Customer.id == order.customer_id
        ).first()
        
        customer_name = (
            order.delivery_name
            or (f"{customer.first_name} {customer.last_name}".strip()
                if customer else "Unknown")
        )
        customer_phone = customer.phone if customer else "Unknown"
        
        orders_list.append({
            "order_id": order.id,
            "order_number": order.order_number,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "total_amount": order.total_amount,
            "status": order.status,
            "payment_status": order.payment_status,
            "created_at": str(order.created_at),
            "item_count": len(order.items) if order.items else 0
        })
    
    return {
        "total_orders": len(orders_list),
        "orders": orders_list
    }


@app.get("/admin/orders/{order_id}")
def admin_get_order_details(order_id: int, db: Session = Depends(get_db), token: str = Depends(verify_admin_token)):
    """
    Get complete order details with all items (admin only)
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get customer
    customer = db.query(models.Customer).filter(
        models.Customer.id == order.customer_id
    ).first()
    
    # Get order items
    items = db.query(models.OrderItem).filter(
        models.OrderItem.order_id == order_id
    ).all()
    
    items_list = []
    for item in items:
        items_list.append({
            "product_name": item.product_name,
            "quantity": item.quantity,
            "price": item.price_at_time,
            "subtotal": item.subtotal
        })
    
    name = (
        order.delivery_name
        or (f"{customer.first_name} {customer.last_name}".strip()
            if customer else "Unknown")
    )

    return {
        "order_number": order.order_number,
        "created_at": str(order.created_at),
        "customer": {
            "first_name": order.delivery_first_name or "",
            "last_name": order.delivery_last_name or "",
            "name": order.delivery_name or "Unknown",
            "email": order.delivery_email or (customer.email if customer else "Unknown"),
            "phone": order.delivery_phone or (customer.phone if customer else "Unknown"),
        },
        "delivery": {
            "address": order.delivery_address,
            "phone": order.delivery_phone,
            "city": order.delivery_city,
            "state": order.delivery_state,
            "note": order.delivery_note,
        },
        "items": items_list,
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "total_amount": order.total_amount,
        "status": order.status,
        "payment_status": order.payment_status
    }


@app.put("/admin/orders/{order_id}/status")
def admin_update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token),
):
    """
    Update order status (admin only)
    status options: pending, paid, processing, shipped, delivered, cancelled
    payment_status options: unpaid, paid, failed, refunded
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update status
    order.status = update.status

    # Update payment status if provided
    if update.payment_status:
        order.payment_status = update.payment_status

    db.commit()

    return {
        "message": f"Order {order.order_number} updated successfully",
        "order_id": order.id,
        "new_status": order.status,
        "new_payment_status": order.payment_status,
    }


@app.post("/admin/orders/{order_id}/refund")
async def refund_order(order_id: int, db: Session = Depends(get_db), token: str = Depends(verify_admin_token)):
    """
    Refund a paid order with Paystack and restore stock.
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.payment_status != "paid":
        raise HTTPException(status_code=400, detail="Order is not paid and cannot be refunded")

    if not order.payment_reference:
        raise HTTPException(status_code=400, detail="No payment reference found for this order")

    paystack_secret_key = os.getenv("PAYSTACK_SECRET_KEY")
    if not paystack_secret_key:
        raise HTTPException(status_code=500, detail="PAYSTACK_SECRET_KEY is not configured")

    payload = {
        "transaction": order.payment_reference,
        "amount": round(order.total_amount * 100),
    }

    headers = {
        "Authorization": f"Bearer {paystack_secret_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.paystack.co/refund",
                json=payload,
                headers=headers,
            )
            response_data = response.json() if response.content else {}
            print(f"[REFUND] Paystack response status: {response.status_code}, body: {response_data}")
    except Exception as exc:
        print(f"[REFUND] Exception calling Paystack refund API: {exc}")
        raise HTTPException(status_code=502, detail="Refund failed on Paystack's end — check server logs")

    if response.status_code != 200 or not response_data.get("status", False):
        print(f"[REFUND] Paystack refund failed. Status: {response.status_code}, body: {response_data}")
        raise HTTPException(status_code=502, detail="Refund failed on Paystack's end — check server logs")

    try:
        order.payment_status = "refunded"
        order.status = "cancelled"

        items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
        for it in items:
            prod = db.query(models.Product).filter(models.Product.id == it.product_id).first()
            if prod:
                qty_before = prod.stock_quantity
                prod.stock_quantity += (it.quantity or 0)
                db.add(prod)

                log = models.StockLog(
                    product_id=prod.id,
                    order_id=order.id,
                    change_type="refund",
                    quantity_change=it.quantity or 0,
                    quantity_before=qty_before,
                    quantity_after=prod.stock_quantity,
                    note=f"Refund: order {order.order_number}"
                )
                db.add(log)
            else:
                print(f"[REFUND] Product {it.product_id} not found while restoring stock.")

        db.commit()

    except Exception as exc:
        print(f"[REFUND] Refund succeeded on Paystack but DB update failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Refund went through on Paystack but DB update failed; manual follow-up may be required",
        )

    return {
        "message": "Refund successful",
        "order_number": order.order_number,
        "refunded_amount": order.total_amount,
        "stock_restored": True,
    }


@app.get("/admin/customers")
def admin_get_all_customers(db: Session = Depends(get_db), token: str = Depends(verify_admin_token)):
    """
    Get all customers with their order history (admin only)
    """
    customers = db.query(models.Customer).order_by(
        models.Customer.created_at.desc()
    ).all()
    
    customers_list = []
    for customer in customers:
        # Get customer's orders
        orders = db.query(models.Order).filter(
            models.Order.customer_id == customer.id
        ).all()
        
        total_spent = sum(order.total_amount for order in orders)
        order_count = len(orders)
        
        customers_list.append({
            "id": customer.id,
            "name": f"{customer.first_name} {customer.last_name}",
            "email": customer.email,
            "phone": customer.phone,
            "address": f"{customer.address}, {customer.city}, {customer.state}",
            "joined": str(customer.created_at),
            "has_account": customer.has_account,
            "total_orders": order_count,
            "total_spent": total_spent
        })
    
    return {
        "total_customers": len(customers_list),
        "customers": customers_list
    }


@app.get("/api/paystack-public-key")
def get_public_key():
    """
    Return the Paystack public key for frontend
    """
    from dotenv import load_dotenv
    import os

    load_dotenv()
    PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")

    if not PAYSTACK_PUBLIC_KEY:
        raise HTTPException(status_code=500, detail="Paystack public key not configured")

    return {"public_key": PAYSTACK_PUBLIC_KEY}


def send_order_confirmation_email(customer_email: str, order_data: dict):
    """Send a real order confirmation email via Gmail SMTP."""
    sender_email = os.getenv("GMAIL_SENDER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        print("[EMAIL] Gmail credentials not configured — skipping email")
        return

    try:
        subject = (
            f"Order Confirmation #{order_data.get('order_number', '')} "
            "- Halari House of Seasoning"
        )

        plain_text = f"""
Dear {order_data.get('customer_name', 'Customer')},

Thank you for your order! Your payment was successful.

ORDER SUMMARY:
"""

        for item in order_data.get('items', []):
            name = item.get('product_name', 'Item')
            qty = item.get('quantity', 1)
            price = item.get('price', item.get('subtotal', 0))
            try:
                price_str = f"₦{int(price):,}"
            except Exception:
                price_str = f"₦{price}"
            plain_text += f"{qty}x {name} - {price_str}\n"

        try:
            subtotal_str = f"₦{int(order_data.get('subtotal', 0)):,}"
            delivery_str = f"₦{int(order_data.get('delivery_fee', 3000)):,}"
            total_str = f"₦{int(order_data.get('total_amount', 0)):,}"
        except Exception:
            subtotal_str = str(order_data.get('subtotal', 0))
            delivery_str = str(order_data.get('delivery_fee', 3000))
            total_str = str(order_data.get('total_amount', 0))

        delivery_address = order_data.get('delivery_address', '')
        delivery_city = order_data.get('delivery_city', '')
        delivery_state = order_data.get('delivery_state', '')

        plain_text += f"""
Subtotal: {subtotal_str}
Delivery Fee: {delivery_str}
TOTAL PAID: {total_str}

DELIVERY ADDRESS:
{delivery_address}
{delivery_city}, {delivery_state}

We will begin processing your order shortly.
Thank you for shopping with Halari House of Seasoning!
"""

        items_html = ""
        for item in order_data.get('items', []):
            name = item.get('product_name', 'Item')
            qty = item.get('quantity', 1)
            price = item.get('price', item.get('subtotal', 0))
            try:
                price_str = f"₦{int(price):,}"
            except Exception:
                price_str = f"₦{price}"
            row_bg = "#ffffff" if order_data.get('items', []).index(item) % 2 == 0 else "#F5E6D3"
            items_html += f"""
                <tr style="background-color:{row_bg};">
                  <td style="padding:10px 14px; color:#333;
                             font-size:14px;">{name}</td>
                  <td style="padding:10px 14px; color:#333;
                             font-size:14px; text-align:center;">{qty}</td>
                  <td style="padding:10px 14px; color:#333;
                             font-size:14px; text-align:right;">{price_str}</td>
                </tr>
            """

        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order Confirmation</title>
</head>
<body style="margin:0; padding:0; background-color:#F5E6D3;
             font-family: Arial, sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0"
         style="background-color:#F5E6D3; padding: 30px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background-color:#ffffff; border-radius:12px;
                      overflow:hidden;
                      box-shadow: 0 4px 12px rgba(0,0,0,0.1);">

          <!-- HEADER -->
          <tr>
            <td style="background-color:#4A2C1A;
                       padding: 40px 30px; text-align: center;">
              <h1 style="color:#F5E6D3; margin:0; font-size:28px;
                         letter-spacing:2px;">🌶️ HALARI</h1>
              <p style="color:#F5E6D3; margin:8px 0 0 0; font-size:14px;
                        letter-spacing:1px; opacity:0.85;">
                HOUSE OF SEASONING
              </p>
            </td>
          </tr>

          <!-- SUCCESS BANNER -->
          <tr>
            <td style="background-color:#5a3a22; padding: 16px 30px;
                       text-align:center;">
              <p style="color:#F5E6D3; margin:0; font-size:15px;">
                ✅ Payment Successful — Your order is confirmed!
              </p>
            </td>
          </tr>

          <!-- BODY -->
          <tr>
            <td style="padding: 30px;">

              <p style="color:#4A2C1A; font-size:16px; margin:0 0 20px 0;">
                Dear <strong>{order_data.get('customer_name', 'Customer')}</strong>,
              </p>

              <p style="color:#555; font-size:14px; line-height:1.6;">
                Thank you for shopping with us! We have received your order
                and will begin processing it shortly. Here is your
                order summary:
              </p>

              <!-- ORDER NUMBER BOX -->
              <div style="background:#F5E6D3; border-left: 4px solid #4A2C1A;
                          padding: 14px 18px; border-radius: 6px;
                          margin: 20px 0;">
                <p style="margin:0; color:#4A2C1A; font-size:13px;
                          letter-spacing:1px;">ORDER NUMBER</p>
                <p style="margin:4px 0 0 0; color:#4A2C1A; font-size:20px;
                          font-weight:bold;">
                  #{order_data.get('order_number', '')}
                </p>
              </div>

              <!-- ITEMS TABLE -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="margin: 20px 0; border-collapse: collapse;
                            border-radius: 8px; overflow:hidden;">
                <tr style="background-color:#4A2C1A;">
                  <th style="padding:10px 14px; color:#F5E6D3;
                             text-align:left; font-size:13px;">Item</th>
                  <th style="padding:10px 14px; color:#F5E6D3;
                             text-align:center; font-size:13px;">Qty</th>
                  <th style="padding:10px 14px; color:#F5E6D3;
                             text-align:right; font-size:13px;">Price</th>
                </tr>
                {items_html}
              </table>

              <!-- TOTALS -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="margin: 10px 0; border-collapse: collapse;">
                <tr>
                  <td style="padding:8px 0; color:#555; font-size:14px;">
                    Subtotal
                  </td>
                  <td style="padding:8px 0; color:#555; font-size:14px;
                             text-align:right;">{subtotal_str}</td>
                </tr>
                <tr>
                  <td style="padding:8px 0; color:#555; font-size:14px;">
                    Delivery Fee
                  </td>
                  <td style="padding:8px 0; color:#555; font-size:14px;
                             text-align:right;">{delivery_str}</td>
                </tr>
                <tr style="border-top: 2px solid #4A2C1A;">
                  <td style="padding:12px 0; color:#4A2C1A; font-size:16px;
                             font-weight:bold;">
                    Total Paid
                  </td>
                  <td style="padding:12px 0; color:#4A2C1A; font-size:16px;
                             font-weight:bold; text-align:right;">{total_str}</td>
                </tr>
              </table>

              <!-- DELIVERY ADDRESS -->
              <div style="background:#F5E6D3; border-radius:8px;
                          padding:16px 18px; margin: 20px 0;
                          border: 1px solid #4A2C1A;">
                <p style="margin:0 0 8px 0; color:#4A2C1A; font-size:13px;
                          font-weight:bold; letter-spacing:1px;">
                  📦 DELIVERY ADDRESS
                </p>
                <p style="margin:0; color:#4A2C1A; font-size:14px;
                          line-height:1.6;">
                  {delivery_address}<br>
                  {delivery_city}, {delivery_state}
                </p>
              </div>

              <p style="color:#555; font-size:14px; line-height:1.6;
                        margin: 20px 0 0 0;">
                If you have any questions about your order, please
                don't hesitate to reach out to us. We are happy to help!
              </p>

            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="background-color:#F5E6D3; padding: 24px 30px;
                       text-align:center;
                       border-top: 2px solid #4A2C1A;">
              <p style="color:#4A2C1A; font-size:14px; margin:0 0 8px 0;
                        font-weight:bold;">
                🌶️ Halari House of Seasoning
              </p>
              <p style="color:#4A2C1A; font-size:12px; margin:0;
                        opacity:0.7;">
                Thank you for your order. We appreciate your business!
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
        """

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = customer_email
        message.attach(MIMEText(plain_text, "plain", "utf-8"))
        message.attach(MIMEText(html_body, "html", "utf-8"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, customer_email, message.as_string())

        print(f"[EMAIL] Order confirmation sent successfully")

    except Exception as exc:
        print(f"[EMAIL] Failed to send order confirmation: {exc}")


def fulfill_order(db: Session, order, paystack_amount_kobo: int, paystack_response: dict = None):
    """Fulfill an order after Paystack verification."""
    if order.payment_status == "paid":
        print(f"[INFO] Order {order.order_number} is already paid. Skipping processing.")
        return paystack_response or {"status": "already_paid"}

    order_amount_naira = order.total_amount
    order_amount_kobo = round(order_amount_naira * 100)

    if paystack_amount_kobo != order_amount_kobo:
        print(f"[ERROR] Amount mismatch! Paystack: {paystack_amount_kobo} kobo (₦{paystack_amount_kobo/100}), Order: {order_amount_kobo} kobo (₦{order_amount_naira})")
        order.payment_status = "failed"
        db.add(order)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Amount mismatch. Paid: ₦{paystack_amount_kobo/100}, Expected: ₦{order_amount_naira}")

    try:
        # Update order status
        order.status = "processing"
        order.payment_status = "paid"
        db.add(order)

        # Send order confirmation email
        customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
        if customer:
            items = db.query(models.OrderItem).filter(
                models.OrderItem.order_id == order.id
            ).all()

            items_list = []
            for it in items:
                items_list.append({
                    "product_name": it.product_name,
                    "quantity": it.quantity,
                    "price": it.price_at_time,
                    "subtotal": it.subtotal
                })

            order_data = {
                "order_number": order.order_number,
                "customer_name": (
                    order.delivery_name
                    or f"{order.delivery_first_name or ''} {order.delivery_last_name or ''}".strip()
                    or (f"{customer.first_name} {customer.last_name}".strip() if customer else "Customer")
                ),
                "items": items_list,
                "subtotal": order.subtotal,
                "delivery_fee": order.delivery_fee,
                "total_amount": order.total_amount,
                "delivery_address": order.delivery_address,
                "delivery_city": order.delivery_city,
                "delivery_state": order.delivery_state
            }

            send_order_confirmation_email(customer.email, order_data)
        else:
            print("[EMAIL] No customer found; confirmation email skipped")

        # Decrement stock
        items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
        for it in items:
            prod = db.query(models.Product).filter(models.Product.id == it.product_id).first()
            if prod:
                if prod.stock_quantity < (it.quantity or 0):
                    raise Exception(
                        f"Insufficient stock for {prod.name}: "
                        f"need {it.quantity}, have {prod.stock_quantity}"
                    )

                old_qty = prod.stock_quantity
                new_qty = max(0, old_qty - (it.quantity or 0))
                print(f"[STOCK] Reducing Product {prod.id} from {old_qty} -> {new_qty}")
                prod.stock_quantity = new_qty
                db.add(prod)

                log = models.StockLog(
                    product_id=prod.id,
                    order_id=order.id,
                    change_type="sale",
                    quantity_change=-(it.quantity or 0),
                    quantity_before=old_qty,
                    quantity_after=new_qty,
                    note=f"Sale: order {order.order_number}"
                )
                db.add(log)
            else:
                init_qty = max(0, 100 - (it.quantity or 0))
                new_prod = models.Product(id=it.product_id, name=it.product_name, price=it.price_at_time, stock_quantity=init_qty, low_stock_threshold=10)
                db.add(new_prod)
                print(f"[STOCK] Created Product {it.product_id} with stock {init_qty}")

        # ONE single commit — everything or nothing
        db.commit()

    except Exception as e:
        db.rollback()
        print(f'[ERROR] fulfill_order failed, rolling back: {e}')
        raise HTTPException(status_code=500, detail="Order fulfillment failed — please contact support")

    return paystack_response or {"status": "success"}


@app.get("/api/verify-payment/{reference}")
@limiter.limit("10/minute")
async def verify_payment(request: Request, reference: str, db: Session = Depends(get_db)):
    """
    Verify payment with Paystack
    """
    print("=" * 50)
    print("🔔 VERIFY PAYMENT FUNCTION WAS CALLED!")
    print("=" * 50)
    print(f"[DEBUG] ===== verify_payment CALLED =====")
    print(f"[DEBUG] reference: {reference}")
    import os
    from dotenv import load_dotenv
    import httpx

    load_dotenv()
    PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

    if not PAYSTACK_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Paystack secret key not configured")

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Payment verification failed")

        data = response.json()

        status = data.get('data', {}).get('status')
        if not status or status.lower() != 'success':
            return data

        order = db.query(models.Order).filter(models.Order.payment_reference == reference).first()

        if not order:
            print(f"[ERROR] Order not found for payment reference: {reference}")
            raise HTTPException(status_code=404, detail="Order not found for this payment reference")

        paystack_amount_kobo = data.get('data', {}).get('amount', 0)
        fulfill_order(db, order, paystack_amount_kobo, data)
        return data


@app.post("/webhook/paystack")
@limiter.limit("30/minute")
async def paystack_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Handle Paystack webhook events."""
    raw_body = await request.body()
    signature = request.headers.get("x-paystack-signature")

    load_dotenv()
    PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
    if not PAYSTACK_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Paystack secret key not configured")

    if not signature:
        raise HTTPException(status_code=401, detail="Unauthorized")

    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode("utf-8"),
        raw_body,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, signature):
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = json.loads(raw_body)
    if payload.get("event") != "charge.success":
        return {"received": True}

    data = payload.get("data", {})
    reference = data.get("reference")
    amount_kobo = data.get("amount")

    if not reference:
        print("[WEBHOOK ALERT] charge.success webhook missing reference")
        return {"received": True}

    order = db.query(models.Order).filter(models.Order.payment_reference == reference).first()
    if not order:
        print(f"[WEBHOOK ALERT] No matching order for paid reference: {reference}")
        return {"received": True}

    try:
        fulfill_order(db, order, amount_kobo, payload)
    except HTTPException as exc:
        print(f"[WEBHOOK ALERT] fulfill_order rejected reference {reference}: {exc.detail}")
    return {"received": True}


@app.post("/test/send-email/{order_id}")
def test_send_email(order_id: int, db: Session = Depends(get_db)):
    """Test endpoint to trigger the simulated email for a given order id."""
    print(f"[TEST ENDPOINT] send-email called for order_id: {order_id}")
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()

    items_list = []
    for it in items:
        items_list.append({
            'product_name': it.product_name,
            'quantity': it.quantity,
            'price': it.price_at_time,
            'subtotal': it.subtotal
        })

    order_data = {
        'order_number': order.order_number,
        'customer_name': f"{customer.first_name} {customer.last_name}" if customer else 'Customer',
        'items': items_list,
        'subtotal': order.subtotal,
        'delivery_fee': order.delivery_fee,
        'total_amount': order.total_amount,
        'delivery_address': order.delivery_address
    }

    print(f"[TEST ENDPOINT] About to call send_order_confirmation_email for order: {order.order_number}")
    send_order_confirmation_email(customer.email if customer else 'unknown@example.com', order_data)
    print('SENDING ADMIN NOTIFICATION TO: admin@halarihouse.com')

    return {"message": "Test email sent (check server logs)", "order_id": order.id}