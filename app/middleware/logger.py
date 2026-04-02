import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("enterprise-ai-gateway")

def log_request(tenant_name: str, provider: str, model: str, status: str, cost_usd: float = 0):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "tenant": tenant_name,
        "provider": provider,
        "model": model,
        "status": status,
        "cost_usd": cost_usd
    }
    logger.info(json.dumps(log_entry))

def log_error(tenant_name: str, error: str):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "tenant": tenant_name,
        "error": error
    }
    logger.error(json.dumps(log_entry))