import pytest
import math
from core.stream import Stream
from core.continued_fraction import ContinuedFraction
from core.algorithms import Euclid
from core.riemann_siegel import stirling_theta, BERNOULLI_MAP
import core.unary as physics_backend
import core.science_mode as science_backend

# [HELPER] Factory to switch universes
def get_matter_factory(mode):
    if mode == "physics": return physics_backend.U
    if mode == "science": return science_backend.U
    raise ValueError(f"Unknown Universe: {mode}")

def evaluate_stream(cf_obj, depth=10):
    """
    Collapses a CF stream into a float for "Lab Verification".
    """
    terms = []
    iterator = iter(cf_obj)
    for _ in range(depth):
        try:
            terms.append(int(next(iterator)))
        except StopIteration:
            break
            
    # Collapse [a0; a1, a2...] -> Float
    if not terms: return 0.0
    val = 0.0
    for t in reversed(terms):
        if val == 0: val = float(t)
        else: val = float(t) + (1.0 / val)
    return val

class TestRiemannSiegel:
    """
    Specifications for the Riemann-Siegel Phase Engine.
    Verifies that the Stirling Series Generator produces the correct
    phase angles theta(t) for the Zeta function.
    """

    # --- 1. Bernoulli Constants Spec ---
    # We rely on these specific rationals for the Horner's Expansion.
    bernoulli_cases = [
        # (Index n, Numerator, Denominator)
        (2, 1, 6),      # B2 = 1/6
        (4, -1, 30),    # B4 = -1/30
        (6, 1, 42),     # B6 = 1/42
    ]
    bernoulli_ids = ["B2=1/6", "B4=-1/30", "B6=1/42"]

    @pytest.mark.parametrize("n, num, den", bernoulli_cases, ids=bernoulli_ids)
    def test_bernoulli_constants(self, n, num, den):
        print(f"\n[LAB] Verifying Bernoulli Constant B_{n}")
        
        # 1. Fetch from Registry
        if n not in BERNOULLI_MAP:
            pytest.fail(f"B_{n} not found in BERNOULLI_MAP")
            
        b_val = BERNOULLI_MAP[n]
        
        print(f"       Expected: {num}/{den}")
        print(f"       Got:      {b_val}")
        
        # 2. Verify Exact Rational Match
        assert b_val == (num, den)

    # --- 2. Stirling Theta Spec (The Main Event) ---
    # Formula: theta(t) ~ (t/2)*ln(t/2pi) - t/2 - pi/8 + 1/(48t) ...
    # Test Case: t = 2*pi (~6.28)
    # Why? ln(t/2pi) -> ln(1) -> 0. The log term vanishes.
    # Expected: 0 - pi - pi/8 + 1/(96pi)
    #         = -1.125*pi + 0.0033
    #         ~= -3.53429 - 0.0033 (Wait, 1/48t is +)
    #         ~= -3.534 + 0.003 = -3.531
    theta_cases = [
        # (Name, t_input, Expected_Float, Tolerance)
        # Note: We use a tuple (p, q) for t to keep it Rational for the engine
        ("Theta(2pi)", (44, 7), -3.53, 0.2), # 44/7 approx 2*pi
    ]
    theta_ids = ["t=2pi"]

    @pytest.mark.parametrize("mode", ["science"]) # Physics mode omitted for heavy calc to avoid timeout
    @pytest.mark.parametrize("name, t_rat, expected, tol", theta_cases, ids=theta_ids)
    def test_stirling_generator(self, mode, name, t_rat, expected, tol):
        print(f"\n[LAB] Stirling Engine Test: {name} ({mode})")
        print(f"       Input t: {t_rat[0]}/{t_rat[1]}")
        
        # 1. Materialize 't' as a Stream (Rational Number)
        # We use the ContinuedFraction class to wrap the input
        # But stirling_theta might expect a raw Rational stream generator?
        # Let's assume it accepts a ContinuedFraction object or a stream.
        # Based on Phase 2, we should pass a ContinuedFraction object.
        
        backend = get_matter_factory(mode)
        p, q = t_rat
        # Create input t as a CF object
        t_proc = Euclid(backend(p), backend(q))
        t_cf = ContinuedFraction(Stream(t_proc))
        
        # 2. Run the Generator
        print("       Invoking Stirling Generator...")
        # This returns a ContinuedFraction object representing theta(t)
        theta_cf = stirling_theta(t_cf)
        
        # 3. Observe the Stream
        print("       Observing Output Stream (First 15 terms):")
        
        # We peek at the terms to ensure it's not empty/dead
        vals = []
        iterator = iter(theta_cf)
        for i in range(15):
            try:
                term = next(iterator)
                vals.append(int(term))
                print(f"       [{i}] {term}")
            except StopIteration:
                print("       (EOS)")
                break
                
        # 4. Collapse and Verify
        # We calculate the convergent value of the stream
        # [a0; a1, a2...]
        observed_val = evaluate_stream(vals)
        
        print(f"       Convergent Value: {observed_val:.5f}")
        print(f"       Expected Target:  {expected:.5f}")
        
        error = abs(observed_val - expected)
        print(f"       Error: {error:.5f}")
        
        assert error < tol, f"Stirling Generator Diverged! Error {error} > {tol}"

    # --- 3. The 'Zero' Location Check ---
    # We verify the engine doesn't crash on the first zero location t=14.13...
    # We don't assert value strictly, just liveness.
    def test_first_zero_liveness(self):
        print(f"\n[LAB] Liveness Check: First Zero (t ~ 14.13)")
        
        # t = 1413 / 100
        backend = science_backend.U
        t_proc = Euclid(backend(1413), backend(100))
        t_cf = ContinuedFraction(Stream(t_proc))
        
        try:
            theta_cf = stirling_theta(t_cf)
            iterator = iter(theta_cf)
            head = next(iterator)
            print(f"       Success: Engine yielded first term {head}")
            assert head is not None
        except Exception as e:
            pytest.fail(f"Engine crashed on first zero: {e}")