from fastapi import APIRouter, Depends, HTTPException, Header
from prisma import Prisma
from app.utils.prisma import get_prisma
from datetime import datetime, timedelta
from decimal import Decimal

router = APIRouter()

@router.get("/summary/{user_id}")
async def get_financial_summary(
    user_id: str,
    start_date: str = None,
    end_date: str = None,
    prisma: Prisma = Depends(get_prisma)
):
    try:
        # Define date range (default to current month if not specified)
        if not start_date:
            today = datetime.utcnow()
            start_date = datetime(today.year, today.month, 1)
        else:
            start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            
        if not end_date:
            end_date = datetime.utcnow()
        else:
            end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

        # Get all transactions for the period
        transactions = await prisma.transactions.find_many(
            where={
                "user_id": user_id,
                "date": {
                    "gte": start_date,
                    "lte": end_date
                }
            }
        )

        # Calculate totals
        total_income = sum(
            Decimal(str(t.amount)) for t in transactions 
            if t.type == "INCOME"
        )
        total_expenses = sum(
            Decimal(str(t.amount)) for t in transactions 
            if t.type == "EXPENSE"
        )
        
        # Calculate balance
        balance = total_income - total_expenses

        return {
            "period": {
                "start": start_date,
                "end": end_date
            },
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "balance": float(balance),
            "transaction_count": len(transactions)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/monthly/{user_id}")
async def get_monthly_report(
    user_id: str,
    year: int = None,
    month: int = None,
    prisma: Prisma = Depends(get_prisma)
):
    try:
        # Use current year and month if not specified
        if not year or not month:
            today = datetime.utcnow()
            year = today.year
            month = today.month

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        transactions = await prisma.transactions.find_many(
            where={
                "user_id": user_id,
                "date": {
                    "gte": start_date,
                    "lt": end_date
                }
            },
            order={"date": "asc"}
        )

        # Group by category
        categories = {}
        for t in transactions:
            if t.category not in categories:
                categories[t.category] = {
                    "INCOME": Decimal("0"),
                    "EXPENSE": Decimal("0")
                }
            categories[t.category][t.type] += Decimal(str(t.amount))

        return {
            "year": year,
            "month": month,
            "categories": {
                cat: {
                    "income": float(values["INCOME"]),
                    "expenses": float(values["EXPENSE"]),
                    "balance": float(values["INCOME"] - values["EXPENSE"])
                }
                for cat, values in categories.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))