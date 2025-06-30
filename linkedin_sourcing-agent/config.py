"""
Configuration Module
===================

Manages all configuration settings for the AI Sourcing Agent.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration settings"""

    def __init__(self):
        # API Keys
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
        self.tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
        self.serper_api_key: Optional[str] = os.getenv("SERPER_API_KEY")

        # Application Settings
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.cache_enabled: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.max_suppliers: int = int(os.getenv("MAX_SUPPLIERS", "50"))

        # Database Settings
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/sourcing.db")

        # Cache Settings
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

        # Validate critical settings
        self._validate_config()

    def _validate_config(self):
        """Validate critical configuration settings"""
        if not self.openai_api_key and not self.google_api_key:
            raise ValueError("Either OPENAI_API_KEY or GOOGLE_API_KEY must be set")

        if not self.tavily_api_key and not self.serper_api_key:
            print("Warning: No search API key found. Web search functionality will be limited.")

    @property
    def has_search_api(self) -> bool:
        """Check if search API is available"""
        return bool(self.tavily_api_key or self.serper_api_key)

    @property
    def has_openai(self) -> bool:
        """Check if OpenAI API is available"""
        return bool(self.openai_api_key)

    @property
    def has_google(self) -> bool:
        """Check if Google API is available"""
        return bool(self.google_api_key)
