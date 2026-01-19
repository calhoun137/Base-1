import pytest
from algorithms import Euclid
from stream import Stream
from complex_mode import C, GaussianInteger
import complex_mode as complex_backend

class TestComplexEuclid:
    """
    Specifications for the Euclidean Algorithm in the Complex Plane.
    Verifies that the Hurwitz Division logic correctly drives the 
    Tiling Generator to decompose Gaussian Rational Numbers.
    """

    # --- 1. Define The Math ---
    complex_cases = [
        # (Numerator, Denominator, Expected_Sequence)
        
        # Case 1: Exact Division
        # 10 / (3+i) = 3-i
        # Math: 10(3-i) / 10 = 3-i. Remainder 0.
        # Sequence: [3-i]
        (C(10, 0), C(3, 1), [C(3, -1)]),

        # Case 2: Two-Step Expansion
        # (5+2i) / (2+i)
        # Step 1: (5+2i)/(2+i) ~ 2.4 - 0.2i -> Round(2). Rem = 1.
        # Step 2: (2+i)/1 = 2+i. Rem = 0.
        # Sequence: [2, 2+i]
        (C(5, 2), C(2, 1), [C(2, 0), C(2, 1)]),

        # Case 3: Rotation/Units
        # i / 1 = i
        (C(0, 1), C(1, 0), [C(0, 1)]),
    ]

    case_ids = [
        "10 / (3+i)",
        "(5+2i) / (2+i)",
        "i / 1"
    ]

    # --- 2. The Experiment ---
    @pytest.mark.parametrize("num, den, expected_seq", complex_cases, ids=case_ids)
    def test_complex_tiling(self, num, den, expected_seq):
        print(f"\n[LAB] Complex Tiling: {num} / {den}")
        
        # 1. Initialize The Machine
        # Euclid is polymorphic; it works because GaussianInteger implements __truediv__
        process = Euclid(num, den)
        stream = Stream(process)
        
        # 2. Observe the Stream
        result_sequence = []
        limit = len(expected_seq) + 2 # Safety buffer
        
        print(f"       Stream: ", end="")
        
        for _ in range(limit):
            if stream.head is None:
                print("(End)")
                break
                
            term = stream.consume()
            result_sequence.append(term)
            print(f"{term} -> ", end="")
            
        print("") # Newline
        
        # 3. Verification
        # We verify length first
        assert len(result_sequence) == len(expected_seq), \
            f"Length Mismatch. Expected {len(expected_seq)}, Got {len(result_sequence)}"
            
        # We verify values component-wise
        for i, (got, exp) in enumerate(zip(result_sequence, expected_seq)):
            # We assume the 'science_mode' backend for the values inside C()
            # but we cast to int just to be safe and universal
            assert int(got.real) == int(exp.real) and int(got.imag) == int(exp.imag), \
                f"Term {i} Mismatch. Expected {exp}, Got {got}"