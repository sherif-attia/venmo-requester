import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio

from app.models.config import AppConfig, VenmoConfig, EmailConfig, GoogleSheetsConfig
from app.models.payment import PaymentRequest
from app.services.container import ServiceContainer
from app.services.email_service import EmailService
from app.services.sheets_service import SheetsService
from app.services.venmo_service import VenmoService

# Load environment variables from .env file
load_dotenv()

def create_config() -> AppConfig:
    """
    Create application configuration from environment variables.
    
    This function:
    1. Loads environment variables from .env file
    2. Creates configuration objects for each service
    3. Returns a complete AppConfig instance
    
    Returns:
        AppConfig instance with all configurations loaded
    """
    return AppConfig(
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
        google_sheets=GoogleSheetsConfig(
            credentials_path=Path(os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")),
            spreadsheet_id=os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )

async def main():
    """
    Main application entry point.
    
    This function:
    1. Sets up logging
    2. Loads configuration
    3. Initializes services
    4. Processes pending payment requests
    5. Handles errors and sends notifications
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = create_config()
        
        # Create and connect service container
        container = ServiceContainer(config)
        await container.__connect__()
        
        # Get services from container
        email_service = container.email_service
        sheets_service = container.sheets_service
        venmo_service = container.venmo_service
        
        # Process pending requests
        pending_requests = await sheets_service.get_payment_requests()
        logger.info(f"Found {len(pending_requests)} pending requests")
        
        for request in pending_requests:
            try:
                # Request payment from each user
                success = await venmo_service.request_payment(
                    user_id=request.user_id,
                    amount=request.amount,
                    note=request.note
                )
                if success:
                    logger.info(f"Successfully requested payment from {request.user_id}")
                else:
                    logger.warning(f"Failed to request payment from {request.user_id}")
            except Exception as e:
                logger.error(f"Error processing request for {request.user_id}: {str(e)}")
                email_service.send_error_notification(e, f"processing request for {request.user_id}")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        if 'container' in locals():
            await container.__disconnect__()
            container.email_service.send_error_notification(e, "main execution")

if __name__ == "__main__":
    # Run the main function using asyncio
    asyncio.run(main())
