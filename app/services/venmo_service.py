from typing import Protocol, List, Optional
import aiohttp
from app.models.config import VenmoConfig
from app.models.payment import PaymentRequest

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
    
    async def get_user_id(self, username: str) -> Optional[str]:
        """Get Venmo user ID from username"""
        ...
    
    async def get_pending_requests(self) -> List[dict]:
        """Get list of pending payment requests"""
        ...

class VenmoAPIService:
    """
    Implementation of Venmo service using the Venmo API.
    
    This service handles:
    1. Authentication with Venmo API
    2. Making payment requests
    3. Error handling for API operations
    """
    
    def __init__(self, config: VenmoConfig):
        """
        Initialize the Venmo API service with configuration.
        
        Args:
            config: Venmo configuration containing API credentials
        """
        self.config = config
        self.base_url = "https://api.venmo.com/v1"
        self.headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json"
        }
    
    async def request_payment(self, user_id: str, amount: float, note: str) -> bool:
        """
        Request a payment from a Venmo user using the Venmo API.
        
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
            data = {
                "user_id": user_id,
                "amount": venmo_amount,
                "note": note,
                "audience": "private"
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/payments",
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_data = await response.json()
                        raise RuntimeError(f"Venmo API error: {error_data.get('message', 'Unknown error')}")
                        
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error while making Venmo request: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while making Venmo request: {str(e)}")
    
    async def get_user_id(self, username: str) -> Optional[str]:
        """Get Venmo user ID from username"""
        # TODO: Implement actual Venmo API call
        return None
    
    async def get_pending_requests(self) -> List[dict]:
        """Get list of pending payment requests"""
        # TODO: Implement actual Venmo API call
        return []

class VenmoAPIError(Exception):
    """
    Custom exception for Venmo API errors.
    
    This exception is raised when:
    1. The API returns an error response
    2. There's a network error
    3. Any other unexpected error occurs
    """
    pass 