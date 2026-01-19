import pytest
import math
from stream import Stream
from continued_fraction import ContinuedFraction
from gosper import GosperState
from algorithms import Euclid
import unary as physics_backend
import science_mode as science_backend

# [HELPER] Factory to switch universes
def get_backend(mode):
    if mode == "physics": return physics_backend
    if mode == "science": return science_backend
    raise ValueError(f"Unknown Universe: {mode}")

def create_cf(mode, p, q):
    """
    Helper to construct a Continued Fraction from a Rational Number.
    """
    backend = get_backend(mode)
    # 1. Matter
    num = backend.U(p)
    den = backend.U(q)
    # 2. Process (Euclid)
    proc = Euclid(num, den)
    # 3. Stream & Object
    return ContinuedFraction(Stream(proc))

class TestGosperEngine:
    """
    Specifications for the Bihomographic Gosper Engine.
    Verifies:
    1. Thermodynamics: Mass and Entropy are correctly observed.
    2. Arithmetic: +, -, *, / produce correct CF streams.
    """

    # --- 1. Thermodynamic Specs ---
    @pytest.mark.parametrize("mode", ["physics", "science"])
    def test_thermodynamics(self, mode):
        print(f"\n[LAB] Thermodynamics Check ({mode})")
        backend = get_backend(mode)
        
        # Construct a specific State Cube
        # z = (1x + 2xy + ... + 1) / ...
        # We set 8 coefficients manually
        coeffs = [
            backend.U(1), backend.U(2), backend.U(0), backend.U(0), # A, B, C, D
            backend.U(0), backend.U(0), backend.U(0), backend.U(1)  # E, F, G, H
        ]
        
        # Total Mass = 1 + 2 + 1 = 4
        expected_mass = 4
        
        # Initialize State
        state = GosperState(*coeffs)
        
        # Check Mass
        current_mass = state.mass
        print(f"       Mass: {current_mass} (Expect {expected_mass})")
        assert current_mass == expected_mass
        
        # Check Entropy (S = ln(Mass))
        expected_entropy = math.log(expected_mass)
        current_entropy = state.entropy
        print(f"       Entropy: {current_entropy:.5f} (Expect {expected_entropy:.5f})")
        
        assert abs(current_entropy - expected_entropy) < 1e-9

    # --- 2. Arithmetic Specs ---
    arithmetic_cases = [
        # (Op, (Num1, Den1), (Num2, Den2), Expected_Seq)
        
        # Addition: 1/2 + 1/3 = 5/6 -> [0; 1, 5]
        ("Add", (1, 2), (1, 3), [0, 1, 5]),
        
        # Multiplication: 3/2 * 4/5 = 12/10 = 6/5 -> [1; 5]
        ("Mul", (3, 2), (4, 5), [1, 5]),
        
        # Integer Addition: 10/1 + 5/1 = 15 -> [15]
        ("Add", (10, 1), (5, 1), [15]),
        
        # Division: (1/1) / (2/1) = 0.5 -> [0; 2]
        ("Div", (1, 1), (2, 1), [0, 2]),
        
        # Subtraction: 1/2 - 1/3 = 1/6 -> [0; 6]
        # Note: Subtraction relies on the NegativeInteger backend logic
        ("Sub", (1, 2), (1, 3), [0, 6]),
    ]

    case_ids = [
        f"{op}: {n1}/{d1}, {n2}/{d2}" 
        for op, (n1, d1), (n2, d2), _ in arithmetic_cases
    ]

    @pytest.mark.parametrize("mode", ["physics", "science"])
    @pytest.mark.parametrize("op, val1, val2, expected_seq", arithmetic_cases, ids=case_ids)
    def test_arithmetic(self, mode, op, val1, val2, expected_seq):
        print(f"\n[LAB] {op} [{mode}]: {val1} and {val2}")
        
        # 1. Create Operands
        cf_a = create_cf(mode, *val1)
        cf_b = create_cf(mode, *val2)
        
        # 2. Perform Operation (Spawns the Engine)
        if op == "Add":   cf_result = cf_a + cf_b
        elif op == "Sub": cf_result = cf_a - cf_b
        elif op == "Mul": cf_result = cf_a * cf_b
        elif op == "Div": cf_result = cf_a / cf_b
        
        # 3. Consume Result Stream
        result_sequence = []
        limit = len(expected_seq) + 2
        
        print(f"       Stream: ", end="")
        
        # We iterate manually to handle the finite stream termination
        iterator = iter(cf_result)
        for _ in range(limit):
            try:
                term = next(iterator)
                val = int(term)
                result_sequence.append(val)
                print(f"{val} ", end="")
            except StopIteration:
                print("(End)", end="")
                break
                
        print("")
        
        # 4. Verification
        assert result_sequence == expected_seq, \
            f"Arithmetic Fail {op}. Expected {expected_seq}, Got {result_sequence}"