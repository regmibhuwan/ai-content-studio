"""
Configuration management using Pydantic Settings.

Loads environment variables and provides centralized configuration.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable loading."""

    # API Keys
    openai_api_key: str = Field(..., description="OpenAI API key")
    tavily_api_key: str = Field(..., description="Tavily Search API key")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/articles.db",
        description="Database connection URL",
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    debug_mode: bool = Field(default=True, description="Debug mode")

    # LLM Settings
    llm_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    llm_temperature: float = Field(default=0.7, description="LLM temperature")
    max_tokens: int = Field(default=2000, description="Max tokens per request")

    # Image Generation
    image_model: str = Field(default="dall-e-3", description="Image generation model")
    image_size: str = Field(default="1024x1024", description="Generated image size")

    # Application Settings
    app_name: str = Field(default="AI Content Studio", description="Application name")
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Singleton settings object
    """
    return Settings()

