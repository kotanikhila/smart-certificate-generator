# Smart Certificate Generator - Generate for Lavanya
Write-Host "🚀 Generating Certificate for Lavanya" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

# Step 1: Login
Write-Host "`n1️⃣ Logging in..." -ForegroundColor Cyan
$login = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/login" -Body @{
    username = "test@example.com"
    password = "test123456"
} -ContentType "application/x-www-form-urlencoded"

$token = $login.access_token
Write-Host "   ✅ Login successful!" -ForegroundColor Green

# Step 2: Generate Certificate
Write-Host "`n2️⃣ Generating certificate for Lavanya..." -ForegroundColor Cyan
$headers = @{
    "Authorization" = "Bearer $token"
    "accept" = "application/json"
}

# Build the URL with query parameters
$recipient_name = "lavanya"
$recipient_email = "lava@gmail.com"
$certificate_title = "Certificate of Achievement"
$certificate_description = "First certificate of achievement"
$recipient_company = "Super Tech"

$url = "http://localhost:8000/api/certificates/generate?recipient_name=$([System.Web.HttpUtility]::UrlEncode($recipient_name))&recipient_email=$([System.Web.HttpUtility]::UrlEncode($recipient_email))&certificate_title=$([System.Web.HttpUtility]::UrlEncode($certificate_title))&certificate_description=$([System.Web.HttpUtility]::UrlEncode($certificate_description))&recipient_company=$([System.Web.HttpUtility]::UrlEncode($recipient_company))"

try {
    $cert = Invoke-RestMethod -Method Post -Uri $url -Headers $headers
    Write-Host "   ✅ Certificate generated successfully!" -ForegroundColor Green
    Write-Host "   📄 ID: $($cert.certificate.certificate_id)" -ForegroundColor Yellow
    Write-Host "   👤 Recipient: $($cert.certificate.recipient)" -ForegroundColor Yellow
    Write-Host "   📧 Email: $($cert.certificate.email)" -ForegroundColor Yellow
    Write-Host "   🔗 Verify: $($cert.certificate.verification_url)" -ForegroundColor Yellow
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $errorBody = $reader.ReadToEnd()
        Write-Host "   Error Details: $errorBody" -ForegroundColor Red
    }
}

# Step 3: Verify the certificate
Write-Host "`n3️⃣ Verifying certificate..." -ForegroundColor Cyan
if ($cert) {
    $certId = $cert.certificate.certificate_id
    try {
        $verify = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/certificates/verify/$certId"
        if ($verify.valid) {
            Write-Host "   ✅ Certificate is valid!" -ForegroundColor Green
            Write-Host "   👤 Recipient: $($verify.recipient_name)" -ForegroundColor Yellow
            Write-Host "   📅 Issued: $($verify.issue_date)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ Verification failed" -ForegroundColor Red
    }
}

# Step 4: Show files
Write-Host "`n4️⃣ Checking generated files..." -ForegroundColor Cyan
$files = Get-ChildItem -Path "generated_certificates" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($files) {
    Write-Host "   ✅ Found $($files.Count) files" -ForegroundColor Green
    $files | Select-Object -First 5 | ForEach-Object {
        Write-Host "   - $($_.Name) ($([math]::Round($_.Length/1024, 2)) KB) - $($_.LastWriteTime)" -ForegroundColor Gray
    }
}

Write-Host "`n" + "=" * 60 -ForegroundColor Yellow
Write-Host "✅ Complete!" -ForegroundColor Green
