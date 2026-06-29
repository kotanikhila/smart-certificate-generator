import requests
import json

# Register a test user
response = requests.post(
    "http://localhost:8000/api/auth/register",
    params={
        "email": "test@example.com",
        "password": "test123456",
        "full_name": "Test User",
        "user_type": "foundation"
    }
)

print("Registration Response:", response.json())

# Login to get token
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={
        "username": "test@example.com",
        "password": "test123456"
    }
)

print("Login Response:", response.json())
