"""
    Esse código é o módulo principal do projeto, responsável por iniciar
todas funcionalidades do sistema.

author: github.com/dreeilima
"""
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from .routes import users, whatsapp, transactions, categories, auth, reports
from fastapi.responses import RedirectResponse
from .db.prisma import create_prisma, is_connected
from .core.config import settings
import uuid
from decimal import Decimal

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

prisma = create_prisma()

app = FastAPI(
    title="FinControl API",
    version="1.0.0"
)

# Configurar encoder personalizado para JSONResponse
app.json_encoder = CustomJSONEncoder

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(categories.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "FinControl API is running"}

@app.head("/")
async def head_root():
    return {"message": "FinControl API is running"}

@app.get("/", include_in_schema=False)
async def redirect():
    return RedirectResponse("/docs#")

@app.on_event("startup")
async def startup():
    try:
        global is_connected
        if not is_connected:
            print("Iniciando conexão com o banco...")
            await prisma.connect()
            is_connected = True
            print("Conexão estabelecida com sucesso")
        print("\n=== CONFIGURAÇÕES ===")
        print(f"WhatsApp URL: {settings.whatsapp_service_url}")
        print(f"WhatsApp Secret Key: {'*' * len(settings.whatsapp_secret_key)}")
        print(f"Env file path: {settings.Config.env_file}")
    except Exception as e:
        if "Already connected" not in str(e):
            print(f"Erro ao conectar: {str(e)}")
            # Não levante a exceção, apenas registre
            print("Continuando mesmo com erro de conexão...")

@app.on_event("shutdown")
async def shutdown():
    prisma = create_prisma()
    if prisma.is_connected():
        await prisma.disconnect()

# Essa função salva a documentação OpenAPI dos dados do FastApi em um JSON
@app.on_event("startup")
def save_openapi_json():
    openapi_data = app.openapi()
    # salva arquivo
    with open("openapi.json", "w") as file:
        json.dump(openapi_data, file)

print("\n=== CONFIGURAÇÕES ===")
print(f"WhatsApp URL: {settings.whatsapp_service_url}")
