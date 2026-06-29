import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.username = settings.EMAIL_USERNAME
        self.password = settings.EMAIL_PASSWORD
        self.from_email = settings.EMAIL_FROM
        
    def send_certificate_email(self, recipient_email: str, recipient_name: str, 
                               certificate_id: str, certificate_path: Path, 
                               qr_path: Path, subject: Optional[str] = None,
                               body: Optional[str] = None) -> bool:
        try:
            msg = MIMEMultipart('mixed')
            msg['From'] = self.from_email
            msg['To'] = recipient_email
            msg['Subject'] = subject or f"Your Certificate - {certificate_id}"
            
            email_body = body or self._get_default_email_body(recipient_name, certificate_id)
            msg.attach(MIMEText(email_body, 'html'))
            
            # Attach certificate
            if certificate_path.exists():
                with open(certificate_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={certificate_path.name}')
                    msg.attach(part)
            
            # Attach QR
            if qr_path.exists():
                with open(qr_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={qr_path.name}')
                    msg.attach(part)
            
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, [recipient_email], msg.as_string())
            
            logger.info(f"Email sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_bulk_emails(self, recipients: List[dict], subject: Optional[str] = None) -> dict:
        results = {"total": len(recipients), "success": 0, "failed": 0, "errors": []}
        for recipient in recipients:
            success = self.send_certificate_email(
                recipient_email=recipient['email'],
                recipient_name=recipient['name'],
                certificate_id=recipient['certificate_id'],
                certificate_path=Path(recipient['certificate_path']),
                qr_path=Path(recipient['qr_path']),
                subject=subject
            )
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"email": recipient['email'], "error": "Failed to send"})
        return results
    
    def _get_default_email_body(self, name: str, cert_id: str) -> str:
        return f"""
        <html>
        <head><style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #1a56db; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .footer {{ text-align: center; color: #666; margin-top: 20px; }}
            .button {{ display: inline-block; background: #1a56db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        </style></head>
        <body>
            <div class="container">
                <div class="header"><h1>🎓 Certificate of Achievement</h1></div>
                <div class="content">
                    <p>Dear {name},</p>
                    <p>Congratulations! Your certificate has been issued.</p>
                    <p><strong>Certificate ID:</strong> {cert_id}</p>
                    <p>Please find your certificate attached to this email.</p>
                    <p>Verify your certificate at: <a href="https://smart-certificate-generator.vercel.app/verify/{cert_id}">Verify Certificate</a></p>
                </div>
                <div class="footer"><p>Smart Certificate Generator</p></div>
            </div>
        </body>
        </html>
        """
