"""Credential-free adapters. No observed agricultural values are invented."""
from typing import Protocol
from pathlib import Path
from ..config import STORAGE_ROOT, DEMO_OTP
class OtpAdapter(Protocol):
    async def send(self, phone: str) -> dict: ...
class DemoOtpAdapter:
    async def send(self, phone):
        return {'mode': 'simulated', 'demo_code': DEMO_OTP, 'message': 'Simulated OTP. No SMS was sent.'}
class VisionAdapter(Protocol):
    async def detect(self, upload_ids: list[str]) -> dict: ...
class NoDataVisionAdapter:
    async def detect(self, upload_ids):
        return {'status': 'unavailable', 'mode': 'demo', 'disease': None, 'confidence': None, 'reason': 'Vision is not connected. Uploaded images have not been diagnosed.'}
class WeatherAdapter(Protocol):
    async def get(self, location: str) -> dict: ...
class NoDataWeatherAdapter:
    async def get(self, location):
        return {'status': 'no_data', 'location': location, 'temperature': None, 'rainfall': None, 'observed_at': None, 'stale': False, 'reason': 'No live weather provider is connected.'}
class TranscriptionAdapter(Protocol):
    async def transcribe(self, upload_ids: list[str], language: str) -> dict: ...
class DisabledTranscriptionAdapter:
    async def transcribe(self, upload_ids, language):
        return {'status': 'unavailable', 'transcript': None, 'language': language, 'mode': 'demo', 'reason': 'No speech provider is connected. Please add a typed description.'}
class WhatsAppAdapter(Protocol):
    async def send(self, job: dict) -> dict: ...
class DemoWhatsAppAdapter:
    async def send(self, job):
        return {'delivered': False, 'mode': 'simulated', 'provider_error': 'DEMO_NO_DELIVERY', 'retryable': job['retries'] < 2}
class ObjectStore(Protocol):
    async def put(self, key: str, data: bytes) -> None: ...
    def path(self, key: str) -> Path: ...
class LocalPrivateObjectStore:
    """Demo-only disk adapter; never exposed as a public directory."""
    def path(self, key):
        target = (STORAGE_ROOT / key).resolve()
        if target.parent != STORAGE_ROOT: raise ValueError('Invalid storage key')
        return target
    async def put(self, key, data):
        import asyncio
        STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(self.path(key).write_bytes, data)
otp_adapter = DemoOtpAdapter()
vision_adapter = NoDataVisionAdapter()
weather_adapter = NoDataWeatherAdapter()
transcription_adapter = DisabledTranscriptionAdapter()
whatsapp_adapter = DemoWhatsAppAdapter()
object_store = LocalPrivateObjectStore()