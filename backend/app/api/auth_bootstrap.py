"""Bootstrap login helper for demo OTP: valid phone required."""
from .security.auth import session
from ..config import FARMER_PHONE


def bootstrap_farmer_session() -> dict:
    """Return a signed-in farmer session dict from the demo config phone.

    Used by smoke tests that cannot work through the /auth/otp flow.
    """
    from ..db import db
    from .auth import get_or_create
    user = get_or_create(FARMER_PHONE)
    return session(user, auth_method='bootstrap_demo')
