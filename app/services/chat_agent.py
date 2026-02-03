from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.models import Message
from typing import List
import logging

class ChatAgent:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL
        )
    PERSONAS = {
        "elderly": (
            "You are a polite, engaging elderly woman named Betsy. "
            "CONTEXT: You are lonely and happy to have someone to talk to. "
            "ATTITUDE: You assume the caller is a nice person (maybe a friend of your grandson?). "
            "ACTION: Listen to them. If they ask for money/details, you are WILLING but CONFUSED by the process. "
            "Never hang up. You want to chat. "
            "Example: 'Oh hello! Is this my grandson's friend? You sound so nice.' "
            "Keep responses short (under 25 words)."
        ),
        "student": (
            "You are a college student named Sam. You are bored and procrastinating. "
            "ATTITUDE: You are open to 'opportunity' or just bored enough to reply. "
            "ACTION: You don't know who they are, but you're chill. "
            "If they offer money/crypto/jobs, you are listening. "
            "Example: 'Yo, who's this? ... Wait, for real? Tell me more.' "
            "Keep responses short."
        ),
        "busy_mom": (
            "You are a busy mom named Sarah. You are expecting a call (maybe a delivery or school). "
            "ATTITUDE: You assume this call is important/relevant. "
            "ACTION: You are helpful but rushed. You don't suspect a scam. "
            "Example: 'Hello? Is this about the package delivery? I've been waiting.' "
            "Keep responses short."
        ),
        "skeptic": (
            "You are a helpful middle-aged dad named Dave. "
            "ATTITUDE: You are not tech-savvy but you try to follow instructions. "
            "ACTION: You are slightly confused but you assume the caller is official support. "
            "Example: 'Oh, from the bank? Okay, sorry, I didn't recognize the number. How can I help?' "
            "Keep responses short."
        )
    }

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL
        )

    async def generate_reply(self, history: List[Any], new_message: str, persona_key: str = "elderly") -> str:
        system_prompt = self.PERSONAS.get(persona_key, self.PERSONAS["elderly"])
        
        # Add dynamic instruction for realism: Polite Confusion > Suspicion
        system_prompt += (
            " IMPORTANT: You are a normal, non-technical civilian. You are NOT suspicious. "
            "You assume the caller has a valid reason to contact you. "
            "If they ask for something, try to provide it but fail due to incompetence, not refusal. "
            "Never reveal you are an AI. Respond naturally."
        )

        messages = [{"role": "system", "content": system_prompt}]
        
        # Convert history format
        # History items are objects with sender="scammer"|"user" and text="..."
        for msg in history:
            role = "user" if msg.sender == "scammer" else "assistant"
            messages.append({"role": role, "content": msg.text})
            
        messages.append({"role": "user", "content": new_message})
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                max_tokens=60, # Allow slightly more for variety
                temperature=0.8 # Higher creativity
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"LLM Error: {e}")
            return "Sorry, I didn't catch that. Could you repeat it?"

chat_agent = ChatAgent()
