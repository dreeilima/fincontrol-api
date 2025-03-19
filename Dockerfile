FROM python:3.11-slim

WORKDIR /app

# Instalar dependências necessárias
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copiar schema do Prisma primeiro
COPY prisma ./prisma

# Gerar o Prisma Client
RUN prisma generate

# Copiar o resto do código
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
