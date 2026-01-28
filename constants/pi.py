from typing import Iterator, Tuple, Any
from core.science_mode import U as ScienceU
from core.algorithms import Euclid
from core.stream import Stream
from core.continued_fraction import ContinuedFraction
from core.transcendental import gcf_to_scf

# --- Constructive Pi Generator ---

def pi_gcf_source(backend_factory) -> Iterator[Tuple[Any, Any]]:
    """
    Generates the Generalized Continued Fraction for (Pi - 3).
    Formula: 0 + 1^2 / (6 + 3^2 / (6 + 5^2 / ...))
    
    Uses the provided 'backend_factory' (U) to ensure all arithmetic 
    obeys the physics of the chosen universe (String Concat vs Integers).
    """
    U = backend_factory
    
    # 1. The Inversion Step (0 + 1/...)
    # We must explicitly yield (1, 0) to set the transform to 0 + 1/z
    ONE = U(1)
    ZERO = U(0)
    yield (ONE, ZERO)
    
    # 2. The Series Loop
    # We start at n=2 because n=1 (1^2) is handled by the (1, 0) term above?
    # Wait, the formula is 1^2 / (6 + ...).
    # The (1, 0) term sets up 1/z. 
    # The next term must be (3^2, 6) corresponding to 6 + 9/z.
    # So we need the loop to generate odd squares starting from 3^2.
    
    # Initial State: n = 2
    n = U(2)
    TWO = U(2)
    SIX = U(6)
    
    while True:
        # Calculate Odd Number: 2n - 1
        # Physics: ||...| + ||...| - |
        n_doubled = n * TWO
        odd = n_doubled - ONE
        
        # Calculate Square: odd * odd
        a_val = odd * odd
        
        # Denominator is always 6
        b_val = SIX
        
        yield (a_val, b_val)
        
        # Increment n
        n = n + ONE

def constructive_pi_stream(backend_factory=ScienceU) -> Iterator[Any]:
    """
    Returns the SCF Stream for Pi: [3; 7, 15, 1, 292...]
    """
    # 1. Generate the GCF Stream for (Pi - 3)
    # We inject the desired backend (ScienceU by default for speed, 
    # but compatible with PhysicsU).
    gcf_gen = pi_gcf_source(backend_factory)
    
    # 2. Transduce to SCF
    scf_gen_fraction = gcf_to_scf(gcf_gen)
    
    # 3. Splice Integer Part (3)
    THREE = backend_factory(3)
    yield THREE
    
    # Consume leading zero from fractional part [0; 7, 15...]
    try:
        leading_zero = next(scf_gen_fraction)
        # In PhysicsMode, we must check vacuum property carefully
        is_vac = False
        if hasattr(leading_zero, 'is_vacuum'): is_vac = leading_zero.is_vacuum
        elif hasattr(leading_zero, 'mass'): is_vac = (leading_zero.mass == 0)
        
        if not is_vac:
             yield leading_zero
    except StopIteration:
        pass

    yield from scf_gen_fraction

def GET_PI(backend_factory=ScienceU) -> ContinuedFraction:
    """Factory for a fresh Pi stream."""
    return ContinuedFraction(Stream(constructive_pi_stream(backend_factory)))