from typing import Protocol, List, Optional
import httpx
from app.models.config import VenmoConfig

class IVenmoService(Protocol):
    """
    Interface defining the contract for Venmo service implementations.
    
    This protocol ensures that any implementation of the Venmo service
    must provide these methods with the specified signatures.
    """
    
    async def request_payment(self, user_id: str, amount: float, note: str) -> bool:
        """
        Request payment from a Venmo user.
        
        Args:
            user_id: Venmo user ID to request payment from
            amount: Amount to request (positive number)
            note: Message to accompany the payment request
            
        Returns:
            bool: True if request was successful, False otherwise
        """
        ...
    
    async def get_user_id(self, username: str) -> Optional[str]:
        """Get Venmo user ID from username"""
        ...
    
    async def get_pending_requests(self) -> List[dict]:
        """Get list of pending payment requests"""
        ...

class VenmoAPIService(IVenmoService):
    """
    Implementation of IVenmoService using the Venmo API.
    
    This service handles:
    1. Authentication with Venmo API
    2. Making payment requests
    3. Error handling and response processing
    """
    
    def __init__(self, config: VenmoConfig):
        """
        Initialize the Venmo API service.
        
        Args:
            config: Venmo configuration containing access token and other settings
        """
        self.config = config
        self._client = None  # Will be initialized in __connect__
    
    async def __connect__(self):
        """
        Initialize the HTTP client for making API requests.
        
        This is called by the dependency injector when the service is first accessed.
        """
        self._client = httpx.AsyncClient()
    
    async def __disconnect__(self):
        """
        Clean up the HTTP client.
        
        This is called by the dependency injector when the service is being disposed.
        """
        if self._client:
            await self._client.aclose()
    
    async def request_payment(self, user_id: str, amount: float, note: str) -> bool:
        """
        Request payment from a Venmo user.
        
        This method:
        1. Converts the positive amount to negative (required by Venmo API)
        2. Makes an authenticated request to the Venmo API
        3. Handles the response and any potential errors
        
        Args:
            user_id: Venmo user ID to request payment from
            amount: Amount to request (positive number)
            note: Message to accompany the payment request
            
        Returns:
            bool: True if request was successful, False otherwise
            
        Raises:
            VenmoAPIError: If there's an error with the API request
            RuntimeError: If the client is not initialized
        """
        if not self._client:
            raise RuntimeError("Venmo client not initialized")
        
        # Convert amount to negative for payment request
        request_amount = -abs(amount)
        
        try:
            response = await self._client.post(
                "https://api.venmo.com/v1/payments",
                headers={
                    "Authorization": f"Bearer {self.config.access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "user_id": user_id,
                    "amount": request_amount,
                    "note": note,
                    "audience": "private"  # Keep requests private by default
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("payment", {}).get("status") == "pending"
            else:
                error_data = response.json()
                raise VenmoAPIError(f"Venmo API error: {error_data}")
        except httpx.HTTPError as e:
            raise VenmoAPIError(f"Network error: {str(e)}")
        except Exception as e:
            raise VenmoAPIError(f"Unexpected error: {str(e)}")
    
    async def get_user_id(self, username: str) -> Optional[str]:
        """Get Venmo user ID from username"""
        if not self._client:
            raise RuntimeError("Venmo client not initialized")
        
        try:
            # TODO: Implement actual Venmo API call
            return None
        except Exception as e:
            # TODO: Handle specific Venmo API errors
            raise
    
    async def get_pending_requests(self) -> List[dict]:
        """Get list of pending payment requests"""
        if not self._client:
            raise RuntimeError("Venmo client not initialized")
        
        try:
            # TODO: Implement actual Venmo API call
            return []
        except Exception as e:
            # TODO: Handle specific Venmo API errors
            raise 

class VenmoAPIError(Exception):
    """
    Custom exception for Venmo API errors.
    
    This exception is raised when:
    1. The API returns an error response
    2. There's a network error
    3. Any other unexpected error occurs
    """
    pass 