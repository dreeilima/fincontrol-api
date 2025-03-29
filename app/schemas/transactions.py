from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime
from typing import Optional
import uuid
import re
from enum import Enum
from ..db.models import MessageType

def validate_decimal(v):
    try:
        if isinstance(v, str):
            if not re.match(r'^\d+(\.\d{2})?$', v):  # Aceita valores sem centavos
                raise ValueError('O valor deve estar no formato "XX.XX" ou "XX"')
            return Decimal(v)
        elif isinstance(v, (int, float)):
            return Decimal(f"{float(v):.2f}")
        elif isinstance(v, Decimal):
            return v
        raise ValueError('Tipo de valor inválido')
    except Exception as e:
        raise ValueError(f'Erro ao validar valor decimal: {str(e)}')

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

    model_config = {
        "from_attributes": True,  # Novo formato para V2 (antigo orm_mode)
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v),
            Decimal: lambda v: str(v)
        }
    }

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

class PeriodType(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    CATEGORY = "CATEGORY"

class ReportRequest(BaseModel):
    type: MessageType
    phone: str
    user_id: str
    period: PeriodType = Field(default=PeriodType.MONTHLY)

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    }

class MessageType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    BALANCE = "BALANCE"
    STATEMENT = "STATEMENT"
    REPORT = "REPORT"
    CATEGORIES = "CATEGORIES"
    CATEGORY_REPORT = "CATEGORY_REPORT"
    EDIT = "EDIT" 