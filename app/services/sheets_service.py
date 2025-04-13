from typing import Protocol, List
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.models.payment import PaymentRequest
from app.models.config import GoogleSheetsConfig

class SheetsService(Protocol):
    """Protocol defining the interface for sheet services"""
    def get_payment_requests(self) -> List[PaymentRequest]: ...

class GoogleSheetsService:
    """Service for interacting with Google Sheets"""
    
    def __init__(self, config: GoogleSheetsConfig):
        self.config = config
        self._service = self._build_service()

    def _build_service(self):
        """Build the Google Sheets service"""
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.config.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            return build('sheets', 'v4', credentials=creds)
        except Exception as e:
            raise RuntimeError(f"Failed to build Google Sheets service: {str(e)}")

    def get_payment_requests(self) -> List[PaymentRequest]:
        """Fetch payment requests from the configured spreadsheet"""
        try:
            # Get the values from the first sheet
            result = self._service.spreadsheets().values().get(
                spreadsheetId=self.config.spreadsheet_id,
                range='A:C'  # Columns A (venmo_id), B (note), C (amount)
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []

            # Skip header row and process data
            return [
                PaymentRequest(
                    venmo_id=row[0],
                    note=row[1],
                    amount=row[2]
                )
                for row in values[1:]  # Skip header row
            ]

        except HttpError as e:
            raise RuntimeError(f"Failed to fetch data from Google Sheets: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while fetching payment requests: {str(e)}") 