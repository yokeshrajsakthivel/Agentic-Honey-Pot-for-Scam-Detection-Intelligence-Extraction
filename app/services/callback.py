import httpx
import logging
from typing import Dict, Any

class CallbackService:
    def __init__(self):
        # Load from settings to allow override
        from app.core.config import settings
        self.callback_url = settings.CALLBACK_URL
    
    async def send_final_report(self, session_id: str, intelligence: Dict[str, Any], status: str = "completed"):
        payload = {
            "sessionId": session_id,
            "status": status,
            "extracted_data": intelligence
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Fire and forget or await? Usually fire-and-forget for speed, 
                # but let's await with timeout to log errors.
                logging.info(f"Sending callback for session {session_id} to {self.callback_url}")
                response = await client.post(self.callback_url, json=payload, timeout=5.0)
                if response.status_code != 200:
                    logging.error(f"Callback failed: {response.status_code} {response.text}")
                else:
                    logging.info("Callback successful")
            except Exception as e:
                logging.error(f"Callback error: {e}")

callback_service = CallbackService()
