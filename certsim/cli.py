import click
from certsim.certificate import create_certificate
from certsim.key_management import generate_keys
from certsim.signature import sign_document, verify_signature, sign_document_with_pkcs7, verify_pkcs7
from certsim.utils import console, ascii_art

@click.group(invoke_without_command=True)
@click.pass_context
def certsim(ctx):
    """🌐 CertSim: Simulador de Geração de Certificados Digitais."""
    if ctx.invoked_subcommand is None:
        console.print("[bold blue]" + ascii_art)  # Exibe a arte ASCII ao iniciar o CLI
        console.print("[yellow]Use um dos comandos abaixo para começar:[/]")
        console.print(" - generate-keys: Para gerar as chaves.")
        console.print(" - create-certificate: Para criar um certificado digital.")
        console.print(" - sign-document: Para assinar digitalmente um documento.")
        console.print(" - verify-signature: Para verificar a assinatura digital de um documento.")

# Comandos essenciais
certsim.add_command(generate_keys)
certsim.add_command(create_certificate)
certsim.add_command(sign_document)
certsim.add_command(verify_signature)
certsim.add_command(sign_document_with_pkcs7)
certsim.add_command(verify_pkcs7)

if __name__ == '__main__':
    certsim()
