"""
Configuration management using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./discord_agents.db",
        description="Database connection URL"
    )
    
    # Discord Bot Configuration
    discord_new_agent_poll_interval: int = Field(
        default=10,
        ge=1,
        le=300,
        description="Seconds between database polls for agent updates"
    )
    discord_max_message_length: int = Field(
        default=2000,
        description="Discord's character limit per message"
    )
    
    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: Literal["text", "json"] = Field(
        default="text",
        description="Log output format"
    )
    log_file: str = Field(
        default="logs/discord_bot.log",
        description="Path to log file"
    )
    log_to_console: bool = Field(
        default=True,
        description="Enable console logging"
    )
    log_to_file: bool = Field(
        default=True,
        description="Enable file logging"
    )
    
    # Application Settings
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    # AI Agent Configuration (Optional)
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for LLM agents"
    )
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for LLM agents"
    )
    
    # Performance Settings
    max_concurrent_bots: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of concurrent bot instances"
    )
    shutdown_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Seconds to wait for graceful shutdown"
    )
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v:
            raise ValueError("Database URL cannot be empty")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
