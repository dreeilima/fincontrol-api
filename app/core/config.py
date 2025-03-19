from decouple import config
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = config('DATABASE_URL', default='postgresql://[seu-user]:[sua-senha]@[seu-host]/[seu-db]')
    
    # WhatsApp
    whatsapp_service_url: str = config('WHATSAPP_SERVICE_URL', default='http://127.0.0.1:3000')
    whatsapp_secret_key: str = config('WHATSAPP_SECRET_KEY', default='fincontrol-whatsapp-key-2024')
    
    # Server
    ip: str = config('ip', default="127.0.0.1")
    port: int = config('port', default=8000, cast=int)
    
    # Token settings
    access_token_expire_minutes: int = config('access_token_expire_minutes', default=30, cast=int)
    reset_token_expire_hours: int = config('reset_token_expire_hours', default=24, cast=int)
    
    # JWT
    secret_key: str = config('SECRET_KEY', default='your-secret-key-here')
    algorithm: str = config('ALGORITHM', default='HS256')

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 
