from typing import Iterator, Tuple, Any
import math
import science_mode as science
from science_mode import U, S, FastInteger

class GCFState:
    """
    A 2x2 Matrix State Machine for processing Generalized Continued Fractions.
    Refactored to use Matter Protocol.
    """
    def __init__(self):
        self.A = science.U(1)
        self.B = science.U(0)
        self.C = science.U(0)
        self.D = science.U(1)

    @property
    def mass(self) -> int:
        # [PROTOCOL] Use proper mass property, avoiding len()
        return self.A.mass + self.B.mass + self.C.mass + self.D.mass

    @property
    def entropy(self) -> float:
        m = self.mass
        if m == 0: return 0.0
        # Safe Log calculation for massive numbers
        if isinstance(m, int) and m.bit_length() > 1000:
            return m.bit_length() * 0.693
        try:
            return math.log(m)
        except OverflowError:
            return float('inf')

    def ingest(self, a: Any, b: Any):
        new_A = self.A * b + self.B
        new_B = self.A * a
        new_C = self.C * b + self.D
        new_D = self.C * a
        self.A, self.B, self.C, self.D = new_A, new_B, new_C, new_D

    def emit(self, k: Any):
        new_A = self.C
        new_B = self.D
        new_C = self.A - (self.C * k)
        new_D = self.B - (self.D * k)
        self.A, self.B, self.C, self.D = new_A, new_B, new_C, new_D

    def probe(self) -> Any:
        def get_floor(num, den):
            # [PROTOCOL] Use is_vacuum property
            if den.is_vacuum: return None
            q, _ = num / den
            return q

        f1 = get_floor(self.A, self.C)
        f2 = get_floor(self.B, self.D)
        
        if f1 is not None and f2 is not None:
            if f1 == f2: return f1
        return None

def gcf_to_scf(gcf_stream: Iterator[Tuple[Any, Any]]) -> Iterator[Any]:
    state = GCFState()
    stream_active = True
    
    while True:
        k = state.probe()
        if k is not None:
            yield k
            state.emit(k)
            continue
            
        consumed = False
        if stream_active:
            try:
                a, b = next(gcf_stream)
                state.ingest(a, b)
                consumed = True
            except StopIteration:
                stream_active = False
        
        if not consumed and k is None:
            if not stream_active:
                curr_num, curr_den = state.A, state.C
                while not curr_den.is_vacuum:
                    q, r = curr_num / curr_den
                    yield q
                    curr_num, curr_den = curr_den, r
                break
            else:
                pass

def ln_generator(x_input: Any) -> Iterator[Tuple[Any, Any]]:
    if isinstance(x_input, int): x = science.U(x_input)
    else: x = x_input
    
    yield (x, science.U(0))
    yield (x, science.U(1))
    
    k = 2
    while True:
        k_u = science.U(k)
        prev_k = science.U(k - 1)
        a = prev_k * prev_k * x
        b = k_u
        yield (a, b)
        k += 1

def e_generator(x_input: Any) -> Iterator[Tuple[Any, Any]]:
    if isinstance(x_input, int): x = science.U(x_input)
    else: x = x_input

    x_sq = x * x
    yield (science.U(2) * x, science.U(1))
    term2_b = science.U(2) - x
    yield (x_sq, term2_b)
    
    k = 1
    while True:
        val_b = 4 * k + 2
        yield (x_sq, science.U(val_b))
        k += 1