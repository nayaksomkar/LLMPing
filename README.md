# LLMPing

Test LLM providers (Mistral, Groq, Google, Cerebras) via CLI or API server.

## How it works

You create two files — `config.json` (which providers/models to test) and `.env` (API keys). The Docker image reads them and calls the LLMs.

## Quick start in any project

```
your-project/
├── config.json     <-- list providers + models here
└── .env            <-- put API keys here
```

**config.json:**
```json
{
  "defaultProvider": "mistral",
  "defaultModel": "mistral-small-latest",
  "providerModels": [
    ["mistral", "mistral-small-latest"],
    ["groq", "llama-3.1-8b-instant"]
  ]
}
```

**.env:**
```
MISTRAL_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=
CEREBRAS_API_KEY=
```

---

## Use as CLI (one-shot)

```bash
docker run --rm \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/.env:/app/.env \
  llmping --prompt "Say hello"
```

Output:
```json
{
  "prompt": "Say hello",
  "results": [
    { "provider": "mistral", "model": "mistral-small-latest", "ok": true, "text": "Hello!", "status": "OK", "error": null },
    { "provider": "groq", "model": "llama-3.1-8b-instant", "ok": true, "text": "Hi there!", "status": "OK", "error": null }
  ]
}
```

## Use as API server

```bash
# Start server
docker run --rm -d -p 8000:8000 \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/.env:/app/.env \
  --name llmping-server llmping

# Show help
docker run --rm llmping --help

# --- 3 parameters you can send ---
#   prompt    = the text to ask the LLM
#   provider  = which provider to use (from config.json)
#   model     = which model to use (from config.json)

# Test all providers from config.json
curl "http://localhost:8000/ping?prompt=hello"

# Test one specific provider (uses its default model)
curl "http://localhost:8000/ping?prompt=hello&provider=mistral"

# Test specific provider + specific model
curl "http://localhost:8000/ping?prompt=hello&provider=mistral&model=mistral-small-latest"

# POST version — same thing with JSON body
curl -X POST http://localhost:8000/ping \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me a joke", "provider": "mistral", "model": "mistral-small-latest"}'

# Health check
curl http://localhost:8000/

# Stop it
docker stop llmping-server
```

## First time? Build the image

```bash
git clone https://github.com/nayaksomkar/LLMPing.git
cd LLMPing
docker build -t llmping .
```

Then use the commands above in any project.

## Response format

| Field | Meaning |
|-------|---------|
| `ok` | `true` if the call worked |
| `text` | The LLM's reply |
| `status` | `"OK"` or `"FAILED"` |
| `error` | Error message (null if ok) |
