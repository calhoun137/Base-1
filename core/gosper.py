from dataclasses import dataclass
from typing import Any, Optional, List, Tuple, Iterator
import math
from .stream import Stream

# --- Helper Functions ---

def safe_int_val(obj: Any) -> int:
    """Safe integer extraction."""
    if hasattr(obj, '__int__'): return int(obj)
    # Fallback to mass protocol if int conversion is missing/unsafe
    if hasattr(obj, 'mass'): return obj.mass
    return 0

@dataclass
class GosperState:
    a: Any; b: Any; c: Any; d: Any
    e: Any; f: Any; g: Any; h: Any

    @property
    def mass(self) -> int:
        """Sum of component masses."""
        return (self.a.mass + self.b.mass + self.c.mass + self.d.mass +
                self.e.mass + self.f.mass + self.g.mass + self.h.mass)

    @property
    def entropy(self) -> float:
        m = self.mass
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

    while True:
        def get_floor(num, den):
            # [PROTOCOL]
            if den.is_vacuum: return None 
            q, _ = num / den
            return q

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