import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

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

# --- 2. The Experiments ---

class TestCartographyLab:

    @pytest.mark.parametrize("mode", ["physics", "science"])
    def test_field_census(self, mode):
        """
        Experiment: Enumerate the population of the Field.
        Expectation: p^n elements (2^3 = 8).
        """
        print(f"\n[LAB] Census of F_8 in {mode.upper()}...")
        GF = make_field(mode)
        
        population = []
        for citizen in GF:
            population.append(citizen)
            print(f"       Citizen: {citizen} (Mass: {citizen.mass})")
            
        count = len(population)
        print(f"       Total Population: {count}")
        
        assert count == 8
        unique_ids = set(str(c) for c in population)
        assert len(unique_ids) == 8

    @pytest.mark.parametrize("mode", ["physics", "science"])
    def test_inverse_law(self, mode):
        """
        Experiment: Verify the Law of Inversion.
        For every a != 0, a * a^-1 = 1.
        """
        print(f"\n[LAB] Checking Inverses in {mode.upper()}...")
        GF = make_field(mode)
        one = GF.one()
        
        for a in GF:
            if a.is_vacuum:
                with pytest.raises(ZeroDivisionError):
                    _ = a.inverse()
                continue
            
            inv = a.inverse()
            product = a * inv
            
            print(f"       {a} * {inv} = {product}")
            
            # Verify Identity
            # Using mass check + string repr to ensure it is EXACTLY 1
            assert product.mass == one.mass
            assert str(product) == str(one)

    @pytest.mark.parametrize("mode", ["physics", "science"])
    def test_frobenius_orbit(self, mode):
        """
        Experiment: Trace the "Frobenius Stream".
        """
        print(f"\n[LAB] Frobenius Stream (Orbit of x) in {mode.upper()}")
        GF = make_field(mode)
        
        x_coeffs = [0, 1]
        if mode == "physics": x_raw = [unary.U(c) for c in x_coeffs]
        else: x_raw = [science_mode.U(c) for c in x_coeffs]
        
        x = GF(x_raw)
        orbit_stream = iter(x)
        
        expected_cycle_strs = [
            str(x),           # x
            str(x**2),        # x^2
            str(x**4)         # x^2 + x
        ]
        
        print(f"       Expected Cycle: {expected_cycle_strs}")
        
        observed_cycle = []
        for _ in range(3):
            state = next(orbit_stream)
            observed_cycle.append(str(state))
            print(f"       t={len(observed_cycle)-1}: {state}")
            
        assert observed_cycle == expected_cycle_strs
        
        closure = next(orbit_stream)
        print(f"       t=3: {closure} (Closure)")
        assert str(closure) == expected_cycle_strs[0]

    @pytest.mark.parametrize("mode", ["physics"])
    def test_field_atlas(self, mode):
        """
        Experiment: Generate and View the Field Atlas.
        This test exists to print the tables to the console.
        """
        print(f"\n[LAB] Generating Atlas for {mode.upper()}...")
        GF = make_field(mode)
        
        # Generate the Reference Book
        atlas_text = GF.atlas()
        
        # Print it for the user to see with -s
        print("\n" + atlas_text)
        
        # Verify content exists
        assert "ADDITION TABLE" in atlas_text
        assert "MULTIPLICATION TABLE" in atlas_text
        assert "Modulus:" in atlas_text