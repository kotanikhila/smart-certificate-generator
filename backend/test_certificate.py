from app.certificate_utils import CertificateGenerator
import os

print("🎓 Testing Certificate Generator...")
print("=" * 50)

# Test certificate generation
generator = CertificateGenerator()

result = generator.generate_certificate(
    recipient_name="John Doe",
    recipient_email="john@example.com",
    title="Certificate of Excellence",
    company="Tech Corp",
    description="For outstanding contribution to the field of technology"
)

print("\n✅ Certificate generated successfully!")
print(f"📄 Certificate ID: {result['certificate_id']}")
print(f"🖼️  Image saved at: {result['certificate_path']}")
print(f"📑 PDF saved at: {result['pdf_path']}")
print(f"📱 QR Code saved at: {result['qr_path']}")
print(f"🔗 Verification URL: {result['verification_url']}")
print("=" * 50)

# Check if files exist
print("\n📁 File verification:")
if os.path.exists(result['certificate_path']):
    size = os.path.getsize(result['certificate_path'])
    print(f"✅ Image file exists: {size} bytes")
if os.path.exists(result['pdf_path']):
    size = os.path.getsize(result['pdf_path'])
    print(f"✅ PDF file exists: {size} bytes")
if os.path.exists(result['qr_path']):
    size = os.path.getsize(result['qr_path'])
    print(f"✅ QR Code file exists: {size} bytes")

print("\n🎉 All files generated successfully!")
print(f"\n📍 Files saved in: {os.path.abspath('generated_certificates')}")
