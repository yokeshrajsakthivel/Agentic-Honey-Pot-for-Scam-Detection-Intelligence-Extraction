import httpx
import logging
from typing import Dict, Any

class CallbackService:
    def __init__(self):
        # Load from settings to allow override
        from app.core.config import settings
        self.callback_url = settings.CALLBACK_URL
    
    async def send_final_report(self, session_id: str, intelligence: Dict[str, Any], status: str = "completed", scam_detected: bool = False, message_count: int = 0):
        # Flatten extracted_data if needed, but the requirement basically asks for 
        # specific top-level keys that match the validation error.
        
        payload = {
            "sessionId": session_id,
            "status": status,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": message_count,
            "extractedIntelligence": intelligence, # As per "Field required" loc=["body", "extractedIntelligence"]
            "extracted_data": intelligence, # Keep this for backward compat if needed, or redundancy
            "agentNotes": f"Session processed by Agentic Honeypot. Scam Detected: {scam_detected}. Intelligence gathered."
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Fire and forget or await? Usually fire-and-forget for speed, 
                # but let's await with timeout to log errors.
                logging.info(f"Sending callback for session {session_id} to {self.callback_url}")
                response = await client.post(self.callback_url, json=payload, timeout=10.0)
                if response.status_code != 200:
                    logging.error(f"Callback failed: {response.status_code} {response.text}")
                else:
                    logging.info("Callback successful")
            except Exception as e:
                logging.error(f"Callback error: {e}")

callback_service = CallbackService()
