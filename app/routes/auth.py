from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..core.security import verify_password, create_access_token
from ..db.prisma import get_prisma
from prisma import Prisma
from ..db.models import Token

router = APIRouter(tags=["auth"])

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    prisma: Prisma = Depends(get_prisma)
):
    user = await prisma.users.find_unique(where={"email": form_data.username})
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"} 