from dotenv import load_dotenv
load_dotenv()

import asyncpg
import os
from datetime import datetime

async def get_connection():
    return await asyncpg.connect(os.getenv("DATABASE_URL"))

async def setup_database():
    conn = await get_connection()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            api_key TEXT NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT TRUE,
            rate_limit INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_logs (
            id SERIAL PRIMARY KEY,
            tenant_id INTEGER REFERENCES tenants(id),
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt_tokens INTEGER DEFAULT 0,
            completion_tokens INTEGER DEFAULT 0,
            cost_usd FLOAT DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    # Crear tenant de prueba
    await conn.execute("""
        INSERT INTO tenants (name, api_key, rate_limit)
        VALUES ('demo-tenant', 'demo-key-12345', 100)
        ON CONFLICT (name) DO NOTHING
    """)
    await conn.close()

async def get_tenant_by_key(api_key: str) -> dict:
    conn = await get_connection()
    row = await conn.fetchrow(
        "SELECT * FROM tenants WHERE api_key = $1 AND is_active = TRUE",
        api_key
    )
    await conn.close()
    return dict(row) if row else None

async def log_usage(tenant_id: int, provider: str, model: str,
                    prompt_tokens: int, completion_tokens: int, cost_usd: float):
    conn = await get_connection()
    await conn.execute("""
        INSERT INTO usage_logs (tenant_id, provider, model, prompt_tokens, completion_tokens, cost_usd)
        VALUES ($1, $2, $3, $4, $5, $6)
    """, tenant_id, provider, model, prompt_tokens, completion_tokens, cost_usd)
    await conn.close()