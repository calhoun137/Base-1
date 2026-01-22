import math
from typing import Iterator, Any, List, Tuple, Optional
from .stream import Stream
from .continued_fraction import ContinuedFraction
from .algorithms import Euclid
from .science_mode import U, S
from . import science_mode

# --- 1. Constants & Registry ---

BERNOULLI_MAP = {
    2: (1, 6),
    4: (-1, 30),
    6: (1, 42),
    8: (-1, 30),
    10: (5, 66)
}

def pi_generator() -> Iterator[Any]:
    coeffs = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2]
    for c in coeffs:
        yield U(c)

# [FIX] Factories for Constants
# Streams are single-use. We must create a fresh stream for every operation.

def GET_PI() -> ContinuedFraction:
    return ContinuedFraction(Stream(pi_generator()))

def GET_TWO() -> ContinuedFraction:
    return ContinuedFraction(Stream(Euclid(U(2), U(1))))

def GET_EIGHT() -> ContinuedFraction:
    return ContinuedFraction(Stream(Euclid(U(8), U(1))))

def GET_FORTY_EIGHT() -> ContinuedFraction:
    return ContinuedFraction(Stream(Euclid(U(48), U(1))))

def GET_ONE() -> ContinuedFraction:
    return ContinuedFraction(Stream(Euclid(U(1), U(1))))

# --- 2. Stream Buffering (Robust) ---

class CachedStream:
    """
    A robust stream buffer that eagerly consumes a finite source
    and serves infinite independent cursors.
    """
    def __init__(self, source_stream: Stream):
        self.data: List[Any] = []
        # Eagerly consume the entire source
        while True:
            try:
                if source_stream.head is None: break
                self.data.append(source_stream.consume())
            except StopIteration:
                break

    def spawn(self) -> Stream:
        """Create a new independent read-head."""
        return Stream(self._reader())

    def _reader(self) -> Iterator[Any]:
        for item in self.data:
            yield item

def collapse_to_float(cf: ContinuedFraction, depth: int = 20) -> float:
    terms = []
    iterator = iter(cf)
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

def from_float(val: float, precision: int = 1000000) -> ContinuedFraction:
    num = int(val * precision)
    den = precision
    proc = Euclid(U(num), U(den))
    return ContinuedFraction(Stream(proc))

# --- 3. The Stirling Engine ---

def stirling_theta(t: ContinuedFraction) -> ContinuedFraction:
    """
    Computes the Riemann-Siegel Theta phase angle.
    theta(t) ~ (t/2)*ln(t/2pi) - t/2 - pi/8 + 1/(48t) ...
    """
    
    # 1. Cache the Input Variable 't'
    t_cache = CachedStream(t.stream)
    
    t_log_source = ContinuedFraction(t_cache.spawn())
    t_linear = ContinuedFraction(t_cache.spawn())
    t_sub = ContinuedFraction(t_cache.spawn())
    t_series = ContinuedFraction(t_cache.spawn())
    
    # 2. Compute Transcendental Log Term (Collapse Strategy)
    val_t = collapse_to_float(t_log_source)
    val_pi = math.pi
    
    try:
        val_arg = val_t / (2 * val_pi)
        if val_arg <= 0:
            log_val = 0.0
        else:
            log_val = math.log(val_arg)
    except Exception:
        log_val = 0.0

    log_cf = from_float(log_val)
    
    # 3. Build Terms (Arithmetic Layer)
    # [FIX] Use Factories to generate fresh streams for every op
    
    # Term A: (t/2) * ln(...)
    t_half = t_linear / GET_TWO()
    term_a = t_half * log_cf
    
    # Term B: t/2 (Used for subtraction)
    # We must use a FRESH 'TWO' here!
    term_b = t_sub / GET_TWO()
    
    # Term C: pi/8
    term_c = GET_PI() / GET_EIGHT()
    
    # Term D: Stirling Correction (1 / 48t)
    denom_d = GET_FORTY_EIGHT() * t_series
    term_d = GET_ONE() / denom_d
    
    # 4. Assembly (Linear Combination)
    # theta = Term A - Term B - Term C + Term D
    
    # (A - B)
    res_1 = term_a - term_b
    
    # (res_1 - C)
    res_2 = res_1 - term_c
    
    # (res_2 + D)
    theta = res_2 + term_d
    
    return theta