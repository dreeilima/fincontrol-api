from ..db.prisma import create_prisma, prisma
from fastapi import Depends
import asyncio
from asyncio import sleep

async def ensure_connection():
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Tentativa de conexão {retry_count + 1}/{max_retries}...")
            await prisma.connect()
            print("Conexão estabelecida com sucesso")
            return
        except Exception as e:
            print(f"Erro na tentativa {retry_count + 1}: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                await asyncio.sleep(1)  # Wait 1 second before retrying
                try:
                    await prisma.disconnect()
                except:
                    pass  # Ignore disconnect errors
    
    raise Exception("Failed to connect after maximum retries")

async def get_prisma():
    try:
        await ensure_connection()
        yield create_prisma()
    finally:
        pass  # FastAPI cuida do disconnect