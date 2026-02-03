# 🍯 Agentic Honeypot - Scam Detection & Intelligence Extraction

A state-of-the-art **AI-powered Honeypot API** designed to engage scammers, waste their time, and extract actionable intelligence (UPIs, Bank Details, URLs) while detecting scam intent in real-time.

Built for the **Agentic Honeypot Hackathon**.

---

## 🚀 Features

-   **🤖 Agentic AI Personas**: Dynamically switches between personas (Grandma Betsy, Student Sam, etc.) to keep scammers engaged.
-   **🛡️ Real-time Scam Detection**: Uses `all-MiniLM-L6-v2` embeddings + LLM Hybrids for high-accuracy checks.
-   **🕵️ Intelligence Extraction**: Automatically pulls UPI IDs, Phone Numbers, Crypto Wallets, and URLs from chats.
-   **📡 Automated Reporting**:
    *   **Webhook**: Pushes final reports to a configurable callback URL.
    *   **Dashboard API**: Pulls active session lists and detailed logs on-demand.
-   **🔑 Enterprise Security**: Protected via `x-api-key` header.
-   **⚡ High Performance**: Fully Async FastAPI backend.

---

## 🛠️ Installation

### Prerequisites
-   Python 3.10+
-   [Groq API Key](https://console.groq.com/) (or OpenAI/Mistral)

### 1. Clone & Install
```bash
git clone <repo-url>
cd Honeypot
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file (see `.env.example` if available, or use the one below):
```ini
# Security
API_KEY=hackathon-secret-key

# LLM Provider (Groq Recommended for speed)
LLM_API_KEY=gsk_...
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant

# Reporting
CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

### 3. Run Locally
```bash
uvicorn app.main:app --reload --port 8000
```
*Port 8000 is default, but the system works dynamically if needed.*

---

## 🎮 Interactive Scammer Test

We included a CLI tool to simulate being a scammer talking to the AI.
It **automatically finds** the running server port (8000-8005).

```bash
python interactive_tester.py
```

---

## 🌐 API Endpoints

All endpoints require header: `x-api-key: your-secret-key`

### 1. Chat with Agent
**POST** `/message`
```json
{
  "sessionId": "session-123",
  "message": "Hello, I am calling from your bank.",
  "conversationHistory": []
}
```
**Response**:
```json
{
  "reply": "Oh hello! Is this about my pension?",
  "scam_detected": true,
  "confidence_score": 0.95
}
```

### 2. List Active Traps (Dashboard)
**GET** `/sessions`
*Returns a list of all active sessions and their stats.*

### 3. Get Session Details
**GET** `/session/{sessionId}`
*Returns full logs and extracted intelligence (UPIs, etc.) for a specific session.*

---

## ☁️ Deployment

### Option A: Render (Recommended)
1.  Push code to GitHub.
2.  Go to [Render Dashboard](https://dashboard.render.com).
3.  New -> **Blueprint**.
4.  Connect repo. It will use `render.yaml` to auto-configure.

### Option B: Local Tunnel (ngrok)
```bash
ngrok http 8000
```
Use the provided HTTPS URL.

---

## 📁 Project Structure

-   `app/main.py`: API Entry point & Routes
-   `app/services/chat_agent.py`: LLM Persona Logic
-   `app/services/scam_detector.py`: Scam Scoring Engine
-   `app/services/intelligence.py`: Data Extraction (Regex + LLM)
-   `app/services/callback.py`: Webhook Service
-   `interactive_tester.py`: CLI Testing Tool
