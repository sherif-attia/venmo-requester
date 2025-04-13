# Standard library imports
from datetime import datetime
from decimal import Decimal
from typing import Protocol

# Third-party imports
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Local application imports
from app.models.config import GoogleSheetsConfig
from app.models.payment import PaymentDate, PaymentFrequency, PaymentRequest
from app.services.payment_requests import IPaymentRequestRepository

class GoogleSheetsPaymentRequestRepository:
    """
    Repository implementation using Google Sheets as the data source.
    
    This implementation:
    1. Handles Google Sheets API authentication
    2. Retrieves and parses payment request data
    3. Converts raw data into PaymentRequest objects
    4. Filters requests based on current date and frequency
    """
    
    def __init__(self, config: GoogleSheetsConfig):
        """
        Initialize the repository with Google Sheets configuration.
        
        Args:
            config: Google Sheets configuration containing credentials and spreadsheet ID
        """
        self.config = config
        try:
            creds = ServiceAccountCredentials.from_service_account_file(
                self.config.credentials_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )
            self._service = build("sheets", "v4", credentials=creds)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google Sheets repository: {str(e)}")
    
    async def get_payment_requests(self) -> list[PaymentRequest]:
        """
        Retrieve payment requests that should be processed today from the Google Sheets spreadsheet.
        
        This method:
        1. Reads data from the configured spreadsheet
        2. Parses the data into PaymentRequest objects
        3. Filters requests based on current date and frequency:
           - Monthly requests: processed on the specified day of the month
           - Yearly requests: processed on the specified month and day
        
        Returns:
            list[PaymentRequest]: List of PaymentRequest objects that should be processed today
            
        Raises:
            RuntimeError: If the repository is not properly initialized
            HttpError: If there's an error with the Google Sheets API
        """
        try:
            # Read data from the spreadsheet
            result = self._service.spreadsheets().values().get(
                spreadsheetId=self.config.spreadsheet_id,
                range="A:E"  # Updated to include payment_date column
            ).execute()
            
            values = result.get("values", [])
            if not values:
                return []
            
            # Skip header row
            rows = values[1:]
            
            # Get current date for filtering
            today = datetime.now()
            
            # Parse rows into PaymentRequest objects
            payment_requests = []
            for row in rows:
                if len(row) >= 5:  # Ensure we have all required columns
                    try:
                        # Parse amount by removing $ and converting to Decimal
                        amount = Decimal(row[2].replace('$', ''))
                        
                        # Create payment request
                        request = PaymentRequest(
                            venmo_id=row[0],
                            note=row[1],
                            amount=amount,
                            frequency=PaymentFrequency(row[3].lower()),
                            payment_date=PaymentDate(value=row[4])
                        )
                        
                        # Check if this request should be processed today
                        should_process = False
                        if request.frequency == PaymentFrequency.MONTHLY:
                            should_process = today.day == int(request.payment_date.value)
                        elif request.frequency == PaymentFrequency.YEARLY:
                            month, day = map(int, request.payment_date.value.split('-'))
                            should_process = today.month == month and today.day == day
                        
                        if should_process:
                            payment_requests.append(request)
                            
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing row {row}: {e}")
                        continue
            
            return payment_requests
            
        except HttpError as e:
            raise RuntimeError(f"Google Sheets API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}") 