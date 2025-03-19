from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime
from typing import Optional
import uuid
import re

def validate_decimal(v):
    if isinstance(v, str):
        # Verificar se o formato é correto (ex: "50.00")
        if not re.match(r'^\d+\.\d{2}$', v):
            raise ValueError('O valor deve estar no formato "XX.XX"')
        return Decimal(v)
    elif isinstance(v, (int, float)):
        # Converter para string com 2 casas decimais e depois para Decimal
        return Decimal(f"{float(v):.2f}")
    elif isinstance(v, Decimal):
        return v
    raise ValueError('Tipo de valor inválido')

class TransactionBase(BaseModel):
    amount: Decimal = Field(
        ..., 
        description="Valor da transação", 
        max_digits=10, 
        decimal_places=2,
        examples=["50.00", "1000.00"],
        validate_default=True
    )
    description: Optional[str] = Field(None, description="Descrição da transação")
    category: str = Field(..., description="Categoria da transação")
    date: datetime = Field(default_factory=datetime.utcnow, description="Data da transação")

    @field_validator('amount', mode='before')
    def validate_amount(cls, v):
        return validate_decimal(v)

class TransactionCreate(TransactionBase):
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v),
            Decimal: lambda v: str(v)
        }

class TransactionOut(TransactionBase):
    id: str
    user_id: str
    type: str
    created_at: datetime
    updated_at: datetime
    bankAccountId: Optional[str] = None
    categoryId: Optional[str] = None
    accountId: Optional[str] = None

    class Config:
        from_attributes = True 