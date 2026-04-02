from app.proxy.providers import call_provider
from app.middleware.rate_limiter import check_rate_limit
from app.middleware.logger import log_request, log_error
from app.auth.models import log_usage

async def process_request(
    tenant: dict,
    provider: str,
    model: str,
    messages: list
) -> dict:

    # Verificar rate limit
    rate_limit_result = await check_rate_limit(
        tenant_id=tenant["id"],
        limit=tenant["rate_limit"]
    )

    if not rate_limit_result["allowed"]:
        log_error(tenant["name"], f"Rate limit exceeded: {rate_limit_result}")
        raise ValueError(
            f"Rate limit exceeded. Limit: {rate_limit_result['limit']} requests/hour. "
            f"Retry after {rate_limit_result['retry_after_seconds']} seconds."
        )

    # Llamar al provider
    result = await call_provider(provider, messages, model)

    # Loguear uso
    log_request(
        tenant_name=tenant["name"],
        provider=provider,
        model=model,
        status="success",
        cost_usd=result["cost_usd"]
    )

    # Persistir en base de datos
    await log_usage(
        tenant_id=tenant["id"],
        provider=provider,
        model=model,
        prompt_tokens=result["prompt_tokens"],
        completion_tokens=result["completion_tokens"],
        cost_usd=result["cost_usd"]
    )

    # Agregar info de rate limit a la respuesta
    result["rate_limit"] = rate_limit_result

    return result