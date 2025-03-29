# Documentação de Testes - FinControl

## 1. Comandos Básicos

### 1.1 Registro de Transações
- ✅ Registro de receitas (`ganhei`)
  - Exemplo: `ganhei 1000 de salário`
  - Exemplo: `ganhei 500 de freela`
  - Exemplo: `ganhei 200 de investimentos`

- ✅ Registro de despesas (`gastei`)
  - Exemplo: `gastei 50 em almoço`
  - Exemplo: `gastei 200 em compras`
  - Exemplo: `gastei 100 em farmácia`

### 1.2 Consultas
- ✅ Consulta de saldo (`saldo`)
  - Mostra saldo atual
  - Exibe resumo das últimas transações

- ✅ Extrato de transações (`extrato`)
  - Mostra todas as transações
  - Formatação melhorada com IDs encurtados

### 1.3 Conselhos e Dicas
- ✅ Conselhos financeiros (`conselhos`)
  - Análise financeira estratégica
  - Recomendações personalizadas
  - Plano de ação concreto
  - Formato estruturado com emojis

- ✅ Dicas práticas (`dicas`)
  - Dicas para categorias principais
  - Truques do dia a dia
  - Hábitos positivos
  - Tom mais leve e motivador

## 2. Relatórios

### 2.1 Tipos de Relatórios
- ✅ Relatório diário
  - Mostra transações do dia atual

- ✅ Relatório semanal
  - Ajustado para mostrar apenas a semana atual
  - Formatação de datas em português

- ✅ Relatório mensal
  - Resumo completo do mês
  - Totais e médias

- ✅ Relatório anual
  - Visão geral do ano
  - Tendências e comparações

- ✅ Relatório por categoria
  - Detalhes específicos por categoria
  - Totais e médias por categoria

## 3. Ajustes de Formatação

### 3.1 Valores Monetários
- ✅ Formatação com vírgula para centavos
- ✅ Símbolo da moeda (R$)
- ✅ Separadores de milhares

### 3.2 Datas e Períodos
- ✅ Datas no formato brasileiro
- ✅ Nomes dos meses em português
- ✅ IDs das transações encurtados (6 caracteres)

### 3.3 Respostas de IA
- ✅ Formatação consistente com emojis
- ✅ Uso de markdown para destaque
- ✅ Parágrafos contínuos sem bullets
- ✅ Limite de 3 parágrafos por resposta
- ✅ Tom adaptado ao tipo de resposta

## 4. Comandos de Ajuda

### 4.1 Sistema de Ajuda
- ✅ Ajuda geral (`ajuda`)
  - Lista todos os comandos disponíveis
  - Exemplos de uso

- ✅ Ajuda específica (`ajuda [comando]`)
  - Detalhes do comando
  - Exemplos específicos

### 4.2 Remoção de Comandos
- ❌ Editar transação (removido)
  - Agora disponível apenas no site
- ❌ Excluir transação (removido)
  - Agora disponível apenas no site

## 5. Correções de Bugs

### 5.1 Problemas Resolvidos
- ✅ Discrepância entre saldo e extrato
  - Removido limite de 10 transações no extrato
  - Valores agora consistentes

- ✅ Relatório de categoria
  - Corrigido processamento de categorias
  - Formatação adequada dos resultados

- ✅ Relatório semanal
  - Ajustado para mostrar apenas semana atual
  - Formatação de datas corrigida

- ✅ Respostas de IA
  - Corrigido escopo das variáveis
  - Formatação consistente
  - Diferenciação entre conselhos e dicas

## 6. Funcionalidades Atuais

### 6.1 Disponíveis via WhatsApp
1. Registro de transações
2. Consulta de saldo e extrato
3. Geração de relatórios
4. Gerenciamento de categorias
5. Sistema de ajuda
6. Conselhos financeiros personalizados
7. Dicas práticas de economia

### 6.2 Disponíveis apenas no Site
1. Edição de transações
2. Exclusão de transações
3. Configurações avançadas
4. Gestão de conta

## 7. Próximos Passos

### 7.1 Possíveis Melhorias
- [ ] Adicionar mais tipos de relatórios
- [ ] Implementar gráficos nos relatórios
- [ ] Adicionar mais opções de filtro
- [ ] Melhorar sistema de categorias
- [ ] Expandir base de dicas e conselhos
- [ ] Adicionar mais personalização nas respostas

### 7.2 Manutenção
- [ ] Monitorar uso dos comandos
- [ ] Coletar feedback dos usuários
- [ ] Ajustar formatação conforme necessário
- [ ] Atualizar documentação
- [ ] Refinar respostas da IA

# Configuração de Ambientes

## Estrutura de Arquivos de Ambiente

O projeto utiliza uma estrutura separada para gerenciar ambientes de desenvolvimento (local) e produção:

```
/
├── .env.local (para API)
├── .env.production (para API)
├── .env (gerado automaticamente para API)
├── whatsapp-service/
│   ├── .env.local
│   ├── .env.production
│   └── .env (gerado automaticamente)
└── scripts/
    └── manage_env.py
```

## Configurações por Ambiente

### API (Arquivos na raiz)

#### Ambiente Local (.env.local)
```
ip=127.0.0.1
port=8000
DATABASE_URL=postgresql://neondb_owner:nJB0UyDGXu2I@ep-yellow-haze-a5kf8qsl-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
access_token_expire_minutes=30
reset_token_expire_hours=24
whatsapp_service_url=http://localhost:3000
whatsapp_secret_key=fincontrol-whatsapp-key-2024
SECRET_KEY=fincontrol-secret-key-2024
ALGORITHM=HS256
WEBHOOK_URL=http://localhost:8000/whatsapp/webhook
ENVIRONMENT=development
DEBUG=True
```

#### Ambiente de Produção (.env.production)
```
ip=164.90.170.224
port=8000
DATABASE_URL=postgresql://neondb_owner:nJB0UyDGXu2I@ep-yellow-haze-a5kf8qsl-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
access_token_expire_minutes=30
reset_token_expire_hours=24
whatsapp_service_url=http://164.90.170.224:3000
whatsapp_secret_key=fincontrol-whatsapp-key-2024
SECRET_KEY=fincontrol-secret-key-2024
ALGORITHM=HS256
WEBHOOK_URL=http://164.90.170.224:8000/whatsapp/webhook
ENVIRONMENT=production
DEBUG=False
```

### WhatsApp Service (Arquivos na pasta whatsapp-service)

#### Ambiente Local (.env.local)
```
port=3000
api_url=http://localhost:8000
whatsapp_secret_key=fincontrol-whatsapp-key-2024
ENVIRONMENT=development
DEBUG=True
```

#### Ambiente de Produção (.env.production)
```
port=3000
api_url=http://164.90.170.224:8000
whatsapp_secret_key=fincontrol-whatsapp-key-2024
ENVIRONMENT=production
DEBUG=False
```

## Como Usar

Para alternar entre os ambientes, use o script `manage_env.py`:

```bash
# Para configurar a API em ambiente local
python scripts/manage_env.py api local

# Para configurar a API em produção
python scripts/manage_env.py api production

# Para configurar o WhatsApp Service em ambiente local
python scripts/manage_env.py whatsapp-service local

# Para configurar o WhatsApp Service em produção
python scripts/manage_env.py whatsapp-service production
```

O script irá automaticamente:
1. Identificar o serviço (api ou whatsapp-service)
2. Selecionar o ambiente correto (local ou production)
3. Copiar o arquivo de ambiente apropriado para o local correto
4. Gerar o arquivo `.env` necessário para o funcionamento do serviço

## Observações

- Os arquivos de ambiente da API estão na raiz do projeto
- Os arquivos de ambiente do WhatsApp Service estão em sua própria pasta
- O script `manage_env.py` gerencia automaticamente a localização correta dos arquivos
- As variáveis de ambiente são diferentes para cada serviço e ambiente
- O modo DEBUG está ativado apenas no ambiente local para facilitar o desenvolvimento 