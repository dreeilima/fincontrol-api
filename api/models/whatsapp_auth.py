from sqlalchemy import Column, String, Text
from database.database import Base

class WhatsAppAuth(Base):
    __tablename__ = "whatsapp_auth"

    id = Column(String, primary_key=True, default="whatsapp")
    credentials = Column(Text)