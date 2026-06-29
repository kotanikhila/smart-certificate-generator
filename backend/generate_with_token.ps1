# Smart Certificate Generator - Generate with Token
Write-Host "🚀 Generating Certificate" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

# Your token from login
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJibGFuZCI6InNvbGxlZCI6ImV4YW1wbGUyZ29tIiwidXNlIjoiZ2V0Z2V0IiwidXNlIjoiZ2V0Z2V0IjoiZ2V0Z2V0IjoiZ2V0Z3N0IjoiZ2V0Z3N0IjoiZ2V0IjoiZ2V0Z3N0IjoiZ3N0IjoiZ2V0Z3N0IjoiZ3N0"

Write-Host "Token: $($token.Substring(0,40))..." -ForegroundColor Gray

# Headers with authorization
$headers = @{
    "Authorization" = "Bearer $token"
    "accept" = "application/json"
}

# Certificate details
$recipients = @(
    @{name = "lavanya"; email = "lava@gmail.com"; company = "Super Tech"; title = "Certificate of Achievement"; desc = "First certificate of achievement"},
    @{name = "John Doe"; email = "john@example.com"; company = "Tech Corp"; title = "Excellence Award"; desc = "For outstanding performance"},
    @{name = "Jane Smith"; email = "jane@example.com"; company = "AI Labs"; title = "Innovation Award"; desc = "For innovative solutions"}
)

foreach ($r in $recipients) {
    Write-Host "`n📄 Generating for $($r.name)..." -ForegroundColor Yellow
    
    $url = "http://localhost:8000/api/certificates/generate?recipient_name=$([System.Web.HttpUtility]::UrlEncode($r.name))&recipient_email=$([System.Web.HttpUtility]::UrlEncode($r.email))&certificate_title=$([System.Web.HttpUtility]::UrlEncode($r.title))&certificate_description=$([System.Web.HttpUtility]::UrlEncode($r.desc))&recipient_company=$([System.Web.HttpUtility]::UrlEncode($r.company))"
    
    try {
        $cert = Invoke-RestMethod -Method Post -Uri $url -Headers $headers
        Write-Host "   ✅ Generated: $($cert.certificate.certificate_id)" -ForegroundColor Green
        Write-Host "   🔗 Verify: $($cert.certificate.verification_url)" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# List all certificates
Write-Host "`n📋 All Certificates:" -ForegroundColor Cyan
try {
    $certs = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/certificates/" -Headers $headers
    foreach ($c in $certs) {
        Write-Host "   - $($c.certificate_id) | $($c.recipient_name) | $($c.status)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Error fetching certificates" -ForegroundColor Red
}

Write-Host "`n" + "=" * 60 -ForegroundColor Yellow
Write-Host "✅ Complete!" -ForegroundColor Green
Write-Host "📁 Check generated_certificates/ folder" -ForegroundColor Cyan
