import os
import click
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import pkcs7, Encoding
from cryptography.hazmat.primitives.serialization.pkcs7 import PKCS7Options
from certsim.key_management import load_private_key
from certsim.utils import console, get_user_folder, get_default_user_name
from cryptography import x509
from cryptography.x509.oid import NameOID
from tkinter import Tk, Text, Toplevel, Scrollbar, RIGHT, LEFT, Y, BOTH, Canvas
import mimetypes
import fitz
from tkinter.filedialog import askopenfilename, askdirectory
from OpenSSL import crypto
from asn1crypto import cms, pem


@click.command()
def sign_document():
    """✍️ Assina digitalmente um documento usando a chave privada e anexa o certificado."""
    user_name = get_default_user_name()
    folder_path = get_user_folder(user_name)
    private_key_path = os.path.join(folder_path, "chave_privada.pem")
    cert_path = os.path.join(folder_path, "certificado.pem")

    if not os.path.exists(private_key_path):
        console.print("[red]❌ Arquivo 'chave_privada.pem' não encontrado. Por favor, gere a chave privada primeiro usando 'generate_keys'.[/]")
        return

    if not os.path.exists(cert_path):
        console.print("[red]❌ Certificado não encontrado. Por favor, gere o certificado primeiro usando 'create_certificate'.[/]")
        return

    console.print("📂 Abrindo seletor de arquivos...")
    root = Tk()
    root.withdraw()  # Esconde a janela principal do tkinter
    document_path = askopenfilename(title="Selecione o documento para assinar")

    if not document_path or not os.path.exists(document_path):
        console.print("[red]❌ Nenhum arquivo válido selecionado.[/]")
        return

    # Solicitar o diretório de destino para salvar a pasta com a assinatura, certificado e documento original
    console.print("📂 Selecione o diretório para salvar a assinatura, o certificado e o documento original.")
    save_directory = askdirectory(title="Selecione o diretório para salvar os arquivos")
    
    if not save_directory:
        console.print("[red]❌ Nenhum diretório selecionado.[/]")
        return

    # Criar a pasta principal e a subpasta 'document'
    output_folder = os.path.join(save_directory, "assinatura_com_certificado")
    os.makedirs(output_folder, exist_ok=True)

    document_folder = os.path.join(output_folder, "document")
    os.makedirs(document_folder, exist_ok=True)

    # Copiar o documento original para a subpasta 'document'
    document_name = os.path.basename(document_path)
    document_destination = os.path.join(document_folder, document_name)
    try:
        with open(document_path, "rb") as src, open(document_destination, "wb") as dst:
            dst.write(src.read())
        console.print(f"[green]✔️ Documento original salvo na subpasta '{document_folder}'.")
    except Exception as e:
        console.print(f"[red]❌ Erro ao salvar o documento original: {e}")
        return

    # Assinar o documento
    with open(document_destination, "rb") as file:
        document_content = file.read()

    private_key = load_private_key(folder_path)
    if private_key is None:
        return

    console.print("✍️ Assinando o documento...")
    signature = private_key.sign(
        document_content,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Salvar a assinatura digital na pasta de saída
    signature_file_path = os.path.join(output_folder, "assinatura_digital.txt")
    with open(signature_file_path, "wb") as signature_file:
        signature_file.write(signature)

    # Copiar o certificado para a mesma pasta da assinatura
    signed_cert_path = os.path.join(output_folder, "certificado_assinatura.pem")
    try:
        with open(cert_path, "rb") as cert_file:
            with open(signed_cert_path, "wb") as signed_cert_file:
                signed_cert_file.write(cert_file.read())
        console.print(f"[green]✔️ Certificado e assinatura salvos com sucesso na pasta '{output_folder}'.")
    except Exception as e:
        console.print(f"[red]❌ Erro ao salvar o certificado: {e}")

@click.command()
def sign_document_with_pkcs7():
    """✍️ Assina digitalmente um documento e empacota em PKCS#7."""
    user_name = get_default_user_name()
    folder_path = get_user_folder(user_name)
    private_key_path = os.path.join(folder_path, "chave_privada.pem")
    cert_path = os.path.join(folder_path, "certificado.pem")

    if not os.path.exists(private_key_path):
        console.print("[red]❌ Arquivo 'chave_privada.pem' não encontrado. Por favor, gere a chave privada primeiro usando 'generate_keys'.[/]")
        return

    if not os.path.exists(cert_path):
        console.print("[red]❌ Certificado não encontrado. Por favor, gere o certificado primeiro usando 'create_certificate'.[/]")
        return

    console.print("📂 Abrindo seletor de arquivos...")
    root = Tk()
    root.withdraw()  # Esconde a janela principal do tkinter
    document_path = askopenfilename(title="Selecione o documento para assinar")

    if not document_path or not os.path.exists(document_path):
        console.print("[red]❌ Nenhum arquivo válido selecionado.[/]")
        return

    # Solicitar o diretório de destino
    console.print("📂 Selecione o diretório para salvar o arquivo PKCS#7 assinado.")
    save_directory = askdirectory(title="Selecione o diretório para salvar o arquivo PKCS#7")

    if not save_directory:
        console.print("[red]❌ Nenhum diretório selecionado.[/]")
        return

    with open(document_path, "rb") as file:
        document_content = file.read()

    # Usar o método `load_private_key` existente para carregar a chave privada
    private_key = load_private_key(folder_path)
    if private_key is None:
        return

    # Carregar o certificado digital
    with open(cert_path, "rb") as f:
        cert_pem = f.read()
        cert = x509.load_pem_x509_certificate(cert_pem)

    # Assinar o documento com PKCS#7 (CMS) e embutir o conteúdo
    console.print("✍️ Assinando o documento e criando o PKCS#7...")

    # Criar a assinatura PKCS#7 e embutir o conteúdo do documento
    signed_data = pkcs7.PKCS7SignatureBuilder().set_data(document_content).add_signer(
        cert,
        private_key,
        hashes.SHA256()
    ).sign(Encoding.DER, [PKCS7Options.Binary])

    # Salvar o arquivo PKCS#7 (DER)
    output_pkcs7_path = os.path.join(save_directory, "documento_assinado.pkcs7")
    with open(output_pkcs7_path, "wb") as f:
        f.write(signed_data)

    console.print(f"[green]✔️ Documento empacotado com PKCS#7 e salvo em '{output_pkcs7_path}'.")

@click.command()
def verify_signature():
    """🔍 Verifica a assinatura digital de um documento usando o certificado anexado e exibe detalhes sobre quem assinou."""
    user_name = get_default_user_name()
    folder_path = get_user_folder(user_name)

    # Abrir o documento original
    console.print("📂 Abrindo seletor de arquivos para o documento original...")
    root = Tk()
    root.withdraw()
    document_path = askopenfilename(title="Selecione o documento original para verificar")

    if not document_path or not os.path.exists(document_path):
        console.print("[red]❌ Nenhum arquivo de documento válido selecionado.[/]")
        return

    # Abrir o arquivo de assinatura digital
    console.print("📂 Abrindo seletor de arquivos para a assinatura digital...")
    signature_path = askopenfilename(title="Selecione o arquivo da assinatura digital")

    if not signature_path or not os.path.exists(signature_path):
        console.print("[red]❌ Nenhum arquivo de assinatura válido selecionado.[/]")
        return

    # Abrir o certificado associado à assinatura
    console.print("📂 Abrindo seletor de arquivos para o certificado associado...")
    cert_path = askopenfilename(title="Selecione o certificado digital (certificado_assinatura.pem)")

    if not cert_path or not os.path.exists(cert_path):
        console.print("[red]❌ Nenhum certificado válido selecionado.[/]")
        return

    # Carregar o documento original
    with open(document_path, "rb") as file:
        document_content = file.read()

    # Carregar a assinatura digital
    with open(signature_path, "rb") as sig_file:
        signature = sig_file.read()

    # Carregar o certificado digital
    with open(cert_path, "rb") as cert_file:
        cert_data = cert_file.read()

    # Ler e decodificar o certificado para obter a chave pública e informações
    cert = x509.load_pem_x509_certificate(cert_data)

    public_key = cert.public_key()

    # Extraindo as informações do certificado (Quem assinou)
    subject = cert.subject
    issuer = cert.issuer
    country = subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value
    state = subject.get_attributes_for_oid(NameOID.STATE_OR_PROVINCE_NAME)[0].value
    locality = subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value
    organization = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
    common_name = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

    console.print(f"🔎 [cyan]Detalhes do certificado do assinante:[/]")
    console.print(f" - País: {country}")
    console.print(f" - Estado/Província: {state}")
    console.print(f" - Localidade: {locality}")
    console.print(f" - Organização: {organization}")
    console.print(f" - Nome Comum (Assinante): {common_name}")

    # Verificar a assinatura usando a chave pública extraída do certificado
    try:
        public_key.verify(
            signature,
            document_content,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        console.print("[green]✔️ Assinatura válida: O documento não foi alterado desde a assinatura.[/]")
        console.print(f"[green]✔️ Assinado por: {common_name}, da organização {organization}.")
    except Exception as e:
        console.print(f"[red]❌ Assinatura inválida: O documento pode ter sido alterado. Erro: {e}")


def display_document(content, extension):
    root = Toplevel()  # Abre uma nova janela no Tkinter
    root.title(f"Visualizador de {extension.upper()}")

    # Verificar o tipo de documento
    if extension == 'txt':
        # Exibir texto no Tkinter
        text_widget = Text(root)
        text_widget.insert('1.0', content.decode('utf-8'))
        text_widget.pack(fill=BOTH, expand=True)
    elif extension == 'pdf':
        # Usar uma biblioteca externa para visualizar PDF
        console.print("📄 Visualizando PDF (use bibliotecas como PyMuPDF ou pdf2image).")
        # Aqui você pode integrar PyMuPDF ou pdf2image para exibir o PDF
        # Um exemplo fictício: exibir uma mensagem
        label = Text(root)
        label.insert('1.0', "Visualizador de PDF não implementado.")
        label.pack(fill=BOTH, expand=True)
    else:
        # Para qualquer outro formato, por enquanto, exibir uma mensagem
        label = Text(root)
        label.insert('1.0', f"Visualizador para {extension} não implementado.")
        label.pack(fill=BOTH, expand=True)

    root.mainloop()

@click.command()
def verify_pkcs7():
    """🔍 Verifica a assinatura digital empacotada em PKCS#7 e exibe detalhes sobre o certificado, além de abrir o conteúdo se embutido."""
    console.print("📂 Abrindo seletor de arquivos para o arquivo PKCS#7...")
    root = Tk()
    root.withdraw()
    pkcs7_file = askopenfilename(title="Selecione o arquivo PKCS#7")

    if not pkcs7_file or not os.path.exists(pkcs7_file):
        console.print("[red]❌ Nenhum arquivo PKCS#7 válido selecionado.[/]")
        return

    # Carregar o arquivo PKCS#7
    with open(pkcs7_file, "rb") as f:
        pkcs7_data = f.read()

    # Verificar se o PKCS#7 está em formato PEM e converter para DER
    if pem.detect(pkcs7_data):
        _, _, pkcs7_data = pem.unarmor(pkcs7_data)

    try:
        # Carregar o PKCS#7 como um objeto CMS (Cryptographic Message Syntax)
        content_info = cms.ContentInfo.load(pkcs7_data)
        assert content_info['content_type'].native == 'signed_data', "O arquivo não contém dados assinados."

        signed_data = content_info['content']
        certs = signed_data['certificates']

        # Verificar o certificado
        if certs:
            for cert_choice in certs:
                if cert_choice.name == 'certificate':
                    cert = cert_choice.chosen
                    subject = cert.subject
                    console.print(f"✔️ Certificado incluído no PKCS#7: {subject.native}")
                else:
                    console.print(f"[yellow]⚠️ Encontrada uma escolha de certificado não reconhecida: {cert_choice.name}")
        else:
            console.print("[red]❌ Nenhum certificado foi encontrado no PKCS#7.")

        # Verificar a assinatura e exibir informações do signatário
        for signer_info in signed_data['signer_infos']:
            signer_id = signer_info['sid']
            if signer_id.name == 'issuer_and_serial_number':
                issuer = signer_id.chosen['issuer']
                serial_number = signer_id.chosen['serial_number'].native
                console.print(f"✔️ Assinatura verificada para o signatário: Issuer {issuer.native}, Serial Number: {serial_number}")
            elif signer_id.name == 'subject_key_identifier':
                subject_key_id = signer_id.chosen.native
                console.print(f"✔️ Assinatura verificada para o signatário: Subject Key Identifier: {subject_key_id}")
            else:
                console.print(f"[yellow]⚠️ Tipo de identificador do signatário não reconhecido: {signer_id.name}")

        # Verificar se o conteúdo do documento está embutido
        if signed_data['encap_content_info']['content'] is not None:
            document_content = signed_data['encap_content_info']['content'].native
            console.print("[green]✔️ Conteúdo do documento está embutido no PKCS#7.")

            # Detectar a extensão do documento embutido (supondo que você saiba ou detecte)
            mime_type, encoding = mimetypes.guess_type(pkcs7_file)
            if mime_type:
                extension = mime_type.split('/')[-1]  # Obter a extensão do tipo mime
            else:
                extension = 'txt'  # Padrão para texto, caso não seja detectado

            # Exibir o conteúdo usando o visualizador com base na extensão
            display_document(document_content, extension)
        else:
            console.print("[yellow]⚠️ O documento assinado não está embutido no PKCS#7 (assinatura destacada). Será necessário fornecer o arquivo original para verificação.")
    except Exception as e:
        console.print(f"[red]❌ Erro ao verificar o PKCS#7: {e}")