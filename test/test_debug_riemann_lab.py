import sys
import os

# Add the project root to path so we can import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.science_mode import U
from core.algorithms import Euclid
from core.stream import Stream
from core.continued_fraction import ContinuedFraction
from core.riemann_siegel import CachedStream, collapse_to_float, from_float, GET_PI

def debug_stream(name, cf_obj, depth=5):
    """Peek into a stream without consuming it permanently (using a fork)."""
    print(f"\n[PROBE] Inspecting {name}...")
    
    # We need to be careful. If we consume the stream, it's gone.
    # But ContinuedFraction wraps a Stream. 
    # If we iterate it, does it consume the underlying? Yes.
    # So we can't easily peek unless we fork it again.
    # For this debug lab, we assume we can consume things because we are just diagnosing.
    
    vals = []
    iterator = iter(cf_obj)
    for _ in range(depth):
        try:
            val = next(iterator)
            vals.append(str(val))
        except StopIteration:
            break
    print(f"       Terms: {vals}")
    return vals

def run_diagnostic():
    print("=== RIEMANN-SIEGEL DIAGNOSTIC LAB ===")
    
    # 1. Setup Input t = 44/7
    print("[STEP 1] Initializing Input t = 44/7")
    t_proc = Euclid(U(44), U(7))
    t_stream = Stream(t_proc)
    
    # 2. Test Cache Mechanism
    print("[STEP 2] Caching Stream...")
    t_cache = CachedStream(t_stream)
    print(f"       Cache Buffer Size: {len(t_cache.data)}")
    print(f"       Cache Contents:    {[str(x) for x in t_cache.data]}")
    
    if len(t_cache.data) == 0:
        print(">>> FATAL: Cache is empty! The input stream was not captured.")
        return

    # 3. Test Forking
    print("[STEP 3] Spawning Forks...")
    t_log_source = ContinuedFraction(t_cache.spawn())
    t_sub = ContinuedFraction(t_cache.spawn())
    
    # 4. Debug Log Term
    print("[STEP 4] Calculating Log Term (Collapse)...")
    val_t = collapse_to_float(t_log_source)
    print(f"       Collapsed Float Value: {val_t}")
    # We expect ~6.28
    
    # 5. Debug Term B (The Missing Pi)
    print("[STEP 5] Calculating Term B (t / 2)...")
    TWO = ContinuedFraction(Stream(Euclid(U(2), U(1))))
    
    # NOTE: Gosper Engine consumes streams. We cannot reuse TWO unless we recreate it
    # or if it generates infinite 2s (it doesn't, it's rational 2).
    # Euclid(2,1) yields [2]. That's it.
    
    term_b = t_sub / TWO
    
    # Inspect the output of Term B
    b_vals = debug_stream("Term B (t/2)", term_b)
    
    # We expect [3, 7] (approx 3.14)
    # If we get [0], we found the bug.
    
    # 6. Debug Subtraction
    print("[STEP 6] Simulating Subtraction (0 - Term B)...")
    
    # Re-create streams because we consumed them above
    t_sub_2 = ContinuedFraction(t_cache.spawn())
    TWO_2 = ContinuedFraction(Stream(Euclid(U(2), U(1))))
    term_b_2 = t_sub_2 / TWO_2
    
    ZERO_STREAM = ContinuedFraction(Stream(Euclid(U(0), U(1)))) # [0]
    
    diff = ZERO_STREAM - term_b_2
    debug_stream("Difference (0 - t/2)", diff)

def test_riemann_lab():
    run_diagnostic()