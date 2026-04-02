from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.routes import router

load_dotenv()

app = FastAPI(
    title="Enterprise AI Gateway",
    description="Production-ready AI gateway with auth, rate limiting, multi-tenancy and logging",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}