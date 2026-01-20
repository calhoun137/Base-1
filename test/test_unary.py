import pytest
from unary import U, S, NonNegativeInteger, NegativeInteger

# [HELPER] - Keeps your assertions clean
def assert_physics(result, expected_val, expected_type):
    # This print only shows up if the test FAILS (or if you use -s)
    print(f"\n   -> Check: {result} (Type: {type(result).__name__})")
    print(f"   -> Expect: {expected_val} (Type: {expected_type.__name__})")
    
    assert int(result) == expected_val
    assert isinstance(result, expected_type)

class TestBase1Arithmetic:
    
    # --- 1. Define the Data ---
    addition_cases = [
        (U(2), U(3),  5, NonNegativeInteger),
        (S(2), S(3), -5, NegativeInteger),
        (U(5), S(3),  2, NonNegativeInteger),
        (S(5), U(2), -3, NegativeInteger),
        (U(3), U(0),  3, NonNegativeInteger),
    ]
    
    # --- 2. Define Readable IDs for the Console ---
    # This generates output like: test_addition[U(2)+U(3)=5]
    addition_ids = [
        f"{a}+{b}={exp}" for a, b, exp, _ in addition_cases
    ]

    @pytest.mark.parametrize("a, b, expected_val, expected_type", addition_cases, ids=addition_ids)
    def test_addition(self, a, b, expected_val, expected_type):
        print(f"\n[LAB] Fusion: Combining {a} and {b}") # Visible with -s
        result = a + b
        assert_physics(result, expected_val, expected_type)

    # --- Division Cases ---
    div_cases = [
        (U(7), U(2),  3,  1), 
        (S(7), U(2), -3, -1),
        (U(7), S(2), -3,  1), 
        (S(7), S(2),  3, -1), 
    ]
    
    div_ids = [f"{n}/{d}" for n, d, _, _ in div_cases]

    @pytest.mark.parametrize("n, d, q_exp, r_exp", div_cases, ids=div_ids)
    def test_division(self, n, d, q_exp, r_exp):
        print(f"\n[LAB] Tiling: Fitting {d} into {n}")
        q, r = n / d
        print(f"   -> Result: Q={q}, R={r}")
        
        # Verify values
        assert int(q) == q_exp
        assert int(r) == r_exp
        
        # Verify Reconstruction (Fundamental Theorem)
        reconstructed = (d * q) + r
        print(f"   -> Reconstruct: {d}*{q} + {r} = {reconstructed}")
        assert int(reconstructed) == int(n)

    # --- Modulo Cases (The Field Requirement) ---
    # Logic: Modulo operates on Mass (Length) but preserves Dividend Sign.
    # |5| % |3| = 2. 
    # S(5) % U(3) -> Remainder is -2 (S(2))
    mod_cases = [
        (U(5), U(3), 2, NonNegativeInteger),
        (S(5), U(3), -2, NegativeInteger), # Corrected Expectation
        (U(5), U(5), 0, NonNegativeInteger),
        (U(0), U(5), 0, NonNegativeInteger),
    ]

    mod_ids = [f"{n}%{d}={exp}" for n, d, exp, _ in mod_cases]

    @pytest.mark.parametrize("n, d, expected_val, expected_type", mod_cases, ids=mod_ids)
    def test_modulo(self, n, d, expected_val, expected_type):
        print(f"\n[LAB] Modulo: {n} % {d}")
        result = n % d
        
        # Special check for Vacuum result representation
        if expected_val == 0:
            assert result.is_vacuum
        
        assert_physics(result, expected_val, expected_type)