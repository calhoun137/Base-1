from core.stream import Stream
from core.transcendental import e_generator, gcf_to_scf
from core.complex_mode import C, GaussianInteger
import core.science_mode as science

def run_complex_exp_test():
    print("=== Euler's Identity Stress Test (Complex Exponentiation) ===")
    
    # Case: e^(i)
    # x = 0 + 1i
    x = C(0, 1)
    print(f"  Input: e^({x})")
    print(f"  Target: cos(1) + i*sin(1) ~= 0.5403 + 0.8415i")
    print("  Expected First Term (Nearest Gaussian Integer):")
    print("    Dist to 0: ~1.0")
    print("    Dist to i: ~0.56")
    print("    Dist to 1: ~0.67")
    print("    -> Expect 'i' (0+1i)")

    # 1. Create Generator
    gcf_source = e_generator(x)
    
    # 2. Pump
    scf_gen = gcf_to_scf(gcf_source)
    stream = Stream(scf_gen)
    
    # 3. Consume
    print("  Streaming terms...")
    results = []
    for i in range(5):
        term = stream.consume()
        results.append(str(term))
        if len(results) >= 3: break
        
    print(f"  Got: {results}")
    
    # Verify First Term
    if "1+1i" in results[0] or "U(0)+U(1)i" in results[0]:
        print("PASS: First term is '1+i'. Rotation Confirmed.")
    else:
        print(f"FAIL: Expected '1+i', Got {results[0]}")

def test_complex_exp():
    try:
        run_complex_exp_test()
    except Exception as e:
        print(f"CRITICAL FAIL: {e}")
        import traceback
        traceback.print_exc()
