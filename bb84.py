# This will be a simulation of BB84 QKE
import random
import logging


LENGTH = 1000
BASIS = ["+", "x"]
EVE = True


def generate_alice_bits(n: int) -> list[int]:
    """
        Alice will generate a random bit string of length n
    """
    rand_bits = [random.randint(0, 1) for _ in range(n)]
    return rand_bits


def generate_rand_basis(n: int) -> list[str]:
    """
        Function for generating basis list
    """
    return [random.choice(BASIS) for _ in range(n)]


def bob_measured_bits(bob_basis: list[str], alice_basis: list[str], alice_bits: list[int]) -> list[int]:
    """
        Bob will measure the qubits from Alice
        To simulate Bob and Alice will compare basis lists

        If they match Bob would have measured the bit correctly
        else Bob will measure a random bit, 0 or 1
    """
    bob_bits = [alice_bits[i] if bob_basis[i] == alice_basis[i] else random.randint(0,1) for i in range(len(alice_bits))]
    return bob_bits


def sift_keys(alice_basis: list[str],  bob_basis: list[str], alice_bits: list[int], bob_bits: list[int]):
    """
        Alice and Bob will compare basis lists in order to sift the key from the bit lists
    """
    alice_key_list = sift_keys_helper(alice_bits, alice_basis, bob_basis)
    bob_key_list = sift_keys_helper(bob_bits, alice_basis, bob_basis)
    return alice_key_list, bob_key_list


def sift_keys_helper(bit_list: list[int], alice_basis: list[str], bob_basis: list[str]):
    return [bit_list[i] for i in range(len(alice_basis)) if alice_basis[i] == bob_basis[i]]


def error_check(alice_bits: list[int], bob_bits: list[int]):
    """
        Sample Alice and Bob's bits to check their error rate.
        If above a certain threshold, likely eve observed the qubits before Bob
    """
    n = len(alice_bits)
    sample_size = n // 2
    sample_indices = set(random.sample(range(n), sample_size))
    
    error = 0
    alice_final_key = []
    bob_final_key = []

    for i in range(len(alice_bits)):
        if i in sample_indices:
            if alice_bits[i] != bob_bits[i]:
                error += 1
        else:
            alice_final_key.append(alice_bits[i])
            bob_final_key.append(bob_bits[i])
    
    error_rate = error / sample_size
    return alice_final_key, bob_final_key, error_rate


def eve(n: int, alice_basis, alice_bits):
    """
        Eve will "observe" the bit list from Alice, corrupting the list
    """
    eve_basis = generate_rand_basis(n)
    eve_bits = [alice_bits[i] if eve_basis[i] == alice_basis[i] else random.randint(0,1) for i in range(len(alice_bits))]
    return eve_basis, eve_bits

def simulation():
    # We will go through each process of the key exchange simulating Alice and Bob.
    # We will also generate an Eve to see if Alice and Bob can correctly throw away a key that was observed by Eve
    # Alice will generate a bits list of a certain length.
    alice_bits = generate_alice_bits(LENGTH)
    logging.debug(f"Alice produces random bit list: {alice_bits}")

    # Alice will also generate a basis list of the same length
    alice_basis = generate_rand_basis(LENGTH)
    logging.debug(f"Alice produces random basis list: {alice_basis}")
    logging.debug(f"-----------------------------------------------------------------------------------------")
    input()

    # Eve will observe here
    # Simulate if Eve observes
    if EVE:
        fake_alice_basis, fake_alice_bits = eve(LENGTH, alice_basis, alice_bits)
        logging.debug(f"Eve produces random basis list: {fake_alice_basis}")
        logging.debug(f"Eve produces random bit list: {fake_alice_bits}")
        logging.debug(f"-----------------------------------------------------------------------------------------")
        input()

    # Bob will also generate a basis list
    bob_basis = generate_rand_basis(LENGTH)
    logging.debug(f"Bob produces random basis list: {bob_basis}")

    # In the event that Eve attacks
    if EVE:
        bob_bits = bob_measured_bits(bob_basis, fake_alice_basis, fake_alice_bits)
        logging.debug(f"Bob measures bits: {bob_bits}")
        logging.debug(f"-----------------------------------------------------------------------------------------")
        input()

    else:
        # Alice and Bob will compare their basis list, and Bob will "derive" a bit list
        bob_bits = bob_measured_bits(bob_basis, alice_basis, alice_bits)
        logging.debug(f"Bob measures bits: {bob_bits}")
        logging.debug(f"-----------------------------------------------------------------------------------------")
        input()

    # Now the bit lists will be sifted based on the basis lists matches
    alice_key, bob_key = sift_keys(alice_basis, bob_basis, alice_bits, bob_bits)
    logging.debug(f"Alice key is {alice_key}")
    logging.debug(f"Bob key is {bob_key}")
    logging.debug(f"-----------------------------------------------------------------------------------------")
    input()

    # Finally we will error check the actual bits publically
    alice_final, bob_final, error_rate = error_check(alice_key, bob_key)
    logging.debug(f"Alice Final: {alice_final}")
    logging.debug(f"Bob Final: {bob_final}")
    print(f"error rate {error_rate}")
    return error_rate

def main():
    logging.basicConfig(level=logging.DEBUG)
    simulation()

if __name__ == "__main__":
    main()