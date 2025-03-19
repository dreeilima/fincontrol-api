from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

# Criar engine assíncrona
engine = create_async_engine(settings.database_url)

# Criar fábrica de sessões assíncronas
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Função para obter sessão do banco
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close() 