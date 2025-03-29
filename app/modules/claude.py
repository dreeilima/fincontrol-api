from typing import Dict, Any
from datetime import datetime
import anthropic

# Mensagens de resposta
REGISTRATION_INFO = """
🌟 *Bem-vindo ao FinControl!* 🌟

Para começar a gerenciar suas finanças de forma inteligente, você precisa criar sua conta em nosso site.

🌐 *Acesse:* {siteUrl}

✨ *No site você poderá:*
• 📝 Criar sua conta personalizada
• 💎 Escolher o plano ideal para você
• ⚙️ Configurar suas preferências
• 📱 Começar a usar o FinControl via WhatsApp

💡 *Dica:* Após criar sua conta, volte aqui e me envie um "oi" para começarmos essa jornada financeira juntos!
"""

WELCOME_REGISTERED_USER = """
👋 *Olá {name}!* 👋

Que alegria ter você de volta! Vou te ajudar a gerenciar suas finanças de forma simples e prática.

📱 *Como usar o FinControl*

1️⃣ *Registrar Receitas* 💰
   • "ganhei 1000 de salário"
   • "ganhei 500 de freela"
   • "ganhei 200 de investimentos"

2️⃣ *Registrar Despesas* 💸
   • "gastei 50 em almoço"
   • "gastei 200 em compras"
   • "gastei 100 em farmácia"

3️⃣ *Consultas* 📊
   • "💰 saldo" - Ver seu saldo atual
   • "📋 extrato" - Ver suas transações
   • "📈 relatório" - Ver relatórios
   • "📊 relatório diário" - Relatório do dia
   • "📊 relatório semanal" - Relatório da semana
   • "📊 relatório mensal" - Relatório do mês
   • "📊 relatório anual" - Relatório do ano

4️⃣ *Relatórios por Categoria* 🏷️
   • "relatório categoria alimentação"
   • "relatório categoria transporte"
   • "relatório categoria moradia"



💡 *Dicas Rápidas:*
• Use vírgula para centavos (ex: 10,50)
• Pode usar "ontem" ou "mês passado" nas descrições
• Categorias são detectadas automaticamente


❓ Use "ajuda" para ver mais detalhes sobre cada comando.

Como posso te ajudar hoje? 😊
"""

ERROR_MESSAGE = """
❌ *Ops! Algo deu errado* ❌

Não consegui processar sua solicitação. 

💡 *O que fazer?*
• Verifique se o comando está correto
• Use "❓ ajuda" para ver os comandos disponíveis
• Tente novamente com o formato correto

🔄 *Exemplo de uso correto:*
• "ganhei 1000 de salário"
• "gastei 50 em almoço"
"""

TRANSACTION_CONFIRMATION = """
✅ *Transação Registrada com Sucesso!* ✅

📝 *Detalhes da {type}:*
💰 Valor: R$ {amount}
📄 Descrição: {description}
🏷️ Categoria: {category}
📅 Data: {date}

🎯 *Dica:* 💰 digite "saldo" para ver seu saldo atual
"""

TRANSACTION_ERROR = """
❌ *Não consegui registrar sua {type}* ❌

💡 *Verifique se:*
• O valor está correto (ex: 10,50)
• A descrição está clara
• O formato está correto

📝 *Exemplos corretos:*
• "ganhei 1000 de salário"
• "gastei 50 em almoço"

❓ Use "ajuda" para ver mais exemplos e dicas.
"""

BALANCE_RESPONSE = """
💰 *Seu Saldo Atual* 💰
━━━━━━━━━━━━━━━━━━━━━

🏦 *R$ {balance}*
{status_emoji} Status: {status}

🔄 *Resumo Rápido:*
📈 Últimas receitas: R$ {total_receitas:.2f}
📉 Últimas despesas: R$ {total_despesas:.2f}

💡 *Dica:* Use "📋 extrato" para ver todas as transações.
"""

STATEMENT_RESPONSE = """
📋 *Seu Extrato Financeiro* 📋
━━━━━━━━━━━━━━━━━━━━━

📊 *Resumo Geral:*
📈 Receitas: R$ {total_receitas:.2f}
📉 Despesas: R$ {total_despesas:.2f}
💰 Saldo: R$ {saldo:.2f}

🔍 *Todas as Transações:*
{transactions_list}

💡 *Dica:* Use "📈 relatório" para ver análises mais detalhadas.
"""

REPORT_RESPONSE = """
📊 *Relatório {period_name}* 📊
━━━━━━━━━━━━━━━━━━━━━

💰 *Resumo Financeiro:*
📈 Receitas: R$ {receitas:.2f} ({num_receitas} transações)
📉 Despesas: R$ {despesas:.2f} ({num_despesas} transações)
💰 Saldo: {saldo_emoji} R$ {saldo:.2f}

📈 *Médias por Transação:*
📈 Receita média: R$ {media_receitas:.2f}
📉 Despesa média: R$ {media_despesas:.2f}

🏷️ *Top 5 Categorias:*
{lista_categorias}

💡 *Dicas:*
• Digite 'relatório categoria [nome]' para mais detalhes
• Use 'relatório [diário/semanal/mensal/anual]'

🎯 *Dica:* Quer ver o relatório de alguma categoria específica?
"""

CATEGORY_REPORT_RESPONSE = """
📊 *Relatório da Categoria: {category}* 📊
━━━━━━━━━━━━━━━━━━━━━

💰 *Resumo:*
📈 Total gasto: R$ {total:.2f}
📊 Média por transação: R$ {media:.2f}
🔄 Última transação: R$ {ultima:.2f}

{meses_list}

💡 *Dica:* Use "📋 extrato" para ver todas as transações desta categoria.
"""

EDIT_RESPONSE = """
✅ *Transação Atualizada com Sucesso!* ✅

📝 *Novos Detalhes:*
💰 Valor: R$ {valor:.2f}
📄 Descrição: {description}
🏷️ Categoria: {category}

💡 *Dica:* Use "📋 extrato" para ver todas as suas transações.
"""

NO_TRANSACTIONS = "📭 Nenhuma transação encontrada."
NO_TRANSACTIONS_BALANCE = "📭 Nenhuma transação encontrada. Seu saldo é R$ 0,00"
NO_TRANSACTIONS_STATEMENT = "📭 Nenhuma transação encontrada no seu extrato."
NO_TRANSACTIONS_CATEGORY = "❌ Nenhuma transação encontrada na categoria '{category}'"

HELP_MESSAGE = """
📱 *Comandos do FinControl* 📱
━━━━━━━━━━━━━━━━━━━━━

1️⃣ *Registrar Transações*
   • "ganhei 1000 de salário"
   • "ganhei 500 de freela"
   • "ganhei 200 de investimentos"
   • "gastei 50 em almoço"
   • "gastei 200 em compras"
   • "gastei 100 em farmácia"

   💡 *Dicas para registro:*
   • Use vírgula para centavos (ex: 10,50)
   • Pode usar "ontem" ou "mês passado" nas descrições
   • Categorias são detectadas automaticamente
   • Exemplos com datas: "ganhei 300 dia 15/03", "gastei 150 ontem"

2️⃣ *Consultas Básicas*
   • "💰 saldo" - Ver seu saldo atual e resumo das últimas transações
   • "📋 extrato" - Ver todas as suas transações com detalhes
   • "categorias" - Ver todas as suas categorias cadastradas

3️⃣ *Relatórios*
   • "📊 relatório" - Relatório mensal completo
   • "📊 relatório diário" - Relatório do dia atual
   • "📊 relatório semanal" - Relatório da semana atual
   • "📊 relatório mensal" - Relatório do mês atual
   • "📊 relatório anual" - Relatório do ano atual
   • "📊 relatório categoria [nome]" - Relatório específico de uma categoria

   💡 *Exemplos de relatórios por categoria:*
   • "relatório categoria alimentação"
   • "relatório categoria transporte"
   • "relatório categoria moradia"

4️⃣ *Gerenciar Categorias*
   • "nova categoria [nome]" - Criar uma nova categoria
   • "excluir categoria [nome]" - Excluir uma categoria existente

   💡 *Dicas para categorias:*
   • Use nomes simples e descritivos
   • Evite espaços no nome da categoria
   • Exemplos: alimentação, transporte, moradia, lazer, saúde

5️⃣ *Conselhos Financeiros*
   • "conselhos" - Receba uma análise completa das suas finanças
   • "dicas" - Sugestões personalizadas de economia e investimentos

   💡 *O que você receberá:*
   • Avaliação do seu cenário financeiro atual
   • Dicas específicas baseadas nos seus dados
   • Sugestões de melhorias
   • Recomendações de investimentos

6️⃣ *Ajuda*
   • "ajuda" - Ver todos os comandos disponíveis
   • "ajuda [comando]" - Ver detalhes de um comando específico

   💡 *Exemplos de ajuda específica:*
   • "ajuda saldo" - Detalhes sobre consulta de saldo
   • "ajuda relatório" - Detalhes sobre relatórios
   • "ajuda nova categoria" - Como criar categorias

❓ *Precisa de mais ajuda com algum comando específico?*
Digite "ajuda" seguido do comando que deseja saber mais.
"""

HELP_DETAILS = """
📚 *Detalhes do Comando: {command}* 📚
━━━━━━━━━━━━━━━━━━━━━

{details}

💡 *Exemplos:*
{examples}

❓ Precisa de mais ajuda com outro comando?
"""

HELP_DETAILS_MAP = {
    "ganhei": {
        "details": "Registra uma nova receita no sistema. Você pode incluir a data da transação usando 'dia DD/MM' ou palavras como 'ontem' ou 'mês passado'.",
        "examples": "• ganhei 1000 de salário\n• ganhei 500 de freela\n• ganhei 200 de investimentos\n• ganhei 300 dia 15/03\n• ganhei 400 ontem"
    },
    "gastei": {
        "details": "Registra uma nova despesa no sistema. Você pode incluir a data da transação usando 'dia DD/MM' ou palavras como 'ontem' ou 'mês passado'.",
        "examples": "• gastei 50 em almoço\n• gastei 200 em compras\n• gastei 100 em farmácia\n• gastei 150 dia 10/03\n• gastei 80 ontem"
    },
    "saldo": {
        "details": "Mostra seu saldo atual e um resumo das últimas transações, incluindo totais de receitas e despesas recentes.",
        "examples": "• saldo\n• 💰 saldo"
    },
    "extrato": {
        "details": "Mostra todas as suas transações com detalhes, incluindo data, valor, descrição e categoria. As transações são ordenadas da mais recente para a mais antiga.",
        "examples": "• extrato\n• 📋 extrato"
    },
    "relatório": {
        "details": "Gera relatórios financeiros detalhados. Você pode especificar o período (diário, semanal, mensal, anual) ou uma categoria específica.",
        "examples": "• relatório\n• relatório diário\n• relatório semanal\n• relatório mensal\n• relatório anual\n• relatório categoria alimentação"
    },
    "categorias": {
        "details": "Mostra todas as suas categorias cadastradas e o total gasto em cada uma.",
        "examples": "• categorias"
    },
    "conselhos": {
        "details": "Receba uma análise financeira personalizada baseada nos seus dados. O sistema analisa seu saldo, receitas, despesas e categorias para fornecer dicas específicas e sugestões de melhorias.",
        "examples": "• conselhos\n• dicas\n• 💡 conselhos"
    }
}

async def generateResponse(context: Dict[str, Any]) -> str:
    """
    Gera uma resposta baseada no contexto fornecido.
    
    Args:
        context (Dict[str, Any]): Contexto com as informações necessárias para gerar a resposta
        
    Returns:
        str: Mensagem formatada
    """
    try:
        print(f"\n=== GERANDO RESPOSTA ===")
        print(f"Contexto recebido: {context}")
        
        response_type = context.get("type")
        print(f"Tipo de resposta: {response_type}")
        
        if response_type == "INCOME":
            if context.get("step") == "CONFIRMATION":
                return TRANSACTION_CONFIRMATION.format(
                    type="receita",
                    amount=context.get("amount", 0),
                    description=context.get("description", ""),
                    category=context.get("category", ""),
                    date=context.get("date", "")
                )
            elif context.get("step") == "ERROR":
                return TRANSACTION_ERROR.format(type="receita")
            return "❌ Desculpe, ocorreu um erro ao processar sua receita."
            
        elif response_type == "EXPENSE":
            if context.get("step") == "CONFIRMATION":
                return TRANSACTION_CONFIRMATION.format(
                    type="despesa",
                    amount=context.get("amount", 0),
                    description=context.get("description", ""),
                    category=context.get("category", ""),
                    date=context.get("date", "")
                )
            elif context.get("step") == "ERROR":
                return TRANSACTION_ERROR.format(type="despesa")
            return "❌ Desculpe, ocorreu um erro ao processar sua despesa."
            
        elif response_type == "REGISTRATION_INFO":
            return REGISTRATION_INFO.format(siteUrl=context.get("siteUrl", ""))
            
        elif response_type == "WELCOME_REGISTERED_USER":
            return WELCOME_REGISTERED_USER.format(name=context.get("userName", ""))
            
        elif response_type == "ERROR":
            error_type = context.get("errorType", "")
            if error_type == "TRANSACTION_NOT_FOUND":
                return "❌ Transação não encontrada. Verifique o ID e tente novamente."
            return "❌ Ocorreu um erro. Tente novamente mais tarde."
            
        elif response_type == "TRANSACTION":
            print(f"Step: {context.get('step')}")
            if context.get("step") == "CONFIRMATION":
                tipo = "despesa" if context.get("type") == "EXPENSE" else "receita"
                print(f"Tipo: {tipo}")
                print(f"Amount: {context.get('amount')}")
                print(f"Description: {context.get('description')}")
                print(f"Category: {context.get('category')}")
                print(f"Date: {context.get('date')}")
                
                return TRANSACTION_CONFIRMATION.format(
                    type=tipo,
                    amount=context.get("amount", 0),
                    description=context.get("description", ""),
                    category=context.get("category", ""),
                    date=context.get("date", "")
                )
            elif context.get("step") == "ERROR":
                return TRANSACTION_ERROR.format(type=context.get("type", ""))
            return "❌ Desculpe, ocorreu um erro ao processar sua transação."
            
        elif response_type == "BALANCE":
            return BALANCE_RESPONSE.format(
                balance=context.get("balance", 0),
                status_emoji=context.get("status_emoji", ""),
                status=context.get("status", ""),
                total_receitas=context.get("total_receitas", 0),
                total_despesas=context.get("total_despesas", 0)
            )
            
        elif response_type == "STATEMENT":
            return STATEMENT_RESPONSE.format(
                total_receitas=context.get("total_receitas", 0),
                total_despesas=context.get("total_despesas", 0),
                saldo=context.get("saldo", 0),
                transactions_list=context.get("transactions_list", "")
            )
            
        elif response_type == "REPORT":
            period_name = context.get("period_name", "")
            receitas = context.get("receitas", 0)
            num_receitas = context.get("num_receitas", 0)
            despesas = context.get("despesas", 0)
            num_despesas = context.get("num_despesas", 0)
            saldo_emoji = context.get("saldo_emoji", "➡️")
            saldo = context.get("saldo", 0)
            media_receitas = context.get("media_receitas", 0)
            media_despesas = context.get("media_despesas", 0)
            lista_categorias = context.get("lista_categorias", "")
            instrucoes = context.get("instrucoes", "")
            
            message = f"📊 Relatório {period_name} 📊\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            message += f"💰 Resumo Financeiro:\n"
            message += f"📈 Receitas: R$ {receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" ({num_receitas} transações)\n"
            message += f"📉 Despesas: R$ {despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" ({num_despesas} transações)\n"
            message += f"💰 Saldo: {saldo_emoji} R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n\n"
            
            message += f"📈 Médias por Transação:\n"
            message += f"📈 Receita média: R$ {media_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n"
            message += f"📉 Despesa média: R$ {media_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n\n"
            
            message += f"🏷 Top 5 Categorias:\n{lista_categorias}\n"
            
            message += f"\n💡 Dicas:\n"
            message += f"• Digite 'relatório categoria [nome]' para mais detalhes\n"
            message += f"• Use 'relatório [diário/semanal/mensal/anual]'\n\n"
            message += f"🎯 Dica: Quer ver o relatório de alguma categoria específica?\n"
            message += f"{instrucoes}"
            return message
            
        elif response_type == "CATEGORY_REPORT":
            category = context.get("category", "")
            total = context.get("total", 0)
            media = context.get("media", 0)
            ultima = context.get("ultima", 0)
            meses_list = context.get("meses_list", "")
            
            if total == 0:
                return f"📊 Relatório da Categoria: {category} 📊\n━━━━━━━━━━━━━━━━━━━━━\n\nNenhuma transação encontrada para esta categoria."
            
            # Formatar mensagem
            message = f"📊 Relatório da Categoria: {category} 📊\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            message += f"💰 Resumo:\n"
            message += f"📈 Total gasto: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n"
            message += f"📊 Média por transação: R$ {media:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n"
            message += f"🔄 Última transação: R$ {ultima:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n\n"
            
            # Adicionar gastos por mês
            message += f"{meses_list}"
            
            message += f"\n💡 Dica: Use \"📋 extrato\" para ver todas as transações desta categoria."
            return message
            
        elif response_type == "EDIT":
            tipo = context.get("tipo", "")
            valor = context.get("valor", 0)
            description = context.get("description", "")
            category = context.get("category", "")
            
            message = f"✅ Transação atualizada com sucesso!\n\n"
            message += f"📝 Detalhes:\n"
            message += f"• Tipo: {tipo}\n"
            message += f"• Valor: R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n"
            message += f"• Descrição: {description}\n"
            message += f"• Categoria: {category}\n\n"
            message += f"💡 Use 'extrato' para ver todas as transações."
            return message
            
        elif response_type == "DELETE":
            message = f"✅ Transação excluída com sucesso!\n\n"
            message += f"💡 Use 'extrato' para ver todas as transações."
            return message
            
        elif response_type == "NO_TRANSACTIONS":
            return NO_TRANSACTIONS
            
        elif response_type == "NO_TRANSACTIONS_BALANCE":
            return NO_TRANSACTIONS_BALANCE
            
        elif response_type == "NO_TRANSACTIONS_STATEMENT":
            return NO_TRANSACTIONS_STATEMENT
            
        elif response_type == "NO_TRANSACTIONS_CATEGORY":
            return NO_TRANSACTIONS_CATEGORY.format(category=context.get("category", ""))
            
        elif response_type == "WEEKLY_REPORT":
            receitas = context.get("receitas", 0)
            despesas = context.get("despesas", 0)
            saldo = context.get("saldo", 0)
            media_receita = context.get("media_receita", 0)
            media_despesa = context.get("media_despesa", 0)
            top_categorias = context.get("top_categorias", [])
            total_receitas = context.get("total_receitas", 0)
            total_despesas = context.get("total_despesas", 0)
            
            message = f"📊 Relatório Semanal 📊\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            message += f"💰 Resumo Financeiro:\n"
            message += f"📈 Receitas: R$ {receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" ({total_receitas} transações)\n"
            message += f"📉 Despesas: R$ {despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" ({total_despesas} transações)\n"
            message += f"💰 Saldo: {'↗' if saldo >= 0 else '↘'} R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n\n"
            
            message += f"📈 Médias por Transação:\n"
            message += f"📈 Receita média: R$ {media_receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n"
            message += f"📉 Despesa média: R$ {media_despesa:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n\n"
            
            message += f"🏷 Top 5 Categorias:\n"
            for cat in top_categorias:
                message += f"• {cat['name']}: R$ {cat['amount']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" ({cat['count']} transações)\n"
            
            message += f"\n💡 Dicas:\n"
            message += f"• Digite 'relatório categoria [nome]' para mais detalhes\n"
            message += f"• Use 'relatório [diário/semanal/mensal/anual]'\n\n"
            message += f"🎯 Dica: Quer ver o relatório de alguma categoria específica?"
            return message
            
        elif response_type == "HELP_MESSAGE":
            return HELP_MESSAGE
            
        elif response_type == "HELP_DETAILS":
            command = context.get("command", "")
            details = HELP_DETAILS_MAP.get(command, {
                "details": "Comando não encontrado.",
                "examples": "Use 'ajuda' para ver todos os comandos disponíveis."
            })
            return HELP_DETAILS.format(
                command=command,
                details=details["details"],
                examples=details["examples"]
            )
            
        elif response_type == "FINANCIAL_ADVICE":
            # Encaminhar para o claude.js
            return None
            
        else:
            print(f"Tipo de resposta não reconhecido: {response_type}")
            return "❓ Desculpe, não entendi sua solicitação. Use 'ajuda' para ver os comandos disponíveis."
            
    except Exception as e:
        print(f"Erro ao gerar resposta: {str(e)}")
        return "❌ Desculpe, ocorreu um erro ao gerar a resposta." 