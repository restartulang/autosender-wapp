from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio
import config

@dataclass
class SendResult:
    success: bool
    http_status: int
    confirm_text: str
    retry_count: int
    error_message: str
    duration_ms: int

class BaseSender(ABC):
    @abstractmethod
    async def send(self, sandi_text: str, log_id: int = 0) -> SendResult:
        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        pass

class TesterSender(BaseSender):
    async def send(self, sandi_text: str, log_id: int = 0) -> SendResult:
        await asyncio.sleep(2)
        return SendResult(
            success=True, 
            http_status=200, 
            confirm_text='[SIMULASI] Berhasil', 
            retry_count=0, 
            error_message='', 
            duration_ms=2000
        )
        
    async def health_check(self) -> bool:
        return True

class PlaywrightSender(BaseSender):
    def __init__(self):
        from automation.playwright_bot import PlaywrightBot
        self.bot = PlaywrightBot()
        
    async def send(self, sandi_text: str, log_id: int = 0) -> SendResult:
        return await self.bot.send(sandi_text, log_id)
        
    async def health_check(self) -> bool:
        return await self.bot.check_login()

class SenderFactory:
    @staticmethod
    def create() -> BaseSender:
        if config.SENDER_MODE == 'playwright':
            return PlaywrightSender()
        return TesterSender()
