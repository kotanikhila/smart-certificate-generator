from app.database import SessionLocal
from app.models import User
import hashlib
import base64

def simple_hash(password: str) -> str:
    salt = "cert_salt_2024"
    combined = salt + password
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    return base64.b64encode(hash_bytes).decode()

db = SessionLocal()

try:
    # Check if user exists
    existing = db.query(User).filter(User.email == "test@example.com").first()
    if existing:
        print("⚠️ User already exists!")
        print(f"Email: {existing.email}")
        print(f"Name: {existing.full_name}")
        print(f"Type: {existing.user_type}")
    else:
        # Create user with simple hash
        user = User(
            email="test@example.com",
            password_hash=simple_hash("test123456"),
            full_name="Test User",
            user_type="foundation",
            is_verified=True
        )
        db.add(user)
        db.commit()
        print("✅ User created successfully!")
        print(f"Email: {user.email}")
        print(f"Name: {user.full_name}")
        print(f"Type: {user.user_type}")
        print(f"Password: test123456")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
