import httpx
import logging
from typing import Dict, Any

class CallbackService:
    CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
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
                logging.info(f"Sending callback for session {session_id}")
                response = await client.post(self.CALLBACK_URL, json=payload, timeout=5.0)
                if response.status_code != 200:
                    logging.error(f"Callback failed: {response.status_code} {response.text}")
                else:
                    logging.info("Callback successful")
            except Exception as e:
                logging.error(f"Callback error: {e}")

callback_service = CallbackService()
