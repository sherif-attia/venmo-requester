from typing import Protocol, List, Optional
import httpx
from app.models.config import VenmoConfig

class VenmoService(Protocol):
    """Interface for Venmo service operations"""
    
    async def request_payment(self, user_id: str, amount: float, note: str) -> bool:
        """Request payment from a Venmo user"""
        ...
    
    async def get_user_id(self, username: str) -> Optional[str]:
        """Get Venmo user ID from username"""
        ...
    
    async def get_pending_requests(self) -> List[dict]:
        """Get list of pending payment requests"""
        ...

class VenmoAPIService(VenmoService):
    """Implementation of Venmo service using Venmo API"""
    
    def __init__(self, config: VenmoConfig):
        self.config = config
        self._client = None
    
    async def __connect__(self):
        """Initialize httpx client"""
        self._client = httpx.AsyncClient()
    
    async def __disconnect__(self):
        """Cleanup httpx client"""
        if self._client:
            await self._client.aclose()
    
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
    """Custom exception for Venmo API errors"""
    pass 