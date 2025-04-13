from typing import Protocol, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.models.payment import PaymentRequest
from app.models.config import EmailConfig

class IEmailService(Protocol):
    """
    Interface defining the contract for email service implementations.
    
    This protocol ensures that any implementation of the email service
    must provide these methods with the specified signatures.
    """
    
    def send_error_notification(self, error: Exception, context: str) -> None:
        """
        Send an error notification email.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
        """
        ...
        
    def send_success_report(self, payments: List[PaymentRequest]) -> None:
        """
        Send a report of successful payment requests.
        
        Args:
            payments: List of successful payment requests to report
        """
        ...

class GmailService:
    """
    Implementation of email service using Gmail SMTP.
    
    This service handles:
    1. SMTP connection management
    2. Email composition and sending
    3. Error handling for email operations
    """
    
    def __init__(self, config: EmailConfig):
        """
        Initialize the Gmail service with email configuration.
        
        Args:
            config: Email configuration containing SMTP credentials
        """
        self.config = config
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_error_notification(self, error: Exception, context: str) -> None:
        """
        Send an error notification email using Gmail SMTP.
        
        This method:
        1. Creates a multipart email message
        2. Sets up the email content with error details
        3. Connects to Gmail SMTP server
        4. Sends the email
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            
        Raises:
            RuntimeError: If there's an error sending the email
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_user
            msg['To'] = self.config.notification_email
            msg['Subject'] = f"Error in Venmo Auto Request: {context}"
            
            # Create email body
            body = f"""
            An error occurred in the Venmo Auto Request application:
            
            Context: {context}
            Error: {str(error)}
            Type: {type(error).__name__}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_app_password)
                server.send_message(msg)
                
        except Exception as e:
            raise RuntimeError(f"Failed to send error notification email: {str(e)}")
            
    def send_success_report(self, payments: List[PaymentRequest]) -> None:
        """
        Send a report of successful payment requests using Gmail SMTP.
        
        This method:
        1. Creates a multipart email message
        2. Sets up the email content with payment details
        3. Connects to Gmail SMTP server
        4. Sends the email
        
        Args:
            payments: List of successful payment requests to report
            
        Raises:
            RuntimeError: If there's an error sending the email
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_user
            msg['To'] = self.config.notification_email
            msg['Subject'] = "Venmo Auto Request: Success Report"
            
            # Create email body
            body = """
            The following payment requests were successfully sent:
            
            """
            for payment in payments:
                body += f"- {payment.user_id}: ${payment.amount:.2f} for {payment.note}\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_app_password)
                server.send_message(msg)
                
        except Exception as e:
            raise RuntimeError(f"Failed to send success report email: {str(e)}") 