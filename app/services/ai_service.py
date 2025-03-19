from anthropic import Anthropic
from fastapi import HTTPException
import os

class FinancialAdvisorService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
        self.system_prompt = """Você é um consultor financeiro especializado em análise de gastos pessoais.
        Suas respostas devem ser profissionais, claras, amigáveis e em português. Use um tom interativo e acolhedor para engajar o usuário."""

    async def analisar_transacoes(self, transacoes: list):
        try:
            mensagem = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{
                    "role": "system",
                    "content": self.system_prompt
                }, {
                    "role": "user",
                    "content": f"Analise estas transações e forneça insights úteis e amigáveis:\n{transacoes}"
                }]
            )
            return mensagem.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))