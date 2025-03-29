from decouple import config
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = config('DATABASE_URL')
    
    # WhatsApp
    whatsapp_service_url: str = config('whatsapp_service_url')
    whatsapp_secret_key: str = config('whatsapp_secret_key')
    
    # Server
    ip: str = config('ip')
    port: int = config('port', cast=int)
    
    # Token settings
    access_token_expire_minutes: int = config('access_token_expire_minutes', cast=int)
    reset_token_expire_hours: int = config('reset_token_expire_hours', cast=int)
    
    # Security
    secret_key: str = config('SECRET_KEY')
    algorithm: str = config('ALGORITHM')
    
    # Webhook
    webhook_url: str = config('WEBHOOK_URL')
    
    # Environment
    environment: str = config('ENVIRONMENT', default='development')
    debug: bool = config('DEBUG', default=False, cast=bool)

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 
