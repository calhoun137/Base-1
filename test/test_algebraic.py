import pytest
from stream import Stream
from polynomial import Polynomial
from algorithms import AlgebraicStream
import unary as physics_backend
import science_mode as science_backend

# [HELPER] Factory to switch universes and build matter
def make_poly(mode, coeffs_ints):
    """
    Constructs a Polynomial in the specified universe.
    coeffs_ints: List[int] (e.g. [-2, 0, 1] for x^2 - 2)
    """
    if mode == "physics":
        U, S = physics_backend.U, physics_backend.S
    elif mode == "science":
        U, S = science_backend.U, science_backend.S
    else:
        raise ValueError(f"Unknown Universe: {mode}")

    # Convert raw ints to Physical/Science Integers
    c_objs = []
    for c in coeffs_ints:
        if c >= 0:
            c_objs.append(U(c))
        else:
            c_objs.append(S(abs(c)))
            
    return Polynomial(c_objs)

class TestAlgebraicNumbers:
    """
    Specifications for Algebraic Number Generation.
    Verifies that the 'AlgebraicStream' algorithm correctly converts
    roots of polynomials P(x)=0 into Continued Fraction streams.
    """

    # --- 1. Define The Math (Universal Truths) ---
    algebraic_cases = [
        # (Name, Coeffs[low->high], Expected Sequence)
        
        # Sqrt(2): Root of x^2 - 2 = 0
        # Coeffs: [-2, 0, 1]
        # CF: [1; 2, 2, 2, ...]
        ("Sqrt(2)", [-2, 0, 1], [1, 2, 2, 2, 2]),

        # Golden Ratio (phi): Root of x^2 - x - 1 = 0
        # Coeffs: [-1, -1, 1]
        # CF: [1; 1, 1, 1, 1]
        ("GoldenRatio", [-1, -1, 1], [1, 1, 1, 1, 1]),

        # Sqrt(3): Root of x^2 - 3 = 0
        # Coeffs: [-3, 0, 1]
        # CF: [1; 1, 2, 1, 2]
        ("Sqrt(3)", [-3, 0, 1], [1, 1, 2, 1, 2]),
    ]
    
    # Human-Readable IDs
    case_ids = [name for name, _, _ in algebraic_cases]

    # --- 2. The Experiment ---
    @pytest.mark.parametrize("mode", ["physics", "science"])
    @pytest.mark.parametrize("name, coeffs, expected_seq", algebraic_cases, ids=case_ids)
    def test_algebraic_stream(self, mode, name, coeffs, expected_seq):
        
        # 1. Create the 'Matter' (Polynomial)
        poly = make_poly(mode, coeffs)
        
        print(f"\n[LAB] Universe: {mode.upper()}")
        print(f"       Target:   {name}")
        print(f"       Poly:     {poly}")
        
        # 2. Start the Process
        # (AlgebraicStream is the generator that solves P(x)=0)
        process = AlgebraicStream(poly)
        stream = Stream(process)
        
        # 3. Consume and Monitor
        result_sequence = []
        limit = len(expected_seq)
        
        print(f"       Stream:   ", end="")
        
        # Safety Brake: loop only as far as we expect + buffer
        # This prevents infinite loops if the engine stalls
        for _ in range(limit + 2):
            if len(result_sequence) == limit:
                break
                
            if stream.head is None:
                print("(Terminated Early)", end="")
                break
            
            term = stream.consume()
            val = int(term)
            result_sequence.append(val)
            print(f"{val} ", end="")
            
        print("") # Newline
        
        # 4. Verification
        assert result_sequence == expected_seq, \
            f"Stream Mismatch in {mode}.\nExpected: {expected_seq}\nGot:      {result_sequence}"

        # 5. Thermodynamic Check (Implicit)
        # If we got here, the 'mass' (polynomial coefficients) didn't explode 
        # beyond memory limits, and the 'entropy' (calculation steps) remained finite.