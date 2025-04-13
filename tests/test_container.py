from pathlib import Path
from unittest.mock import patch

import pytest

from app.models.config import AppConfig, EmailConfig, GoogleSheetsConfig, VenmoConfig
from app.services.container import ServiceContainer


@pytest.fixture
def mock_config():
    """Create a mock configuration"""
    return AppConfig(
        email=EmailConfig(
            smtp_user="test@example.com",
            smtp_app_password="test_password",
            notification_email="notify@example.com",
        ),
        google_sheets=GoogleSheetsConfig(
            credentials_path=Path("test_credentials.json"), spreadsheet_id="test_spreadsheet_id"
        ),
        venmo=VenmoConfig(
            access_token="test_token",
            client_id="test_client_id",
            client_secret="test_client_secret",
        ),
        log_level="INFO",
    )


def test_it_should_initialize_with_config(mock_config):
    """Test that the container initializes with the provided config"""
    container = ServiceContainer(mock_config)
    assert container.config == mock_config


def test_it_should_lazily_create_email_service(mock_config):
    """Test that the email service is created only when first accessed"""
    container = ServiceContainer(mock_config)
    assert container._email_service is None

    # Access the service
    service = container.email_service
    assert service is not None
    assert container._email_service is service

    # Second access should return the same instance
    assert container.email_service is service


def test_it_should_lazily_create_sheets_service(mock_config):
    """Test that the sheets service is created only when first accessed"""
    container = ServiceContainer(mock_config)
    assert container._sheets_service is None

    # Access the service
    service = container.sheets_service
    assert service is not None
    assert container._sheets_service is service

    # Second access should return the same instance
    assert container.sheets_service is service


@patch("app.services.email_service.GmailService")
def test_it_should_create_email_service_with_config(mock_gmail_service, mock_config):
    """Test that the email service is created with the correct config"""
    container = ServiceContainer(mock_config)
    container.email_service

    mock_gmail_service.assert_called_once_with(mock_config.email)


@patch("app.services.sheets_service.GoogleSheetsService")
def test_it_should_create_sheets_service_with_config(mock_sheets_service, mock_config):
    """Test that the sheets service is created with the correct config"""
    container = ServiceContainer(mock_config)
    container.sheets_service

    mock_sheets_service.assert_called_once_with(mock_config.google_sheets)
