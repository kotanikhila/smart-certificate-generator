import requests
import json
import traceback

try:
    print("Testing Registration...")
    response = requests.post(
        "http://localhost:8000/api/auth/register",
        data={
            "email": "test@example.com",
            "password": "test123456",
            "full_name": "Test User",
            "user_type": "foundation"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
