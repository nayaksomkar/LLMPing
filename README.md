# LLMPing

LLMPing is a minimal starter repo for testing LLM providers and building more provider-based functions on top of it.

## What it does

- Reads provider/model settings from `config.json`
- Loads API keys from `.env`
- Sends a prompt to a provider using LangChain
- Returns a JSON-friendly result that can be reused by other functions

## Files

- `config.json`: provider/model pairs and defaults
- `config.py`: config loading and API key lookup
- `lanchainfunc.py`: provider wrapper that returns structured JSON-like output
- `main.py`: simple CLI entry point

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Or with `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Create a `.env` file in the project root (or copy `.env.example` and edit it):

```bash
MISTRAL_API_KEY=your_key_here
GOOGLE_GENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
CEREBRAS_API_KEY=your_key_here
```

Do not commit your real `.env` file.

## Config

Example `config.json`:

```json
{
  "defaultProvider": "mistral",
  "defaultModel": "mistral-small-latest",
  "providerModels": [
    ["google_genai", "gemini-2.5-flash"],
    ["mistral", "mistral-small-latest"],
    ["groq", "llama-3.1-8b-instant"]
  ]
}
```

## Usage

Use `call_chain()` with a provider, model, and prompt. It returns a JSON-friendly dictionary.

```python
from lanchainfunc import call_chain

result = call_chain("mistral", "mistral-small-latest", "Ping")
print(result)
```

Example output:

```json
{
  "provider": "mistral",
  "model": "mistral-small-latest",
  "prompt": "Ping",
  "ok": true,
  "text": "Hello from the model",
  "status": "OK",
  "error": null
}
```

Run the CLI with:

```bash
python main.py --provider mistral --model mistral-small-latest --prompt "Say hello"
```

### Simple examples

- Chatbot-style prompt:

```python
provider = "mistral"
model = "mistral-small-latest"
prompt = "You are a friendly assistant. Reply briefly and warmly."

result = call_chain(provider, model, prompt)
print(result)
```

Example output:

```json
{
  "provider": "mistral",
  "model": "mistral-small-latest",
  "prompt": "You are a friendly assistant. Reply briefly and warmly.",
  "ok": true,
  "text": "Hello! I am here to help.",
  "status": "OK",
  "error": null
}
```

- Creative prompt:

```python
provider = "mistral"
model = "mistral-small-latest"
prompt = "Write a short poem about dinosaurs in 50 words."

result = call_chain(provider, model, prompt)
print(result)
```

Example output:

```json
{
  "provider": "mistral",
  "model": "mistral-small-latest",
  "prompt": "Write a short poem about dinosaurs in 50 words.",
  "ok": true,
  "text": "Ancient giants roamed the earth, their footsteps shaking time. With tails and teeth, they ruled the day, then vanished, leaving only rhyme.",
  "status": "OK",
  "error": null
}
```

## Extend it

This repo is meant to be a starting point. Add more functions by reusing `call_chain()` and extending `lanchainfunc.py` or `config.json`.

## Local tests

Tests are for local development and are not meant to be uploaded to GitHub.

```bash
python -m pytest -q
```
