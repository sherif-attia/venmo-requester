from decimal import Decimal
import pytest
from pydantic import ValidationError

from app.models.payment import PaymentRequest, PaymentResult
from app.models.config import EmailConfig, VenmoConfig, AppConfig

def test_it_should_reject_negative_payment_amounts():
    """Test that negative amounts are rejected"""
    with pytest.raises(ValidationError):
        PaymentRequest(
            venmo_username="johndoe",
            full_name="John Doe",
            amount=Decimal("-25.50"),  # Negative amount should fail
            description="March Utilities",
            email="john@example.com"
        )

def test_it_should_validate_email_format():
    """Test that invalid email formats are rejected"""
    with pytest.raises(ValidationError):
        PaymentRequest(
            venmo_username="johndoe",
            full_name="John Doe",
            amount=Decimal("25.50"),
            description="March Utilities",
            email="not-an-email"  # Invalid email format should fail
        )

def test_it_should_handle_payment_success_and_failure_states():
    """Test that error messages are properly handled"""
    request = PaymentRequest(
        venmo_username="johndoe",
        full_name="John Doe",
        amount=Decimal("25.50"),
        description="March Utilities",
        email="john@example.com"
    )
    
    # Test successful payment
    success_result = PaymentResult(
        request=request,
        success=True,
        error_message=None
    )
    assert success_result.success is True
    assert success_result.error_message is None
    
    # Test failed payment with error message
    error_message = "Insufficient funds"
    failed_result = PaymentResult(
        request=request,
        success=False,
        error_message=error_message
    )
    assert failed_result.success is False
    assert failed_result.error_message == error_message

def test_it_should_properly_mask_sensitive_config_values():
    """Test that secrets are properly handled in config"""
    # Test that secrets are properly masked in string representation
    config = VenmoConfig(
        access_token="secret_token",
        client_id="secret_id",
        client_secret="secret_secret"
    )
    
    # Verify secrets are masked in string representation
    config_str = str(config)
    assert "secret_token" not in config_str
    assert "secret_id" not in config_str
    assert "secret_secret" not in config_str
    
    # Verify we can still access the actual values
    assert config.access_token.get_secret_value() == "secret_token"
    assert config.client_id.get_secret_value() == "secret_id"
    assert config.client_secret.get_secret_value() == "secret_secret" 