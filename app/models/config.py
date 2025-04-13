from pydantic import BaseModel, EmailStr, SecretStr, FilePath

class VenmoConfig(BaseModel):
    access_token: SecretStr
    client_id: SecretStr
    client_secret: SecretStr

class EmailConfig(BaseModel):
    smtp_user: EmailStr
    smtp_app_password: SecretStr
    notification_email: EmailStr

class GoogleSheetsConfig(BaseModel):
    credentials_path: FilePath
    spreadsheet_id: str

class AppConfig(BaseModel):
    venmo: VenmoConfig
    email: EmailConfig
    google_sheets: GoogleSheetsConfig
    log_level: str = "INFO" 