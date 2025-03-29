from decouple import config
import termcolor
import os


# Caminho do arquivo .env
ENV_PATH = ".env"

# Verifica se o arquivo .env existe
if not os.path.exists(ENV_PATH):
    with open(ENV_PATH, "w") as env_file:
        # Escreve as variáveis padrões no arquivo
        env_file.write("IP=127.0.0.1\n")
        env_file.write("PORT=8000\n")
        env_file.write("DATABASE_URL=sqlite:///./test.db\n")
    print(termcolor.colored(
        ".env criado com valores padrão. Por favor, revise e ajuste conforme necessário.",
        color="red",
        attrs=["bold"]
        )
    )

# Forçar o uso de localhost para desenvolvimento
IP = "127.0.0.1"  # Alterado de config("IP") para valor fixo
PORT = int(config("port", default=8000))
DATABASE_URL = config("DATABASE_URL")
