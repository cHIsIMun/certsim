import os
import click
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID
from cryptography import x509
from datetime import datetime, timedelta, timezone
from certsim.key_management import load_private_key
from certsim.utils import console, get_user_folder, get_default_user_name

@click.command()
def create_certificate():
    """📝 Cria um certificado digital X.509 com informações específicas."""
    user_name = get_default_user_name()  # Usa o nome da máquina como nome do usuário
    folder_path = get_user_folder(user_name)
    private_key_path = os.path.join(folder_path, "chave_privada.pem")
    
    if not os.path.exists(private_key_path):
        console.print("[red]❌ Arquivo 'chave_privada.pem' não encontrado. Por favor, gere a chave privada primeiro usando 'generate_keys'.[/]")
        return
    
    # Solicitar informações do usuário com valores padrão
    country = click.prompt("🌍 Nome do país", default="BR")
    state = click.prompt("🏞️ Estado/Província", default="TO")
    locality = click.prompt("🏙️ Localidade", default="Palmas")
    organization = click.prompt("🏢 Nome da organização", default="FC Solutions")
    common_name = click.prompt("👤 Nome comum", default=user_name)
    valid_from = datetime.now(timezone.utc)
    valid_to = valid_from + timedelta(days=365)

    console.print(f"📄 [cyan]Criando certificado digital para {common_name}...[/]")
    
    private_key = load_private_key(folder_path)
    if private_key is None:
        return
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    
    cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
        private_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(
        valid_from).not_valid_after(valid_to).sign(private_key, hashes.SHA256())

    cert_path = os.path.join(folder_path, "certificado.pem")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(encoding=serialization.Encoding.PEM))
    
    console.print(f"[green]✔️ Certificado gerado e salvo como '{cert_path}'.")
