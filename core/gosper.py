from dataclasses import dataclass
from typing import Any, Optional, List, Tuple, Iterator
import math
import contextvars
from .stream import Stream
from .science_mode import FastInteger

# --- Telemetry System ---
PROBE_CONTEXT = contextvars.ContextVar('gosper_probe', default=None)

# --- Helper Functions ---
def safe_int_val(obj: Any) -> int:
    """Safe integer extraction."""
    if hasattr(obj, '__int__'): return int(obj)
    if hasattr(obj, 'mass'): return obj.mass
    return 0

class GosperProbe:
    """
    A Context Manager for monitoring the internal state of Gosper Engines.
    """
    def __init__(self):
        self.log = []
        self.token = None

    def __enter__(self):
        self.token = PROBE_CONTEXT.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        PROBE_CONTEXT.reset(self.token)

    def record(self, state_obj):
        """
        Captures the Entropy and the Fano Projection (RGB Vector) of the state.
        """
        # 1. Scalar Entropy
        entropy = state_obj.entropy
        
        # 2. Fano Vector (3-component mass distribution)
        # We project the 8-dim coefficients onto the 3 Fano Axes (RGB)
        # We use ABSOLUTE MASS for the Fano vector too, because negative mass
        # in a coefficient still contributes to the "weight" of that Fano axis.
        
        # Extract masses: a,b,c,d,e,f,g,h
        masses = [
            abs(safe_int_val(state_obj.a)), abs(safe_int_val(state_obj.b)),
            abs(safe_int_val(state_obj.c)), abs(safe_int_val(state_obj.d)),
            abs(safe_int_val(state_obj.e)), abs(safe_int_val(state_obj.f)),
            abs(safe_int_val(state_obj.g)), abs(safe_int_val(state_obj.h))
        ]
        
        total_mass = sum(masses)
        if total_mass == 0: total_mass = 1
        
        # Project onto 3 Axes (RGB) using bitmask logic of the Fano Plane
        # Red Channel (Bit 0): Indices 1, 3, 5, 7 (b, d, f, h)
        r_mass = masses[1] + masses[3] + masses[5] + masses[7]
        
        # Green Channel (Bit 1): Indices 2, 3, 6, 7 (c, d, g, h)
        g_mass = masses[2] + masses[3] + masses[6] + masses[7]
        
        # Blue Channel (Bit 2): Indices 4, 5, 6, 7 (e, f, g, h)
        b_mass = masses[4] + masses[5] + masses[6] + masses[7]
        
        # Normalize to [0, 1]
        r = r_mass / total_mass
        g = g_mass / total_mass
        b = b_mass / total_mass
        
        self.log.append({
            "entropy": entropy,
            "depth": state_obj.depth,
            "fano_r": r,
            "fano_g": g,
            "fano_b": b
        })

@dataclass
class GosperState:
    a: Any; b: Any; c: Any; d: Any
    e: Any; f: Any; g: Any; h: Any
    depth: int = 0 

    @property
    def mass(self) -> int:
        return (safe_int_val(self.a) + safe_int_val(self.b) + safe_int_val(self.c) + safe_int_val(self.d) +
                safe_int_val(self.e) + safe_int_val(self.f) + safe_int_val(self.g) + safe_int_val(self.h))

    @property
    def entropy(self) -> float:
        # [CRITICAL FIX] Use absolute value for entropy.
        # Negative mass has the same information content as positive mass.
        m = abs(self.mass)
        
        if m == 0: return 0.0
        if isinstance(m, int) and m.bit_length() > 1000:
            return m.bit_length() * 0.693
        try:
            return math.log(m)
        except OverflowError:
            return float('inf')

    def ingest_x(self, p: Any):
        oa, ob, oc, od = self.a, self.b, self.c, self.d
        oe, of, og, oh = self.e, self.f, self.g, self.h
        self.a, self.b, self.c, self.d = oa * p + oc, ob * p + od, oa, ob
        self.e, self.f, self.g, self.h = oe * p + og, of * p + oh, oe, of

    def ingest_y(self, q: Any):
        oa, ob, oc, od = self.a, self.b, self.c, self.d
        oe, of, og, oh = self.e, self.f, self.g, self.h
        self.a, self.b, self.c, self.d = oa * q + ob, oa, oc * q + od, oc
        self.e, self.f, self.g, self.h = oe * q + of, oe, og * q + oh, og

    def emit(self, k: Any):
        oa, ob, oc, od = self.a, self.b, self.c, self.d
        oe, of, og, oh = self.e, self.f, self.g, self.h
        na, nb, nc, nd = oa-(oe*k), ob-(of*k), oc-(og*k), od-(oh*k)
        self.a, self.b, self.c, self.d = oe, of, og, oh
        self.e, self.f, self.g, self.h = na, nb, nc, nd

def gosper_engine(
    x_stream: Stream, y_stream: Stream,
    a: Any, b: Any, c: Any, d: Any, 
    e: Any, f: Any, g: Any, h: Any
) -> Iterator[Any]:
    
    state = GosperState(a, b, c, d, e, f, g, h)
    x_alive = True
    y_alive = True

    # Retrieve active probe
    probe = PROBE_CONTEXT.get()

    while True:
        # [TELEMETRY HOOK]
        if probe:
            probe.record(state)

        def get_floor(num, den):
            if den.is_vacuum: return None 
            q, _ = num / den
            
            # [FLOOR DIVISION FIX]
            n_val = int(num)
            d_val = int(den)
            if d_val == 0: return None
            q_floor = n_val // d_val
            if int(q) == q_floor: return q
            else:
                diff = q_floor - int(q)
                return q + diff

        candidates = []
        candidates.append(get_floor(state.a, state.e))

        if x_alive and y_alive:
            num = state.a + state.b + state.c + state.d
            den = state.e + state.f + state.g + state.h
            candidates.append(get_floor(num, den))
            
        if y_alive:
            num = state.a + state.b
            den = state.e + state.f
            candidates.append(get_floor(num, den))
            
        if x_alive:
            num = state.a + state.c
            den = state.e + state.g
            candidates.append(get_floor(num, den))

        k = None
        valid_candidates = [c for c in candidates if c is not None]
        
        if valid_candidates and len(valid_candidates) == len(candidates):
            first = valid_candidates[0]
            first_val = safe_int_val(first)
            is_consensus = True
            for c in valid_candidates[1:]:
                if safe_int_val(c) != first_val:
                    is_consensus = False
                    break
            if is_consensus: k = first

        if k is not None:
            yield k
            state.emit(k)
            continue

        consumed = False
        if x_alive:
            x_term = x_stream.head
            if x_term is None: x_alive = False 
            else:
                state.ingest_x(x_stream.consume())
                consumed = True
        
        if not consumed and y_alive:
            y_term = y_stream.head
            if y_term is None: y_alive = False
            else:
                state.ingest_y(y_stream.consume())
                consumed = True
                
        if not x_alive and not y_alive and not consumed:
            curr_num = state.a
            curr_den = state.e
            while not curr_den.is_vacuum:
                q, r = curr_num / curr_den
                yield q
                curr_num, curr_den = curr_den, r
            break