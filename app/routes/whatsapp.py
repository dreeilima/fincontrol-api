from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from ..services.whatsapp import WhatsAppService
from ..db.models import (
    Message, 
    WhatsAppMessage, 
    MessageType,
    TransactionType,
    TransactionCreate,
    TransactionResponse,
    PeriodType
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
from typing import Optional, List, Dict, Any
import locale

# Configurar locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
    except:
        locale.setlocale(locale.LC_TIME, '')

# Mapeamento de meses em inglês para português
MESES = {
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

# Mapeamento reverso para ordenação
MESES_REVERSE = {
    'Janeiro': 1,
    'Fevereiro': 2,
    'Março': 3,
    'Abril': 4,
    'Maio': 5,
    'Junho': 6,
    'Julho': 7,
    'Agosto': 8,
    'Setembro': 9,
    'Outubro': 10,
    'Novembro': 11,
    'Dezembro': 12
}

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
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    category: Optional[str] = None
    period: Optional[PeriodType] = Field(default=PeriodType.MONTHLY)
    transaction_id: Optional[str] = None
    date: Optional[str] = None
    financialContext: Optional[Dict[str, Any]] = None

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
        return Decimal(str(v))

    @field_validator('user_id', mode='before')
    def validate_user_id(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator('type', mode='before')
    def validate_type(cls, v):
        if isinstance(v, MessageType):
            return v
        return MessageType(v)

    @field_validator('period')
    def validate_period(cls, v):
        if not v:
            return PeriodType.MONTHLY
        
        try:
            if isinstance(v, str):
                return PeriodType(v.upper())
            return v
        except ValueError:
            raise ValueError(f"Período inválido. Valores aceitos: {', '.join([p.value for p in PeriodType])}")

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
        
        # Formatar número do telefone
        phone = request.phone
        if phone.startswith("+"):
            phone = phone[1:]  # Remove o + se existir
        
        print(f"\n=== WEBHOOK RECEBIDO ===")
        print(f"Telefone: {phone}")
        print(f"Tipo: {request.type}")
        
        # Verificar se o usuário existe
        user = await prisma.users.find_first(
            where={"phone": phone}
        )
        
        if not user:
            print(f"Usuário não encontrado para o telefone: {phone}")
            raise HTTPException(
                status_code=404,
                detail=f"Usuário não encontrado para o telefone {phone}"
            )

        print(f"Usuário encontrado: {user.name}")
        
        # Processar comandos
        if request.type in [MessageType.INCOME, MessageType.EXPENSE]:
            print("\n=== PROCESSANDO TRANSAÇÃO ===")
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
            
            # Ajustar para timezone de São Paulo (UTC-3)
            tz_sp = timezone(timedelta(hours=-3))
            current_time = datetime.now(tz_sp)
            
            # Criar transação
            transaction_data = {
                "id": str(uuid.uuid4()),
                "user_id": request.user_id,
                "amount": str(amount),
                "description": request.description,
                "category": category.name,
                "type": request.type,
                "date": datetime.fromisoformat(request.date.replace('Z', '+00:00')).replace(hour=0, minute=0, second=0, microsecond=0),
                "categoryId": category.id
            }
            
            print(f"Dados da transação: {transaction_data}")
            
            # Registrar transação
            transaction = await prisma.transactions.create(data=transaction_data)
            print(f"Transação registrada: {transaction}")
            
            # Gerar mensagem de confirmação
            message_context = {
                "type": "TRANSACTION",
                "step": "CONFIRMATION",
                "type": request.type.value,
                "amount": abs(float(transaction.amount)),
                "description": transaction.description,
                "category": transaction.category,
                "date": transaction.date.strftime("%d/%m/%Y")
            }
            
            print(f"Contexto da mensagem: {message_context}")
            message = await whatsapp.generate_response(message_context)
            print(f"Mensagem gerada: {message}")
            
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.BALANCE:
            transactions = await prisma.transactions.find_many(
                where={"user_id": user.id}
            )
            if not transactions:
                message_context = {"type": "NO_TRANSACTIONS_BALANCE"}
                message = await whatsapp.generate_response(message_context)
                return WebhookResponse(message=message)

            # Calcular saldo corretamente
            saldo = Decimal('0')
            print("\n=== DETALHAMENTO DO SALDO ===")
            for t in transactions:
                valor = Decimal(str(t.amount))
                print(f"{'Receita' if valor > 0 else 'Despesa'}: {t.description} = R$ {abs(float(valor)):.2f}")
                saldo += valor
            
            print(f"Saldo Final: R$ {float(saldo):.2f}")
            
            # Formatar mensagem
            status_emoji = "✅" if saldo >= 0 else "❌"
            total_receitas = sum(float(t.amount) for t in transactions if float(t.amount) > 0)
            total_despesas = abs(sum(float(t.amount) for t in transactions if float(t.amount) < 0))
            
            message_context = {
                "type": "BALANCE",
                "balance": abs(float(saldo)),
                "status_emoji": status_emoji,
                "status": "Positivo" if saldo >= 0 else "Negativo",
                "total_receitas": total_receitas,
                "total_despesas": total_despesas
            }
            
            message = await whatsapp.generate_response(message_context)
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.STATEMENT:
            transactions = await prisma.transactions.find_many(
                where={"user_id": user.id},
                order={"date": "desc"}
            )
            if not transactions:
                message_context = {"type": "NO_TRANSACTIONS_STATEMENT"}
                message = await whatsapp.generate_response(message_context)
                return WebhookResponse(message=message)
            
            # Calcular totais
            total_receitas = sum(float(t.amount) for t in transactions if float(t.amount) > 0)
            total_despesas = abs(sum(float(t.amount) for t in transactions if float(t.amount) < 0))
            saldo = total_receitas - total_despesas
            
            # Formatar lista de transações
            transactions_list = "\n\n".join(
                f"{'📥' if t.type == 'INCOME' else '📤'} *{t.category}*\n"
                f"💰 Valor: R$ {abs(float(t.amount)):.2f}\n"
                f"📝 Descrição: {t.description}\n"
                f"📅 Data: {t.date.strftime('%d/%m/%Y')}\n"
                f"🔑 ID: #{t.id[-6:].upper()}\n"
                f"━━━━━━━━━━━━━━━"
                for t in transactions
            )
            
            message_context = {
                "type": "STATEMENT",
                "total_receitas": total_receitas,
                "total_despesas": total_despesas,
                "saldo": saldo,
                "transactions_list": transactions_list
            }
            
            message = await whatsapp.generate_response(message_context)
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.REPORT:
            try:
                tz_sp = timezone(timedelta(hours=-3))
                now = datetime.now(tz_sp)
                
                # Definir período de busca
                period = request.period
                print(f"\n=== GERANDO RELATÓRIO ===")
                print(f"Período recebido: {period}")
                print(f"Usuário: {user.id}")
                
                # Mapear nomes amigáveis
                period_names = {
                    PeriodType.DAILY: "Diário",
                    PeriodType.WEEKLY: "Semanal", 
                    PeriodType.MONTHLY: "Mensal",
                    PeriodType.YEARLY: "Anual"
                }
                
                # Definir data inicial
                if period == PeriodType.MONTHLY:
                    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                elif period == PeriodType.YEARLY:
                    start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                elif period == PeriodType.WEEKLY:
                    start_date = now - timedelta(days=7)
                else:  # DAILY
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                
                print(f"Data inicial: {start_date}")
                
                # Buscar transações do período
                transactions = await prisma.transactions.find_many(
                    where={
                        "user_id": user.id,
                        "date": {
                            "gte": start_date
                        }
                    },
                    order={"date": "desc"}
                )
                
                print(f"Transações encontradas: {len(transactions)}")
                
                if not transactions:
                    message_context = {"type": "NO_TRANSACTIONS"}
                    message = await whatsapp.generate_response(message_context)
                    return WebhookResponse(message=message)
                
                # Calcular totais
                receitas = sum(float(t.amount) for t in transactions if float(t.amount) > 0)
                despesas = abs(sum(float(t.amount) for t in transactions if float(t.amount) < 0))
                saldo = receitas - despesas
                
                # Calcular médias
                num_receitas = len([t for t in transactions if float(t.amount) > 0])
                num_despesas = len([t for t in transactions if float(t.amount) < 0])
                media_receitas = receitas / num_receitas if num_receitas > 0 else 0
                media_despesas = despesas / num_despesas if num_despesas > 0 else 0
                
                # Agrupar por categoria
                categorias = {}
                for t in transactions:
                    if t.category not in categorias:
                        categorias[t.category] = {"total": 0, "count": 0}
                    categorias[t.category]["total"] += abs(float(t.amount))
                    categorias[t.category]["count"] += 1
                
                # Ordenar categorias por valor
                top_categorias = sorted(
                    categorias.items(), 
                    key=lambda x: x[1]["total"], 
                    reverse=True
                )[:5]
                
                # Formatar lista de categorias
                lista_categorias = "\n".join(
                    f"• {cat}: R$ {dados['total']:.2f} ({dados['count']} transações)" 
                    for cat, dados in top_categorias
                )

                # Determinar tendência do saldo
                saldo_emoji = "↗️" if saldo > 0 else "↙️" if saldo < 0 else "➡️"
                
                message_context = {
                    "type": "REPORT",
                    "period_name": period_names[period],
                    "receitas": receitas,
                    "num_receitas": num_receitas,
                    "despesas": despesas,
                    "num_despesas": num_despesas,
                    "saldo_emoji": saldo_emoji,
                    "saldo": saldo,
                    "media_receitas": media_receitas,
                    "media_despesas": media_despesas,
                    "lista_categorias": lista_categorias
                }
                
                message = await whatsapp.generate_response(message_context)
                return WebhookResponse(message=message)
                
            except ValueError as ve:
                print(f"Erro de validação: {str(ve)}")
                raise HTTPException(
                    status_code=422,
                    detail=f"Erro de validação: {str(ve)}"
                )
            except Exception as e:
                print(f"Erro ao gerar relatório: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao gerar relatório: {str(e)}"
                )
            
        elif request.type == MessageType.CATEGORY_REPORT:
            if not request.category:
                raise HTTPException(
                    status_code=400,
                    detail="Categoria não especificada"
                )
            
            transactions = await prisma.transactions.find_many(
                where={
                    "user_id": user.id,
                    "category": request.category
                },
                order={"date": "desc"}
            )
            
            if not transactions:
                message_context = {
                    "type": "NO_TRANSACTIONS_CATEGORY",
                    "category": request.category
                }
                message = await whatsapp.generate_response(message_context)
                return WebhookResponse(message=message)
            
            # Calcular totais
            total = sum(abs(float(t.amount)) for t in transactions)
            media = total / len(transactions)
            ultima = abs(float(transactions[0].amount))
            
            # Agrupar por mês
            gastos_por_mes = {}
            for t in transactions:
                # Converter para o timezone de São Paulo
                tz_sp = timezone(timedelta(hours=-3))
                data_sp = t.date.astimezone(tz_sp)
                
                # Obter o mês em inglês usando locale en_US
                locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
                mes_original = data_sp.strftime("%B").capitalize()
                print(f"\n=== DEBUG MÊS ===")
                print(f"Data original: {t.date}")
                print(f"Data SP: {data_sp}")
                print(f"Mês original (en_US): {mes_original}")
                print(f"Mapeamento: {MESES}")
                
                try:
                    mes = MESES[mes_original]  # Usar o mapeamento para português
                    print(f"Mês traduzido: {mes}")
                    print(f"Codificação do mês: {mes.encode('utf-8')}")
                except KeyError:
                    print(f"Erro: Mês '{mes_original}' não encontrado no mapeamento")
                    continue
                
                if mes not in gastos_por_mes:
                    gastos_por_mes[mes] = 0
                gastos_por_mes[mes] += abs(float(t.amount))
            
            print("\n=== DEBUG GASTOS POR MÊS ===")
            print(f"Gastos por mês: {gastos_por_mes}")
            
            # Formatar lista de meses
            meses_list = ""
            for mes, valor in sorted(gastos_por_mes.items(), key=lambda x: MESES_REVERSE[x[0]]):
                linha = f"• {mes}: R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                print(f"\n=== DEBUG LINHA ===")
                print(f"Mês: {mes}")
                print(f"Valor: {valor}")
                print(f"Linha formatada: {linha}")
                print(f"Codificação da linha: {linha.encode('utf-8')}")
                meses_list += linha + "\n"
            
            print("\n=== DEBUG LISTA FINAL ===")
            print(f"Lista de meses: {meses_list}")
            print(f"Codificação da lista: {meses_list.encode('utf-8')}")
            
            message_context = {
                "type": "CATEGORY_REPORT",
                "category": request.category,
                "total": total,
                "media": media,
                "ultima": ultima,
                "meses_list": meses_list
            }
            
            message = await whatsapp.generate_response(message_context)
            return WebhookResponse(message=message)
            
        elif request.type == "HELP_MESSAGE":
            message_context = {
                "type": "HELP_MESSAGE"
            }
            message = await whatsapp.generate_response(message_context)
            return WebhookResponse(message=message)
            
        elif request.type == "HELP_DETAILS":
            message_context = {
                "type": "HELP_DETAILS",
                "command": request.command
            }
            message = await whatsapp.generate_response(message_context)
            return WebhookResponse(message=message)
            
        elif request.type == MessageType.FINANCIAL_ADVICE:
            if not request.financialContext:
                raise HTTPException(
                    status_code=400,
                    detail="Contexto financeiro não fornecido"
                )
            
            message_context = {
                "type": "FINANCIAL_ADVICE",
                "userName": user.name,
                "financialContext": request.financialContext
            }
            message = await whatsapp.generate_response(message_context)
            return WebhookResponse(message=message)
            
        else:
            raise HTTPException(status_code=400, detail="Tipo de comando inválido")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Erro no webhook: {str(e)}")
        if hasattr(e, 'errors'):
            error_msg = e.errors()[0].get('msg', str(e))
            raise HTTPException(
                status_code=422,
                detail=f"Erro de validação: {error_msg}"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Erro no webhook: {str(e)}"
        )

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
        print("\n=== GERANDO QR CODE ===")
        qr_data = await whatsapp.get_qr()
        print("QR Code gerado com sucesso")
        return qr_data
    except Exception as e:
        print(f"Erro ao gerar QR code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar QR code: {str(e)}"
        )


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

async def get_weekly_report(user_id: int) -> Dict[str, Any]:
    """Gera relatório semanal de gastos"""
    try:
        # Obter data atual no timezone de São Paulo
        tz_sp = timezone(timedelta(hours=-3))
        now = datetime.now(tz_sp)
        
        # Calcular início da semana (segunda-feira)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calcular fim da semana (domingo)
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        print(f"\n=== RELATÓRIO SEMANAL ===")
        print(f"Início da semana: {start_of_week}")
        print(f"Fim da semana: {end_of_week}")
        
        # Buscar transações da semana atual
        transactions = await prisma.transactions.find_many(
            where={
                "user_id": user_id,
                "date": {
                    "gte": start_of_week,
                    "lte": end_of_week
                }
            },
            order={"date": "desc"}
        )
        
        if not transactions:
            return {
                "type": "NO_TRANSACTIONS"
            }
        
        # Calcular totais
        receitas = sum(float(t.amount) for t in transactions if float(t.amount) > 0)
        despesas = abs(sum(float(t.amount) for t in transactions if float(t.amount) < 0))
        saldo = receitas - despesas
        
        # Contar transações
        total_receitas = len([t for t in transactions if float(t.amount) > 0])
        total_despesas = len([t for t in transactions if float(t.amount) < 0])
        
        # Calcular médias
        media_receita = receitas / total_receitas if total_receitas > 0 else 0
        media_despesa = despesas / total_despesas if total_despesas > 0 else 0
        
        # Agrupar por categoria
        categorias = {}
        for t in transactions:
            if t.category not in categorias:
                categorias[t.category] = {"amount": 0, "count": 0}
            categorias[t.category]["amount"] += abs(float(t.amount))
            categorias[t.category]["count"] += 1
        
        # Ordenar categorias por valor
        top_categorias = [
            {"name": cat, "amount": data["amount"], "count": data["count"]}
            for cat, data in sorted(categorias.items(), key=lambda x: x[1]["amount"], reverse=True)[:5]
        ]
        
        return {
            "type": "WEEKLY_REPORT",
            "receitas": receitas,
            "despesas": despesas,
            "saldo": saldo,
            "media_receita": media_receita,
            "media_despesa": media_despesa,
            "top_categorias": top_categorias,
            "total_receitas": total_receitas,
            "total_despesas": total_despesas
        }
    except Exception as e:
        print(f"Erro ao gerar relatório semanal: {str(e)}")
        return {
            "type": "ERROR",
            "error": str(e)
        }

@router.get("/financial-context/{user_id}")
async def get_financial_context(
    user_id: str,
    prisma: Prisma = Depends(get_prisma)
):
    try:
        await ensure_connection()
        
        # Buscar transações do mês atual
        tz_sp = timezone(timedelta(hours=-3))
        now = datetime.now(tz_sp)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        transactions = await prisma.transactions.find_many(
            where={
                "user_id": user_id,
                "date": {
                    "gte": start_of_month
                }
            },
            order={"date": "desc"}
        )
        
        # Calcular totais do mês
        monthly_income = sum(float(t.amount) for t in transactions if float(t.amount) > 0)
        monthly_expenses = abs(sum(float(t.amount) for t in transactions if float(t.amount) < 0))
        
        # Buscar saldo total
        all_transactions = await prisma.transactions.find_many(
            where={"user_id": user_id}
        )
        balance = sum(float(t.amount) for t in all_transactions)
        
        # Analisar categorias com mais gastos
        expense_categories = {}
        for t in transactions:
            if float(t.amount) < 0:
                category = t.category
                amount = abs(float(t.amount))
                expense_categories[category] = expense_categories.get(category, 0) + amount
        
        # Ordenar categorias por valor gasto
        top_categories = sorted(
            expense_categories.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Formatar top categorias
        top_expense_categories = "\n".join(
            f"• {cat}: R$ {val:.2f}"
            for cat, val in top_categories
        )
        
        # Analisar tendências
        trends = []
        if monthly_expenses > monthly_income:
            trends.append("Seus gastos estão maiores que suas receitas este mês")
        if monthly_expenses > 0 and monthly_expenses / monthly_income > 0.8:
            trends.append("Você está gastando mais de 80% da sua renda")
        if balance < 0:
            trends.append("Seu saldo está negativo")
        if not transactions:
            trends.append("Nenhuma transação registrada este mês")
        
        return {
            "balance": f"R$ {abs(float(balance)):.2f}",
            "monthlyIncome": f"R$ {monthly_income:.2f}",
            "monthlyExpenses": f"R$ {monthly_expenses:.2f}",
            "topExpenseCategories": top_expense_categories,
            "trends": "\n".join(f"• {t}" for t in trends)
        }
        
    except Exception as e:
        print(f"Erro ao buscar contexto financeiro: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar contexto financeiro: {str(e)}"
        )