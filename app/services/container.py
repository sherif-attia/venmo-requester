from typing import Protocol
from magic_di import Connectable, DependencyInjector
from app.models.config import AppConfig
from app.services.email_service import EmailService, GmailService
from app.services.sheets_service import SheetsService, GoogleSheetsService
from app.services.venmo_service import VenmoService, VenmoAPIService

class ServiceContainer(Connectable):
    """Container for managing service instances"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self._injector = DependencyInjector()
        self._injector.bind({
            EmailService: GmailService,
            SheetsService: GoogleSheetsService,
            VenmoService: VenmoAPIService
        })

    async def __connect__(self):
        await self._injector.connect()

    async def __disconnect__(self):
        await self._injector.disconnect()

    @property
    def email_service(self) -> EmailService:
        """Get the email service instance"""
        return self._injector.inject(EmailService)(self.config.email)

    @property
    def sheets_service(self) -> SheetsService:
        """Get the sheets service instance"""
        return self._injector.inject(SheetsService)(self.config.google_sheets)
        
    @property
    def venmo_service(self) -> VenmoService:
        """Get the Venmo service instance"""
        return self._injector.inject(VenmoService)(self.config.venmo) 