from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from ..services.whatsapp import WhatsAppService
from ..db.models import (
    Message, 
    WhatsAppMessage, 
    MessageType,
    TransactionType,
    TransactionCreate,
    TransactionResponse
)
from ..core.config import settings
from ..core.auth import get_current_user
from ..db.prisma import get_prisma
from ..utils.prisma import ensure_connection
from prisma import Prisma
import httpx
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from ..schemas.transactions import validate_decimal

router = APIRouter()
whatsapp = WhatsAppService(
    base_url=settings.whatsapp_service_url,
    secret_key=settings.whatsapp_secret_key
)

print("\n=== WHATSAPP ROUTER ===")
print(f"Service URL: {settings.whatsapp_service_url}")
print(f"Secret Key: {'*' * len(settings.whatsapp_secret_key)}")

class WebhookRequest(BaseModel):
    type: MessageType
    phone: str
    user_id: str
    amount: Optional[Decimal] = Field(
        None,
        description="Valor da transação",
        examples=["50.00", "1000.00"]
    )
    description: Optional[str] = None
    category: Optional[str] = None
    period: Optional[str] = None
    transaction_id: Optional[str] = None

    model_config = {
        "json_encoders": {
            Decimal: str,
            uuid.UUID: str,
            datetime: lambda v: v.isoformat()
        }
    }

    @field_validator('amount', mode='before')
    def validate_amount(cls, v):
        if v is None:
            return v
        return validate_decimal(v)

    @field_validator('user_id', mode='before')
    def validate_user_id(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator('type', mode='before')
    def validate_type(cls, v):
        if isinstance(v, str):
            return MessageType(v.upper())
        return v

    @field_validator('period', mode='before')
    def validate_period(cls, v):
        if v not in ['diario', 'semanal', 'mensal']:
            raise ValueError("Período inválido")
        return v

class WebhookResponse(BaseModel):
    message: str
    success: bool = True

    model_config = {
        "json_encoders": {
            uuid.UUID: str,
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
    }

@router.post("/webhook")
async def webhook(
    request: WebhookRequest,
    prisma: Prisma = Depends(get_prisma)
) -> WebhookResponse:
    try:
        await ensure_connection()
        now = datetime.now(timezone.utc)
        
        if request.type in [MessageType.INCOME, MessageType.EXPENSE]:
            amount = Decimal(str(request.amount)) if request.amount else Decimal('0')
            if request.type == MessageType.EXPENSE:
                amount = -amount  # Torna o valor negativo para despesas
            
            # Primeiro, verificar se a categoria existe
            category = await prisma.categories.find_first(
                where={
                    "user_id": request.user_id,
                    "name": request.category,
                    "type": request.type
                }
            )
            
            # Se não existir, criar
            if not category:
                category = await prisma.categories.create(
                    data={
                        "id": str(uuid.uuid4()),
                        "user_id": request.user_id,
                        "name": request.category,
                        "type": request.type
                    }
                )
            
            # Criar transação
            transaction_data = TransactionCreate(
                amount=amount,
                description=request.description,
                category=category.name,
                type=request.type,
                date=now
            )
            
            transaction = await prisma.transactions.create(
                data={
                    "id": str(uuid.uuid4()),
                    "user_id": request.user_id,
                    **transaction_data.model_dump(),
                    "categoryId": category.id
                }
            )
            
            response = TransactionResponse(
                id=transaction.id,
                amount=transaction.amount,
                description=transaction.description,
                category=transaction.category,
                type=transaction.type,
                date=transaction.date,
                created_at=transaction.created_at
            )
            
            # Para receitas e despesas
            tipo = "Receita" if request.type == MessageType.INCOME else "Despesa"
            emoji = "📥" if request.type == MessageType.INCOME else "📤"
            message = (
                f"{emoji} *{tipo} registrada com sucesso!*\n\n"
                f"💰 *Valor:* R$ {abs(float(response.amount)):.2f}\n"
                f"📝 *Descrição:* {response.description}\n"
                f"🏷️ *Categoria:* {response.category}\n"
                f"📅 *Data:* {response.date.strftime('%d/%m/%Y %H:%M')}\n"
                f"🆔 *ID:* {response.id[:8]}"
            )
            
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.BALANCE:
            # Buscar saldo
            transactions = await prisma.transactions.find_many(
                where={"user_id": request.user_id}
            )
            # Converter transações para formato serializável
            transactions_formatted = [{
                **t.dict(),
                'id': str(t.id),
                'user_id': str(t.user_id),
                'amount': float(t.amount)
            } for t in transactions]
            balance = sum(t['amount'] for t in transactions_formatted)
            emoji = "📈" if balance >= 0 else "📉"
            message = (
                f"💰 *Resumo Financeiro*\n\n"
                f"{emoji} *Saldo atual:* R$ {abs(float(balance)):.2f}\n"
                f"{'✅ Positivo' if balance >= 0 else '❌ Negativo'}"
            )
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.STATEMENT:
            # Buscar últimas 10 transações
            transactions = await prisma.transactions.find_many(
                where={"user_id": request.user_id},
                order={"date": "desc"},
                take=10
            )
            
            if not transactions:
                return WebhookResponse(message="Nenhuma transação encontrada")
            
            # Formatar mensagem
            message = "📋 *Últimas Transações:*\n\n"
            
            for t in transactions:
                emoji = "📥" if t.type == "INCOME" else "📤"
                valor = abs(float(t.amount))
                data = t.date.strftime("%d/%m/%Y")
                
                message += f"{emoji} *{t.category}*\n"
                message += f"💰 R$ {valor:.2f}\n"
                message += f"📝 {t.description}\n"
                message += f"📅 {data}\n"
                message += f"🆔 {t.id[:8]}\n"
                message += "➖➖➖➖➖➖➖➖\n\n"
            
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.CATEGORIES:
            # Buscar categorias
            print("User ID:", request.user_id)
            categories = await prisma.categories.find_many(
                where={"user_id": request.user_id}
            )
            print("Categorias encontradas:", categories)
            # Converter UUID para string
            categories_formatted = [{
                **c.dict(),
                'id': str(c.id),
                'user_id': str(c.user_id)
            } for c in categories]
            print("Categorias formatadas:", categories_formatted)
            message = "📊 *Suas Categorias*\n\n"
            message += "*Receitas:*\n"
            for c in categories_formatted:
                if c['type'] == "INCOME":
                    message += f"📥 {c['name']}\n"
            message += "\n*Despesas:*\n"
            for c in categories_formatted:
                if c['type'] == "EXPENSE":
                    message += f"📤 {c['name']}\n"
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.REPORT:
            # Verificar se temos o período
            if not request.period:
                raise HTTPException(
                    status_code=400, 
                    detail="Período não especificado"
                )
            
            # Buscar transações do período
            now = datetime.now(timezone.utc)
            
            # Definir período
            if request.period == 'diario':
                start_date = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
            elif request.period == 'semanal':
                start_date = now - timedelta(days=7)
            else:  # mensal
                start_date = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
            
            # Buscar transações
            transactions = await prisma.transactions.find_many(
                where={
                    "user_id": request.user_id,
                    "date": {"gte": start_date}
                },
                order={"date": "desc"}
            )
            
            # Calcular totais
            receitas = sum(float(t.amount) for t in transactions if t.type == "INCOME")
            despesas = sum(abs(float(t.amount)) for t in transactions if t.type == "EXPENSE")
            saldo = receitas - despesas
            
            # Agrupar por categoria
            categorias = {}
            for t in transactions:
                if t.type == "EXPENSE":
                    if t.category not in categorias:
                        categorias[t.category] = 0
                    categorias[t.category] += abs(float(t.amount))
            
            # Ordenar categorias por valor
            cat_ordenadas = sorted(
                categorias.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Formatar mensagem
            periodo_texto = {
                'diario': 'hoje',
                'semanal': 'últimos 7 dias',
                'mensal': 'este mês'
            }
            message = (
                f"📊 *Relatório Financeiro - {periodo_texto[request.period]}*\n\n"
                f"📥 *Receitas:* R$ {receitas:.2f}\n"
                f"📤 *Despesas:* R$ {despesas:.2f}\n"
                f"💰 *Saldo:* R$ {saldo:.2f}\n\n"
                f"*Top Categorias (Despesas):*\n"
            )
            for cat, valor in cat_ordenadas[:5]:  # Top 5 categorias
                percent = (valor/despesas * 100) if despesas > 0 else 0
                message += f"🏷️ {cat}: R$ {valor:.2f} ({percent:.1f}%)\n"
            
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.CATEGORY_REPORT:
            # Dicionário de tradução de meses
            meses_dict = {
                'January': 'Janeiro',
                'February': 'Fevereiro',
                'March': 'Março',
                'April': 'Abril',
                'May': 'Maio',
                'June': 'Junho',
                'July': 'Julho',
                'August': 'Agosto',
                'September': 'Setembro',
                'October': 'Outubro',
                'November': 'Novembro',
                'December': 'Dezembro'
            }
            
            # Buscar transações da categoria
            transactions = await prisma.transactions.find_many(
                where={
                    "user_id": request.user_id,
                    "category": request.category
                },
                order={"date": "desc"}
            )
            
            if not transactions:
                return WebhookResponse(
                    message=f"❌ Nenhuma transação encontrada na categoria '{request.category}'"
                )
            
            # Calcular totais
            total = sum(abs(float(t.amount)) for t in transactions)
            media = total / len(transactions)
            ultima = abs(float(transactions[0].amount))
            
            # Agrupar por mês
            meses = {}
            for t in transactions:
                mes = meses_dict[t.date.strftime("%B")]  # Traduzir o mês
                if mes not in meses:
                    meses[mes] = 0
                meses[mes] += abs(float(t.amount))
            
            # Formatar mensagem
            message = f"📊 *Relatório da Categoria: {request.category}*\n\n"
            message += f"💰 *Resumo:*\n"
            message += f"📈 Total gasto: R$ {total:.2f}\n"
            message += f"📊 Média por transação: R$ {media:.2f}\n"
            message += f"🔄 Última transação: R$ {ultima:.2f}\n\n"
            
            if meses:
                message += "📅 *Gastos por Mês:*\n"
                for mes, valor in meses.items():
                    message += f"• {mes}: R$ {valor:.2f}\n"
            
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.EDIT:
            # Verificar se a transação existe e pertence ao usuário
            transaction = await prisma.transactions.find_first(
                where={
                    "id": request.transaction_id,
                    "user_id": request.user_id
                }
            )
            
            if not transaction:
                return WebhookResponse(
                    message="❌ Transação não encontrada ou não pertence a você"
                )
            
            # Preparar dados para atualização
            update_data = {}
            
            if request.amount is not None:
                # Manter o sinal original (positivo para receita, negativo para despesa)
                amount = abs(float(request.amount))
                if transaction.type == "EXPENSE":
                    amount = -amount
                update_data["amount"] = str(amount)
            
            if request.description:
                update_data["description"] = request.description
            
            if request.category:
                update_data["category"] = request.category
            
            # Atualizar transação
            updated = await prisma.transactions.update(
                where={"id": request.transaction_id},
                data={
                    **update_data,
                    "updated_at": datetime.now(timezone.utc)
                }
            )
            
            # Formatar mensagem de resposta
            tipo = "Despesa" if updated.type == "EXPENSE" else "Receita"
            valor = abs(float(updated.amount))
            
            message = f"✅ {tipo} atualizada!\n\n"
            message += f"💰 Valor: R$ {valor:.2f}\n"
            message += f"📝 Descrição: {updated.description}\n"
            message += f"🏷️ Categoria: {updated.category}"
            
            return WebhookResponse(message=message)
            
        else:
            raise HTTPException(status_code=400, detail="Tipo de comando inválido")
            
    except Exception as e:
        print(f"Erro no webhook: {str(e)}")
        # Se for erro de validação, retornar mensagem mais amigável
        if hasattr(e, 'errors'):
            error_msg = e.errors()[0].get('msg', str(e))
            raise HTTPException(status_code=422, detail=f"Erro de validação: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Erro no webhook: {str(e)}")

@router.post("/send")
async def send_message(message: Message):
    try:
        await whatsapp.send_message(
            to=message.to,
            message=message.text
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/qr", response_class=HTMLResponse)
async def get_qr():
    try:
        qr_data = await whatsapp.get_qr()
        print("QR Code recebido com sucesso:", qr_data is not None)
        return qr_data
    except Exception as e:
        print(f"Erro ao obter QR code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter QR code: {str(e)}")


@router.get("/auth")
async def get_whatsapp_auth(prisma: Prisma = Depends(get_prisma)):
    await ensure_connection()
    auth = await prisma.whatsapp_auth.find_first()
    if not auth:
        return {"credentials": None}
    return {"credentials": auth.credentials}

@router.post("/auth")
async def save_whatsapp_auth(data: dict, prisma: Prisma = Depends(get_prisma)):
    await ensure_connection()
    auth = await prisma.whatsapp_auth.find_first()
    if not auth:
        auth = await prisma.whatsapp_auth.create(
            data={
                "id": "whatsapp",
                "credentials": data.get("credentials")
            }
        )
    else:
        auth = await prisma.whatsapp_auth.update(
            where={"id": "whatsapp"},
            data={"credentials": data.get("credentials")}
        )
    return {"status": "success"}