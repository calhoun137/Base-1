import pytest
from polynomial import Polynomial
from unary import U, S

# [HELPER]
def assert_poly(poly, expected_coeffs_ints):
    """
    Verifies polynomial coefficients match expected integers.
    """
    print(f"\n   -> Poly: {poly}")
    print(f"   -> Expect: {expected_coeffs_ints}")
    
    # Check 1: Degree match (ignoring trailing zeros, but Poly handles that)
    assert len(poly) == len(expected_coeffs_ints)
    
    # Check 2: Coeff match
    for i, coeff in enumerate(poly.coeffs):
        assert int(coeff) == expected_coeffs_ints[i], \
            f"Coeff Mismatch at x^{i}: Got {int(coeff)}, Expected {expected_coeffs_ints[i]}"

class TestPolynomials:
    
    # --- 1. Evaluation Spec ---
    # P(x) = x^2 - 2x + 1  -> [1, -2, 1]
    p_quad = Polynomial([U(1), S(2), U(1)])
    
    eval_cases = [
        (p_quad, U(3), 4),  # P(3) = 9 - 6 + 1 = 4
        (p_quad, U(0), 1),  # P(0) = 1
        (p_quad, U(1), 0),  # P(1) = 0 (Root)
        (p_quad, S(2), 9),  # P(-2) = 4 - (-4) + 1 = 9
    ]
    eval_ids = ["P(3)=4", "P(0)=1", "P(1)=0", "P(-2)=9"]

    @pytest.mark.parametrize("poly, x, expected", eval_cases, ids=eval_ids)
    def test_evaluation(self, poly, x, expected):
        print(f"\n[LAB] Eval {poly} at x={x}")
        res = poly.evaluate(x)
        assert int(res) == expected

    # --- 2. Ring Operations Spec ---
    # P = x + 1 ([1, 1])
    # Q = x - 1 ([-1, 1])
    P = Polynomial([U(1), U(1)])
    Q = Polynomial([S(1), U(1)])
    
    arith_cases = [
        (P, Q, "add", [0, 2]),       # 2x
        (P, Q, "mul", [-1, 0, 1]),   # x^2 - 1
        (P, P, "mul", [1, 2, 1]),    # (x+1)^2 = x^2 + 2x + 1
    ]
    arith_ids = ["(x+1)+(x-1)=2x", "(x+1)(x-1)=x^2-1", "(x+1)^2"]

    @pytest.mark.parametrize("p1, p2, op, expected_coeffs", arith_cases, ids=arith_ids)
    def test_ring_ops(self, p1, p2, op, expected_coeffs):
        print(f"\n[LAB] {op.upper()}: {p1} , {p2}")
        if op == "add": res = p1 + p2
        elif op == "mul": res = p1 * p2
        
        assert_poly(res, expected_coeffs)

    # --- 3. Division Spec ---
    div_cases = [
        # A. Perfect Division: (x^2 + 2x + 1) / (x + 1) = x + 1
        (Polynomial([U(1), U(2), U(1)]), Polynomial([U(1), U(1)]), [1, 1], [0]),
        
        # B. Remainder: (x^2 + 2x + 5) / (x + 1) = x + 1, R=4
        (Polynomial([U(5), U(2), U(1)]), Polynomial([U(1), U(1)]), [1, 1], [4]),
        
        # C. Integer Constraint (The Blunt Chisel): 3x^2 / 2x
        # 3/2 = 1 (in integers). Q = x. R = 3x^2 - 2x^2 = x^2.
        # R (x^2) cannot be divided by 2x anymore because 1/2 = 0.
        (Polynomial([U(0), U(0), U(3)]), Polynomial([U(0), U(2)]), [0, 1], [0, 0, 1]),
    ]
    div_ids = ["Perfect Square", "Remainder 4", "Blunt Chisel (3x^2 / 2x)"]

    @pytest.mark.parametrize("dividend, divisor, exp_q, exp_r", div_cases, ids=div_ids)
    def test_division(self, dividend, divisor, exp_q, exp_r):
        print(f"\n[LAB] Div: {dividend} / {divisor}")
        
        q, r = dividend / divisor
        
        print(f"   -> Quotient: {q}")
        print(f"   -> Remainder: {r}")
        
        assert_poly(q, exp_q)
        assert_poly(r, exp_r)
        
        # Verify Reconstruction: D = d*Q + R
        print("   -> Verifying Reconstruction...")
        recon = (divisor * q) + r
        
        # We check coeffs directly against original dividend
        # (assert_poly handles trailing zeros which might differ slightly in representation but not value)
        # We just iterate and check int values
        for i in range(len(dividend.coeffs)):
            val_recon = int(recon.coeffs[i]) if i < len(recon.coeffs) else 0
            val_orig = int(dividend.coeffs[i])
            assert val_recon == val_orig