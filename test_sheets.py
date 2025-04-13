import asyncio
from pathlib import Path

from app.models.config import GoogleSheetsConfig
from app.services.payment_requests.google_sheets import GoogleSheetsPaymentRequestRepository


async def main():
    # Create configuration
    config = GoogleSheetsConfig(
        spreadsheet_id="YOUR_SPREADSHEET_ID",  # Replace with your spreadsheet ID
        credentials_path=Path(
            "path/to/your/credentials.json"
        ),  # Replace with path to your credentials
    )

    # Initialize repository
    repo = GoogleSheetsPaymentRequestRepository(config)

    try:
        # Get payment requests
        requests = await repo.get_payment_requests()

        # Print results
        print(f"Found {len(requests)} payment requests:")
        for request in requests:
            print(f"- {request.venmo_id}: ${request.amount} for {request.note}")
            print(f"  Frequency: {request.frequency}")
            print(f"  Payment Date: {request.payment_date.value}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
