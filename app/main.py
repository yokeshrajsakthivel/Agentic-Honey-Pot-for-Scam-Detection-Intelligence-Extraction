import logging
import time
import asyncio
from fastapi import FastAPI, Header, HTTPException, Depends, BackgroundTasks
from app.core.config import settings
from app.schemas.models import IncomingMessage, HoneypotResponse
from app.services.scam_detector import scam_detector
from app.services.chat_agent import chat_agent
from app.services.intelligence import intelligence_extractor
from app.services.session_manager import session_manager
from app.services.callback import callback_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Dependency for API key
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.post("/message", response_model=HoneypotResponse)
async def handle_message(
    payload: IncomingMessage, 
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    start_time = time.time()
    
    # 0. Normalize Payload (Hackathon Logic Protection)
    # Ensure sessionId is string
    session_id = str(payload.sessionId) if payload.sessionId else "unknown"
    
    # Ensure user_msg_content is extracted safely
    user_msg_content = ""
    if isinstance(payload.message, str):
        user_msg_content = payload.message
    elif hasattr(payload.message, "text") and payload.message.text:
         user_msg_content = payload.message.text
    elif isinstance(payload.message, dict):
         user_msg_content = payload.message.get("text", "")
    
    # Fallback if empty
    if not user_msg_content:
        user_msg_content = "Hello" # Prevent empty string errors in LLM
        logging.warning(f"Empty message content received for session {session_id}")

    logger.info(f"Received message for session {session_id}: {user_msg_content}")
    logger.info(f"Full Payload Raw: {payload.dict()}")

    # 1. Parallel Execution of Services
    # We want to respond fast (<500ms target, though LLM might take 1-2s).
    # We must await the LLM reply for the response.
    # Scam detection and Intelligence extraction can run in parallel.
    
    # Retrieve assigned persona from session
    session = session_manager.get_session(session_id)
    persona = session.get("persona", "elderly") # Fallback to elderly
    
    # Handle optional history (it might be None from permissive schema)
    history_raw = payload.conversationHistory or []
    # Normalize history items to objects if they are dicts (Pydantic might leave them as dicts in Union)
    history = []
    for item in history_raw:
        if isinstance(item, dict):
            # Create object manually or use simple namespace/dict wrapper
            # ChatAgent expects objects with .sender and .text attributes if it's MessageDetail
            # But wait, ChatAgent imports Message from models? No, it uses Any now.
            # Let's just make sure ChatAgent handles dicts too.
            # Actually, easiest is to ensure it's a list of objects or dicts consistent for ChatAgent.
            # Let's pass it as is and update ChatAgent to handle dict access safely?
            # Better: Convert to MessageDetail objects here if possible or just let ChatAgent handle it.
            # Let's convert to simple objects for safety.
            class SimpleMsg:
                sender = item.get("sender", "user")
                text = item.get("text", "")
            history.append(SimpleMsg())
        else:
            history.append(item)
    
    chat_task = asyncio.create_task(chat_agent.generate_reply(history, user_msg_content, persona_key=persona))
    scam_task = asyncio.create_task(scam_detector.predict(user_msg_content))
    # Intelligence is now also an async LLM task
    intel_task = asyncio.create_task(intelligence_extractor.extract(user_msg_content))
    
    # Wait for all
    reply_text, scam_result, intelligence_data = await asyncio.gather(chat_task, scam_task, intel_task)
    
    # 2. Update Session
    session_manager.update_session(session_id, intelligence_data)
    session = session_manager.get_session(session_id)
    
    # 3. Check for Callback Trigger
    # Example rule: After 5 messages, send intelligence OR if scam confidence is high
    if session["message_count"] % 5 == 0 or scam_result.get("scamDetected", False):
        background_tasks.add_task(
            callback_service.send_final_report, 
            session_id, 
            session["intelligence"],
            session["message_count"],
            scam_result.get("scamDetected", False)
        )

    # 4. Construct Response
    processing_time = (time.time() - start_time) * 1000
    logger.info(f"Processed in {processing_time:.2f}ms")
    
    return HoneypotResponse(
        reply=reply_text,
        scam_detected=scam_result.get("scamDetected", False),
        confidence_score=scam_result.get("score", 0.0)
    )

# Add root endpoint for robustness (Hackathon Tester Safe-guard)
@app.post("/", response_model=HoneypotResponse)
async def root_handle_message(
    payload: IncomingMessage, 
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Mirror of /message for testers that forget the path"""
    return await handle_message(payload, background_tasks, api_key)

@app.get("/")
def root_status():
    return {"status": "Agentic Honeypot Active", "info": "Send POST requests to /message"}

from typing import List
from app.schemas.models import SessionSummary

@app.get("/sessions", response_model=List[SessionSummary])
async def list_sessions(api_key: str = Depends(verify_api_key)):
    """List all active honeypot sessions"""
    # This is a direct access to the internal session store.
    # In a real DB, this would be a query.
    # We map the raw dict to the schema.
    sessions = []
    
    # We need to access the private _sessions safely
    # Ideally, session_manager should have a list_sessions() method
    # But for hackathon speed, we'll access the property if possible
    # Let's add a safe method to SessionManager first? 
    # Or just iterate since it's in-memory.
    
    all_data = session_manager._sessions # Accessing protected member for speed
    for sid, data in all_data.items():
        sessions.append(SessionSummary(
            sessionId=sid,
            message_count=data.get("message_count", 0),
            persona=data.get("persona", "unknown"),
            last_active=data.get("last_active", 0.0)
        ))
    return sessions

@app.get("/session/{session_id}")
async def get_session_details(session_id: str, api_key: str = Depends(verify_api_key)):
    """Get full intelligence for a specific session"""
    session = session_manager.get_session(session_id)
    return session

@app.get("/health")
def health_check():
    return {"status": "ok"}
