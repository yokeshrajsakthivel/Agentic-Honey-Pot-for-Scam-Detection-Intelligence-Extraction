from sentence_transformers import SentenceTransformer, util
import torch
from app.core.config import settings
import logging
from openai import AsyncOpenAI
import json

# Basic scam phrases to compare against if model is not enough, 
# or use zero-shot classification. For now, embedding similarity to known scam clusters makes sense,
# but a fine-tuned classifier is better. 
# For hackathon: Use Zero-Shot Classification or simple keyword + sentiment + specific known scam patterns.
# BETTER APPROACH: Use a specialized classifier or simple heuristics with embeddings.

class ScamDetector:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL
        )
        self.system_prompt = (
            "You are a Scam Detection AI. Analyze the user's message. "
            "Determine if it has scam intent (phishing, financial fraud, urgency, asking for sensitive info). "
            "Return ONLY a JSON object with keys: "
            "'score' (float 0.0-1.0), 'scamDetected' (boolean), 'reason' (string). "
            "Example: {\"score\": 0.95, \"scamDetected\": true, \"reason\": \"Asked for bank details\"}."
        )
        # Lazy load model
        self.model = None

    def get_model(self):
        if self.model is None:
            logging.info("Lazy loading SentenceTransformer model...")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        return self.model

    async def predict(self, text: str):
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=100,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logging.error(f"Scam Detection Error: {e}")
            # Fail safe
            return {"score": 0.0, "scamDetected": False, "reason": "Error during analysis"}

scam_detector = ScamDetector()
