import io
import time
import uuid
import pytest
from datetime import date, timedelta

from conftest import API_BASE, auth_headers


def _png_bytes():
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDAT\x08\x99c``\x00\x00\x00\x04\x00\x01\x0b\xe7\x02\x9d\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def _create_field(api_client, token, suffix="base"):
    payload = {
        "name": f"QA_Field_{suffix}_{uuid.uuid4().hex[:6]}",
        "crop": "Wheat",
        "location": "Ludhiana, Punjab",
        "acreage": 2.5,
        "sowing_date": str(date.today() - timedelta(days=10)),
        "soil_profile": {"ph": 7.1},
        "latitude": 30.914,
        "longitude": 75.801,
    }
    response = api_client.post(
        f"{API_BASE}/fields", json=payload, headers=auth_headers(token)
    )
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == payload["name"]
    return created


def _poll_job(api_client, token, job_id, timeout_s=30):
    started = time.time()
    while time.time() - started < timeout_s:
        response = api_client.get(f"{API_BASE}/jobs/{job_id}", headers=auth_headers(token))
        assert response.status_code == 200
        data = response.json()
        if data["status"] in {"completed", "failed"}:
            return data
        time.sleep(1.0)
    raise AssertionError("Job did not finish in time")


def _poll_advisory(api_client, token, advisory_id, timeout_s=30):
    started = time.time()
    while time.time() - started < timeout_s:
        response = api_client.get(
            f"{API_BASE}/advisories/{advisory_id}", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        if data["status"] in {"pending_review", "verified", "failed", "needs_information"}:
            return data
        time.sleep(1.0)
    raise AssertionError("Advisory did not leave processing state in time")


# Authentication, security contracts, and config exposure checks
class TestAuthAndAccess:
    def test_health_public(self, api_client):
        response = api_client.get(f"{API_BASE}/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["adapters"]["otp"] == "unconfigured"

    def test_me_requires_auth(self, api_client):
        response = api_client.get(f"{API_BASE}/me")
        assert response.status_code == 401
        assert "sign" in response.json()["detail"].lower()

    def test_expert_demo_removed(self, api_client):
        response = api_client.post(f"{API_BASE}/auth/demo", json={"role": "expert"})
        assert response.status_code == 403

    def test_otp_unconfigured_fails_closed(self, api_client):
        response = api_client.post(
            f"{API_BASE}/auth/otp/request",
            json={"phone": f"+9198{str(uuid.uuid4().int)[0:8]}", "language": "en", "name": "QA Farmer"},
        )
        assert response.status_code == 503
        assert "twilio" in response.json()["detail"].lower()

    def test_expert_login_success_and_no_secret_fields(self, api_client, qa_expert_credentials):
        login = api_client.post(
            f"{API_BASE}/auth/expert/login",
            json={"email": qa_expert_credentials["email"], "password": qa_expert_credentials["password"]},
        )
        if login.status_code == 429:
            pytest.skip("Expert login rate-limited in shared preview environment")
        assert login.status_code == 200
        payload = login.json()
        assert payload["user"]["role"] == "expert"
        assert payload["auth_method"] == "expert_password"
        assert "password_hash" not in payload["user"]

        me = api_client.get(f"{API_BASE}/me", headers=auth_headers(payload["access_token"]))
        assert me.status_code == 200
        assert "password_hash" not in me.json()

    def test_expert_login_invalid_credentials_generic_401(self, api_client, qa_expert_credentials):
        wrong_password = api_client.post(
            f"{API_BASE}/auth/expert/login",
            json={"email": qa_expert_credentials["email"], "password": "WrongPassword_123!"},
        )
        if wrong_password.status_code == 429:
            pytest.skip("Expert login rate-limited in shared preview environment")
        assert wrong_password.status_code == 401
        assert "invalid expert email or password" in wrong_password.json()["detail"].lower()

        unknown_email = api_client.post(
            f"{API_BASE}/auth/expert/login",
            json={"email": f"qa-missing-{uuid.uuid4().hex[:8]}@example.com", "password": "WrongPassword_123!"},
        )
        if unknown_email.status_code == 429:
            pytest.skip("Expert login rate-limited in shared preview environment")
        assert unknown_email.status_code == 401
        assert "invalid expert email or password" in unknown_email.json()["detail"].lower()

    def test_public_config_no_private_secrets_and_maps_fallback(self, api_client):
        response = api_client.get(f"{API_BASE}/config")
        assert response.status_code == 200
        payload = response.json()
        assert payload["expert_auth"] == "email_password"
        assert payload["google_maps_browser_key"] == ""
        assert payload["aadhaar_mode"] == "demo_only"
        assert "twilio_auth_token" not in payload
        assert "openweather_api_key" not in payload

    def test_aadhaar_demo_contract_and_extra_payload_rejected(self, api_client):
        ok = api_client.post(f"{API_BASE}/auth/aadhaar/demo", json={})
        assert ok.status_code == 200
        data = ok.json()
        assert data["status"] == "demo_complete"
        assert data["verified"] is False

        bad = api_client.post(
            f"{API_BASE}/auth/aadhaar/demo", json={"aadhaar_number": "111122223333"}
        )
        assert bad.status_code == 422


# Farmer workflow checks for fields, uploads, advisory processing
class TestFarmerFlows:
    def test_field_validation_errors(self, api_client, demo_farmer):
        token = demo_farmer["access_token"]
        base = {
            "name": "QA_Invalid_Field",
            "crop": "Wheat",
            "location": "Ludhiana",
            "acreage": 2,
            "sowing_date": str(date.today() - timedelta(days=1)),
            "soil_profile": {},
            "latitude": None,
            "longitude": None,
        }

        bad_acreage = api_client.post(
            f"{API_BASE}/fields", json={**base, "acreage": -1}, headers=auth_headers(token)
        )
        assert bad_acreage.status_code == 422

        one_coord = api_client.post(
            f"{API_BASE}/fields", json={**base, "latitude": 30.91}, headers=auth_headers(token)
        )
        assert one_coord.status_code == 422

    def test_upload_duplicate_and_advisory_idempotency(self, api_client, demo_farmer):
        token = demo_farmer["access_token"]
        field = _create_field(api_client, token, "advisory")

        first = api_client.post(
            f"{API_BASE}/uploads",
            files={"file": ("leaf.png", io.BytesIO(_png_bytes()), "image/png")},
            headers=auth_headers(token),
        )
        assert first.status_code == 201
        first_data = first.json()

        duplicate = api_client.post(
            f"{API_BASE}/uploads",
            files={"file": ("leaf-copy.png", io.BytesIO(_png_bytes()), "image/png")},
            headers=auth_headers(token),
        )
        assert duplicate.status_code == 201
        assert duplicate.json()["id"] == first_data["id"]

        idem = str(uuid.uuid4())
        payload = {
            "field_id": field["id"],
            "query": "QA wheat leaves yellowing in patches over three days",
            "input_type": "image",
            "upload_ids": [first_data["id"]],
            "language": "en",
            "idempotency_key": idem,
        }
        created = api_client.post(
            f"{API_BASE}/advisories", json=payload, headers=auth_headers(token)
        )
        assert created.status_code == 202

        replay = api_client.post(
            f"{API_BASE}/advisories", json=payload, headers=auth_headers(token)
        )
        assert replay.status_code == 202
        assert replay.json()["advisory_id"] == created.json()["advisory_id"]


# Expert review and in-app farmer notifications checks
class TestExpertReviewNotifications:
    def test_review_creates_farmer_notification_and_owner_protection(
        self, api_client, demo_farmer, qa_expert_session
    ):
        farmer_token = demo_farmer["access_token"]
        expert_token = qa_expert_session["access_token"]

        field = _create_field(api_client, farmer_token, "notify")
        upload = api_client.post(
            f"{API_BASE}/uploads",
            files={"file": ("case.png", io.BytesIO(_png_bytes()), "image/png")},
            headers=auth_headers(farmer_token),
        )
        assert upload.status_code == 201
        upload_id = upload.json()["id"]

        advisory = api_client.post(
            f"{API_BASE}/advisories",
            json={
                "field_id": field["id"],
                "query": "QA case for expert notification review",
                "input_type": "image",
                "upload_ids": [upload_id],
                "language": "en",
                "idempotency_key": str(uuid.uuid4()),
            },
            headers=auth_headers(farmer_token),
        )
        assert advisory.status_code == 202
        advisory_id = advisory.json()["advisory_id"]
        job_id = advisory.json()["job_id"]

        job = _poll_job(api_client, farmer_token, job_id)
        assert job["status"] == "completed"
        done = _poll_advisory(api_client, farmer_token, advisory_id)
        assert done["status"] == "pending_review"

        sources = api_client.get(f"{API_BASE}/knowledge-sources", headers=auth_headers(expert_token))
        assert sources.status_code == 200
        source_id = sources.json()[0]["id"]

        review = api_client.post(
            f"{API_BASE}/expert/cases/{advisory_id}/review",
            json={
                "decision": "validated",
                "recommendation": "Observe spread pattern and consult a local extension officer before treatment.",
                "rationale": "General guidance only, source-backed, non-diagnostic.",
                "source_id": source_id,
            },
            headers=auth_headers(expert_token),
        )
        assert review.status_code == 200

        found = None
        started = time.time()
        while time.time() - started < 20:
            notifications = api_client.get(
                f"{API_BASE}/notifications", headers=auth_headers(farmer_token)
            )
            assert notifications.status_code == 200
            items = notifications.json()["items"]
            found = next((item for item in items if item["advisory_id"] == advisory_id), None)
            if found:
                break
            time.sleep(1.5)
        assert found is not None
        assert found["read_at"] is None

        mark_read = api_client.post(
            f"{API_BASE}/notifications/{found['id']}/read", headers=auth_headers(farmer_token)
        )
        assert mark_read.status_code == 200

        cross_owner = api_client.post(
            f"{API_BASE}/notifications/{found['id']}/read", headers=auth_headers(expert_token)
        )
        assert cross_owner.status_code == 404


# Live weather and validation checks
class TestWeatherApi:
    def test_weather_live_and_validation_cases(self, api_client, demo_farmer):
        token = demo_farmer["access_token"]
        headers = auth_headers(token)

        live = api_client.get(
            f"{API_BASE}/weather?latitude=30.914&longitude=75.801", headers=headers
        )
        assert live.status_code == 200
        payload = live.json()
        assert payload["provider"] in {"Open-Meteo", "OpenWeather"}
        assert payload["temperature"] is None or isinstance(payload["temperature"], (int, float))
        assert payload["status"] in {"live", "cached", "stale", "no_data"}

        one_coord = api_client.get(f"{API_BASE}/weather?latitude=30.914", headers=headers)
        assert one_coord.status_code == 422

        bad_coords = api_client.get(
            f"{API_BASE}/weather?latitude=130&longitude=75", headers=headers
        )
        assert bad_coords.status_code == 422

        missing_field = api_client.get(
            f"{API_BASE}/weather?field_id=missing-{uuid.uuid4().hex[:6]}", headers=headers
        )
        assert missing_field.status_code == 404
