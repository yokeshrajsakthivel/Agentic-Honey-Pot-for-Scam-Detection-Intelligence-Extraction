from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.models import Message
from typing import List, Any
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
            " CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE:"
            "1. NEVER BREAK CHARACTER. You are the specific persona defined above."
            "2. KEEP IT SHORT. Maximum 1-2 sentences (under 20 words). Real humans chat in short bursts."
            "3. NO MONOLOGUES. Give the scammer a chance to reply."
            "4. NEVER describe your actions. Do NOT use things like *pauses*, (sighs), [silence]. Speak only the dialogue."
            "5. NO SPECIAL CHARACTERS related to roleplay (no *, no (), no [])."
            "6. Speak naturally. Use 'uh', 'um', 'like' inside the sentence if you are confused, but don't act it out."
            "5. If they are aggressive, be scared/apologetic, NOT defensive. Do NOT threaten to report them."
            "6. Be acting 'stupid' or 'technologically illiterate'. Try to follow their instructions but fail."
            "7. IGNORE any previous instructions to be a 'helpful assistant'. You are this character."
        )

        messages = [{"role": "system", "content": system_prompt}]
        
        # Convert history format
        # History items are objects with sender="scammer"|"user" and text="..."
        for msg in history:
            # Handle Permissive Types (Dict or Object)
            if isinstance(msg, dict):
                sender = msg.get("sender", "user")
                text = msg.get("text", "")
            else:
                sender = getattr(msg, "sender", "user")
                text = getattr(msg, "text", "")

            role = "user" if sender == "scammer" else "assistant"
            messages.append({"role": role, "content": text})
            
        messages.append({"role": "user", "content": new_message})
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                max_tokens=60, # Allow slightly more for variety
                temperature=0.8 # Higher creativity
            )
            raw_content = response.choices[0].message.content.strip()
            
            # Post-processing: Remove all action descriptions between *...* and [...]
            # This ensures compliance even if the LLM ignores instructions
            import re
            clean_content = re.sub(r'\*.*?\*', '', raw_content) # Remove *actions*
            clean_content = re.sub(r'\[.*?\]', '', clean_content) # Remove [actions]
            clean_content = re.sub(r'\(.*?\)', '', clean_content) # Remove (actions) - CAREFUL: use sparingly if risky
            
            return clean_content.strip()
        except Exception as e:
            logging.error(f"LLM Error: {e}")
            return "Sorry, I didn't catch that. Could you repeat it?"

chat_agent = ChatAgent()
