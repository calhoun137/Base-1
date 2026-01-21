from typing import Iterator, Any
import math

def Euclid(numerator: Any, denominator: Any) -> Iterator[Any]:
    """
    The Euclidean Algorithm as a Generative Process.
    Converts a Rational Number (p/q) into a Stream.
    Refactored to use 'is_vacuum' Protocol.
    """
    curr_num = numerator
    curr_den = denominator

    while True:
        # [FIX] Protocol Check:
        # We must check .is_vacuum instead of len().
        # ScienceMode objects have len()=1 even when they are zero (Mass=0).
        if hasattr(curr_den, 'is_vacuum'):
            if curr_den.is_vacuum:
                break
        elif hasattr(curr_den, '__len__'):
             # Fallback for legacy objects or raw lists
             if len(curr_den) == 0:
                 break
        elif isinstance(curr_den, int):
             if curr_den == 0:
                 break
            
        quotient, remainder = curr_num / curr_den
        yield quotient
        curr_num = curr_den
        curr_den = remainder

def AlgebraicStream(poly: Any, max_iter: int = 1000) -> Iterator[Any]:
    """
    The Generalized Euclidean Algorithm for Polynomials.
    Generates the Continued Fraction for the positive root of P(x)=0.
    """
    
    # Detect Backend for Factory
    sample = poly.coeffs[0]
    if hasattr(sample, '_val'): 
        from .science_mode import U
        ONE = U(1)
        ZERO = U(0)
    else: 
        from .unary import U
        ONE = U(1)
        ZERO = U(0)

    current_P = poly

    for step in range(max_iter):
        
        # --- 1. Thermodynamic Observation ---
        # [FIX] Use .mass property instead of implied length
        m = current_P.mass
        
        # Safe Log calculation
        if isinstance(m, int) and m.bit_length() > 1000:
             entropy = m.bit_length() * 0.693
        else:
             entropy = math.log(m) if m > 0 else 0

        # --- 2. Locate the Floor (k) ---
        k_int = 0
        val_at_k = current_P.evaluate(ZERO)
        
        start_sign = (val_at_k > ZERO) 
        
        while True:
            next_k_obj = U(k_int + 1)
            val_next = current_P.evaluate(next_k_obj)
            
            # [FIX] Exact root check using Protocol
            is_root = False
            if hasattr(val_next, 'is_vacuum'): 
                is_root = val_next.is_vacuum
            elif hasattr(val_next, '__len__'): 
                is_root = (len(val_next) == 0)
            elif isinstance(val_next, int): 
                is_root = (val_next == 0)

            if is_root: 
                yield next_k_obj
                return 

            next_sign = (val_next > ZERO)
            
            if start_sign != next_sign:
                # Sign flipped. Floor is k.
                break
                
            k_int += 1
            val_at_k = val_next
            
            if k_int > 1000: 
                raise RuntimeError("Failed to isolate root (scan exceeded 1000).")

        # --- 3. Emit ---
        k_obj = U(k_int)
        yield k_obj
        
        # --- 4. Transform (The Accordion) ---
        # x -> 1 / (x - k)
        P_shifted = current_P.shift(k_obj)
        current_P = P_shifted.reverse()
        
        # Check termination (Constant polynomial)
        # Poly.__len__ returns number of coefficients, so <=1 means constant.
        if len(current_P) <= 1:
            break