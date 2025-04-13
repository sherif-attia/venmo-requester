from typing import Protocol, List
import yagmail

from app.models.payment import PaymentRequest
from app.models.config import EmailConfig

class EmailService(Protocol):
    """Protocol defining the interface for email services"""
    def send_success_report(self, payments: List[PaymentRequest]) -> None: ...
    def send_error_notification(self, error: Exception, context: str) -> None: ...

class GmailService:
    """Implementation of EmailService using Gmail"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.client = yagmail.SMTP(
            user=config.smtp_user,
            password=config.smtp_app_password
        )

    def send_success_report(self, payments: List[PaymentRequest]) -> None:
        """Send a report of successful payment requests"""
        subject = "Venmo Auto-Request: Monthly Report"
        contents = [
            "Monthly Venmo requests have been sent:",
            *[f"- {p.venmo_id}: ${p.amount} for {p.note}" for p in payments]
        ]
        self.client.send(self.config.notification_email, subject, contents)

    def send_error_notification(self, error: Exception, context: str) -> None:
        """Send a notification about an error that occurred"""
        subject = "Venmo Auto-Request: Error Report"
        self.client.send(
            self.config.notification_email,
            subject,
            f"Error occurred during {context}: {str(error)}"
        ) 