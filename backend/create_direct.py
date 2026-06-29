from app.database import SessionLocal
from app.models import User
from app.routers.auth import get_password_hash

db = SessionLocal()

try:
    # Check if user exists
    existing = db.query(User).filter(User.email == "test@example.com").first()
    if existing:
        print(f"⚠️ User already exists: {existing.email}")
        print(f"   ID: {existing.id}")
        print(f"   Name: {existing.full_name}")
    else:
        # Create user directly
        hashed = get_password_hash("test123456")
        user = User(
            email="test@example.com",
            password_hash=hashed,
            full_name="Test User",
            user_type="foundation",
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("✅ User created successfully!")
        print(f"Email: {user.email}")
        print(f"Name: {user.full_name}")
        print(f"ID: {user.id}")
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
