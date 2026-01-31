from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Agentic Honeypot API"
    
    # Security
    API_KEY: str = "hackathon-secret-key"  # Change in production
    
    # LLM Settings (Groq / Together / Mistral / OpenAI compatible)
    LLM_API_KEY: str = "insert-your-key-here"
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1" 
    LLM_MODEL: str = "mixtral-8x7b-32768"
    
    # Scam Detection
    SCAM_SCORE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"

settings = Settings()
