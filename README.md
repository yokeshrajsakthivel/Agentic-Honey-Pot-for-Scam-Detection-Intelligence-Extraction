# Agentic Honeypot (Scam Detection & Intelligence Extraction)

A production-ready, high-performance REST API built with FastAPI, specifically designed for the Agentic Honeypot Hackathon.

## Features
- **Scam Detection**: Real-time classification using lightweight Transformers (`all-MiniLM-L6-v2`).
- **AI Persona**: Integrated LLM chat agent ("Grandma Betsy") to engage scammers.
- **Intelligence Extraction**: Extracts UPI IDs, URLs, Phone Numbers, and Keywords using spaCy.
- **Async & Fast**: Built on FastAPI with concurrent execution of AI tasks.
- **Docker Ready**: One-command deployment.

## Quick Start

### 1. Set API Keys
Update `app/core/config.py` or set via Environment Variables:
- `LLM_API_KEY`: Your key for Groq/Mistral/OpenAI.
- `LLM_BASE_URL`: Base URL for the LLM provider.

### 2. Build & Run
```bash
docker build -t honeypot .
docker run -p 8000:8000 honeypot
```

### 3. API Usage
POST `/message`
Header: `x-api-key: hackathon-secret-key`
Payload:
```json
{
  "sessionId": "12345",
  "message": "Verify your bank account now!",
  "conversationHistory": [],
  "metadata": {}
}
```

See `walkthrough.md` for more details.
