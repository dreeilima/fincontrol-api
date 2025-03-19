from fastapi import APIRouter, HTTPException, Depends, Body, Request, Form
from ..db.models import UserCreate, UserOut, UserUpdate, ProfileCreate, ProfileOut
from ..db.prisma import get_prisma
from prisma import Prisma
from ..utils.prisma import ensure_connection
import uuid
from datetime import datetime
from ..core.security import get_password_hash
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: str

@router.get("/phone/{phone}", response_model=UserResponse)
async def get_user_by_phone(
    phone: str,
    prisma: Prisma = Depends(get_prisma)
):
    await ensure_connection()
    print(f"Buscando usuário com telefone: {phone}")
    
    try:
        # Buscar usuário com query raw
        result = await prisma.query_raw(
            "SELECT id, email, name, phone FROM users WHERE phone = $1",
            phone.replace("@c.us", "").replace("+", "")
        )
        print("Resultado da query:", result)
        
        if not result or len(result) == 0:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado"
            )
            
        user = result[0]
        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            phone=user["phone"]
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/register", response_model=UserResponse)
async def register_user(
    request: Request,
    prisma: Prisma = Depends(get_prisma)
):
    try:
        print("Iniciando registro de usuário...")
        
        # Ler dados
        request_data = await request.json()
        print("Dados recebidos:", request_data)
        
        # Gerar ID único
        user_id = str(uuid.uuid4())
        print(f"ID gerado: {user_id}")
        
        # Criar usuário
        new_user = await prisma.users.create(
            data={
                "id": user_id,
                "email": request_data["email"],
                "name": request_data["name"],
                "phone": request_data["phone"],
                "password": get_password_hash(request_data["password"]),
                "role": "USER",
                "is_active": True,
                "notification_email": True,
                "notification_push": True,
                "emailNotifications": True,
                "marketingEmails": False
            }
        )
        print("Usuário criado com sucesso:", new_user.id)
        
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            phone=new_user.phone
        )
        
    except Exception as e:
        print(f"Erro ao registrar usuário: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao registrar usuário: {str(e)}"
        )

@router.get("/", response_model=list[UserOut])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    prisma: Prisma = Depends(get_prisma)
):
    try:
        return await prisma.users.find_many(
            skip=skip,
            take=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: str, prisma: Prisma = Depends(get_prisma)):
    try:
        user = await prisma.users.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str, 
    user: UserUpdate, 
    prisma: Prisma = Depends(get_prisma)
):
    try:
        update_data = user.dict(exclude_unset=True)
        updated_user = await prisma.users.update(
            where={"id": user_id},
            data=update_data
        )
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}", response_model=UserOut)
async def delete_user(user_id: str, prisma: Prisma = Depends(get_prisma)):
    try:
        user = await prisma.users.delete(where={"id": user_id})
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}/profile", response_model=UserOut)
async def create_user_profile(
    user_id: str,
    profile: ProfileCreate,
    prisma: Prisma = Depends(get_prisma)
):
    try:
        print("Received request:")
        print(f"user_id: {user_id}")
        print(f"profile data: {profile}")

        # Verificar o estado atual do banco
        existing_user = await prisma.users.find_unique(
            where={"id": user_id},
            include={"profile": True}
        )
        print(f"Existing user: {existing_user}")
        
        if existing_user and existing_user.profile:
            print(f"Existing profile: {existing_user.profile}")
        
        now = datetime.utcnow()
        
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        try:
            print("Attempting to create new profile...")
            new_profile = await prisma.profiles.create({
                "id": user_id,
                "phone": profile.phone,
                "full_name": existing_user.name or "",
                "email": existing_user.email or "",
                "created_at": now,
                "updated_at": now
            })
            print(f"Successfully created new profile: {new_profile}")
        except Exception as create_error:
            print(f"Error creating profile: {create_error}")
            raise HTTPException(status_code=400, detail=str(create_error))
        
        # Buscar usuário atualizado
        updated_user = await prisma.users.find_unique(
            where={"id": user_id},
            include={"profile": True}
        )
        print(f"Final user state: {updated_user}")
        
        return updated_user
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/check/{phone}")
async def check_user_by_phone(
    phone: str,
    prisma: Prisma = Depends(get_prisma)
):
    try:
        print(f"Verificando usuário com telefone: {phone}")
        # Buscar em users
        user = await prisma.users.find_first(
            where={"phone": phone}
        )
        print("Usuário encontrado:", user)

        # Buscar em profiles
        profile = await prisma.profiles.find_first(
            where={"phone": phone}
        )
        print("Perfil encontrado:", profile)

        return {
            "user": user,
            "profile": profile
        }
    except Exception as e:
        print(f"Erro ao verificar usuário: {str(e)}")
        return {"error": str(e)}

@router.get("/profiles/all")
async def list_all_profiles(
    prisma: Prisma = Depends(get_prisma)
):
    try:
        profiles = await prisma.profiles.find_many(
            include={"user": True}
        )
        return {
            "total": len(profiles),
            "profiles": [{
                "id": p.id,
                "phone": p.phone,
                "full_name": p.full_name,
                "user_id": p.user.id if p.user else None
            } for p in profiles]
        }
    except Exception as e:
        print(f"Erro ao listar profiles: {str(e)}")
        return {"error": str(e)}