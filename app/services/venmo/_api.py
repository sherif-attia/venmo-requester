import httpx

from app.models.config import VenmoConfig

# HTTP status codes
HTTP_OK = 200


class VenmoAPIService:
    """Implementation of Venmo service using the Venmo API.

    This service handles:
    1. Authentication with Venmo API
    2. Making payment requests
    3. Error handling for API operations
    """

    def __init__(self, config: VenmoConfig):
        """Initialize the Venmo API service with configuration.

        Args:
            config: Venmo configuration containing API credentials
        """
        self.config = config
        self.base_url = "https://api.venmo.com/v1"
        self.headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json",
        }

    async def request_payment(self, user_id: str, amount: float, note: str) -> bool:
        """Request a payment from a Venmo user using the Venmo API.

        This method:
        1. Formats the payment request data
        2. Makes an authenticated request to the Venmo API
        3. Handles the API response

        Args:
            user_id: The Venmo user ID to request payment from
            amount: The amount to request
            note: A note to include with the payment request

        Returns:
            bool: True if the request was successful, False otherwise

        Raises:
            RuntimeError: If there's an error with the Venmo API
        """
        try:
            # Convert amount to negative for Venmo API
            venmo_amount = -abs(amount)

            # Prepare request data
            data = {"user_id": user_id, "amount": venmo_amount, "note": note, "audience": "private"}

            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payments", headers=self.headers, json=data,
                )

                if response.status_code == httpx.codes.OK:
                    return True
                error_data = response.json()
                raise RuntimeError(
                    f"Venmo API error: {error_data.get('message', 'Unknown error')}",
                )

        except httpx.HTTPError as e:
            raise RuntimeError(f"Network error while making Venmo request: {e!s}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while making Venmo request: {e!s}")

    async def get_user_id(self, username: str) -> str | None:
        """Get Venmo user ID from username.

        Args:
            username: The Venmo username to look up

        Returns:
            str | None: The user ID if found, None otherwise
        """
        # TODO: Implement actual Venmo API call
        return None

    async def get_pending_requests(self) -> list[dict]:
        """Get list of pending payment requests.

        Returns:
            list[dict]: List of pending payment requests
        """
        # TODO: Implement actual Venmo API call
        return []
