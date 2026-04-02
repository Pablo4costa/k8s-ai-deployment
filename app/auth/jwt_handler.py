from dotenv import load_dotenv
load_dotenv()

import jwt
import os
from datetime import datetime, timedelta
from app.config import settings

def create_token(tenant_name: str, tenant_id: int) -> str:
    payload = {
        "tenant_name": tenant_name,
        "tenant_id": tenant_id,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")