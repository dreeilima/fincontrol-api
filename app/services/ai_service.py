from anthropic import Anthropic
from fastapi import HTTPException
import os

class FinancialAdvisorService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
        self.system_prompt = """Você é um consultor financeiro especializado em análise de gastos pessoais.
        Suas respostas devem ser profissionais, claras, amigáveis e em português. Use um tom interativo e acolhedor para engajar o usuário."""

    async def analisar_transacoes(self, context: dict):
        try:
            is_advice = context.get("message", "").lower().includes("conselhos")
            is_tips = context.get("message", "").lower().includes("dicas")
            financial_context = context.get("financialContext", {})
            
            prompt = f"""Analise o cenário financeiro do usuário e forneça uma análise personalizada.

Contexto Financeiro:
- Saldo atual: {financial_context.get("balance", "R$ 0,00")}
- Receitas do mês: {financial_context.get("monthlyIncome", "R$ 0,00")}
- Despesas do mês: {financial_context.get("monthlyExpenses", "R$ 0,00")}
- Categorias com mais gastos: {financial_context.get("topExpenseCategories", "Nenhum gasto registrado")}
- Tendências: {financial_context.get("trends", "Nenhuma tendência identificada")}

{'Gere uma análise financeira estratégica seguindo EXATAMENTE este formato:' if is_advice else 
'Gere dicas práticas de economia seguindo EXATAMENTE este formato:' if is_tips else 
'Gere uma análise financeira personalizada seguindo EXATAMENTE este formato:'}

💡 *{'Análise Financeira Estratégica' if is_advice else 'Dicas Práticas de Economia' if is_tips else 'Análise Financeira Personalizada'}*
━━━━━━━━━━━━━━━━━━━━━

[Primeiro Parágrafo - {'Avaliação do Cenário' if is_advice else 'Dicas para Categorias Principais' if is_tips else 'Avaliação do Cenário'}]
• {'Analise o saldo atual e tendências' if is_advice else 'Sugira reduções específicas de gastos' if is_tips else 'Analise o saldo atual e tendências'}
• {'Destaque pontos positivos e pontos de atenção' if is_advice else 'Foque nas categorias com mais despesas' if is_tips else 'Destaque pontos positivos e pontos de atenção'}
• {'Mencione padrões de gastos identificados' if is_advice else 'Use emojis divertidos (💡, 🎯, 💪)' if is_tips else 'Mencione padrões de gastos identificados'}

[Segundo Parágrafo - {'Recomendações Estratégicas' if is_advice else 'Truques do Dia a Dia' if is_tips else 'Recomendações Específicas'}]
• {'Sugira melhorias específicas para cada categoria' if is_advice else 'Dê exemplos práticos e acionáveis' if is_tips else 'Sugira melhorias para cada categoria'}
• {'Proponha metas financeiras realistas' if is_advice else 'Sugira substituições inteligentes' if is_tips else 'Proponha metas financeiras realistas'}
• {'Inclua sugestões de investimentos' if is_advice else 'Inclua dicas de economia doméstica' if is_tips else 'Inclua sugestões de investimentos'}

[Terceiro Parágrafo - {'Plano de Ação' if is_advice else 'Hábitos Positivos' if is_tips else 'Ações Práticas'}]
• {'Liste 2-3 ações concretas para implementar agora' if is_advice else 'Liste 2-3 hábitos simples para implementar' if is_tips else 'Liste 2-3 ações concretas para implementar'}
• {'Mantenha o tom motivador e profissional' if is_advice else 'Mantenha o tom leve e motivador' if is_tips else 'Mantenha o tom motivador e profissional'}

IMPORTANTE: 
1. Siga exatamente este formato, incluindo os emojis e a formatação markdown
2. Não inclua títulos adicionais
3. Não use listas com bullets (•) no texto
4. Escreva em parágrafos contínuos
5. Use os emojis sugeridos no início de cada parágrafo
6. {'Mantenha o tom profissional e estratégico' if is_advice else 'Mantenha o tom leve e motivador' if is_tips else 'Mantenha o tom profissional e motivador'}
7. Não adicione linhas em branco extras entre os parágrafos"""

            mensagem = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{
                    "role": "system",
                    "content": self.system_prompt
                }, {
                    "role": "user",
                    "content": prompt
                }]
            )
            return mensagem.content[0].text
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))