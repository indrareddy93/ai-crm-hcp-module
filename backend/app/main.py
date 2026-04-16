from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import hcps, interactions, chat

settings = get_settings()

app = FastAPI(
    title="AI-First CRM — HCP Module",
    description="Log Interaction API with LangGraph-powered chat agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hcps.router)
app.include_router(interactions.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
