import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Create database file
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./halari_spices.db")
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Connect to database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()