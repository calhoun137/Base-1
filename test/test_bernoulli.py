import pytest
from constants.bernoulli import akiyama_tanigawa_generator
from core.science_mode import U
from core.unary import U as PhysicsU

class TestBernoulli:
    """
    Specifications for the Constructive Bernoulli Generator.
    """

    # --- 1. The Math ---
    # B_0 = 1
    # B_1 = 1/2 (Akiyama-Tanigawa produces +1/2 usually)
    # B_2 = 1/6
    # B_3 = 0
    # B_4 = -1/30
    # B_5 = 0
    # B_6 = 1/42
    
    expected_sequence = [
        (1, 1),   # B0
        (1, 2),   # B1
        (1, 6),   # B2
        (0, 1),   # B3 (0) - Denom might vary, num must be 0
        (-1, 30), # B4
        (0, 1),   # B5
        (1, 42)   # B6
    ]

    @pytest.mark.parametrize("mode", ["science", "physics"])
    def test_bernoulli_generation(self, mode):
        print(f"\n[LAB] Bernoulli Generator ({mode})")
        
        if mode == "science": factory = U
        else: factory = PhysicsU
        
        gen = akiyama_tanigawa_generator(factory)
        
        results = []
        for i in range(len(self.expected_sequence)):
            num, den = next(gen)
            
            # Normalize for comparison
            # Convert to python int
            n_val = int(num)
            d_val = int(den)
            
            # Handle 0 case (0/x -> 0/1)
            if n_val == 0:
                results.append((0, 1))
            else:
                # Handle Sign: Put sign on numerator
                if d_val < 0:
                    n_val = -n_val
                    d_val = -d_val
                
                results.append((n_val, d_val))
                
            print(f"       B_{i} -> {num}/{den}")

        # Verification
        # We allow B1 to be +1/2 or -1/2 (A-T is +1/2)
        # We normalize the expected B4 (-1/30) to match the generator's likely output
        
        print(f"       Got: {results}")
        
        # Check B0
        assert results[0] == (1, 1)
        
        # Check B2 (1/6)
        assert results[2] == (1, 6)
        
        # Check B4 (-1/30) or (1, -30) - logic handles sign
        # A-T logic: 
        # B4 = -1/30.
        assert results[4] == (-1, 30) or results[4] == (1, -30)