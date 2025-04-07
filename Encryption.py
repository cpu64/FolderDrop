from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import Name, NameAttribute, SubjectAlternativeName, IPAddress, CertificateBuilder, KeyUsage
from cryptography.x509.oid import NameOID
from OpenSSL import SSL
from flask import Flask
import cherrypy
import os
import datetime
import ipaddress
import tempfile


# Function to create a self-signed certificate with multiple IPs
def create_self_signed_cert(ips: list):
    cert_file = './server.crt'
    key_file = './server.key'

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = Name([
        NameAttribute(NameOID.COUNTRY_NAME, "__"),
        NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "FolderDrop"),
        NameAttribute(NameOID.LOCALITY_NAME, "FolderDrop"),
        NameAttribute(NameOID.ORGANIZATION_NAME, "FolderDrop"),
        NameAttribute(NameOID.COMMON_NAME, "localhost")
    ])

    san_entries = [IPAddress(ipaddress.IPv4Address(ip)) for ip in ips]

    builder = CertificateBuilder()
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(subject)
    builder = builder.not_valid_before(datetime.datetime.now(datetime.UTC))
    builder = builder.not_valid_after(datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365))
    builder = builder.serial_number(1000)
    builder = builder.public_key(private_key.public_key())

    builder = builder.add_extension(
        KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_agreement=False,
            data_encipherment=False,
            key_cert_sign=False,
            crl_sign=False,
            content_commitment=False,
            decipher_only=False,
            encipher_only=False
        ),
        critical=True
    )

    builder = builder.add_extension(SubjectAlternativeName(san_entries), critical=False)

    certificate = builder.sign(private_key=private_key, algorithm=hashes.SHA256())
    # TODO: better temp files
    with open(key_file, "wb") as key_out:
        key_out.write(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL,         encryption_algorithm=serialization.NoEncryption()))

    with open(cert_file, "wb") as cert_out:
        cert_out.write(certificate.public_bytes(serialization.Encoding.PEM))

    context = SSL.Context(SSL.TLS_SERVER_METHOD)
    context.use_certificate_file(cert_file)
    context.use_privatekey_file(key_file)

    os.remove(key_file)
    os.remove(cert_file)

    return context
