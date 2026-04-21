# Post-Quantum Encryption Protocol using ML-KEM and AES

import logging

import kyber_py.ml_kem as ml_kem

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import os


MLKEM_512 = ml_kem.ML_KEM_512
EVE = True


def server_keygen():
    """
        Generate the encapsulation and decapsulation key using ML-KEM
    """

    ek, dk = MLKEM_512.keygen()

    return (ek, dk)


def client_handshake(ek):
    """
        Initiate the handshake
        Generate the shared secret and ciphertext from the ek
    """

    K, c = MLKEM_512.encaps(ek)

    return (K, c)

def server_handshake(dk, c):
    """
        Complete the handshake
        Generate the shared secret from the ciphertext using dk
    """

    K = MLKEM_512.decaps(dk, c)

    return K

def key_derivation(K):
    """
        Use a kdf to derive a key from the shared secret generated from ML-KEM
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
        Toy implementation for ML-KEM between client and server
    """

    # For Debugging
    logging.basicConfig(level=logging.DEBUG)

    # Server generates keys using ML-KEM
    ek, dk = server_keygen()

    # Client encapsulates to derive shared secret and ciphertext
    client_K, c = client_handshake(ek)

    # Server decapsulates ciphertext to derive shared secret
    server_K = server_handshake(dk, c)

    # Check shared secret
    assert client_K == server_K, "Shared secret error"
    logging.debug("Successful Shared Key!")

    # Use HKDF to derive key from shared secret for AES
    client_key = key_derivation(client_K)
    server_key = key_derivation(server_K)

    # Check encryption key
    assert client_key == server_key, "Encryption key derivation error"
    logging.debug("Successful Encryption Key!")

    # Encrypt message
    message = b"This is a test message"
    logging.debug(f"Message: {message}")
    blob = encrypt_message(message, client_key)
    logging.debug(f"AES-GCM Blob: {blob.hex()}")

    if EVE:
        print("I'm eve!")
        


    # Decrypt message
    plaintext = decrypt_ciphertext(blob, server_key)
    logging.debug(f"AES-GCM Plaintext: {plaintext}")

    # Check encryption
    assert message == plaintext, "Encryption error"
    logging.debug("Successful Encryption")

    logging.debug("END OF TEST")

if __name__ == "__main__":
    main()