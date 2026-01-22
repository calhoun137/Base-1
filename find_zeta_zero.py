import math
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.science_mode import U
from core.algorithms import Euclid
from core.stream import Stream
from core.continued_fraction import ContinuedFraction
from core.riemann_siegel import stirling_theta

def evaluate_stream(cf_obj, depth=30):
    terms = []
    iterator = iter(cf_obj)
    for _ in range(depth):
        try:
            terms.append(int(next(iterator)))
        except StopIteration:
            break
            
    if not terms: return 0.0
    val = 0.0
    for t in reversed(terms):
        if val == 0: val = float(t)
        else: val = float(t) + (1.0 / val)
    return val

def analyze_point(t_val, num, den):
    print(f"\n[PROBE] t = {t_val:<6} | Rational: {num}/{den}")
    
    # 1. Materialize
    t_proc = Euclid(U(num), U(den))
    t_cf = ContinuedFraction(Stream(t_proc))
    
    # 2. Compute Phase
    theta_cf = stirling_theta(t_cf)
    
    # 3. Collapse
    theta_val = evaluate_stream(theta_cf)
    
    # 4. Compute Z(t)
    # Z(t) ~ 2 * cos(theta) for N=1
    z_val = 2 * math.cos(theta_val)
    
    print(f"       Theta: {theta_val:.5f} rad")
    print(f"       Z(t):  {z_val:+.5f}")
    
    return z_val

def run_experiment():
    print("=== THE RIEMANN-SIEGEL EXPERIMENT: ZERO SEARCH ===")
    print("Scanning the Critical Line for a sign change...")
    print("Note: Neglecting the Remainder Term R(t) shifts the zero slightly right for low t.")
    
    # We define a scan path: 14.0 -> 14.5 -> 14.8
    # 14.5 was -0.015 (Very close!), so 14.8 should definitely be positive.
    checkpoints = [
        (14.0, 14, 1),
        (14.5, 29, 2),
        (14.8, 74, 5)  # 14.8 = 74/5
    ]
    
    prev_z = None
    prev_t = None
    
    zero_found = False
    
    for t, num, den in checkpoints:
        z = analyze_point(t, num, den)
        
        if prev_z is not None:
            # Check for Sign Flip (The Crossing)
            if (prev_z < 0 and z > 0) or (prev_z > 0 and z < 0):
                print("\n" + "="*50)
                print(">>> SUCCESS: ZERO DETECTED <<<")
                print("="*50)
                print(f"The Riemann Zeta function crossed zero between t={prev_t} and t={t}.")
                print(f"Interval: [{prev_z:.5f}, {z:.5f}]")
                zero_found = True
                break
        
        prev_z = z
        prev_t = t
        
    if not zero_found:
        print("\n>>> INCONCLUSIVE: No sign change in checked points.")

if __name__ == "__main__":
    run_experiment()