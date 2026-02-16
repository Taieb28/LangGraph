
# Render Dashboard → Service → Environment → Environment Variables

# Architecture

Telegram User
   │
   ▼
Telegram Bot
   │  (Webhook)
   ▼
Render Server (FastAPI)
   │
   ▼
LangGraph Agent (Gemini + Tool)
   │
   ▼
Response → Telegram → User
