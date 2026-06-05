# certsim

🇺🇸 English | 🇧🇷 [Português](README.md)

> An educational CLI simulator for generating, signing, and verifying X.509 digital certificates — built around real cryptography and ICP-Brasil concepts.

## Overview

**certsim** is an educational tool that demonstrates, hands-on, how **X.509 digital certificates** are generated, signed, and verified. It creates self-signed certificates (subject = issuer, 365-day validity), signs documents with RSA-PSS, and packages signatures in PKCS#7 (CMS) containers. It illustrates how a private key produces a signature that only the matching public key can validate, and how any change to a document invalidates its signature.

> Educational scope — not a production PKI solution.

## Features

**Key generation**
- `generate-keys` — RSA 2048-bit pair; private key encrypted in PEM (PBKDF2 + SHA-256 from a user password).

**Certificates**
- `create-certificate` — self-signed X.509 certificate with identification attributes (country, state, locality, organization, common name), random serial, validity dates.

**Signing**
- `sign-document` — RSA-PSS + SHA-256 signature, saved alongside the original document.
- `sign-document-with-pkcs7` — bundles document + signature + certificate into a PKCS#7 (CMS) container (DER).

**Verification**
- `verify-signature` — verifies a simple signature with the certificate's public key and shows signer details.
- `verify-pkcs7` — extracts certificate + signature info from a PKCS#7 file.

## Stack

Python · [cryptography](https://cryptography.io) (RSA, X.509, PKCS#7) · click (CLI) · rich (output) · asn1crypto (CMS parsing) · pyOpenSSL · tkinter (file dialogs). Managed with Poetry.

## Running

```bash
poetry install
certsim generate-keys
certsim create-certificate
certsim sign-document
certsim verify-signature
# PKCS#7 variants:
certsim sign-document-with-pkcs7
certsim verify-pkcs7
```

Typical flow: `generate-keys` → `create-certificate` → `sign-document` → `verify-signature`.

## Structure

```
certsim/
├── cli.py              # Click command orchestration
├── certificate.py      # X.509 creation
├── key_management.py   # RSA generation / loading
├── signature.py        # simple + PKCS#7 signing and verification
└── utils.py            # console, paths, hostname
tests/test_certsim.py   # end-to-end suite (pytest)
```

## Project status

Functional and tested end-to-end (key generation, certificate creation, signing, verification, and tamper detection). Minor gaps: PDF viewer is stubbed; PKCS#7 verification extracts info without full cryptographic re-validation.

> 🇧🇷 The full Portuguese documentation is in [README.md](README.md).

## License

This project does not yet declare a license. Until one is added, all rights are reserved by the author.
