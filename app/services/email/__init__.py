from typing import Protocol

from app.models.payment import PaymentRequest


class IEmailService(Protocol):
    """
    Interface defining the contract for email service implementations.

    This protocol ensures that any implementation of the email service
    must provide these methods with the specified signatures.
    """

    def send_error_notification(self, error: Exception, context: str) -> None:
        """
        Send an error notification email.

        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
        """
        ...

    def send_success_report(self, payments: list[PaymentRequest]) -> None:
        """
        Send a report of successful payment requests.

        Args:
            payments: List of successful payment requests to report
        """
        ...


__all__ = ["IEmailService"]
