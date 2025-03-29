import os
import shutil
import sys

def setup_environment(service, env_type):
    """
    Configura o ambiente baseado no serviço e tipo especificado
    """
    if env_type not in ['local', 'production']:
        print("Erro: Tipo de ambiente deve ser 'local' ou 'production'")
        sys.exit(1)

    if service not in ['api', 'whatsapp-service']:
        print("Erro: Serviço deve ser 'api' ou 'whatsapp-service'")
        sys.exit(1)

    # Define o caminho do arquivo de ambiente baseado no serviço
    if service == 'api':
        env_file = f'.env.{env_type}'  # Na raiz para a API
    else:
        env_file = f'{service}/.env.{env_type}'  # Na pasta do serviço para WhatsApp
    
    if not os.path.exists(env_file):
        print(f"Erro: Arquivo {env_file} não encontrado")
        sys.exit(1)

    # Define o caminho do arquivo .env de destino
    if service == 'api':
        target_env = '.env'  # Na raiz para a API
    else:
        target_env = f'{service}/.env'  # Na pasta do serviço para WhatsApp

    # Copia o arquivo de ambiente apropriado
    shutil.copy2(env_file, target_env)
    print(f"Ambiente configurado para {service} em modo {env_type}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python manage_env.py [api|whatsapp-service] [local|production]")
        sys.exit(1)
    
    setup_environment(sys.argv[1], sys.argv[2]) 