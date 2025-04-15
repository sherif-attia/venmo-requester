import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from app.models.config import AppConfig, EmailConfig, GoogleSheetsConfig, VenmoConfig
from app.services.container import ServiceContainer
from app.services.email import IEmailService
from app.services.payment_requests import IPaymentRequestRepository
from app.services.venmo import IVenmoService

# Load environment variables from .env file
load_dotenv()


def create_config() -> AppConfig:
    """Create application configuration from environment variables.

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
            client_secret=os.getenv("VENMO_CLIENT_SECRET"),
        ),
        email=EmailConfig(
            smtp_user=os.getenv("EMAIL_USER"),
            smtp_app_password=os.getenv("EMAIL_APP_PASSWORD"),
            notification_email=os.getenv("NOTIFICATION_EMAIL"),
        ),
        google_sheets=GoogleSheetsConfig(
            credentials_path=Path(os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")),
            spreadsheet_id=os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID"),
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


async def main():
    """Main application entry point.

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
        email_service: IEmailService = container.email_service
        payment_request_repository: IPaymentRequestRepository = container.payment_request_repository
        venmo_service: IVenmoService = container.venmo_service

        # Process pending requests
        pending_requests = await payment_request_repository.get_payment_requests()
        logger.info(f"Found {len(pending_requests)} pending requests")

        successful_requests = []
        for request in pending_requests:
            try:
                # Request payment from each user
                success = await venmo_service.request_payment(
                    user_id=request.user_id,
                    amount=request.amount,
                    note=request.note,
                )
                if success:
                    logger.info(f"Successfully requested payment from {request.user_id}")
                    successful_requests.append(request)
                else:
                    logger.warning(f"Failed to request payment from {request.user_id}")
            except Exception as e:
                logger.error(f"Error processing request for {request.user_id}: {e!s}")
                email_service.send_error_notification(
                    e,
                    f"processing request for {request.user_id}",
                )

        # Send success report if we processed any requests
        if successful_requests:
            email_service.send_success_report(successful_requests)

    except Exception as e:
        logger.error(f"Error in main: {e!s}")
        # Only try to send error notification if we have a container
        if "container" in locals():
            try:
                container.email_service.send_error_notification(e, "main execution")
            except Exception as email_error:
                # If we can't send the error email, at least log it
                logger.error(f"Failed to send error notification: {email_error!s}")


if __name__ == "__main__":
    # Run the main function using asyncio
    asyncio.run(main())
