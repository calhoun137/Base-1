import pytest
from algorithms import Euclid
from stream import Stream
import unary as physics_backend
import science_mode as science_backend

# [HELPER] Factory to switch universes
def get_matter_factory(mode):
    if mode == "physics":
        return physics_backend.U
    elif mode == "science":
        return science_backend.U
    raise ValueError(f"Unknown Universe: {mode}")

class TestRationalNumbers:
    """
    Specifications for Rational Number decomposition (Euclidean Algorithm).
    Verifies that p/q produces the correct Finite Continued Fraction sequence.
    Runs identically on both 'Unary Strings' and 'Fast Integers'.
    """

    # --- 1. Define The Math (Universal Truths) ---
    rational_cases = [
        # (Numerator, Denominator, Expected Sequence)
        (1, 5,   [0, 5]),         # 1/5 -> [0; 5]
        (10, 7,  [1, 2, 3]),      # 10/7 = 1 + 1/(2 + 1/3)
        (3, 2,   [1, 2]),         # 3/2 -> 1 + 1/2
        (415, 93,[4, 2, 6, 7]),   # Standard Euclidean Example
        (7, 1,   [7]),            # Integer Case
    ]
    
    # Human-Readable IDs for the math cases
    case_ids = [f"{p}/{q}" for p, q, _ in rational_cases]

    # --- 2. The Experiment ---
    @pytest.mark.parametrize("mode", ["physics", "science"])
    @pytest.mark.parametrize("num_val, den_val, expected_seq", rational_cases, ids=case_ids)
    def test_euclid_algorithm(self, mode, num_val, den_val, expected_seq):
        
        # 1. Materialize Numbers (in the correct universe)
        U = get_matter_factory(mode)
        p = U(num_val)
        q = U(den_val)
        
        print(f"\n[LAB] Universe: {mode.upper()}")
        print(f"       Decomposing: {p} / {q}")
        
        # 2. Initialize The Machine
        process = Euclid(p, q)
        stream = Stream(process)
        
        # 3. Observe the Stream
        result_sequence = []
        
        # Safety: We add a buffer to the expected length to catch infinite loop bugs
        # (e.g. if the algorithm fails to terminate on the GCD)
        max_steps = len(expected_seq) + 2
        
        print(f"       Stream Output: ", end="")
        
        for _ in range(max_steps):
            if stream.head is None:
                print("(End)")
                break
                
            term = stream.consume()
            # We convert to Python int for verification against the Spec
            val = int(term)
            result_sequence.append(val)
            print(f"{val} -> ", end="")

        # 4. Verify
        # Check 1: Sequence matches exactly
        assert result_sequence == expected_seq, \
            f"\nSequence Mismatch in {mode} mode.\nExpected: {expected_seq}\nActual:   {result_sequence}"
            
        # Check 2: Stream correctly terminated (Vacuum state)
        # If the stream yielded more items than expected, it's a bug.
        assert stream.head is None, "Stream failed to terminate (Infinite Loop detected?)"