# LLMPing FastAPI server — run `python server.py` or use Docker

from typing import Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn

from config import get_config_value
from lanchainfunc import call_chain

app = FastAPI(title="LLMPing", version="0.1.0")

# Request body for POST /ping
class PingRequest(BaseModel):
    prompt: str = "Say hello in 5 words or less."
    provider: Optional[str] = None
    model: Optional[str] = None

# Resolve which provider/model pairs to test
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
    prompt: str = Query("Say hello in 5 words or less."),
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
