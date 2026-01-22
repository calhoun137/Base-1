import pytest
from constants.pi import GET_PI
from core.science_mode import U

class TestConstructiveConstants:
    """
    Specifications for Constructive Constant Generation.
    Verifies that algorithmic streams (like Pi) match known values.
    """

    # --- 1. Define The Math ---
    # Pi SCF: [3; 7, 15, 1, 292, 1, 1, 1, 2...]
    pi_scf_terms = [3, 7, 15, 1, 292, 1, 1, 1, 2]

    def test_constructive_pi(self):
        print(f"\n[LAB] Constructive Pi Generator")
        
        # 1. Materialize
        # We invoke the factory to get a fresh stream
        pi_cf = GET_PI()
        
        # 2. Observe
        print(f"       Generating first {len(self.pi_scf_terms)} terms...")
        
        seq = []
        iterator = iter(pi_cf)
        
        # Safety limit
        for _ in range(len(self.pi_scf_terms) + 2):
            try:
                term = next(iterator)
                seq.append(int(term))
            except StopIteration:
                break
        
        # 3. Verify
        print(f"       Got:      {seq}")
        print(f"       Expected: {self.pi_scf_terms}")
        
        # We check that the generated prefix matches the known sequence
        # We check only up to the length of our reference data
        measured_prefix = seq[:len(self.pi_scf_terms)]
        assert measured_prefix == self.pi_scf_terms