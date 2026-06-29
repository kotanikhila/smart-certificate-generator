import sys
import traceback

try:
    print("🔍 Checking database setup...")
    from app.database import engine, Base
    from app import models
    
    print("✅ Database imports successful!")
    
    # Try to create tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    # Try to create a test user directly
    from sqlalchemy.orm import Session
    from app.auth import get_password_hash
    
    db = Session(engine)
    print("✅ Database session created!")
    
    # Check if user exists
    existing = db.query(models.User).filter(models.User.email == "test@example.com").first()
    if existing:
        print("⚠️ User already exists!")
        print(f"   Email: {existing.email}")
        print(f"   Name: {existing.full_name}")
        print(f"   Type: {existing.user_type}")
    else:
        print("Creating test user directly...")
        test_user = models.User(
            email="test@example.com",
            password_hash=get_password_hash("test123456"),
            full_name="Test User",
            user_type="foundation",
            is_verified=True
        )
        db.add(test_user)
        db.commit()
        print("✅ Test user created successfully!")
    
    db.close()
    print("\n✅ All checks passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
