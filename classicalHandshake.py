# Current Encryption Protocol using ECDH and AES

import logging

from cryptography.hazmat.primitives.asymmetric import ec

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import os


def server_keygen():
    """
        Generate the server private and public key using ECDH
    """

    server_private_key = ec.generate_private_key(ec.SECP384R1())
    server_public_key = server_private_key.public_key()

    return (server_private_key, server_public_key)


def client_handshake(server_public_key):
    """
        Initiate the handshake
        Generate the client shared secret from the server public key and client private key
    """

    client_private_key = ec.generate_private_key(ec.SECP384R1())
    client_public_key = client_private_key.public_key()
    client_shared_secret = client_private_key.exchange(ec.ECDH(), server_public_key)

    return (client_shared_secret, client_public_key)

def server_handshake(server_private_key, client_public_key):
    """
        Complete the handshake
        Generate the shared secret from the client public key and server private key
    """

    server_shared_secret = server_private_key.exchange(ec.ECDH(), client_public_key)

    return server_shared_secret

def key_derivation(K):
    """
        Use a kdf to derive a key from the shared secret generated from ECDH
    """

    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"demo")
    aes_key = hkdf.derive(K)

    return aes_key

def encrypt_message(message, key):
    """
        Encrypt a message using AES-256-GCM
    """
    aad = b"demo"
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, message, aad)

    return nonce+ct

def decrypt_ciphertext(blob, key):
    """
        Decrypt a ciphertext using AES-256-GCM
    """
    aad = b"demo"
    aesgcm = AESGCM(key)
    nonce = blob[:12]
    ciphertext = blob[12:]
    pt = aesgcm.decrypt(nonce, ciphertext, aad)

    return pt

def main():
    """
        Toy implementation for ECDH between client and server
    """

    # For Debugging
    logging.basicConfig(level=logging.DEBUG)

    # Server generates keys using ECDH
    server_private_key, server_public_key = server_keygen()

    # Client performs exchange to derive shared secret
    client_shared_secret, client_public_key= client_handshake(server_public_key)

    # Server performs exchange to derive shared secret
    server_shared_secret = server_handshake(server_private_key, client_public_key)

    # Check shared secret
    assert client_shared_secret == server_shared_secret, "Shared secret error"
    logging.debug("Successful ECDH Shared Key!")

    # Use HKDF to derive key from shared secret for AES
    client_key = key_derivation(client_shared_secret)
    server_key = key_derivation(server_shared_secret)

    # Check encryption key
    assert client_key == server_key, "Encryption key derivation error"
    logging.debug("Successful Encryption Key!")

    # Encrypt message
    message = b"This is a test message"
    logging.debug(f"Message: {message}")
    blob = encrypt_message(message, client_key)
    logging.debug(f"AES-GCM Blob: {blob.hex()}")

    # Decrypt message
    plaintext = decrypt_ciphertext(blob, server_key)
    logging.debug(f"AES-GCM Plaintext: {plaintext}")

    # Check encryption
    assert message == plaintext, "Encryption error"
    logging.debug("Successful Encryption")

    logging.debug("END OF TEST")

if __name__ == "__main__":
    main()