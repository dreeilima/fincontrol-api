import httpx
from typing import Optional, Dict, Any
from app.core.config import settings
from ..modules.claude import generateResponse

class WhatsAppService:
    def __init__(self, base_url: str, secret_key: str):
        self.base_url = base_url.rstrip('/')
        self.secret_key = secret_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.secret_key}"}
        )

    async def send_message(self, to: str, message: str):
        try:
            response = await self.client.post("/send", json={
                "to": to,
                "text": message
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            raise

    async def get_qr(self):
        try:
            print(f"Solicitando QR code de: {self.base_url}/qr")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(f"{self.base_url}/qr", 
                                           headers={"Authorization": f"Bearer {self.secret_key}"})
                response.raise_for_status()
                qr_data = response.json()
                print(f"QR code recebido com sucesso, tamanho: {len(str(qr_data))}")
                return qr_data
        except Exception as e:
            print(f"Erro ao obter QR code: {str(e)}")
            print(f"URL: {self.base_url}/qr")
            print(f"Secret key: {'*' * len(self.secret_key)}")
            raise

    async def register_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra uma nova transação.
        
        Args:
            data (Dict[str, Any]): Dados da transação
            
        Returns:
            Dict[str, Any]: Dados da transação registrada
        """
        try:
            print(f"\n=== REGISTRANDO TRANSAÇÃO ===")
            print(f"Dados: {data}")
            
            response = await self.client.post("/webhook", json=data)
            response.raise_for_status()
            result = response.json()
            
            print(f"Transação registrada com sucesso: {result}")
            return result
            
        except Exception as e:
            print(f"Erro ao registrar transação: {str(e)}")
            raise

    async def generate_response(self, context: dict) -> str:
        """
        Gera uma resposta usando o módulo Claude.
        
        Args:
            context (Dict[str, Any]): Contexto com as informações necessárias para gerar a resposta
            
        Returns:
            str: Mensagem formatada
        """
        try:
            return await generateResponse(context)
        except Exception as e:
            print(f"Erro ao gerar resposta: {str(e)}")
            return "Desculpe, ocorreu um erro ao gerar a resposta."

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()