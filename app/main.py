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
    session_id = payload.sessionId
    user_msg_content = payload.message
    
    logger.info(f"Received message for session {session_id}: {user_msg_content}")

    # 1. Parallel Execution of Services
    # We want to respond fast (<500ms target, though LLM might take 1-2s).
    # We must await the LLM reply for the response.
    # Scam detection and Intelligence extraction can run in parallel.
    
    # Retrieve assigned persona from session
    session = session_manager.get_session(session_id)
    persona = session.get("persona", "elderly") # Fallback to elderly
    
    chat_task = asyncio.create_task(chat_agent.generate_reply(payload.conversationHistory, user_msg_content, persona_key=persona))
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
            session["intelligence"]
        )

    # 4. Construct Response
    processing_time = (time.time() - start_time) * 1000
    logger.info(f"Processed in {processing_time:.2f}ms")
    
    return HoneypotResponse(
        reply=reply_text,
        scam_detected=scam_result.get("scamDetected", False),
        confidence_score=scam_result.get("score", 0.0)
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}
