import pytest
import sys
import os
import core.unary as unary
import core.science_mode as science_mode
from core.galois import GaloisField

# --- 1. The Setup (Factories) ---
def make_field(mode):
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
    if mode == "physics":
        raw = [unary.U(c) for c in coeffs_int]
    elif mode == "science":
        raw = [science_mode.U(c) for c in coeffs_int]
    return field_ctx(raw)

# --- 2. The Math (Data-Driven Truths) ---

annihilation_cases = [
    ([1], [1], 0),          # 1 + 1 -> 0
    ([1, 1], [1, 1], 0),    # (1+x) + (1+x) -> 0
    # [FIX] (1+x^2) + 1 -> x^2. 
    # x^2 has coefficients [0, 0, 1]. The sum of masses is 0+0+1 = 1.
    ([1, 0, 1], [1], 1),    
] 
annihilation_ids = ["1+1=0", "(1+x)+(1+x)=0", "(1+x^2)+1=x^2"]

reduction_cases = [
    # x * x^2 -> 1+x. Expect Mass 2. Coeffs [1, 1]
    ([0, 1], [0, 0, 1], [1, 1], 2), 
]
reduction_ids = ["x*x^2 -> 1+x"]

# --- 3. The Experiments ---

class TestGaloisLab:

    @pytest.mark.parametrize("mode", ["physics", "science"])
    def test_vacuum_existence(self, mode):
        print(f"\n[LAB] Probing Vacuum in {mode.upper()}...")
        GF = make_field(mode)
        z = GF.zero()
        print(f"       Observed: {z} (Mass: {z.mass})")
        assert z.is_vacuum
        assert z.mass == 0
        assert z.is_vacuum # @NOTE: changed to .is_vacuum to avoid issue where str(z) is empty string "", this is one of the reasons we have .is_vacuum property

    @pytest.mark.parametrize("mode", ["physics", "science"])
    @pytest.mark.parametrize("a_raw, b_raw, exp_mass", annihilation_cases, ids=annihilation_ids)
    def test_matter_annihilation(self, mode, a_raw, b_raw, exp_mass):
        print(f"\n[LAB] Fusion Experiment in {mode.upper()}")
        GF = make_field(mode)
        a = make_element(a_raw, GF, mode)
        b = make_element(b_raw, GF, mode)
        
        print(f"       Input A: {a}")
        print(f"       Input B: {b}")
        
        res = a + b
        print(f"       Result:  {res} (Mass {res.mass})")
        
        assert res.mass == exp_mass
        if exp_mass == 0:
            assert res.is_vacuum

    @pytest.mark.parametrize("mode", ["physics", "science"])
    @pytest.mark.parametrize("a_raw, b_raw, exp_coeffs, exp_mass", reduction_cases, ids=reduction_ids)
    def test_polynomial_reduction(self, mode, a_raw, b_raw, exp_coeffs, exp_mass):
        print(f"\n[LAB] Geometry Experiment in {mode.upper()}")
        GF = make_field(mode)
        a = make_element(a_raw, GF, mode)
        b = make_element(b_raw, GF, mode)
        
        print(f"       Op: {a} * {b}")
        
        res = a * b
        print(f"       Got: {res}")
        
        assert res.mass == exp_mass
        for i, val in enumerate(exp_coeffs):
            if i < len(res.coeffs):
                assert int(res.coeffs[i]) == val
            else:
                assert val == 0

    @pytest.mark.parametrize("mode", ["physics", "science"])
    def test_frobenius_symmetry(self, mode):
        print(f"\n[LAB] Frobenius Symmetry Scan in {mode.upper()}")
        GF = make_field(mode)
        a = make_element([1, 1], GF, mode)
        b = make_element([0, 0, 1], GF, mode)
        p = 2
        
        lhs = (a + b) ** p
        print(f"       (A+B)^{p} = {lhs}")
        
        rhs = (a ** p) + (b ** p)
        print(f"       A^{p} + B^{p} = {rhs}")
        
        assert str(lhs) == str(rhs)
        assert lhs.mass == rhs.mass