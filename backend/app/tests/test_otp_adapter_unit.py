import pytest
from fastapi import HTTPException
from pathlib import Path
import sys
import asyncio

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.integrations import otp


class _DummyResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class _DummyAsyncClient:
    def __init__(self, response, captured):
        self.response = response
        self.captured = captured

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, data=None, auth=None):
        self.captured["url"] = url
        self.captured["data"] = data
        self.captured["auth"] = auth
        return self.response


# Twilio Verify adapter unit checks with HTTP fixtures only
def test_send_posts_verifications_with_basic_auth(monkeypatch):
    monkeypatch.setattr(otp.config, "OTP_PROVIDER", "twilio")
    monkeypatch.setattr(otp.config, "TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setattr(otp.config, "TWILIO_AUTH_TOKEN", "auth-token")
    monkeypatch.setattr(otp.config, "TWILIO_VERIFY_SERVICE_SID", "VA123")
    monkeypatch.setattr(otp.config, "TWILIO_VERIFY_BASE_URL", "https://verify.twilio.com/v2")

    captured = {}
    response = _DummyResponse(200, {"status": "pending", "sid": "VE123"})
    monkeypatch.setattr(
        otp.httpx,
        "AsyncClient",
        lambda **kwargs: _DummyAsyncClient(response=response, captured=captured),
    )

    result = asyncio.run(otp.TwilioVerifyAdapter().send("+919999999999"))
    assert result["mode"] == "live"
    assert captured["url"].endswith("/Services/VA123/Verifications")
    assert captured["data"] == {"To": "+919999999999", "Channel": "sms"}
    assert captured["auth"] == ("AC123", "auth-token")


def test_check_requires_approved_and_valid_true(monkeypatch):
    monkeypatch.setattr(otp.config, "OTP_PROVIDER", "twilio")
    monkeypatch.setattr(otp.config, "TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setattr(otp.config, "TWILIO_AUTH_TOKEN", "auth-token")
    monkeypatch.setattr(otp.config, "TWILIO_VERIFY_SERVICE_SID", "VA123")

    async def approved(*args, **kwargs):
        return {"status": "approved", "valid": True}

    async def approved_not_valid(*args, **kwargs):
        return {"status": "approved", "valid": False}

    adapter = otp.TwilioVerifyAdapter()
    monkeypatch.setattr(adapter, "_post", approved)
    ok = asyncio.run(adapter.check("+919999999999", "123456", {"verification_sid": "VE1"}))
    assert ok is True

    monkeypatch.setattr(adapter, "_post", approved_not_valid)
    fail = asyncio.run(adapter.check("+919999999999", "123456", {"verification_sid": "VE1"}))
    assert fail is False


def test_missing_twilio_keys_fails_closed_503(monkeypatch):
    monkeypatch.setattr(otp.config, "OTP_PROVIDER", "auto")
    monkeypatch.setattr(otp.config, "TWILIO_ACCOUNT_SID", "")
    monkeypatch.setattr(otp.config, "TWILIO_AUTH_TOKEN", "")
    monkeypatch.setattr(otp.config, "TWILIO_VERIFY_SERVICE_SID", "")

    with pytest.raises(HTTPException) as exc:
        asyncio.run(otp.TwilioVerifyAdapter().send("+919999999999"))
    assert exc.value.status_code == 503


def test_provider_error_never_approves_or_falls_back(monkeypatch):
    monkeypatch.setattr(otp.config, "OTP_PROVIDER", "twilio")
    monkeypatch.setattr(otp.config, "TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setattr(otp.config, "TWILIO_AUTH_TOKEN", "auth-token")
    monkeypatch.setattr(otp.config, "TWILIO_VERIFY_SERVICE_SID", "VA123")

    async def boom(*args, **kwargs):
        raise HTTPException(503, "SMS verification is temporarily unavailable. Please try again.")

    adapter = otp.TwilioVerifyAdapter()
    monkeypatch.setattr(adapter, "_post", boom)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(adapter.check("+919999999999", "123456", {"verification_sid": "VE1"}))
    assert exc.value.status_code == 503


def test_send_rejects_non_pending_twilio_response(monkeypatch):
    monkeypatch.setattr(otp.config, "OTP_PROVIDER", "twilio")
    monkeypatch.setattr(otp.config, "TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setattr(otp.config, "TWILIO_AUTH_TOKEN", "auth-token")
    monkeypatch.setattr(otp.config, "TWILIO_VERIFY_SERVICE_SID", "VA123")

    captured = {}
    response = _DummyResponse(200, {"status": "approved", "sid": "VE123"})
    monkeypatch.setattr(
        otp.httpx,
        "AsyncClient",
        lambda **kwargs: _DummyAsyncClient(response=response, captured=captured),
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(otp.TwilioVerifyAdapter().send("+919999999999"))
    assert exc.value.status_code == 503
