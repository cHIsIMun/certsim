import os
import re
from rich.console import Console

console = Console()

# Arte ASCII opcional para CLI
ascii_art = r"""
  /$$$$$$                        /$$      /$$$$$$  /$$              
 /$$__  $$                      | $$     /$$__  $$|__/              
| $$  \__/  /$$$$$$   /$$$$$$  /$$$$$$  | $$  \__/ /$$ /$$$$$$/$$$$ 
| $$       /$$__  $$ /$$__  $$|_  $$_/  |  $$$$$$ | $$| $$_  $$_  $$
| $$      | $$$$$$$$| $$  \__/  | $$     \____  $$| $$| $$ \ $$ \ $$
| $$    $$| $$_____/| $$        | $$ /$$ /$$  \ $$| $$| $$ | $$ | $$
|  $$$$$$/|  $$$$$$$| $$        |  $$$$/|  $$$$$$/| $$| $$ | $$ | $$
 \______/  \_______/|__/         \___/   \______/ |__/|__/ |__/ |__/
"""

def get_default_user_name():
    """Obtém o nome da máquina (hostname) para usar como nome de usuário padrão."""
    if os.name == 'nt':  # Verifica se é Windows
        return os.getenv('COMPUTERNAME')
    else:  # Para Linux e Mac
        return os.uname().nodename

def get_user_folder(user_name):
    """Cria e retorna o diretório do usuário, baseado no nome fornecido."""
    folder_name = re.sub(r'\s+', '_', user_name.strip().lower())
    folder_path = os.path.join(os.getcwd(), folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path
