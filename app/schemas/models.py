from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    role: str
    content: str

class Metadata(BaseModel):
    source: Optional[str] = None
    timestamp: Optional[str] = None
    # Add other fields as per hackathon spec if needed

from typing import List, Optional, Dict, Any, Union

class MessageDetail(BaseModel):
    sender: Optional[str] = "scammer"
    text: Optional[str] = ""
    timestamp: Optional[Union[str, int, float]] = None

class IncomingMessage(BaseModel):
    sessionId: Optional[str] = "unknown_session"
    message: Optional[Dict[str, Any]] = None
    conversationHistory: Optional[List[Dict[str, Any]]] = []
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"

class ScamDetectionResult(BaseModel):
    score: float
    is_scam: bool
    confidence: str # "High", "Medium", "Low"

class IntelligenceResult(BaseModel):
    upi_ids: List[str] = []
    urls: List[str] = []
    phone_numbers: List[str] = []
    account_numbers: List[str] = []
    ifsc_codes: List[str] = []
    bank_names: List[str] = []
    crypto_wallets: List[str] = []
    person_names: List[str] = []
    entities: List[str] = [] # Fallback for other orgs/locations
    
class HoneypotResponse(BaseModel):
    status: str = "success"
    reply: str
    scam_detected: bool
    confidence_score: float

class SessionSummary(BaseModel):
    sessionId: str
    message_count: int
    persona: str
    last_active: float

