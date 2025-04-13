from typing import Protocol
from magic_di import Connectable, DependencyInjector
from app.models.config import AppConfig
from app.services.email import IEmailService, GmailService
from app.services.venmo import IVenmoService, VenmoAPIService
from app.services.payment_requests import IPaymentRequestRepository, GoogleSheetsPaymentRequestRepository

class ServiceContainer(Connectable):
    """
    Container class that manages service instances using magic-di.
    
    This container:
    1. Configures which interfaces map to which implementations
    2. Manages the lifecycle of our services
    3. Provides a clean interface for accessing services
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self._injector = DependencyInjector()
        # Bind interfaces to their implementations
        self._injector.bind({
            IEmailService: GmailService,
            IPaymentRequestRepository: GoogleSheetsPaymentRequestRepository,
            IVenmoService: VenmoAPIService
        })

    async def __connect__(self):
        """Initialize all services through the injector"""
        await self._injector.connect()

    async def __disconnect__(self):
        """Cleanup all services through the injector"""
        await self._injector.disconnect()

    @property
    def email_service(self) -> IEmailService:
        """Get the email service instance with email config"""
        return self._injector.inject(IEmailService)(self.config.email)

    @property
    def payment_request_repository(self) -> IPaymentRequestRepository:
        """Get the payment request repository instance with sheets config"""
        return self._injector.inject(IPaymentRequestRepository)(self.config.google_sheets)
        
    @property
    def venmo_service(self) -> IVenmoService:
        """Get the Venmo service instance with Venmo config"""
        return self._injector.inject(IVenmoService)(self.config.venmo) 