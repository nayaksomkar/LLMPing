# LLMPing

**One Docker container. Multiple AI projects. Smart context memory.**

Simple LLM API with automatic provider fallback and optional tag-based session memory.

## How it works

```
Query → Tag-based context lookup → Build prompt → Provider fallback → Answer
```

- **No session_id?** Just answers the query.
- **With session_id?** Stores exchanges as `{summary, tags}`, matches tags on new queries for relevant context.
- **Provider fallback:** Auto-tries providers in order until one works.

## Quick start

```bash
# 1. Copy example.env and add your API keys
cp example.env .env

# 2. Build
docker build -t llmping .

# 3. Run
docker run --rm -d -p 8000:8000 --env-file .env --name llmping llmping

# 4. Test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello world"}'
```

## API

### POST /chat — Get an answer

**Simple (no memory):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?"}'
```

**With session memory:**
```bash
# First message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "My name is Alice and I love Python", "session_id": "user-1"}'

# Follow-up (remembers context via tag matching)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What do I love?", "session_id": "user-1"}'
```

**Response:**
```json
{
  "answer": "Python is a programming language...",
  "provider": "google_genai",
  "model": "gemini-2.5-flash"
}
```

### GET /health — Check status

```bash
curl http://localhost:8000/health
```

## Configuration

### .env file (API keys only)

```env
GEMINI_API_KEY=your_key
MISTRAL_API_KEY=your_key
GROQ_API_KEY=your_key
CEREBRAS_API_KEY=your_key
NVIDIA_API_KEY=your_key
```

### config.json (models and settings)

```json
{
  "defaultProvider": "google_genai",
  "defaultModel": "gemini-2.5-flash",
  "providerModels": [
    ["google_genai", "gemini-2.5-flash"],
    ["mistral", "mistral-small-latest"],
    ["groq", "openai/gpt-oss-20b"],
    ["cerebras", "gpt-oss-120b"],
    ["nvidia", "openai/gpt-oss-20b"]
  ],
  "contextProvider": "groq",
  "contextModel": "openai/gpt-oss-20b",
  "sessionTTL": 1800,
  "sessionMaxHistory": 5,
  "providerTimeout": 30
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `providerModels` | - | Provider:model pairs in fallback order |
| `sessionTTL` | 3600 | Seconds before unused entries are cleaned (1 hour) |
| `sessionMaxHistory` | 20 | Max entries stored per session |
| `providerTimeout` | 30 | Seconds before trying next provider |

## How session memory works (simple explanation)

Think of it like **matching keywords** between what you're asking now and what you asked before.

**How tags work:**
- Tags are just important words from your query (like `python`, `resume`, `dinosaur`)
- Common words like "the", "is", "what" are ignored

**Example:**

| You said earlier | Stored as |
|------------------|-----------|
| "I love Python programming" | Summary: "Q: I love Python... \| A: ..."<br>Tags: `{love, python, programming}` |
| "Help with my resume" | Summary: "Q: Help with resume... \| A: ..."<br>Tags: `{help, resume}` |

**Now you ask:** "What programming language do I like?"

| Query tags | Match against stored | Result |
|------------|---------------------|--------|
| `{programming, language, like}` | "I love Python" has `{programming, love}` | 2 matches ✓ |
| | "Help with resume" has `{}` | 0 matches ✗ |

**Result:** Uses the Python exchange as context, ignores the resume one.

**The more tags match, the more relevant it is.**

This way:
- Resume questions get resume context
- Python questions get Python context
- No mixing between unrelated topics

**Auto-cleanup:** If you don't use a session for 1 hour, old entries get deleted to save memory.

## Provider fallback

```
Try Google → fails? → Try Mistral → fails? → Try Groq → ... → Success!
```

Response tells you which provider handled the request.

## Docker commands

```bash
# Build
docker build -t llmping .

# Run
docker run --rm -d -p 8000:8000 --env-file .env --name llmping llmping

# Stop
docker stop llmping

# View logs
docker logs llmping

# Restart after code changes
docker stop llmping && docker build -t llmping . && docker run --rm -d -p 8000:8000 --env-file .env --name llmping llmping
```

## Provider API keys

| Provider | Get key at |
|----------|------------|
| Google Gemini | https://aistudio.google.com/app/apikey |
| Mistral | https://console.mistral.ai/api-keys/ |
| Groq | https://console.groq.com/keys |
| Cerebras | https://cloud.cerebras.ai/ |
| NVIDIA | https://integrate.nvidia.com/ |

## Two ways to use the API

### `/chat` — For your app or UI (fast, smart fallback)

**What it does:** Sends your query to providers one by one until one succeeds. Returns immediately when a provider works.

**Use this when:** Building an app, chatbot, or anything users interact with.

```bash
# Test /chat (stops at first working provider)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello"}'

# With session memory (remembers context)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello", "session_id": "user-1"}'
```

**Response size:** Casual/small queries → short answers. Complex/longer queries → detailed answers. LLM decides based on query.

**Response:**
```json
{
  "answer": "Hello! How can I help?",
  "provider": "google_genai",
  "model": "gemini-2.5-flash"
}
```

---

### `/ping` — For testing providers (checks all)

**What it does:** Sends your query to ALL configured providers and shows which ones work and which fail.

**Use this when:** Setting up API keys, debugging issues, checking which providers are active.

```bash
# Test all providers at once
curl "http://localhost:8000/ping?prompt=hello" 

# Test only one provider
curl "http://localhost:8000/ping?prompt=hello&provider=google_genai"

# POST version
curl -X POST http://localhost:8000/ping \
  -H "Content-Type: application/json" \
  -d '{"prompt": "hello", "provider": "groq", "model": "openai/gpt-oss-20b"}'
```

**Response:** Shows `ok: true/fail` for each provider with error details.
