import os
import uuid
import json
import requests
import pytest
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / 'frontend' / '.env')
load_dotenv(Path(__file__).resolve().parents[2] / '.env')


BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API_BASE = f"{BASE_URL}/api/v1"
QA_EXPERT_PATH = Path('/app/test_reports/qa_expert_credentials.json')


@pytest.fixture
def api_client():
    """Shared HTTP client for public API tests."""
    session = requests.Session()
    return session


@pytest.fixture
def unique_phone():
    """Generate a unique E.164-compatible demo phone number."""
    return f"+9199{str(uuid.uuid4().int)[0:8]}"


@pytest.fixture
def demo_farmer(api_client):
    """Create farmer session through demo endpoint."""
    response = api_client.post(f"{API_BASE}/auth/demo", json={"role": "farmer"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "farmer"
    return data


@pytest.fixture
def qa_expert_credentials():
    """Read QA-only expert credentials created before test execution."""
    if not QA_EXPERT_PATH.exists():
        pytest.skip('QA expert credentials are missing; run provisioning script first')
    data = json.loads(QA_EXPERT_PATH.read_text())
    if not data.get('email') or not data.get('password'):
        pytest.skip('QA expert credentials file is invalid')
    return data


@pytest.fixture
def qa_expert_session(api_client, qa_expert_credentials):
    """Create authenticated expert session using admin-provisioned QA identity."""
    response = api_client.post(
        f"{API_BASE}/auth/expert/login",
        json={"email": qa_expert_credentials['email'], "password": qa_expert_credentials['password']},
    )
    if response.status_code == 429:
        pytest.skip('Expert login rate-limited in shared preview environment')
    assert response.status_code == 200
    data = response.json()
    assert data['user']['role'] == 'expert'
    assert data['auth_method'] == 'expert_password'
    return data


@pytest.fixture
def expert_phone():
    value = os.environ.get('DEMO_EXPERT_PHONE')
    if not value:
        pytest.skip('DEMO_EXPERT_PHONE not configured')
    return value


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}