#!/bin/bash

# Configurações
API_DIR="/var/www/fincontrol-api"
WHATSAPP_DIR="/var/www/fincontrol-whatsapp"
API_REPO="[URL_DO_REPOSITÓRIO_FINCONTROL_API]"
WHATSAPP_REPO="[URL_DO_REPOSITÓRIO_FINCONTROL_WHATSAPP]"

# Função para log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Deploy da API
log "Iniciando deploy da API..."
if [ ! -d "$API_DIR" ]; then
    log "Clonando repositório da API..."
    git clone $API_REPO $API_DIR
fi

cd $API_DIR
log "Atualizando código da API..."
git pull origin main

log "Configurando ambiente virtual da API..."
python -m venv .venv
source .venv/bin/activate

log "Instalando dependências da API..."
pip install -r requirements.txt

log "Configurando ambiente de produção da API..."
cp .env.production .env

log "Iniciando API em produção..."
python setup.py

# Deploy do WhatsApp Service
log "Iniciando deploy do WhatsApp Service..."
if [ ! -d "$WHATSAPP_DIR" ]; then
    log "Clonando repositório do WhatsApp Service..."
    git clone $WHATSAPP_REPO $WHATSAPP_DIR
fi

cd $WHATSAPP_DIR
log "Atualizando código do WhatsApp Service..."
git pull origin main

log "Instalando dependências do WhatsApp Service..."
npm install

log "Configurando ambiente de produção do WhatsApp Service..."
cp .env.production .env

log "Iniciando WhatsApp Service em produção..."
npm start

log "Deploy concluído com sucesso!" 