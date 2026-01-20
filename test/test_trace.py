import pytest
import sys
import os
import unary
import science_mode
from galois import GaloisField

# --- 1. The Setup (Factories) ---

def make_field(mode):
    """
    Materializes F_2^3.
    P(x) = 1 + x + x^3
    """
    if mode == "physics":
        p = unary.U(2)
        poly = [unary.U(1), unary.U(1), unary.U(0), unary.U(1)]
        return GaloisField(p, 3, poly)
    elif mode == "science":
        p = science_mode.U(2)
        poly = [science_mode.U(1), science_mode.U(1), science_mode.U(0), science_mode.U(1)]
        return GaloisField(p, 3, poly)
    raise ValueError(f"Unknown Universe: {mode}")

def make_element(coeffs_int, field_ctx, mode):
    """Helper to create elements from integer coefficient lists."""
    if mode == "physics":
        raw = [unary.U(c) for c in coeffs_int]
    elif mode == "science":
        raw = [science_mode.U(c) for c in coeffs_int]
    return field_ctx(raw)

# --- 2. The Math (Data-Driven Truths) ---

trace_cases = [
    # (Input Coeffs, Expected Trace Mass, Description)
    
    # Case 1: The Vacuum
    # Tr(0) = 0 + 0 + 0 = 0
    ([], 0, "Trace(0) -> 0"),
    
    # Case 2: The Unit
    # Tr(1) = 1 + 1 + 1 = 3 == 1 (mod 2)
    # Because n=3 (odd), the trace of a constant is the constant itself.
    ([1], 1, "Trace(1) -> 1"),
    
    # Case 3: The Generator (x)
    # Orbit: x -> x^2 -> x^2+x
    # Sum: x + x^2 + x^2 + x = 2x^2 + 2x = 0
    ([0, 1], 0, "Trace(x) -> 0"),
    
    # Case 4: A Mixed Element (1 + x^2)
    # Tr(1 + x^2) = Tr(1) + Tr(x^2) = 1 + 0 = 1
    # Linearity check
    ([1, 0, 1], 1, "Trace(1+x^2) -> 1"),
]
trace_ids = [c[2] for c in trace_cases]

# --- 3. The Experiments ---

class TestSpectralLab:

    @pytest.mark.parametrize("mode", ["physics", "science"])
    @pytest.mark.parametrize("coeffs, exp_mass, desc", trace_cases, ids=trace_ids)
    def test_trace_projection(self, mode, coeffs, exp_mass, desc):
        """
        Experiment: Verify that Trace collapses orbits to the correct Base Field scalar.
        """
        print(f"\n[LAB] Spectral Projection ({desc}) in {mode.upper()}...")
        GF = make_field(mode)
        element = make_element(coeffs, GF, mode)
        
        # 1. Visualize the Orbit (The Process)
        print(f"       Element: {element}")
        orbit = []
        iterator = iter(element)
        for _ in range(GF.n):
            orbit.append(str(next(iterator)))
        print(f"       Orbit:   {' -> '.join(orbit)}")
        
        # 2. Execute Trace
        projection = element.trace()
        print(f"       Result:  {projection} (Mass: {projection.mass})")
        
        # 3. Verify
        # Must be a scalar in the base field (Degree 0 or Vacuum)
        assert projection.mass == exp_mass
        if exp_mass == 0:
            assert projection.is_vacuum
        else:
            # Ensure it is strictly a scalar (no x terms)
            # In F_2, coefficients should be just [1]
            assert len(projection.coeffs) == 1

    @pytest.mark.parametrize("mode", ["physics", "science"])
    def test_trace_linearity(self, mode):
        """
        Experiment: Tr(A + B) = Tr(A) + Tr(B)
        This confirms the Trace is a linear functional.
        """
        print(f"\n[LAB] Linearity Check in {mode.upper()}...")
        GF = make_field(mode)
        
        # A = x
        a = make_element([0, 1], GF, mode) 
        # B = 1
        b = GF.one()
        
        # Tr(A+B)
        sum_elem = a + b
        tr_sum = sum_elem.trace()
        print(f"       Tr(x + 1) = {tr_sum}")
        
        # Tr(A) + Tr(B)
        tr_a = a.trace()
        tr_b = b.trace()
        sum_tr = tr_a + tr_b
        print(f"       Tr(x) + Tr(1) = {tr_a} + {tr_b} = {sum_tr}")
        
        assert str(tr_sum) == str(sum_tr)
        assert tr_sum.mass == sum_tr.mass