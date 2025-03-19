from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from database.database import get_db
from models.whatsapp_auth import WhatsAppAuth

router = APIRouter()

@router.get("/auth")
async def get_whatsapp_auth(db: Session = Depends(get_db)):
    auth = db.query(WhatsAppAuth).first()
    if not auth:
        return {"credentials": None}
    return {"credentials": auth.credentials}

@router.post("/auth")
async def save_whatsapp_auth(data: dict, db: Session = Depends(get_db)):
    auth = db.query(WhatsAppAuth).first()
    if not auth:
        auth = WhatsAppAuth(id="whatsapp", credentials=data.get("credentials"))
        db.add(auth)
    else:
        auth.credentials = data.get("credentials")
    db.commit()
    return {"status": "success"}