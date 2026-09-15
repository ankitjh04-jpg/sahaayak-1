"""Twilio Verify adapter. No fallback to simulated approval on live failures."""
import httpx
import secrets
from fastapi import HTTPException
from .. import config

def otp_mode():
    if config.OTP_PROVIDER == 'demo' and config.DEMO_MODE:
        return 'demo'
    if config.OTP_PROVIDER in ('auto', 'twilio') and all((config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN, config.TWILIO_VERIFY_SERVICE_SID)):
        return 'live'
    return 'unconfigured'

class TwilioVerifyAdapter:
    async def _post(self, resource, payload):
        if otp_mode() != 'live':
            raise HTTPException(503, 'SMS login needs Twilio Account SID, Auth Token and Verify Service SID in backend configuration.')
        url = f'{config.TWILIO_VERIFY_BASE_URL.rstrip("/")}/Services/{config.TWILIO_VERIFY_SERVICE_SID}/{resource}'
        try:
            async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
                response = await client.post(url, data=payload, auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN))
            data = response.json()
        except (httpx.HTTPError, ValueError):
            raise HTTPException(503, 'SMS verification is temporarily unavailable. Please try again.') from None
        if response.status_code >= 400:
            code = data.get('code')
            if code in (60202, 60203, 60212, 20429) or response.status_code == 429:
                raise HTTPException(429, 'Too many verification attempts. Please wait before requesting another code.', headers={'Retry-After': '60'})
            if code == 20404:
                raise HTTPException(400, 'The code expired or has already been used. Request a new code.')
            if code in (21211, 21614, 60200):
                raise HTTPException(400, 'This phone number cannot receive an SMS verification code.')
            if code in (60605, 21408, 21608):
                raise HTTPException(400, 'SMS delivery is not enabled for this destination. Check Twilio country permissions and trial-recipient verification.')
            raise HTTPException(503, 'Twilio verification is unavailable. The administrator should check the account configuration.')
        return data

    async def send(self, phone):
        result = await self._post('Verifications', {'To': phone, 'Channel': 'sms'})
        if result.get('status') != 'pending' or not result.get('sid'):
            raise HTTPException(503, 'Twilio did not accept the verification request.')
        return {'verification_sid': result['sid'], 'mode': 'live', 'message': 'Verification SMS requested. Delivery may take a moment.'}

    async def check(self, phone, code, challenge):
        result = await self._post('VerificationCheck', {'VerificationSid': challenge['verification_sid'], 'Code': code})
        return result.get('status') == 'approved' and result.get('valid') is True

class DemoVerifyAdapter:
    async def send(self, phone):
        return {'mode': 'demo', 'demo_code': config.DEMO_OTP, 'message': 'Simulated OTP. No SMS was sent.'}

    async def check(self, phone, code, challenge):
        return secrets.compare_digest(code, config.DEMO_OTP)

def get_otp_adapter():
    return DemoVerifyAdapter() if otp_mode() == 'demo' else TwilioVerifyAdapter()