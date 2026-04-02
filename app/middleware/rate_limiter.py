from dotenv import load_dotenv
load_dotenv()

import redis.asyncio as redis
import os
from app.config import settings

async def get_redis():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)

async def check_rate_limit(tenant_id: int, limit: int) -> dict:
    r = await get_redis()
    key = f"rate_limit:{tenant_id}"

    current = await r.get(key)
    current_count = int(current) if current else 0

    if current_count >= limit:
        ttl = await r.ttl(key)
        await r.aclose()
        return {
            "allowed": False,
            "current": current_count,
            "limit": limit,
            "retry_after_seconds": ttl
        }

    pipe = r.pipeline()
    pipe.incr(key)
    if current_count == 0:
        pipe.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS)
    await pipe.execute()
    await r.aclose()

    return {
        "allowed": True,
        "current": current_count + 1,
        "limit": limit,
        "remaining": limit - current_count - 1
    }