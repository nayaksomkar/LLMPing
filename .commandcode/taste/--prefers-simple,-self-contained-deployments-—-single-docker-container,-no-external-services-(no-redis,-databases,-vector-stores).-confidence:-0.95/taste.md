# - Prefers simple, self-contained deployments — single Docker container, no external services (no Redis, databases, vector stores). Confidence: 0.95
- Prefers simple, self-contained deployments — single Docker container, no external services (no Redis, databases, vector stores). Confidence: 0.95
- Favors in-memory, ephemeral storage over persistent databases for temporary data (sessions, caches). Confidence: 0.9
- Designs for graceful degradation — optional subsystems (e.g., context summarization) should fail silently without breaking the main request flow. Confidence: 0.9
- Prefers provider-agnostic architectures with automatic fallback chains when integrating third-party APIs. Confidence: 0.9
- Separates secrets from configuration: API keys/secrets live in `.env` only, while non-sensitive settings (models, providers, context) are managed in `config.json`. Confidence: 0.85
- Prefers minimal, simple API contracts (e.g., `POST /chat` with `{session_id, query}` → `{session_id, answer}`). Confidence: 0.85
- Values backward compatibility — preserve existing endpoints/functionality when refactoring. Confidence: 0.85
