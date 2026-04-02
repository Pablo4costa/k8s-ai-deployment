from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import os

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def call_openai(messages: list, model: str = "gpt-4o-mini") -> dict:
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages
    )
    return {
        "content": response.choices[0].message.content,
        "model": model,
        "provider": "openai",
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "cost_usd": (response.usage.prompt_tokens * 0.00000015) +
                    (response.usage.completion_tokens * 0.0000006)
    }

PROVIDERS = {
    "openai": call_openai,
}

async def call_provider(provider: str, messages: list, model: str) -> dict:
    if provider not in PROVIDERS:
        raise ValueError(f"Provider '{provider}' not supported. Available: {list(PROVIDERS.keys())}")
    return await PROVIDERS[provider](messages, model)