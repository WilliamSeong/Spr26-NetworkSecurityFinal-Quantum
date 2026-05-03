# Code for implementing the kyber-py library
# This is a Python implementation of ML-KEM

import kyber_py as kyber
import kyber_py.ml_kem as ml_kem

import logging

logging.basicConfig(level=logging.DEBUG)

def main():
    """
        Main function for implementing ML-KEM from the kyber-py library
        The initial goal will be to get something running with ML_KEM_512
    """

    mlkem_512 = ml_kem.ML_KEM_512

    # Bob generate encapsulation key and decapsulation key
    ek, dk = mlkem_512.keygen()
    logging.debug("encapsulation key:", ek)
    logging.debug("decapsulation key:", dk)

    # Alice encapsulates Bob's ek to produce the secret and cipher
    alice_K, c = mlkem_512.encaps(ek)
    logging.debug(f"Alice Shared Secret: {alice_K}")
    logging.debug(f"Cipher text: {c}")

    # Bob decapsulates Alice's encapsulated ciphertext to derive the same K
    bob_K = mlkem_512.decaps(dk, c)
    logging.debug(f"Bob Shared Secret: {bob_K}")
    logging.debug(bob_K.hex())

    # Check Secrets
    assert(alice_K == bob_K)

    # Secret exchange success
    print("Success!")

if __name__ == "__main__":
    main()