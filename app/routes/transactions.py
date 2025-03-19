from fastapi import APIRouter, Depends, HTTPException, Header
from prisma import Prisma
from app.schemas.transactions import TransactionOut, TransactionCreate
from app.utils.prisma import get_prisma, ensure_connection
from datetime import datetime
import uuid
from decimal import Decimal

router = APIRouter()

@router.get("/user/{user_id}", response_model=list[TransactionOut])
async def get_user_transactions(
    user_id: str,
    prisma: Prisma = Depends(get_prisma)
):
    try:
        return await prisma.transactions.find_many(
            where={"user_id": user_id},
            order={"date": "desc"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/expense", response_model=TransactionOut)
async def create_expense(
    transaction: TransactionCreate,
    user_id: str = Header(..., alias="user-id"),
    prisma: Prisma = Depends(get_prisma)
):
    print("\n=== CRIANDO DESPESA ===")
    print("User ID:", user_id)
    print("Dados da transação:", transaction)
    print("Campos da transação:", transaction.dict().keys())
    print("Headers recebidos:", user_id)
    try:
        await ensure_connection()
        transaction_data = transaction.dict()
        print("\nDados recebidos:", transaction_data)
        
        transaction_data["user_id"] = user_id  # Manter como string
        print("User ID:", transaction_data["user_id"])
        
        transaction_data["type"] = "EXPENSE"
        transaction_data["id"] = str(uuid.uuid4())
        transaction_data["created_at"] = datetime.utcnow()
        transaction_data["updated_at"] = datetime.utcnow()
        
        # Converter amount para Decimal
        if isinstance(transaction_data["amount"], (int, float)):
            transaction_data["amount"] = Decimal(str(transaction_data["amount"]))
        print("Amount convertido:", transaction_data["amount"])
        
        # Garantir que a data está no formato correto
        if isinstance(transaction_data["date"], str):
            transaction_data["date"] = datetime.fromisoformat(transaction_data["date"].replace("Z", "+00:00"))
        
        print("Dados finais:", transaction_data)
        result = await prisma.transactions.create(data=transaction_data)
        print("Transação criada:", result)
        print("=== FIM DA CRIAÇÃO DE DESPESA ===\n")
        return result
    except Exception as e:
        print("Erro detalhado:", str(e))
        print("Tipo do erro:", type(e))
        print("Dados que causaram o erro:", transaction_data)
        # Mostrar o erro de validação completo
        if hasattr(e, 'errors'):
            print("Erros de validação:", e.errors())
        # Se for erro de validação, retornar mensagem mais amigável
        if hasattr(e, 'errors'):
            error_msg = e.errors()[0].get('msg', str(e))
            raise HTTPException(status_code=422, detail=f"Erro de validação: {error_msg}")
        raise HTTPException(status_code=400, detail=f"Erro ao criar transação: {str(e)}") 