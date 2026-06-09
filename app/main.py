from fastapi import FastAPI

from app.routes.api import router as api_router
from app.routes.metrics import router as metrics_router
from app.services.database import init_db


app = FastAPI(
    title="Token Guardian MCP",
    version="0.1.0",
    description="Prompt token, context, and cost observability for MCP clients.",
)

app.include_router(api_router)
app.include_router(metrics_router)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

