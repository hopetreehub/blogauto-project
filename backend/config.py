import os
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable loading"""
    
    # JWT Settings
    secret_key: str = Field(default="your-secret-key-change-this-in-production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 30
    
    # AI API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    
    # Keyword Analysis APIs
    semrush_api_key: Optional[str] = Field(default=None, env="SEMRUSH_API_KEY")
    ahrefs_api_key: Optional[str] = Field(default=None, env="AHREFS_API_KEY")
    google_ads_developer_token: Optional[str] = Field(default=None, env="GOOGLE_ADS_DEVELOPER_TOKEN")
    google_ads_client_id: Optional[str] = Field(default=None, env="GOOGLE_ADS_CLIENT_ID")
    google_ads_client_secret: Optional[str] = Field(default=None, env="GOOGLE_ADS_CLIENT_SECRET")
    google_ads_refresh_token: Optional[str] = Field(default=None, env="GOOGLE_ADS_REFRESH_TOKEN")
    
    # Database
    database_url: str = Field(default="sqlite:///./blogauto.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # AWS
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # Development
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Rate Limits
    openai_max_requests_per_minute: int = 60
    gemini_max_requests_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    def is_ai_configured(self) -> bool:
        """Check if at least one AI service is configured"""
        return bool(self.openai_api_key or self.gemini_api_key)
    
    def is_keyword_analysis_configured(self) -> bool:
        """Check if keyword analysis services are configured"""
        return bool(self.semrush_api_key or self.ahrefs_api_key or self.google_ads_developer_token)
    
    def get_available_ai_services(self) -> list[str]:
        """Get list of available AI services"""
        services = []
        if self.openai_api_key:
            services.append("openai")
        if self.gemini_api_key:
            services.append("gemini")
        return services

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()

# Global settings instance
settings = get_settings()