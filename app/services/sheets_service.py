from typing import Protocol, List
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.models.payment import PaymentRequest
from app.models.config import GoogleSheetsConfig

class IPaymentRequestRepository(Protocol):
    """
    Repository interface for payment request data access.
    
    This protocol defines the contract for accessing payment request data,
    abstracting away the specific implementation details of the data source.
    """
    
    async def get_payment_requests(self) -> List[PaymentRequest]:
        """
        Retrieve all pending payment requests from the repository.
        
        Returns:
            List of PaymentRequest objects containing request data
        """
        ...

class GoogleSheetsPaymentRequestRepository:
    """
    Repository implementation using Google Sheets as the data source.
    
    This implementation:
    1. Handles Google Sheets API authentication
    2. Retrieves and parses payment request data
    3. Converts raw data into PaymentRequest objects
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
    
    async def get_payment_requests(self) -> List[PaymentRequest]:
        """
        Retrieve all pending payment requests from the Google Sheets spreadsheet.
        
        This method:
        1. Reads data from the configured spreadsheet
        2. Parses the data into PaymentRequest objects
        3. Filters for pending requests
        
        Returns:
            List of PaymentRequest objects containing:
            - user_id: Venmo user ID
            - amount: Payment amount
            - note: Payment note
            - status: Request status
            
        Raises:
            RuntimeError: If the repository is not properly initialized
            HttpError: If there's an error with the Google Sheets API
        """
        try:
            # Read data from the spreadsheet
            result = self._service.spreadsheets().values().get(
                spreadsheetId=self.config.spreadsheet_id,
                range="A:D"  # Assuming columns A-D contain the relevant data
            ).execute()
            
            values = result.get("values", [])
            if not values:
                return []
            
            # Convert to list of PaymentRequest objects
            headers = values[0]
            requests = []
            for row in values[1:]:
                if len(row) >= len(headers):
                    data = dict(zip(headers, row))
                    if data.get("status", "").lower() == "pending":
                        requests.append(PaymentRequest(
                            user_id=data["user_id"],
                            amount=float(data["amount"]),
                            note=data["note"]
                        ))
            
            return requests
            
        except HttpError as e:
            raise RuntimeError(f"Google Sheets API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}") 