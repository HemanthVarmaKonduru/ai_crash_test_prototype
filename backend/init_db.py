#!/usr/bin/env python3
"""
Initialize the database with tables
"""
from database import create_tables, engine
from models import Base

def init_database():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
