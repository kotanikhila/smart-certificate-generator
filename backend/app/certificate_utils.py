from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
from datetime import datetime
import uuid

class CertificateGenerator:
    def __init__(self):
        self.output_dir = "generated_certificates"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Try to load fonts
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
    
    def generate_certificate(self, recipient_name, recipient_email, title="Certificate of Achievement", 
                           company="", description="In recognition of outstanding achievement and dedication"):
        # Generate certificate ID
        cert_id = f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create certificate image
        img = Image.new('RGB', (1400, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        # === BORDERS ===
        draw.rectangle([(40, 40), (1360, 960)], outline='#1a56db', width=10)
        draw.rectangle([(60, 60), (1340, 940)], outline='#1a56db', width=3)
        draw.rectangle([(80, 80), (1320, 920)], outline='#e5e7eb', width=2)
        
        # === HEADER & FOOTER BARS ===
        draw.rectangle([(90, 90), (1310, 130)], fill='#1a56db')
        draw.rectangle([(90, 870), (1310, 910)], fill='#1a56db')
        
        # === CORNER DECORATIONS ===
        corner_size = 40
        draw.rectangle([(90, 90), (90 + corner_size, 130)], fill='#1a56db')
        draw.rectangle([(90, 90), (130, 90 + corner_size)], fill='#1a56db')
        draw.rectangle([(1310 - corner_size, 90), (1310, 130)], fill='#1a56db')
        draw.rectangle([(1310 - 40, 90), (1310, 90 + corner_size)], fill='#1a56db')
        draw.rectangle([(90, 870), (90 + corner_size, 910)], fill='#1a56db')
        draw.rectangle([(90, 910 - corner_size), (130, 910)], fill='#1a56db')
        draw.rectangle([(1310 - corner_size, 870), (1310, 910)], fill='#1a56db')
        draw.rectangle([(1310 - 40, 910 - corner_size), (1310, 910)], fill='#1a56db')
        
        # === "THIS IS TO CERTIFY THAT" ===
        draw.text((700, 140), "This is to certify that", fill='#4b5563', font=self.font_sub, anchor='mt')
        
        # === TITLE BACKGROUND ===
        draw.rectangle([(350, 170), (1050, 250)], fill='#eff6ff')
        draw.rectangle([(360, 180), (1040, 240)], outline='#93c5fd', width=1)
        
        # === TITLE ===
        draw.text((700, 210), title, fill='#1a56db', font=self.font_title, anchor='mt')
        
        # === RECIPIENT NAME - CENTERED ===
        name_bbox = draw.textbbox((0, 0), recipient_name, font=self.font_name)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (1400 - name_width) // 2
        draw.text((name_x, 360), recipient_name, fill='#1a3a8a', font=self.font_name)
        
        # === DECORATIVE UNDERLINE ===
        draw.line([(400, 450), (1000, 450)], fill='#1a56db', width=4)
        draw.line([(450, 460), (950, 460)], fill='#93c5fd', width=2)
        
        # === COMPANY NAME ===
        if company:
            draw.text((700, 490), company, fill='#4b5563', font=self.font_sub, anchor='mt')
            desc_y = 530
        else:
            desc_y = 490
        
        # === DESCRIPTION ===
        draw.text((700, desc_y), description, fill='#4b5563', font=self.font_desc, anchor='mt')
        
        # === ISSUE DATE ===
        issue_date = datetime.now().strftime('%B %d, %Y')
        draw.text((700, desc_y + 60), f"Issued on: {issue_date}", fill='#4b5563', font=self.font_date, anchor='mt')
        
        # === CERTIFICATE ID ===
        draw.text((700, desc_y + 100), f"Certificate ID: {cert_id}", fill='#6b7280', font=self.font_small, anchor='mt')
        
        # === QR CODE GENERATION ===
        verification_data = f"http://localhost:3000/verify/{cert_id}"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=4,
        )
        qr.add_data(verification_data)
        qr.make(fit=True)
        
        # Create QR code image with color
        qr_img = qr.make_image(fill_color="#1a3a8a", back_color="white")
        
        # Save QR code
        qr_path = os.path.join(self.output_dir, f"{cert_id}_qr.png")
        qr_img.save(qr_path, 'PNG', quality=95)
        
        # === ADD QR CODE TO CERTIFICATE ===
        # Resize QR code
        qr_resized = qr_img.resize((180, 180), Image.Resampling.LANCZOS)
        
        # Paste QR code - Bottom right area
        # Position: x=1160, y=700 (bottom right corner)
        img.paste(qr_resized, (1160, 700))
        
        # Add border around QR code
        draw.rectangle([(1155, 695), (1345, 885)], outline='#1a56db', width=2)
        
        # === SCAN TO VERIFY ===
        draw.text((1250, 900), "Scan to verify", fill='#6b7280', font=self.font_small, anchor='mt')
        
        # === FOOTER ===
        draw.text((700, 950), "Smart Certificate Generator", fill='#9ca3af', font=self.font_small, anchor='mt')
        
        # === SAVE CERTIFICATE ===
        cert_path = os.path.join(self.output_dir, f"{cert_id}.png")
        img.save(cert_path, 'PNG', quality=95)
        
        # Generate PDF version
        pdf_path = self._generate_pdf(cert_path, cert_id, recipient_name, title, issue_date, verification_data)
        
        return {
            "certificate_id": cert_id,
            "certificate_path": cert_path,
            "pdf_path": pdf_path,
            "qr_path": qr_path,
            "verification_url": verification_data,
            "recipient": recipient_name,
            "email": recipient_email,
            "issued_date": issue_date,
            "title": title
        }
    
    def _generate_pdf(self, image_path, cert_id, recipient_name, title, issue_date, verification_url):
        """Generate PDF version of certificate"""
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        
        pdf_path = os.path.join(self.output_dir, f"{cert_id}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Add the certificate image
        c.drawImage(image_path, 0, 0, width=width, height=height, preserveAspectRatio=True)
        
        # Add QR code
        qr_path = os.path.join(self.output_dir, f"{cert_id}_qr.png")
        if os.path.exists(qr_path):
            c.drawImage(qr_path, width-180, 120, width=140, height=140)
        
        # Add footer with verification info
        c.setFillColor(colors.HexColor('#6b7280'))
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Certificate ID: {cert_id}")
        c.drawString(50, 20, f"Verify at: {verification_url}")
        c.drawString(width-200, 20, "Smart Certificate Generator")
        
        c.save()
        return pdf_path
