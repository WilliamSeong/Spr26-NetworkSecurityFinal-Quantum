"""
Grover's Algorithm — Implementation using Qiskit
Spr26-NetworkSecurityFinal-Quantum | CCNY Network Security
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import math

def build_oracle(n_qubits: int, target: int) -> QuantumCircuit:
    """
    Phase oracle Uw: flips the phase of the target state.
    Uw|x> = -|x>  if x == target
    Uw|x> =  |x>  otherwise
    """
    oracle = QuantumCircuit(n_qubits, name="Oracle")
    # Flip qubits where target bit is 0, so target maps to |11...1>
    target_bits = format(target, f'0{n_qubits}b')
    for i, bit in enumerate(reversed(target_bits)):
        if bit == '0':
            oracle.x(i)
    # Multi-controlled Z: flips phase of |11...1>
    oracle.h(n_qubits - 1)
    oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    oracle.h(n_qubits - 1)
    # Undo the bit flips
    for i, bit in enumerate(reversed(target_bits)):
        if bit == '0':
            oracle.x(i)
    return oracle

def build_diffusion(n_qubits: int) -> QuantumCircuit:
    """
    Grover diffusion operator Us = 2|psi><psi| - I
    Implements inversion about the mean.
    """
    diffusion = QuantumCircuit(n_qubits, name="Diffusion")
    diffusion.h(range(n_qubits))
    diffusion.x(range(n_qubits))
    diffusion.h(n_qubits - 1)
    diffusion.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    diffusion.h(n_qubits - 1)
    diffusion.x(range(n_qubits))
    diffusion.h(range(n_qubits))
    return diffusion

def grovers_algorithm(n_qubits: int, target: int, n_iterations: int = None) -> QuantumCircuit:
    """
    Full Grover's algorithm circuit.

    Args:
        n_qubits:     Number of qubits (search space = 2^n_qubits)
        target:       Index of the marked state (0 <= target < 2^n_qubits)
        n_iterations: Number of Grover iterations; defaults to optimal floor(pi/4 * sqrt(N))

    Returns:
        Assembled QuantumCircuit ready for simulation.
    """
    N = 2 ** n_qubits
    if n_iterations is None:
        n_iterations = max(1, math.floor((math.pi / 4) * math.sqrt(N)))

    qr = QuantumRegister(n_qubits, 'q')
    cr = ClassicalRegister(n_qubits, 'c')
    circuit = QuantumCircuit(qr, cr)

    # Step 1: Equal superposition via Hadamard transform H^n|0>
    circuit.h(qr)
    circuit.barrier()

    # Steps 2+3: Grover iterations (Oracle + Diffusion)
    oracle    = build_oracle(n_qubits, target)
    diffusion = build_diffusion(n_qubits)

    for iteration in range(n_iterations):
        circuit.append(oracle.to_gate(),    qr)
        circuit.append(diffusion.to_gate(), qr)
        circuit.barrier()

    # Step 4: Measure
    circuit.measure(qr, cr)
    return circuit

def run_grover(n_qubits: int, target: int, shots: int = 1024):
    """
    Build, simulate, and print results for Grover's algorithm.

    Args:
        n_qubits: Number of qubits
        target:   Target state index
        shots:    Number of simulation shots
    """
    N            = 2 ** n_qubits
    n_iterations = max(1, math.floor((math.pi / 4) * math.sqrt(N)))

    print("=" * 55)
    print("  Grover's Algorithm")
    print("=" * 55)
    print(f"  Search space N     : {N} states ({n_qubits} qubits)")
    print(f"  Target state       : |{target}> "
          f"({format(target, f'0{n_qubits}b')} in binary)")
    print(f"  Grover iterations  : {n_iterations}  "
          f"(classical avg: {N // 2})")
    print(f"  Theoretical speedup: {(N // 2) / n_iterations:.1f}x")
    print("-" * 55)

    circuit   = grovers_algorithm(n_qubits, target, n_iterations)
    simulator = AerSimulator()
    job       = simulator.run(circuit, shots=shots)
    counts    = job.result().get_counts()

    target_key  = format(target, f'0{n_qubits}b')
    target_count = counts.get(target_key, 0)
    probability  = target_count / shots * 100

    print(f"  Simulation shots   : {shots}")
    print(f"  Target measured    : {target_count}/{shots} times")
    print(f"  Success probability: {probability:.1f}%")
    print("=" * 55)
    print("\n  Top measurement outcomes:")
    for state, count in sorted(counts.items(), key=lambda x: -x[1])[:5]:
        bar   = "█" * int(count / shots * 40)
        marker = " ← TARGET" if state == target_key else ""
        print(f"  |{state}> : {bar} {count}{marker}")
    print()
    return counts

if __name__ == "__main__":
    # Example: 3 qubits (N=8), search for state |5> = |101>
    run_grover(n_qubits=3, target=5, shots=2048)