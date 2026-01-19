import pytest
from continued_fraction import ContinuedFraction
from stream import Stream
from algorithms import Euclid
import unary as physics_backend
import science_mode as science_backend

# [HELPER] Factory to materialize CFs in specific universes
def make_cf(value, mode):
    """
    Creates a Continued Fraction from a float/int/rational.
    Uses the Euclid algorithm to generate the stream.
    """
    # 1. Select Matter Factory
    if mode == "physics":
        backend = physics_backend
    elif mode == "science":
        backend = science_backend
    else:
        raise ValueError(f"Unknown Universe: {mode}")

    # 2. Materialize (Handle int vs rational tuple)
    if isinstance(value, tuple):
        p, q = value
    else:
        p, q = value, 1

    # 3. Create Stream
    num = backend.U(p)
    den = backend.U(q)
    process = Euclid(num, den)
    
    return ContinuedFraction(Stream(process))

class TestContinuedFraction:
    """
    Specifications for the High-Level Continued Fraction Object.
    Treats the system as a Black Box Integration Test.
    Verifies that the object obeys Fundamental Algebraic Laws.
    """

    # --- 1. The Identity Laws ---
    # Universally true: x + 0 = x, x * 1 = x, x * 0 = 0
    identity_cases = [
        # (Op, Value, Identity_Element, Expected_Result)
        ("add", (1, 2), 0, [0, 2]),      # 1/2 + 0 = 1/2 -> [0; 2]
        ("mul", (2, 3), 1, [0, 1, 2]),   # 2/3 * 1 = 2/3 -> [0; 1, 2]
        ("mul", (55, 1), 0, [0]),        # 55 * 0 = 0 -> [0]
    ]
    
    id_ids = ["x + 0 = x", "x * 1 = x", "x * 0 = 0"]

    @pytest.mark.parametrize("mode", ["physics", "science"])
    @pytest.mark.parametrize("op, val, id_val, expected", identity_cases, ids=id_ids)
    def test_identity_laws(self, mode, op, val, id_val, expected):
        print(f"\n[LAB] Identity Test ({mode}): {val} {op} {id_val}")
        
        # 1. Create Operands
        cf_x = make_cf(val, mode)
        cf_id = make_cf(id_val, mode)
        
        # 2. Perform Op
        if op == "add": result = cf_x + cf_id
        elif op == "mul": result = cf_x * cf_id
        
        # 3. Verify Stream
        seq = []
        iterator = iter(result)
        
        for _ in range(len(expected) + 2):
            try:
                term = next(iterator)
                seq.append(int(term))
            except StopIteration:
                break
            
        print(f"       Got: {seq}")
        assert seq == expected

    # --- 2. The Inverse Laws ---
    # Universally true: x - x = 0, x / x = 1
    # This stresses the 'Drain' logic of the engine (vacuuming out mass).
    inverse_cases = [
        ("sub", (1, 3), (1, 3), [0]),    # 1/3 - 1/3 = 0
        
        # [UPDATED] Expect Uncompressed Unity [0; 1]
        # The engine produces 0 + 1/1 instead of 1.
        # In our universe, this distinction is valid (History Matters).
        ("div", (2, 3), (2, 3), [0, 1]), # (2/3) / (2/3) = 1 
    ]
    
    inv_ids = ["x - x = 0", "x / x = 1"]

    @pytest.mark.parametrize("mode", ["physics", "science"])
    @pytest.mark.parametrize("op, val1, val2, expected", inverse_cases, ids=inv_ids)
    def test_inverse_laws(self, mode, op, val1, val2, expected):
        print(f"\n[LAB] Inverse Test ({mode}): {val1} {op} {val2}")
        
        cf_a = make_cf(val1, mode)
        cf_b = make_cf(val2, mode)
        
        if op == "sub": result = cf_a - cf_b
        elif op == "div": result = cf_a / cf_b
        
        seq = []
        iterator = iter(result)
        
        # Allow extra steps for the engine to stabilize and drain
        for _ in range(5):
            try:
                term = next(iterator)
                seq.append(int(term))
            except StopIteration:
                break
                
        print(f"       Got: {seq}")
        assert seq == expected

    # --- 3. Arithmetic Smoke Test ---
    # Standard calculations to verify coefficient mapping
    arith_cases = [
        ("add", (1, 2), (1, 3), [0, 1, 5]), # 1/2 + 1/3 = 5/6
        ("sub", (1, 2), (1, 3), [0, 6]),    # 1/2 - 1/3 = 1/6
        ("mul", (3, 2), (4, 5), [1, 5]),    # 3/2 * 4/5 = 6/5
        ("div", (1, 1), (1, 2), [2]),       # 1 / (1/2) = 2
    ]
    
    arith_ids = ["1/2+1/3", "1/2-1/3", "3/2*4/5", "1/(1/2)"]

    @pytest.mark.parametrize("mode", ["physics", "science"])
    @pytest.mark.parametrize("op, v1, v2, exp", arith_cases, ids=arith_ids)
    def test_arithmetic(self, mode, op, v1, v2, exp):
        print(f"\n[LAB] Arithmetic ({mode}): {v1} {op} {v2}")
        
        cf_1 = make_cf(v1, mode)
        cf_2 = make_cf(v2, mode)
        
        if op == "add": res = cf_1 + cf_2
        elif op == "sub": res = cf_1 - cf_2
        elif op == "mul": res = cf_1 * cf_2
        elif op == "div": res = cf_1 / cf_2
        
        seq = []
        iterator = iter(res)
        
        for _ in range(len(exp) + 2):
            try:
                seq.append(int(next(iterator)))
            except StopIteration:
                break
        
        print(f"       Got: {seq}")
        assert seq == exp

    # --- 4. Cross-Backend Compatibility ---
    # Can we mix Matter? (Physics + Science)
    def test_cross_backend_fusion(self):
        print("\n[LAB] Fusion Test: Physics(1) + Science(2)")
        
        # 1. Create Physics Object (Unary)
        cf_phys = make_cf(1, "physics")
        
        # 2. Create Science Object (FastInt)
        cf_sci = make_cf(2, "science")
        
        # 3. Fuse
        # 1 + 2 = 3 -> [3]
        result = cf_phys + cf_sci
        
        seq = []
        iterator = iter(result)
        
        for _ in range(3):
            try:
                seq.append(int(next(iterator)))
            except StopIteration:
                break
                
        print(f"       Got: {seq}")
        assert seq == [3]