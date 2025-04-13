from typing import Protocol, List
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.models.payment import PaymentRequest
from app.models.config import GoogleSheetsConfig

class ISheetsService(Protocol):
    """
    Interface defining the contract for Google Sheets service implementations.
    
    This protocol ensures that any implementation of the sheets service
    must provide these methods with the specified signatures.
    """
    
    async def get_payment_requests(self) -> List[PaymentRequest]:
        """
        Get a list of payment requests from the spreadsheet.
        
        Returns:
            List of PaymentRequest objects containing request data
        """
        ...

class GoogleSheetsService:
    """
    Implementation of ISheetsService using Google Sheets API.
    
    This service handles:
    1. Authentication with Google Sheets API
    2. Reading data from the spreadsheet
    3. Error handling for API operations
    """
    
    def __init__(self, config: GoogleSheetsConfig):
        """
        Initialize the Google Sheets service.
        
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
            raise RuntimeError(f"Failed to initialize Google Sheets service: {str(e)}")
    
    async def get_payment_requests(self) -> List[PaymentRequest]:
        """
        Get a list of payment requests from the spreadsheet.
        
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
            RuntimeError: If the service is not initialized
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