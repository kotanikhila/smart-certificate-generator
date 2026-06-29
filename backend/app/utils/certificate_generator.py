from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
from datetime import datetime
import uuid
import hashlib

class CertificateGenerator:
    def __init__(self, template_data=None):
        self.template = template_data or {}
        self.output_dir = "generated_certificates"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load fonts
        try:
            self.font_title = ImageFont.truetype("arial.ttf", 48)
            self.font_name = ImageFont.truetype("arial.ttf", 72)
            self.font_sub = ImageFont.truetype("arial.ttf", 26)
            self.font_desc = ImageFont.truetype("arial.ttf", 24)
            self.font_date = ImageFont.truetype("arial.ttf", 20)
            self.font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            self.font_title = ImageFont.load_default()
            self.font_name = ImageFont.load_default()
            self.font_sub = ImageFont.load_default()
            self.font_desc = ImageFont.load_default()
            self.font_date = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
    def generate_certificate(self, data):
        """Generate certificate with all features"""
        cert_id = self._generate_certificate_id(data)
        verification_hash = self._generate_verification_hash(data, cert_id)
        
        # Generate image
        image_path = self._create_certificate_image(data, cert_id, verification_hash)
        
        # Generate QR code
        qr_path = self._generate_qr_code(verification_hash, cert_id)
        
        # Generate PDF
        pdf_path = self._generate_pdf(image_path, cert_id, data)
        
        # Upload to cloud if configured
        cloud_urls = self._upload_to_cloud(image_path, pdf_path, cert_id)
        
        return {
            "certificate_id": cert_id,
            "verification_hash": verification_hash,
            "verification_url": f"https://smart-certificate-generator.vercel.app/verify/{verification_hash}",
            "image_path": image_path,
            "pdf_path": pdf_path,
            "qr_path": qr_path,
            **cloud_urls
        }
    
    def _generate_certificate_id(self, data):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = uuid.uuid4().hex[:6].upper()
        name_hash = hashlib.md5(data['recipient_name'].encode()).hexdigest()[:6]
        return f"CERT-{timestamp}-{name_hash.upper()}-{random_suffix}"
    
    def _generate_verification_hash(self, data, cert_id):
        content = f"{cert_id}|{data['recipient_name']}|{data['recipient_email']}|{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _create_certificate_image(self, data, cert_id, verification_hash):
        img = Image.new('RGB', (1400, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        # Get template settings or use defaults
        template = self.template.get('template_json', {})
        bg_color = template.get('background_color', '#FFFFFF')
        border_color = template.get('border_color', '#1a56db')
        title_color = template.get('title_color', '#1a56db')
        name_color = template.get('name_color', '#1a3a8a')
        text_color = template.get('text_color', '#4b5563')
        
        # Draw borders
        draw.rectangle([(40, 40), (1360, 960)], outline=border_color, width=10)
        draw.rectangle([(60, 60), (1340, 940)], outline=border_color, width=3)
        draw.rectangle([(80, 80), (1320, 920)], outline='#e5e7eb', width=2)
        
        # Header and footer bars
        draw.rectangle([(90, 90), (1310, 130)], fill=border_color)
        draw.rectangle([(90, 870), (1310, 910)], fill=border_color)
        
        # Corner decorations
        corner_size = 40
        for x, y in [(90, 90), (1310-40, 90), (90, 870), (1310-40, 870)]:
            draw.rectangle([(x, y), (x + corner_size, y + 40)], fill=border_color)
            draw.rectangle([(x, y), (x + 40, y + corner_size)], fill=border_color)
        
        # Title section
        draw.text((700, 140), "This is to certify that", fill=text_color, font=self.font_sub, anchor='mt')
        draw.rectangle([(350, 170), (1050, 250)], fill='#eff6ff')
        draw.rectangle([(360, 180), (1040, 240)], outline='#93c5fd', width=1)
        draw.text((700, 210), data.get('certificate_title', 'Certificate of Achievement'), 
                  fill=title_color, font=self.font_title, anchor='mt')
        
        # Recipient name - centered
        name_bbox = draw.textbbox((0, 0), data['recipient_name'], font=self.font_name)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (1400 - name_width) // 2
        draw.text((name_x, 360), data['recipient_name'], fill=name_color, font=self.font_name)
        
        # Decorative underline
        draw.line([(400, 450), (1000, 450)], fill=border_color, width=4)
        draw.line([(450, 460), (950, 460)], fill='#93c5fd', width=2)
        
        # Company and description
        y_pos = 500
        if data.get('recipient_company'):
            draw.text((700, y_pos), data['recipient_company'], fill=text_color, font=self.font_sub, anchor='mt')
            y_pos += 40
        
        if data.get('certificate_description'):
            draw.text((700, y_pos), data['certificate_description'], fill=text_color, font=self.font_desc, anchor='mt')
            y_pos += 50
        
        # Date and ID
        issue_date = datetime.now().strftime('%B %d, %Y')
        draw.text((700, y_pos), f"Issued on: {issue_date}", fill=text_color, font=self.font_date, anchor='mt')
        draw.text((700, y_pos + 40), f"Certificate ID: {cert_id}", fill='#6b7280', font=self.font_small, anchor='mt')
        
        # QR Code
        qr_img = self._generate_qr_code_image(verification_hash, cert_id)
        qr_resized = qr_img.resize((180, 180))
        img.paste(qr_resized, (1160, 720))
        draw.rectangle([(1155, 715), (1345, 905)], outline=border_color, width=2)
        draw.text((1250, 910), "Scan to verify", fill='#6b7280', font=self.font_small, anchor='mt')
        
        # Footer
        draw.text((700, 950), "Smart Certificate Generator", fill='#9ca3af', font=self.font_small, anchor='mt')
        
        # Save
        cert_path = os.path.join(self.output_dir, f"{cert_id}.png")
        img.save(cert_path, 'PNG', quality=95)
        return cert_path
    
    def _generate_qr_code_image(self, hash_val, cert_id):
        verification_url = f"https://smart-certificate-generator.vercel.app/verify/{hash_val}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4)
        qr.add_data(verification_url)
        qr.make(fit=True)
        return qr.make_image(fill_color="#1a3a8a", back_color="white")
    
    def _generate_qr_code(self, hash_val, cert_id):
        qr_img = self._generate_qr_code_image(hash_val, cert_id)
        qr_path = os.path.join(self.output_dir, f"{cert_id}_qr.png")
        qr_img.save(qr_path, 'PNG')
        return qr_path
    
    def _generate_pdf(self, image_path, cert_id, data):
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        
        pdf_path = os.path.join(self.output_dir, f"{cert_id}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        c.drawImage(image_path, 0, 0, width=width, height=height, preserveAspectRatio=True)
        
        qr_path = os.path.join(self.output_dir, f"{cert_id}_qr.png")
        if os.path.exists(qr_path):
            c.drawImage(qr_path, width-200, 150, width=140, height=140)
        
        c.setFillColor(colors.HexColor('#6b7280'))
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Certificate ID: {cert_id}")
        c.drawString(50, 20, f"Verify at: https://smart-certificate-generator.vercel.app/verify/{cert_id}")
        c.drawString(width-200, 20, "Smart Certificate Generator")
        
        c.save()
        return pdf_path
    
    def _upload_to_cloud(self, image_path, pdf_path, cert_id):
        # Placeholder for cloud upload
        return {
            "cloudinary_url": "",
            "aws_s3_url": "",
            "firebase_url": ""
        }
