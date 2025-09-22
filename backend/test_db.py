#!/usr/bin/env python3
"""
Test database connection and operations
"""
from database import SessionLocal, engine
from models import Prompt, Base
from sqlalchemy import text

def test_database():
    """Test database operations"""
    print("Testing database connection...")
    
    # Test connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return
    
    # Test session
    try:
        db = SessionLocal()
        print("✓ Database session created")
        
        # Test query
        prompts = db.query(Prompt).all()
        print(f"✓ Query successful, found {len(prompts)} prompts")
        
        db.close()
    except Exception as e:
        print(f"✗ Database session failed: {e}")
        return
    
    print("✓ All database tests passed!")

if __name__ == "__main__":
    test_database()
