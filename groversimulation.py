from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

secret = [1, 0, 1, 1]

def optimal_all():

    all = [[w,x,y,z] for w in range(2) for x in range(2) for y in range(2) for z in range(2)]
    return all

def secret_checker(input):
    if input == [0, 1, 0, 1]:
        return True
    return False

def oracle(qc):
    # Flip the amp for the target outcome 1011
    qc.x(2)
    qc.h(3)
    qc.mcx([0, 1, 2], 3)
    qc.h(3)
    qc.x(2)

    return qc

def diffuse(qc):
    # Diffuse the qubits to get the desired outcome

    qc.h(range(4))
    qc.x(range(4))
    qc.h(3)
    qc.mcx([0, 1, 2], 3)
    qc.h(3)
    qc.x(range(4))
    qc.h(range(4))

    qc.barrier()
    
    state_post = Statevector(qc)
    print("During oracle/diffuse:")
    print(state_post)

    return qc

def main():
    # initialize qubits
    n = 4
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    qc.barrier()

    state_pre = Statevector(qc)
    print("Before oracle and diffuse:")
    print(state_pre)

    for _ in range(15):
        oracle(qc)
        diffuse(qc)

    state_post = Statevector(qc)
    print("After oracle and diffuse:")
    print(state_post)
    print(qc.draw())

    qc.measure(range(4), range(4))

    simulator = AerSimulator()
    result = simulator.run(qc, shots=1024).result()
    counts = result.get_counts()

    print(counts)


if __name__ == "__main__":
    main()