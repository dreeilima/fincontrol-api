import uvicorn
from app.services.config import IP, PORT
from app.core.config import settings

if __name__ == "__main__":
    print("\n=== INICIANDO SERVIDOR LOCAL ===")
    print(f"API: http://{IP}:{PORT}")
    print(f"WhatsApp Service: {settings.whatsapp_service_url}\n")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # IP fixo para desenvolvimento local
        port=PORT,
        reload=True
    )
