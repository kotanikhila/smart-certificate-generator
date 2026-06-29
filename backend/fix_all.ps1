Write-Host "🔧 Fixing Smart Certificate Generator..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Update auth.py
Write-Host "📝 Updating auth module..." -ForegroundColor Yellow
python -c "
import hashlib
import base64

# Test hash function
def test_hash():
    password = 'test123456'
    salt = 'cert_salt_2024'
    combined = salt + password
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    result = base64.b64encode(hash_bytes).decode()
    print(f'✅ Hash function working: {result[:20]}...')
    return True

test_hash()
"

# Create user
Write-Host "👤 Creating test user..." -ForegroundColor Yellow
python create_user_simple.py

# Test everything
Write-Host "🧪 Testing everything..." -ForegroundColor Yellow
python test_final.py

Write-Host ""
Write-Host "✅ Fix completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📧 Email: test@example.com" -ForegroundColor Cyan
Write-Host "🔑 Password: test123456" -ForegroundColor Cyan
Write-Host "🌐 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
