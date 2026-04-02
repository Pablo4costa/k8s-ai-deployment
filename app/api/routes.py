from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from app.auth.models import setup_database, get_tenant_by_key, get_connection
from app.auth.jwt_handler import create_token, decode_token
from app.proxy.router import process_request

router = APIRouter()

class ChatRequest(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    messages: list

class TokenRequest(BaseModel):
    api_key: str

@router.on_event("startup")
async def startup():
    await setup_database()

@router.post("/auth/token")
async def get_token(request: TokenRequest):
    tenant = await get_tenant_by_key(request.api_key)
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API key")
    token = create_token(tenant["name"], tenant["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "tenant": tenant["name"]
    }

@router.post("/chat")
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    tenant = await get_tenant_by_key_by_id(payload["tenant_id"])
    if not tenant:
        raise HTTPException(status_code=401, detail="Tenant not found")

    try:
        result = await process_request(
            tenant=tenant,
            provider=request.provider,
            model=request.model,
            messages=request.messages
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/{tenant_name}")
async def get_usage(tenant_name: str, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    conn = await get_connection()
    rows = await conn.fetch("""
        SELECT provider, model,
               SUM(prompt_tokens) as total_prompt_tokens,
               SUM(completion_tokens) as total_completion_tokens,
               SUM(cost_usd) as total_cost_usd,
               COUNT(*) as total_requests
        FROM usage_logs ul
        JOIN tenants t ON ul.tenant_id = t.id
        WHERE t.name = $1
        GROUP BY provider, model
    """, tenant_name)
    await conn.close()

    return {
        "tenant": tenant_name,
        "usage": [dict(row) for row in rows]
    }

async def get_tenant_by_key_by_id(tenant_id: int) -> dict:
    conn = await get_connection()
    row = await conn.fetchrow(
        "SELECT * FROM tenants WHERE id = $1 AND is_active = TRUE",
        tenant_id
    )
    await conn.close()
    return dict(row) if row else None