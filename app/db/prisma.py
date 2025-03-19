from prisma import Prisma
from functools import lru_cache
import asyncio
from contextlib import asynccontextmanager

prisma = Prisma()
connection_lock = asyncio.Lock()
is_connected = False

async def ensure_connection():
    global is_connected
    async with connection_lock:
        if not is_connected:
            try:
                await prisma.connect()
                is_connected = True
                print("Conexão com o banco de dados estabelecida")
            except Exception as e:
                if "Already connected" in str(e):
                    is_connected = True
                    print("Conexão já existente, continuando...")
                    return
                print(f"Erro de conexão: {str(e)}")
                raise e

@asynccontextmanager
async def get_db():
    await ensure_connection()
    try:
        yield prisma
    finally:
        # Não desconectamos aqui para manter a conexão persistente
        pass

@lru_cache()
def create_prisma():
    return prisma

async def get_prisma():
    await ensure_connection()
    try:
        yield prisma
    except Exception as e:
        print(f"Erro Prisma: {str(e)}")
        raise e