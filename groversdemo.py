"""
Grover's Algorithm
"""

import math, time, sys
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

# ── colours ─────────────────────────────────────────────
G  = "\033[92m"   # green
C  = "\033[96m"   # cyan
Y  = "\033[93m"   # yellow
R  = "\033[91m"   # red
P  = "\033[95m"   # purple
W  = "\033[97m"   # white
DIM= "\033[2m"    # dim
B  = "\033[1m"    # bold
X  = "\033[0m"    # reset

def clear():   print("\033[2J\033[H", end="")
def pause(msg="  Press ENTER to continue..."):
    input(f"\n{DIM}{msg}{X}")

# ─────────────────────────────────────────────────────────
def banner():
    clear()
    print(f"""
{C}{B}╔══════════════════════════════════════════════════════╗
║          GROVER'S ALGORITHM  —  LIVE DEMO            ║
║        Network Security Final  |  CCNY  2026         ║
╚══════════════════════════════════════════════════════╝{X}
""")

# ─────────────────────────────────────────────────────────
def screen1_problem():
    banner()
    print(f"{W}{B}  THE SEARCH PROBLEM{X}\n")
    print(f"  We have a database of {Y}{B}8 entries{X}.  One is marked.")
    print(f"  Classical computer checks them {R}one by one{X}.\n")

    print(f"  {DIM}Simulating classical search...{X}\n")
    import random
    target = random.randint(0, 7)
    found_at = 0
    for i in range(8):
        icon = "🔍"
        time.sleep(0.18)
        if i == target:
            print(f"  Box {i}  {G}✓  FOUND!{X}   (checked {i+1} boxes)")
            found_at = i + 1
            break
        else:
            print(f"  Box {i}  {DIM}✗  empty{X}")

    print(f"""
  {Y}Classical average : N/2  =  4 checks
  Classical worst   : N    =  8 checks{X}

  {P}For 1 million entries  →  500,000 checks
  For 1 billion  entries  →  500,000,000 checks{X}

  {R}{B}That's impossibly slow at scale.{X}
""")
    pause()

# ─────────────────────────────────────────────────────────
def screen2_how():
    banner()
    print(f"{W}{B}  HOW GROVER'S WORKS — 3 STEPS{X}\n")

    steps = [
        ("1", C,  "SUPERPOSITION",
         "Apply Hadamard gates → all 8 states loaded simultaneously.\n"
         "   Every state has equal amplitude  1/√8 ≈ 0.35"),
        ("2", R,  "ORACLE",
         "The oracle flips the sign of the target state.\n"
         "   Target: +0.35 → −0.35   (invisible to measurement yet)"),
        ("3", G,  "DIFFUSION",
         "Reflect all amplitudes around the mean.\n"
         "   Target shoots to ~0.97   Others collapse to ~0.0\n"
         "   Repeat Oracle+Diffusion  √N  times  →  done"),
    ]

    for num, col, title, desc in steps:
        time.sleep(0.3)
        print(f"  {col}{B}[{num}] {title}{X}")
        print(f"      {desc}\n")

    print(f"""  {Y}Complexity:   Classical O(N)   →   Grover's O(√N){X}

  {DIM}N=8        : classical 4 checks  vs  Grover's 2 iterations
  N=1,000,000 : classical 500,000   vs  Grover's 785 iterations
  N=1 billion : classical 500M      vs  Grover's 15,811{X}
""")
    pause("  Press ENTER to run the quantum simulation...")

# ─────────────────────────────────────────────────────────
def build_oracle(n, target):
    qc = QuantumCircuit(n)
    bits = format(target, f'0{n}b')
    for i, b in enumerate(reversed(bits)):
        if b == '0': qc.x(i)
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    for i, b in enumerate(reversed(bits)):
        if b == '0': qc.x(i)
    return qc

def build_diffusion(n):
    qc = QuantumCircuit(n)
    qc.h(range(n)); qc.x(range(n))
    qc.h(n-1); qc.mcx(list(range(n-1)), n-1); qc.h(n-1)
    qc.x(range(n)); qc.h(range(n))
    return qc

def screen3_run():
    banner()
    N_QUBITS = 3
    N        = 2 ** N_QUBITS
    TARGET   = 5          # |101⟩
    SHOTS    = 2048
    ITERS    = max(1, round((math.pi/4) * math.sqrt(N)))

    print(f"{W}{B}  RUNNING QUANTUM SIMULATION{X}\n")
    print(f"  {DIM}Search space  : {N} states  ({N_QUBITS} qubits){X}")
    print(f"  {Y}Target state  : |{TARGET}⟩  =  |{format(TARGET,f'0{N_QUBITS}b')}⟩  in binary{X}")
    print(f"  {C}Iterations    : {ITERS}   (classical avg: {N//2} checks){X}")
    print(f"  {DIM}Shots         : {SHOTS}{X}\n")

    # Build circuit
    print(f"  {DIM}Building circuit...{X}", end="", flush=True)
    qr = QuantumRegister(N_QUBITS, 'q')
    cr = ClassicalRegister(N_QUBITS, 'c')
    qc = QuantumCircuit(qr, cr)
    qc.h(qr)                                       # superposition
    oracle    = build_oracle(N_QUBITS, TARGET)
    diffusion = build_diffusion(N_QUBITS)
    for _ in range(ITERS):
        qc.append(oracle.to_gate(label="Oracle"),       qr)
        qc.append(diffusion.to_gate(label="Diffusion"), qr)
    qc.measure(qr, cr)
    print(f"  {G}done{X}")

    # Run
    print(f"  {DIM}Simulating on AerSimulator...{X}", end="", flush=True)
    t0  = time.time()
    sim = AerSimulator()
    job = sim.run(transpile(qc, sim), shots=SHOTS)
    counts = job.result().get_counts()
    elapsed = time.time() - t0
    print(f"  {G}done  ({elapsed:.2f}s){X}\n")

    # Results
    target_key  = format(TARGET, f'0{N_QUBITS}b')
    target_hits = counts.get(target_key, 0)
    accuracy    = target_hits / SHOTS * 100

    print(f"{W}{B}  RESULTS{X}")
    print(f"  {'─'*50}")

    all_states = sorted(counts.items(), key=lambda x: -x[1])
    max_count  = all_states[0][1]

    for state, count in all_states[:6]:
        is_target = state == target_key
        bar_len   = int(count / max_count * 36)
        bar       = '█' * bar_len
        col       = G if is_target else DIM
        tag       = f"  {G}{B}← TARGET  ✓{X}" if is_target else ""
        pct       = count / SHOTS * 100
        print(f"  {col}|{state}⟩  {bar:<36}  {count:>4}  ({pct:4.1f}%){X}{tag}")

    print(f"  {'─'*50}\n")
    print(f"  {G}{B}Target |{target_key}⟩ measured  {target_hits}/{SHOTS} times{X}")
    print(f"  {G}{B}Success probability : {accuracy:.1f}%{X}\n")
    print(f"  {Y}Classical would need  ~{N//2} checks on average.{X}")
    print(f"  {G}Grover's found it in  {ITERS} iteration{'s' if ITERS>1 else ''}.{X}")
    speedup = (N//2) / ITERS
    print(f"  {P}{B}Speedup : {speedup:.1f}×  faster{X}\n")

    print(f"{C}{B}  ✓  Demo complete.  Grover's Algorithm works.{X}\n")

# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        screen1_problem()   # CLICK 1
        screen2_how()       # CLICK 2
        screen3_run()       # CLICK 3 — simulation runs
    except KeyboardInterrupt:
        print(f"\n{DIM}  Demo stopped.{X}\n")
