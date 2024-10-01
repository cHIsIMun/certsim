import os
import pytest
import logging
from unittest.mock import patch
from click.testing import CliRunner
from certsim.cli import certsim
from rich.console import Console
from time import sleep

# Configurar o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Criar um console Rich para exibição de mensagens
console = Console()

# Função para obter o nome da máquina
def get_machine_name():
    """Retorna o nome da máquina (hostname)"""
    if os.name == 'nt':
        return os.getenv('COMPUTERNAME')
    else:
        return os.uname().nodename

# Nome da pasta com o nome da máquina
MACHINE_NAME = get_machine_name()

# Caminhos para arquivos gerados durante os testes
PRIVATE_KEY_PATH = os.path.join(MACHINE_NAME, "chave_privada.pem")
CERTIFICATE_PATH = os.path.join(MACHINE_NAME, "certificado.pem")
SIGNATURE_PATH = os.path.join(MACHINE_NAME, "assinatura_digital.txt")
DOCUMENT_PATH = os.path.join(MACHINE_NAME, "test_document.txt")
CERT_ASSINATURA_PATH = os.path.join(MACHINE_NAME, "certificado_assinatura.pem")

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Remover arquivos antigos
    console.print("🧹 [cyan]Setup: Removendo arquivos antigos...[/]")
    yield
    # Teardown: Remover arquivos gerados após os testes
    console.print("🧹 [cyan]Teardown: Removendo arquivos gerados durante o teste.[/]")
    for path in [PRIVATE_KEY_PATH, CERTIFICATE_PATH, SIGNATURE_PATH, DOCUMENT_PATH, CERT_ASSINATURA_PATH]:
        if os.path.exists(path):
            os.remove(path)


def generate_keys(runner):
    """Função para geração de chaves privada e pública."""
    console.print("🔑 [yellow]Gerando chaves...[/]")
    
    # Rodando o comando generate-keys
    result = runner.invoke(certsim, ['generate-keys'], input='password\npassword\n')

    # Mostrando a saída completa do CLI para debugar
    console.print(result.output)
    
    assert result.exit_code == 0, "❌ [red]Erro na geração de chaves.[/]"
    assert os.path.exists(PRIVATE_KEY_PATH), "❌ [red]A chave privada não foi gerada.[/]"
    console.print("✔️ [green]Geração de chaves concluída com sucesso![/]")
    sleep(1)


def create_certificate(runner):
    """Função para criação de certificado digital."""
    console.print("📜 [yellow]Criando certificado...[/]")
    input_data = (
        'BR\n'            # Nome do país
        'TO\n'            # Estado/Província
        'Palmas\n'        # Localidade
        'FC Solutions\n'  # Nome da organização
        'Lucas Vinicius Oliveira Cardoso\n'  # Nome comum
        'password\n'      # Senha para carregar a chave privada
    )
    result = runner.invoke(certsim, ['create-certificate'], input=input_data)
    assert result.exit_code == 0, f"❌ [red]Erro na criação do certificado.[/]"
    assert os.path.exists(CERTIFICATE_PATH), "❌ [red]O certificado digital não foi gerado.[/]"
    console.print("✔️ [green]Criação do certificado concluída com sucesso![/]")
    sleep(1)


def sign_document(runner):
    """Função para assinatura de um documento e anexação do certificado."""
    console.print("✍️ [yellow]Assinando documento...[/]")
    # Criar um documento de teste e escrever um conteúdo
    with open(DOCUMENT_PATH, 'w') as f:
        f.write("Este é um documento de teste para assinatura digital.")
    console.print(f"📄 [cyan]Documento de teste criado em {DOCUMENT_PATH}[/]")
    sleep(1)

    # Mock do Tkinter para simular a seleção de arquivo e certificado
    with patch('certsim.signature.askopenfilename', side_effect=[DOCUMENT_PATH, CERTIFICATE_PATH]):
        result = runner.invoke(certsim, ['sign-document'], input='password\n')
    console.print(result.output)  # Para depurar possíveis erros
    assert result.exit_code == 0, "❌ [red]Erro na assinatura do documento.[/]"
    assert os.path.exists(SIGNATURE_PATH), "❌ [red]A assinatura digital não foi gerada.[/]"
    assert os.path.exists(CERT_ASSINATURA_PATH), "❌ [red]O certificado não foi anexado corretamente.[/]"
    console.print("✔️ [green]Assinatura do documento e anexação do certificado concluídas com sucesso![/]")
    sleep(1)



def verify_signature(runner):
    """Função para verificação de uma assinatura digital válida."""
    console.print("🔍 [yellow]Verificando assinatura digital...[/]")
    # Verificar a assinatura com mock do Tkinter para selecionar documento, assinatura e certificado
    with patch('certsim.signature.askopenfilename', side_effect=[DOCUMENT_PATH, SIGNATURE_PATH, CERT_ASSINATURA_PATH]):
        result = runner.invoke(certsim, ['verify-signature'])
    console.print(result.output)  # Para depurar possíveis erros
    assert result.exit_code == 0, "❌ [red]Erro na verificação da assinatura digital.[/]"
    assert "Assinatura válida" in result.output, "❌ [red]A assinatura digital não foi validada corretamente.[/]"
    assert "Assinado por" in result.output, "❌ [red]Os detalhes do certificado não foram exibidos corretamente.[/]"
    console.print("✔️ [green]Verificação de assinatura e detalhes do certificado concluídos com sucesso![/]")
    sleep(1)




def verify_signature_failure(runner):
    """Função para verificação de uma assinatura digital após alteração do documento."""
    console.print("🛑 [yellow]Verificando assinatura com documento alterado...[/]")
    # Alterar o documento após a assinatura
    with open(DOCUMENT_PATH, 'w') as f:
        f.write("Este é um documento de teste ALTERADO para verificação da assinatura digital.")

    console.print(f"📄 [cyan]Documento alterado e salvo novamente em {DOCUMENT_PATH}[/]")
    sleep(1)

    # Verificar a assinatura com mock do Tkinter
    with patch('certsim.signature.askopenfilename', side_effect=[DOCUMENT_PATH, SIGNATURE_PATH, CERT_ASSINATURA_PATH]):
        result = runner.invoke(certsim, ['verify-signature'])
    console.print(result.output)  # Para depurar possíveis erros
    assert result.exit_code == 0, "❌ [red]Erro na verificação da assinatura digital.[/]"
    assert "Assinatura inválida" in result.output, "❌ [red]A alteração no documento não foi detectada.[/]"
    console.print("✔️ [green]Verificação de assinatura com documento alterado concluída com sucesso![/]")
    sleep(1)


def test_full_sequence():
    """Teste completo de ponta a ponta, executando todas as validações na ordem correta."""
    runner = CliRunner()

    # Executar todas as funções sequencialmente
    generate_keys(runner)
    create_certificate(runner)
    sign_document(runner)
    verify_signature(runner)
    verify_signature_failure(runner)
