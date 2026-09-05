# LLMPing FastAPI server — run `python server.py` or use Docker

import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import get_config_value
from lanchainfunc import call_chain
from llm_service import AllProvidersFailed, LLMService

app = FastAPI(title="LLMPing", version="0.3.0")

# --- CORS Configuration ---
# Allowed origins from env (comma-separated) or allow all by default
_allowed_origins = os.getenv("CORS_ORIGINS", "").strip()
if _allowed_origins:
    _origins = [o.strip() for o in _allowed_origins.split(",") if o.strip()]
else:
    _origins = ["*"]  # Allow all origins by default

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the LLM service
llm_service = LLMService()


# --- Request/Response models ---

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None  # Optional - provides context if given


class ChatResponse(BaseModel):
    answer: str
    provider: str
    model: str


class HealthResponse(BaseModel):
    status: str
    configured_providers: list[str]


# --- Main endpoint ---

@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    """Send a query, get an answer. Optional session_id for context."""
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="query is required")

    try:
        return llm_service.chat(body.query, body.session_id or "")
    except AllProvidersFailed as exc:
        raise HTTPException(
            status_code=503,
            detail={"error": "All providers failed", "details": exc.errors},
        )


@app.get("/health", response_model=HealthResponse)
def health():
    """Health check."""
    return {
        "status": "healthy",
        "configured_providers": llm_service.configured_providers(),
    }


# --- Legacy /ping (backward compatible) ---

class PingRequest(BaseModel):
    prompt: str = "Say hello in 5 words or less."
    provider: Optional[str] = None
    model: Optional[str] = None


def get_provider_models(provider: Optional[str], model: Optional[str]) -> list:
    configured = get_config_value("providerModels") or []
    if provider and model:
        return [[provider, model]]
    if provider:
        selected = [e for e in configured if e[0] == provider]
        if not selected:
            raise ValueError(f"No configured model for provider '{provider}'")
        return selected
    if configured:
        return configured
    dp = get_config_value("defaultProvider")
    dm = get_config_value("defaultModel")
    if dp and dm:
        return [[dp, dm]]
    raise ValueError("No provider models configured")


@app.get("/")
def root():
    return {"service": "LLMPing", "status": "running"}


@app.get("/ping")
def ping_get(
    prompt: str = "Say hello in 5 words or less.",
    provider: Optional[str] = None,
    model: Optional[str] = None,
):
    selected = get_provider_models(provider, model)
    results = [call_chain(p, m, prompt) for p, m in selected]
    return {"prompt": prompt, "results": results}


@app.post("/ping")
def ping_post(body: PingRequest):
    selected = get_provider_models(body.provider, body.model)
    results = [call_chain(p, m, body.prompt) for p, m in selected]
    return {"prompt": body.prompt, "results": results}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
