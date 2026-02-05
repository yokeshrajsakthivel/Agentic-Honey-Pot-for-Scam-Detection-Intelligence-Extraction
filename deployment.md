# 🚀 Deploying Honeypot API Publicly

This guide explains how to expose your Agentic Honeypot API to the internet securely.

## ✅ Security First
Your API is already secured with an API Key.
- **Default Key**: `hackathon-secret-key` (Found in `.env`)
- **Important**: Before going public, change `API_KEY` in `.env` to a strong, random string.

---

## Option 1: Instant Public Access (ngrok)
Best for testing, hackathons, or demos without redeploying.

### 1. Install & Run ngrok
1. Download [ngrok](https://ngrok.com/download).
2. Open a terminal and run your local server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
3. In a **new** terminal window, expose port 8000:
   ```bash
   ngrok http 8000
   ```

### 2. Get Public URL
ngrok will give you a Forwarding URL like:
`https://a1b2-c3d4.ngrok-free.app` -> `http://localhost:8000`

### 3. Use the Public API
Your API is now live!
- **Endpoint**: `https://<your-ngrok-url>/message`
- **Header**: `x-api-key: your-secret-key`

---

## Option 2: Cloud Deployment (Render.com)
Best for permanent hosting (Free Tier available).

1. **Push to GitHub**: specific ensure `Procfile` and `requirements.txt` are committed.
2. **Create Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com/).
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repository.
3. **Configure**:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   - Add `API_KEY`, `LLM_API_KEY`, `LLM_BASE_URL`, etc., in the "Environment" tab.
5. **Deploy**: Click Create Web Service.

You will get a URL like `https://honeypot.onrender.com`.

---

## 🧪 Testing the Public API

**Curl Command:**
```bash
curl -X POST "https://<your-public-url>/message" \
     -H "Content-Type: application/json" \
     -H "x-api-key: hackathon-secret-key" \
     -d '{
           "sessionId": "test-1",
           "message": "Hello!",
           "conversationHistory": [],
           "metadata": {}
         }'
```

---

## Option 3: Docker Deployment 🐳
Host the application anywhere using Docker (VPS, EC2, DigitalOcean).

### 1. Prerequisites
- [Docker Installed](https://www.docker.com/products/docker-desktop/)

### 2. Build the Image
Open a terminal in the project root and run:
```bash
docker build -t agentic-honeypot .
```

### 3. Run the Container
Run the container, exposing port 8000. You need to pass your environment variables.
```bash
docker run -d -p 8000:8000 --name honeypot-api \
  -e API_KEY=hackathon-secret-key \
  -e LLM_API_KEY=your_openai_key \
  -e LLM_BASE_URL=https://api.openai.com/v1 \
  agentic-honeypot
```

### 4. Verify
Check if the container is running:
```bash
docker ps
```
Your API is accessible at `http://localhost:8000`.

### 5. Stop/Remove
```bash
docker stop honeypot-api
docker rm honeypot-api
```

