import pytest
from core.stream import Stream
from core.transcendental import gcf_to_scf, ln_generator, e_generator

class TestTranscendental:
    """
    Specifications for the Transcendental Matrix Pumps.
    Verifies that Generalized Continued Fractions (GCF) are correctly 
    transduced into Simple Continued Fractions (SCF) via the Matrix State.
    """

    # --- Define The Math ---
    transcendental_cases = [
        # (Name, Generator_Func, Input_x, Expected_Prefix)
        
        # ln(2) = ln(1 + 1)
        # GCF Pattern: (1,1), (1,2), (4,3)...
        # SCF: [0; 1, 2, 3, 1, 6...]
        ("ln(2)", ln_generator, 1, [0, 1, 2, 3, 1]),

        # Euler's Number e = e^1
        # SCF: [2; 1, 2, 1, 1, 4, 1, 1...]
        ("e", e_generator, 1, [2, 1, 2, 1, 1, 4, 1, 1]),
    ]

    case_ids = [name for name, _, _, _ in transcendental_cases]

    @pytest.mark.parametrize("name, gen_func, x_val, expected_prefix", transcendental_cases, ids=case_ids)
    def test_transcendental_pump(self, name, gen_func, x_val, expected_prefix):
        print(f"\n[LAB] Pump: {name} (input x={x_val})")
        
        # 1. Initialize the Source (GCF Generator)
        gcf_source = gen_func(x_val)
        
        # 2. Initialize the Pump (Transducer)
        # This converts the matrix stream into an integer stream
        scf_stream_gen = gcf_to_scf(gcf_source)
        stream = Stream(scf_stream_gen)
        
        # 3. Consume and Verify
        # We only check the prefix since these are infinite irrational numbers
        results = []
        limit = len(expected_prefix)
        
        print(f"       Stream: ", end="")
        
        for _ in range(limit + 5): # Buffer to catch "short stream" bugs
            if len(results) == limit:
                break
                
            term = stream.consume()
            if term is None:
                print("(EOS)", end="")
                break
            
            val = int(term)
            results.append(val)
            print(f"{val} ", end="")
            
        print("") # Newline
        
        assert results == expected_prefix, \
            f"Stream Mismatch for {name}.\nExpected: {expected_prefix}\nGot:      {results}"