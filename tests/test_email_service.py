import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from app.services.email_service import GmailService
from app.models.config import EmailConfig
from app.models.payment import PaymentRequest

def test_it_should_initialize_with_valid_config():
    """Test that the service initializes with valid configuration"""
    config = EmailConfig(
        smtp_user="test@example.com",
        smtp_app_password="test_password",
        notification_email="notify@example.com"
    )
    service = GmailService(config)
    assert service.config == config

@patch('yagmail.SMTP')
def test_it_should_send_success_report(mock_smtp):
    """Test that the service correctly sends success reports"""
    # Setup
    config = EmailConfig(
        smtp_user="test@example.com",
        smtp_app_password="test_password",
        notification_email="notify@example.com"
    )
    service = GmailService(config)
    
    # Create test payment requests
    payments = [
        PaymentRequest(
            venmo_id="user1",
            note="March Rent",
            amount=Decimal("500.00")
        ),
        PaymentRequest(
            venmo_id="user2",
            note="Utilities",
            amount=Decimal("75.50")
        )
    ]
    
    # Send report
    service.send_success_report(payments)
    
    # Verify email was sent with correct content
    service.client.send.assert_called_once()
    args = service.client.send.call_args[0]
    assert args[0] == "notify@example.com"  # recipient
    assert args[1] == "Venmo Auto-Request: Monthly Report"  # subject
    assert "user1: $500.00 for March Rent" in args[2]  # content
    assert "user2: $75.50 for Utilities" in args[2]  # content

@patch('yagmail.SMTP')
def test_it_should_send_error_notification(mock_smtp):
    """Test that the service correctly sends error notifications"""
    # Setup
    config = EmailConfig(
        smtp_user="test@example.com",
        smtp_app_password="test_password",
        notification_email="notify@example.com"
    )
    service = GmailService(config)
    
    # Create test error
    error = Exception("Test error message")
    context = "payment processing"
    
    # Send error notification
    service.send_error_notification(error, context)
    
    # Verify email was sent with correct content
    service.client.send.assert_called_once()
    args = service.client.send.call_args[0]
    assert args[0] == "notify@example.com"  # recipient
    assert args[1] == "Venmo Auto-Request: Error Report"  # subject
    assert "Error occurred during payment processing: Test error message" in args[2]  # content

@patch('yagmail.SMTP')
def test_it_should_handle_email_sending_failures(mock_smtp):
    """Test that the service properly handles email sending failures"""
    # Setup
    config = EmailConfig(
        smtp_user="test@example.com",
        smtp_app_password="test_password",
        notification_email="notify@example.com"
    )
    service = GmailService(config)
    
    # Mock the send method to raise an exception
    service.client.send.side_effect = Exception("SMTP Error")
    
    # Test success report failure
    payments = [PaymentRequest(venmo_id="user1", note="Test", amount=Decimal("10.00"))]
    with pytest.raises(Exception) as exc_info:
        service.send_success_report(payments)
    assert "SMTP Error" in str(exc_info.value)
    
    # Test error notification failure
    error = Exception("Test error")
    with pytest.raises(Exception) as exc_info:
        service.send_error_notification(error, "test context")
    assert "SMTP Error" in str(exc_info.value) 