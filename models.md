# Available Models

## Google Gemini (`google_genai`)

- API key: get it from the Google AI Studio dashboard at https://aistudio.google.com/app/apikey
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-2.5-pro`
- `gemini-2.5-flash-preview`
- `gemini-2.5-pro-preview`
- `gemini-3-flash-preview`
- `gemini-3.5-flash`
- `gemini-3.1-flash-lite`
- `gemini-3.1-pro`
- `gemini-flash-latest`
- `gemini-pro-latest`

## Mistral (`mistral`)

- API key: get it from the Mistral Console at https://console.mistral.ai/api-keys/
- `mistral-small-latest`
- `mistral-medium-latest`
- `mistral-large-latest`
- `codestral-latest`
- `ministral-8b-latest`
- `ministral-3b-latest`
- `mistral-saba-2502`
- `mistral-small-2501`
- `mistral-medium-2505`
- `mistral-large-2411`
- `open-mistral-nemo`

## Groq (`groq`)

- API key: get it from the Groq Console at https://console.groq.com/keys
- `llama-3.1-8b-instant`
- `llama-3.3-70b-versatile`
- `openai/gpt-oss-120b`
- `openai/gpt-oss-20b`
- `meta-llama/llama-4-scout-17b-16e-instruct`
- `meta-llama/llama-4-maverick-17b-128e-instruct`
- `qwen/qwen3-32b`
- `compound`
- `compound-mini`
- `whisper-large-v3`
- `whisper-large-v3-turbo`

## Cerebras (`cerebras`)

- API key: get it from the Cerebras Console at https://cloud.cerebras.ai/
- `gpt-oss-120b`
- `zai-glm-4.7` (preview)
- `gemma-4-31b` (preview)

Note: this project uses the `langchain-openai` adapter to talk to Cerebras by
setting a custom `base_url`. You do not need an OpenAI API key to use Cerebras
here — set `CEREBRAS_API_KEY` in your `.env` instead.
