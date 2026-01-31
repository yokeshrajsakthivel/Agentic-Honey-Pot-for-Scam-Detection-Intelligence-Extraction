import re
import json
import logging
from typing import Dict, List
from openai import AsyncOpenAI
from app.core.config import settings

class IntelligenceExtractor:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL
        )
        self.system_prompt = (
            "You are an expert Intelligence Extraction AI. "
            "Identify and extract PROPER NOUNS and FINANCIAL DETAILS from the message. "
            "Return a JSON object with the following keys (use empty lists if not found): "
            "1. 'person_names': Names of people (e.g., 'John Smith'). "
            "2. 'bank_names': Names of banks (e.g., 'Chase', 'HDFC'). "
            "3. 'account_numbers': Any banking account numbers (digits). "
            "4. 'ifsc_codes': Bank routing/IFSC codes. "
            "5. 'crypto_wallets': Wallet addresses. "
            "6. 'upi_ids': Payment IDs (e.g. name@bank). "
            "7. 'phone_numbers': Contact numbers. "
            "8. 'urls': Websites/Links. "
            "9. 'entities': Any other proper nouns (Locations, Companies). "
            "Do NOT extract generic words (money, help, call)."
        )

    async def extract(self, text: str) -> Dict[str, List[str]]:
        # Initialize with all keys
        extracted = {
            "upi_ids": [],
            "urls": [],
            "phone_numbers": [],
            "account_numbers": [],
            "ifsc_codes": [],
            "bank_names": [],
            "crypto_wallets": [],
            "person_names": [],
            "entities": []
        }
        
        # 1. Regex (Only for strict technical formats like UPI/URL/Phone)
        # UPI
        extracted["upi_ids"] = re.findall(r"[\w\.\-_]+@[\w]+", text)
        # URL
        extracted["urls"] = re.findall(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", text)
        
        # 2. LLM Extraction (Dynamic & Comprehensive)
        try:
            # Dynamic Prompt for Structured Data
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=200,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            
            # Merge JSON results into extracted dict
            # We iterate over the keys we expect
            for key in extracted.keys():
                if key in data:
                    # Filter for strings only to avoid TypeError
                    items = [str(x) for x in data[key] if isinstance(x, (str, int, float))]
                    extracted[key].extend(items)
            
        except Exception as e:
            logging.error(f"LLM Extraction failed: {e}")
                 
        # Deduplicate all lists
        for k in extracted:
            extracted[k] = list(set(extracted[k]))
            
        return extracted
intelligence_extractor = IntelligenceExtractor()
