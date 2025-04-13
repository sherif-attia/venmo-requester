from typing import Protocol, List
import yagmail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.models.payment import PaymentRequest
from app.models.config import EmailConfig

class EmailService(Protocol):
    """
    Interface defining the contract for email service implementations.
    
    This protocol ensures that any implementation of the email service
    must provide these methods with the specified signatures.
    """
    
    def send_success_report(self, payments: List[PaymentRequest]) -> None:
        """Send a report of successful payment requests"""
        ...
    def send_error_notification(self, error: Exception, context: str) -> None:
        """
        Send an error notification email.
        
        Args:
            error: The exception that occurred
            context: Description of where/why the error occurred
        """
        ...

class GmailService(EmailService):
    """
    Implementation of EmailService using Gmail SMTP.
    
    This service handles:
    1. SMTP connection management
    2. Email composition and sending
    3. Error handling for email operations
    """
    
    def __init__(self, config: EmailConfig):
        """
        Initialize the Gmail service.
        
        Args:
            config: Email configuration containing SMTP credentials and settings
        """
        self.config = config
        self._smtp = None  # Will be initialized when needed
    
    def _ensure_connected(self):
        """
        Ensure SMTP connection is established.
        
        Creates a new connection if one doesn't exist.
        """
        if not self._smtp:
            self._smtp = smtplib.SMTP("smtp.gmail.com", 587)
            self._smtp.starttls()
            self._smtp.login(self.config.smtp_user, self.config.smtp_app_password)
    
    def send_success_report(self, payments: List[PaymentRequest]) -> None:
        """Send a report of successful payment requests"""
        subject = "Venmo Auto-Request: Monthly Report"
        contents = [
            "Monthly Venmo requests have been sent:",
            *[f"- {p.venmo_id}: ${p.amount} for {p.note}" for p in payments]
        ]
        self._smtp.send_message(self.config.notification_email, subject, contents)

    def send_error_notification(self, error: Exception, context: str) -> None:
        """
        Send an error notification email.
        
        This method:
        1. Creates a formatted error message
        2. Establishes SMTP connection if needed
        3. Sends the email to the configured notification address
        
        Args:
            error: The exception that occurred
            context: Description of where/why the error occurred
        """
        try:
            self._ensure_connected()
            
            msg = MIMEMultipart()
            msg["From"] = self.config.smtp_user
            msg["To"] = self.config.notification_email
            msg["Subject"] = f"Error in {context}"
            
            body = f"""
            An error occurred in {context}:
            
            Error Type: {type(error).__name__}
            Error Message: {str(error)}
            """
            
            msg.attach(MIMEText(body, "plain"))
            
            self._smtp.send_message(msg)
        except Exception as e:
            # If we can't send the error email, at least log it
            print(f"Failed to send error email: {str(e)}")
            raise 