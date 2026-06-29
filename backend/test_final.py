import requests

print("🔑 Testing login...")
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
    print(f"Token: {data['access_token'][:50]}...")
    print(f"User Type: {data['user_type']}")
    print(f"Is Verified: {data['is_verified']}")
    
    # Test certificate generation
    print("\n📄 Generating certificate...")
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    params = {
        "recipient_name": "John Doe",
        "recipient_email": "john@example.com",
        "certificate_title": "Excellence Award"
    }
    
    cert_response = requests.post(
        "http://localhost:8000/api/certificates/generate",
        params=params,
        headers=headers
    )
    
    if cert_response.status_code == 200:
        print("✅ Certificate generated successfully!")
        print(cert_response.json())
    else:
        print("❌ Certificate generation failed:", cert_response.text)
else:
    print("❌ Login failed:", response.text)
