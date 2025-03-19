from fastapi import APIRouter, HTTPException, Depends
from prisma import Prisma
from ..db.prisma import get_prisma
from ..utils.prisma import ensure_connection
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/categories", tags=["categories"])

class CategoryCreate(BaseModel):
    name: str
    type: str
    icon: str | None = None
    color: str | None = None
    user_id: str

@router.post("/")
async def create_category(
    category: CategoryCreate,
    prisma: Prisma = Depends(get_prisma)
):
    try:
        await ensure_connection()
        print(f"\n=== CRIANDO CATEGORIA ===")
        print(f"Dados recebidos: {category}")
        
        # Verificar se já existe
        existing = await prisma.categories.find_first(
            where={
                "user_id": category.user_id,
                "name": category.name
            }
        )
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail="Category already exists"
            )
        
        # Criar categoria
        data = await prisma.categories.create({
            "id": str(uuid.uuid4()),
            "name": category.name,
            "type": category.type,
            "icon": category.icon,
            "color": category.color,
            "user_id": category.user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        return data
        
    except Exception as e:
        print(f"Erro ao criar categoria: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_categories(
    user_id: str,
    type: str | None = None,
    prisma: Prisma = Depends(get_prisma)
):
    try:
        where = {"user_id": user_id}
        if type:
            where["type"] = type
            
        categories = await prisma.categories.find_many(
            where=where,
            order={"name": "asc"}
        )
        return categories
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 