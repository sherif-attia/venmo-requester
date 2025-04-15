from typing import Protocol

from app.models.payment import PaymentRequest


class IPaymentRequestRepository(Protocol):
    """Repository interface for payment request data access.

    This protocol defines the contract for accessing payment request data,
    abstracting away the specific implementation details of the data source.
    """

    async def get_payment_requests(self) -> list[PaymentRequest]:
        """Retrieve all pending payment requests from the repository.

        Returns:
            List of PaymentRequest objects containing request data
        """
        ...


__all__ = ["IPaymentRequestRepository"]
