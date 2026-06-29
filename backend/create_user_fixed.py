import requests
import time

# Wait for server to start
print("Waiting for server...")
time.sleep(2)

try:
    # Test if server is running
    response = requests.get("http://localhost:8000/health")
    print("✅ Server is running!")
except:
    print("❌ Server is not running. Please start the server first.")
    exit()

# Register a test user
print("\n📝 Registering user...")
response = requests.post(
    "http://localhost:8000/api/auth/register",
    params={
        "email": "test@example.com",
        "password": "test123456",
        "full_name": "Test User",
        "user_type": "foundation"
    }
)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✅ Registration successful!")
    print(response.json())
else:
    try:
        print("❌ Registration failed:", response.json())
    except:
        print("❌ Registration failed:", response.text)

# Try login
print("\n🔑 Logging in...")
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={
        "username": "test@example.com",
        "password": "test123456"
    }
)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✅ Login successful!")
    data = response.json()
    print(f"Access Token: {data['access_token'][:50]}...")
    print(f"User Type: {data['user_type']}")
    print(f"Is Verified: {data['is_verified']}")
else:
    try:
        print("❌ Login failed:", response.json())
    except:
        print("❌ Login failed:", response.text)

print("\n✅ User creation script completed!")
