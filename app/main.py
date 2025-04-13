import logging
from pathlib import Path
from dotenv import load_dotenv
import os

from app.models.config import AppConfig, VenmoConfig, EmailConfig
from app.services.email_service import EmailService

# Load environment variables
load_dotenv()

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = AppConfig(
            venmo=VenmoConfig(
                access_token=os.getenv("VENMO_ACCESS_TOKEN"),
                client_id=os.getenv("VENMO_CLIENT_ID"),
                client_secret=os.getenv("VENMO_CLIENT_SECRET")
            ),
            email=EmailConfig(
                smtp_user=os.getenv("EMAIL_USER"),
                smtp_app_password=os.getenv("EMAIL_APP_PASSWORD"),
                notification_email=os.getenv("NOTIFICATION_EMAIL")
            ),
            payment_data_path=os.getenv("PAYMENT_DATA_PATH", "data/payments.csv"),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )

        # Initialize services
        email_service = EmailService(config.email)

        # TODO: Implement payment processing
        logger.info("Starting payment processing...")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        if 'email_service' in locals():
            email_service.send_error_notification(e, "main execution")

if __name__ == "__main__":
    main()
