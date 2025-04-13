# Standard library imports
from pathlib import Path

# Third-party imports
from pydantic import BaseModel, Field

class VenmoConfig(BaseModel):
    """
    Configuration for Venmo API access.
    
    Attributes:
        access_token: OAuth access token for Venmo API
        client_id: OAuth client ID for Venmo API
        client_secret: OAuth client secret for Venmo API
    """
    access_token: SecretStr
    client_id: SecretStr
    client_secret: SecretStr

class EmailConfig(BaseModel):
    """
    Configuration for email notifications.
    
    Attributes:
        smtp_user: Gmail address for sending emails
        smtp_app_password: Gmail app password for SMTP
        notification_email: Email address to send notifications to
    """
    smtp_user: EmailStr
    smtp_app_password: SecretStr
    notification_email: EmailStr

class GoogleSheetsConfig(BaseModel):
    """
    Configuration for Google Sheets access.
    
    Attributes:
        credentials_path: Path to Google service account credentials JSON file
        spreadsheet_id: ID of the Google Spreadsheet to read from
    """
    credentials_path: FilePath
    spreadsheet_id: str

class AppConfig(BaseModel):
    """
    Main application configuration.
    
    This class combines all service-specific configurations
    into a single configuration object.
    
    Attributes:
        venmo: Venmo API configuration
        email: Email service configuration
        google_sheets: Google Sheets configuration
        log_level: Logging level for the application
    """
    venmo: VenmoConfig
    email: EmailConfig
    google_sheets: GoogleSheetsConfig
    log_level: str = "INFO" 