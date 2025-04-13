from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.models.config import GoogleSheetsConfig
from app.models.payment import PaymentRequest
from app.services.payment_requests import GoogleSheetsPaymentRequestRepository

# Test constants
EXPECTED_REQUESTS_COUNT = 2


def test_it_should_initialize_with_valid_config():
    """Test that the service initializes with valid configuration"""
    config = GoogleSheetsConfig(
        credentials_path=Path("test_credentials.json"), spreadsheet_id="test_spreadsheet_id"
    )
    service = GoogleSheetsPaymentRequestRepository(config)
    assert service.config == config


@patch("google.oauth2.service_account.Credentials.from_service_account_file")
@patch("googleapiclient.discovery.build")
def test_it_should_fetch_payment_requests(mock_build, mock_credentials):
    """Test that the service correctly fetches and processes payment requests"""
    # Setup mock service
    mock_service = Mock()
    sheets_mock = mock_service.spreadsheets.return_value
    values_mock = sheets_mock.values.return_value
    get_mock = values_mock.get.return_value
    get_mock.execute.return_value = {
        "values": [
            ["venmo_id", "note", "amount"],  # Header row
            ["user1", "March Rent", "500.00"],
            ["user2", "Utilities", "75.50"],
        ]
    }
    mock_build.return_value = mock_service

    # Initialize service
    config = GoogleSheetsConfig(
        credentials_path=Path("test_credentials.json"), spreadsheet_id="test_spreadsheet_id"
    )
    service = GoogleSheetsPaymentRequestRepository(config)

    # Test fetching requests
    requests = service.get_payment_requests()

    assert len(requests) == EXPECTED_REQUESTS_COUNT
    assert isinstance(requests[0], PaymentRequest)
    assert requests[0].venmo_id == "user1"
    assert requests[0].note == "March Rent"
    assert requests[0].amount == "500.00"


@patch("google.oauth2.service_account.Credentials.from_service_account_file")
@patch("googleapiclient.discovery.build")
def test_it_should_handle_empty_sheet(mock_build, mock_credentials):
    """Test that the service handles empty sheets gracefully"""
    # Setup mock service with empty response
    mock_service = Mock()
    sheets_mock = mock_service.spreadsheets.return_value
    values_mock = sheets_mock.values.return_value
    get_mock = values_mock.get.return_value
    get_mock.execute.return_value = {"values": []}
    mock_build.return_value = mock_service

    config = GoogleSheetsConfig(
        credentials_path=Path("test_credentials.json"), spreadsheet_id="test_spreadsheet_id"
    )
    service = GoogleSheetsPaymentRequestRepository(config)

    requests = service.get_payment_requests()
    assert len(requests) == 0


@patch("google.oauth2.service_account.Credentials.from_service_account_file")
@patch("googleapiclient.discovery.build")
def test_it_should_handle_sheet_errors(mock_build, mock_credentials):
    """Test that the service properly handles Google Sheets API errors"""
    # Setup mock service to raise an error
    mock_service = Mock()
    sheets_mock = mock_service.spreadsheets.return_value
    values_mock = sheets_mock.values.return_value
    get_mock = values_mock.get.return_value
    get_mock.execute.side_effect = Exception("API Error")
    mock_build.return_value = mock_service

    config = GoogleSheetsConfig(
        credentials_path=Path("test_credentials.json"), spreadsheet_id="test_spreadsheet_id"
    )
    service = GoogleSheetsPaymentRequestRepository(config)

    with pytest.raises(RuntimeError) as exc_info:
        service.get_payment_requests()
    assert "Failed to fetch data from Google Sheets" in str(exc_info.value)


@patch("google.oauth2.service_account.Credentials.from_service_account_file")
@patch("googleapiclient.discovery.build")
def test_it_should_handle_missing_columns(mock_build, mock_credentials):
    """Test that the service handles sheets with missing columns"""
    # Setup mock service with incomplete data
    mock_service = Mock()
    sheets_mock = mock_service.spreadsheets.return_value
    values_mock = sheets_mock.values.return_value
    get_mock = values_mock.get.return_value
    get_mock.execute.return_value = {
        "values": [
            ["venmo_id", "note"],  # Missing amount column
            ["user1", "March Rent"],
        ]
    }
    mock_build.return_value = mock_service

    config = GoogleSheetsConfig(
        credentials_path=Path("test_credentials.json"), spreadsheet_id="test_spreadsheet_id"
    )
    service = GoogleSheetsPaymentRequestRepository(config)

    with pytest.raises(RuntimeError) as exc_info:
        service.get_payment_requests()
    assert "Unexpected error" in str(exc_info.value)


@patch("google.oauth2.service_account.Credentials.from_service_account_file")
@patch("googleapiclient.discovery.build")
def test_it_should_handle_invalid_amount_format(mock_build, mock_credentials):
    """Test that the service handles invalid amount formats"""
    # Setup mock service with invalid amount
    mock_service = Mock()
    sheets_mock = mock_service.spreadsheets.return_value
    values_mock = sheets_mock.values.return_value
    get_mock = values_mock.get.return_value
    get_mock.execute.return_value = {
        "values": [["venmo_id", "note", "amount"], ["user1", "March Rent", "not-a-number"]]
    }
    mock_build.return_value = mock_service

    config = GoogleSheetsConfig(
        credentials_path=Path("test_credentials.json"), spreadsheet_id="test_spreadsheet_id"
    )
    service = GoogleSheetsPaymentRequestRepository(config)

    with pytest.raises(RuntimeError) as exc_info:
        service.get_payment_requests()
    assert "Unexpected error" in str(exc_info.value)
