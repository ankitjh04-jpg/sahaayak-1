import io
import uuid
from datetime import date, timedelta

from conftest import API_BASE, auth_headers


def _new_phone() -> str:
    return f"+9198{str(uuid.uuid4().int)[0:8]}"


# OTP policy and identity hardening checks
class TestOtpSecurityContracts:
    def test_otp_unconfigured_returns_503_without_demo_fallback(self, api_client):
        response = api_client.post(
            f"{API_BASE}/auth/otp/request",
            json={"phone": _new_phone(), "language": "en", "name": "QA Farmer"},
        )
        assert response.status_code == 503
        assert "twilio" in response.json()["detail"].lower()

    def test_expert_phone_otp_request_is_blocked(self, api_client, expert_phone):
        response = api_client.post(
            f"{API_BASE}/auth/otp/request",
            json={"phone": expert_phone, "language": "en", "name": "Do Not Escalate"},
        )
        assert response.status_code == 403
        assert "expert sign-in" in response.json()["detail"].lower()

    def test_demo_expert_access_removed(self, api_client):
        response = api_client.post(f"{API_BASE}/auth/demo", json={"role": "expert"})
        assert response.status_code == 403


# Native camera-like image upload and advisory linkage still works for farmer flow
class TestCameraUploadWorkflow:
    @staticmethod
    def _png_bytes():
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDAT\x08\x99c``\x00\x00\x00\x04\x00\x01\x0b\xe7\x02\x9d\x00\x00\x00\x00IEND\xaeB`\x82"
        )

    def test_camera_like_upload_id_used_in_advisory(self, api_client, demo_farmer):
        token = demo_farmer["access_token"]

        field_payload = {
            "name": f"QA Camera Field {uuid.uuid4().hex[:6]}",
            "crop": "Wheat",
            "location": "Ludhiana, Punjab",
            "acreage": 1.8,
            "sowing_date": str(date.today() - timedelta(days=8)),
            "soil_profile": {"ph": 7.0},
            "latitude": 30.9,
            "longitude": 75.8,
        }
        field = api_client.post(
            f"{API_BASE}/fields", json=field_payload, headers=auth_headers(token)
        )
        assert field.status_code == 201
        field_id = field.json()["id"]

        upload = api_client.post(
            f"{API_BASE}/uploads",
            files={"file": ("camera-shot.png", io.BytesIO(self._png_bytes()), "image/png")},
            headers=auth_headers(token),
        )
        assert upload.status_code == 201
        upload_id = upload.json()["id"]

        advisory_create = api_client.post(
            f"{API_BASE}/advisories",
            json={
                "field_id": field_id,
                "query": "Camera upload QA check for advisory body linkage.",
                "input_type": "image",
                "upload_ids": [upload_id],
                "language": "en",
                "idempotency_key": str(uuid.uuid4()),
            },
            headers=auth_headers(token),
        )
        assert advisory_create.status_code == 202
        advisory_id = advisory_create.json()["advisory_id"]

        advisory = api_client.get(
            f"{API_BASE}/advisories/{advisory_id}", headers=auth_headers(token)
        )
        assert advisory.status_code == 200
        payload = advisory.json()
        assert payload["inputs"]["input_type"] == "image"
        assert payload["inputs"]["upload_ids"] == [upload_id]
