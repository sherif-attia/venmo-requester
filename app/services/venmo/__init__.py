from typing import Protocol


class IVenmoService(Protocol):
    """
    Interface defining the contract for Venmo service implementations.

    This protocol ensures that any implementation of the Venmo service
    must provide these methods with the specified signatures.
    """

    async def request_payment(self, user_id: str, amount: float, note: str) -> bool:
        """
        Request a payment from a Venmo user.

        Args:
            user_id: The Venmo user ID to request payment from
            amount: The amount to request
            note: A note to include with the payment request

        Returns:
            bool: True if the request was successful, False otherwise
        """
        ...

    async def get_user_id(self, username: str) -> str | None:
        """
        Get Venmo user ID from username.

        Args:
            username: The Venmo username to look up

        Returns:
            str | None: The user ID if found, None otherwise
        """
        ...

    async def get_pending_requests(self) -> list[dict]:
        """
        Get list of pending payment requests.

        Returns:
            list[dict]: List of pending payment requests
        """
        ...


__all__ = ["IVenmoService"]
