import os
import click
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from certsim.utils import console, get_user_folder, get_default_user_name

@click.command()
def generate_keys():
    """🔑 Gera um par de chaves RSA e salva as chaves privada e pública na pasta do usuário."""
    user_name = get_default_user_name()
    folder_path = get_user_folder(user_name)
    console.print(f"🔧 Gerando chaves para {user_name}...")

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key_path = os.path.join(folder_path, "chave_privada.pem")
    public_key_path = os.path.join(folder_path, "chave_publica.pem")

    password = click.prompt("🔐 Insira uma senha para criptografar a chave privada", hide_input=True, confirmation_prompt=True)
    
    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
        ))

    with open(public_key_path, "wb") as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    console.print(f"[green]✔️ Chave privada e pública geradas e salvas em {folder_path}.")

def load_private_key(folder_path):
    """Carrega a chave privada do arquivo."""
    password = click.prompt("🔐 Insira a senha para desbloquear a chave privada", hide_input=True)
    private_key_path = os.path.join(folder_path, "chave_privada.pem")
    try:
        with open(private_key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=password.encode()
            )
        console.print("[green]🔓 Chave privada carregada com sucesso.[/]")
        return private_key
    except Exception as e:
        console.print(f"[red]❌ Falha ao carregar a chave privada: {e}")
        return None
