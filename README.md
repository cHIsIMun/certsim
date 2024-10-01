### CertSim: Simulador de Geração de Certificados Digitais com Ênfase em Segurança

```
  /$$$$$$                        /$$      /$$$$$$  /$$              
 /$$__  $$                      | $$     /$$__  $$|__/              
| $$  \__/  /$$$$$$   /$$$$$$  /$$$$$$  | $$  \__/ /$$ /$$$$$$/$$$$ 
| $$       /$$__  $$ /$$__  $$|_  $$_/  |  $$$$$$ | $$| $$_  $$_  $$
| $$      | $$$$$$$$| $$  \__/  | $$     \____  $$| $$| $$ \ $$ \ $$
| $$    $$| $$_____/| $$        | $$ /$$ /$$  \ $$| $$| $$ | $$ | $$
|  $$$$$$/|  $$$$$$$| $$        |  $$$$/|  $$$$$$/| $$| $$ | $$ | $$
 \______/  \_______/|__/         \___/   \______/ |__/|__/ |__/ |__/
```

#### **1. Propósito do Projeto**

O **CertSim** é um simulador educativo desenvolvido para demonstrar como a geração, assinatura e verificação de certificados digitais X.509 funcionam, de acordo com as diretrizes da ICP-Brasil (Infraestrutura de Chaves Públicas Brasileira). O objetivo principal é proporcionar uma visão prática de como a criptografia assimétrica pode ser aplicada para garantir a integridade e autenticidade de documentos digitais, ao mesmo tempo em que protege a confidencialidade das chaves privadas.

Este projeto não visa substituir soluções de certificação digital em ambientes de produção, mas sim fornecer uma ferramenta de aprendizado segura e funcional para estudantes e profissionais que desejam compreender o funcionamento de assinaturas digitais e certificados X.509.

#### **2. Tecnologias Utilizadas e Segurança**

- **Python**: A linguagem principal utilizada, confiável e amplamente usada em sistemas de segurança devido à disponibilidade de bibliotecas robustas.
- **Bibliotecas**:
  - **cryptography**: Uma biblioteca amplamente reconhecida e segura, que implementa criptografia assimétrica e simétrica, gerando chaves seguras, assinaturas digitais, e criando/verificando certificados digitais. A biblioteca é desenvolvida com algoritmos robustos e auditados, fornecendo uma base sólida para o desenvolvimento de sistemas de segurança.
  - **asn1crypto**: Fornece suporte à manipulação de estruturas de dados como PKCS#7, um padrão de assinatura digital amplamente usado e seguro.
  - **tkinter**: Usada para criar uma interface gráfica simples para seleção de arquivos e diretórios, garantindo uma interação amigável.
  - **click**: Implementa uma interface de linha de comando para o usuário, permitindo a execução de comandos seguros e a passagem de parâmetros.

#### **3. Estrutura do Projeto**

A estrutura do projeto foi cuidadosamente projetada para separar responsabilidades e manter o sistema seguro e modular.

```
certsim/
    certificate.py
    cli.py
    key_management.py
    signature.py
    utils.py
tests/
    test_certsim.py
```

- **certificate.py**: Responsável pela criação segura de certificados X.509, assinados com chaves privadas RSA.
- **cli.py**: Gerencia os comandos da interface de linha de comando, permitindo que o usuário execute tarefas como gerar chaves, criar certificados, assinar e verificar documentos.
- **key_management.py**: Centraliza a geração e carregamento seguro de chaves privadas e públicas RSA.
- **signature.py**: Lida com a assinatura e verificação de documentos, garantindo a integridade e autenticidade dos dados.
- **utils.py**: Fornece utilitários para manipulação de diretórios, mensagens de saída e formatação de dados.

#### **4. Segurança na Geração de Chaves RSA (key_management.py)**

A geração de chaves RSA é um dos pontos críticos de segurança, pois a chave privada é a principal peça para garantir a autenticidade e a integridade dos documentos assinados. No **CertSim**, as chaves RSA são geradas com um tamanho de 2048 bits, seguindo as recomendações modernas de segurança.

- **Geração de Chave Privada**: 
  - A chave privada é gerada usando o algoritmo RSA com um **exponente público** padrão de 65537, que é considerado seguro e resistente a ataques. O tamanho da chave é de **2048 bits**, garantindo um bom nível de segurança.
  - Após a geração, a chave privada é criptografada com uma senha fornecida pelo usuário, usando o algoritmo **PBKDF2 (Password-Based Key Derivation Function)** com SHA-256, que adiciona uma camada extra de proteção, dificultando a extração de informações mesmo em caso de comprometimento da chave.

- **Armazenamento Seguro da Chave**:
  - A chave privada é serializada e armazenada em formato **PEM** (Privacy-Enhanced Mail) com criptografia simétrica, protegida por uma senha forte.
  - A chave pública é armazenada separadamente e não requer criptografia, pois pode ser compartilhada livremente para verificação de assinaturas.

Exemplo de geração de chaves:
```python
@click.command()
def generate_keys():
    """🔑 Gera um par de chaves RSA e salva as chaves privada e pública na pasta do usuário."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    # Criptografar e salvar a chave privada em formato PEM com proteção de senha
```

#### **5. Criação de Certificado Digital (certificate.py)**

Os certificados digitais garantem a autenticidade e a identidade do assinante. No **CertSim**, os certificados são criados no formato **X.509**, que segue os padrões internacionais para certificados digitais.

- **Assinatura do Certificado**:
  - O certificado é assinado usando a chave privada RSA gerada previamente. Essa assinatura garante que o certificado não foi alterado e que pertence ao titular da chave privada.
  
- **Dados de Identificação**:
  - O certificado contém informações como nome, organização, país, cidade, e outras identificações do titular, garantindo que o documento assinado possa ser associado a uma identidade verificável.

Exemplo de criação de certificado:
```python
@click.command()
def create_certificate():
    """📝 Cria um certificado digital X.509 com informações específicas."""
    cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)
    # O certificado é assinado com a chave privada
```

#### **6. Assinatura de Documentos (signature.py)**

A assinatura de documentos é uma das funcionalidades mais críticas para garantir que o conteúdo de um arquivo não foi alterado. O **CertSim** oferece duas formas seguras de assinatura:

- **Assinatura Simples**:
  - O arquivo é assinado digitalmente usando a chave privada do usuário e o algoritmo **RSA com SHA-256**. A assinatura é armazenada junto com o certificado em uma pasta organizada. O documento original também é armazenado em uma subpasta separada, garantindo que tanto a assinatura quanto o conteúdo possam ser recuperados e verificados com segurança.

- **Assinatura PKCS#7**:
  - O **PKCS#7** é um padrão de empacotamento de dados e assinaturas. O **CertSim** permite que o usuário empacote a assinatura e o conteúdo do documento dentro de um arquivo PKCS#7. Esse formato garante a integridade e facilita o compartilhamento seguro de dados assinados, pois o documento e a assinatura ficam em um único contêiner.

Ambos os métodos de assinatura garantem que a integridade do documento seja protegida e que apenas o titular da chave privada possa assinar o documento.

Exemplo de assinatura com PKCS#7:
```python
@click.command()
def sign_document_with_pkcs7():
    """✍️ Assina digitalmente um documento e empacota em PKCS#7."""
    signed_data = pkcs7.PKCS7SignatureBuilder().set_data(document_content).add_signer(cert, private_key, hashes.SHA256())
    # Assinatura empacotada em PKCS#7 e salva
```

#### **7. Verificação de Assinaturas (signature.py)**

A verificação de assinaturas garante que o documento não foi alterado e que foi assinado por alguém com a chave privada correspondente ao certificado.

- **Verificação Simples**:
  - O comando `verify_signature` permite que o usuário verifique a assinatura de um documento usando o certificado digital anexado. Ele utiliza a chave pública contida no certificado para verificar a integridade da assinatura, garantindo que o documento não foi modificado desde sua assinatura.
  
- **Verificação PKCS#7**:
  - O comando `verify_pkcs7` verifica a assinatura de um pacote PKCS#7. Ele extrai o certificado contido no arquivo e valida a assinatura, garantindo a integridade do pacote de dados.

Exemplo de verificação:
```python
@click.command()
def verify_signature():
    """🔍 Verifica a assinatura digital de um documento usando o certificado anexado."""
    public_key.verify(signature, document_content, padding.PSS(...), hashes.SHA256())
```

#### **8. Fluxo de Funcionamento**

1. **Geração de Chaves RSA**:
   - O usuário gera um par de chaves RSA, onde a chave privada é criptografada e armazenada de forma segura. A chave pública é usada para verificar assinaturas.

2. **Criação de Certificado Digital**:
   - O certificado digital X.509 é criado e assinado com a chave privada, associando informações como nome e organização ao certificado.

3. **Assinatura de Documentos**:
   - O documento pode ser assinado diretamente ou empacotado em um PKCS#7. A chave privada assina o documento, e o certificado é anexado para verificar a autenticidade.

4. **Verificação de Assinaturas**:
   - O destinatário pode verificar a assinatura digital usando o certificado anexado ou um pacote PKCS#7, garantindo que o documento não foi alterado e foi assinado pelo titular do certificado.

#### **9. Conclusão**

O **CertSim** foi desenvolvido com ênfase na segurança em cada etapa do processo, desde a geração de chaves até a assinatura e verificação de documentos. Ele segue padrões internacionais de criptografia e certificação digital, como RSA, X.509 e PKCS#7, proporcionando uma plataforma educativa robusta e confiável para entender a importância da criptografia e dos certificados digitais na proteção de dados e autenticação de documentos.