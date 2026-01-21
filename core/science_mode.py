from typing import Any, Tuple, Union

class FastInteger:
    """
    A High-Performance wrapper around Python's native int.
    Implements the Base-1 Matter Protocol.
    """
    __slots__ = ('_val',)

    def __init__(self, value: Any):
        if isinstance(value, int):
            self._val = value
        elif hasattr(value, '__int__'):
            self._val = int(value)
        else:
            raise TypeError(f"Cannot create FastInteger from {type(value)}")

    # [PROTOCOL] Science Mode: Mass is Magnitude (Arbitrary Precision)
    @property
    def mass(self) -> int:
        return abs(self._val)

    @property
    def is_vacuum(self) -> bool:
        return self._val == 0

    # SAFETY: We return 1 to signify this is an 'Atomic' unit of matter.
    # This prevents legacy code using len() from crashing on massive numbers.
    def __len__(self) -> int:
        return 1

    def __int__(self) -> int:
        return self._val

    def __repr__(self) -> str:
        if self._val >= 0: return f"U({self._val})"
        else: return f"S({abs(self._val)})"

    def __str__(self) -> str:
        return str(self._val)

    # --- Arithmetic Operations (Universal) ---

    def _extract(self, other: Any) -> int:
        if isinstance(other, int): return other
        if hasattr(other, '__int__'): return int(other)
        return NotImplemented

    def __add__(self, other: Any) -> "FastInteger":
        val = self._extract(other)
        if val is NotImplemented: return NotImplemented
        return FastInteger(self._val + val)

    def __radd__(self, other: Any) -> "FastInteger": return self.__add__(other)

    def __sub__(self, other: Any) -> "FastInteger":
        val = self._extract(other)
        if val is NotImplemented: return NotImplemented
        return FastInteger(self._val - val)

    def __rsub__(self, other: Any) -> "FastInteger":
        val = self._extract(other)
        if val is NotImplemented: return NotImplemented
        return FastInteger(val - self._val)

    def __mul__(self, other: Any) -> "FastInteger":
        val = self._extract(other)
        if val is NotImplemented: return NotImplemented
        return FastInteger(self._val * val)

    def __rmul__(self, other: Any) -> "FastInteger": return self.__mul__(other)

    def __truediv__(self, other: Any) -> Tuple["FastInteger", "FastInteger"]:
        denom = self._extract(other)
        if denom is NotImplemented: return NotImplemented
        if denom == 0: raise ZeroDivisionError("ScienceMode: Division by zero")

        num = self._val
        q_mag = abs(num) // abs(denom)
        r_mag = abs(num) % abs(denom)

        if (num < 0) ^ (denom < 0): q_val = -q_mag
        else: q_val = q_mag
            
        if num < 0: r_val = -r_mag
        else: r_val = r_mag

        return (FastInteger(q_val), FastInteger(r_val))

    def __rtruediv__(self, other: Any) -> Tuple["FastInteger", "FastInteger"]:
        num = self._extract(other)
        if num is NotImplemented: return NotImplemented
        return FastInteger(num) / self

    # [NEW] Modulo Operator: Truncated Remainder
    def __mod__(self, other: Any) -> "FastInteger":
        val = self._extract(other)
        if val is NotImplemented: return NotImplemented
        
        m_self = abs(self._val)
        m_other = abs(val)
        
        if m_other == 0: raise ZeroDivisionError("ScienceMode: Modulo by zero")
        
        # Calculate Magnitude of Remainder
        r_mag = m_self % m_other
        
        # Apply Sign of Dividend (self)
        if self._val < 0:
            return FastInteger(-r_mag)
        else:
            return FastInteger(r_mag)

    # --- Comparison Operations ---
    
    def __eq__(self, other: Any) -> bool:
        val = self._extract(other)
        if val is NotImplemented: return False
        return self._val == val
    
    def __lt__(self, other: Any) -> bool:
        val = self._extract(other)
        if val is NotImplemented: return NotImplemented
        return self._val < val

    def __le__(self, other: Any) -> bool:
        val = self._extract(other)
        if val is NotImplemented: return NotImplemented
        return self._val <= val

    def __gt__(self, other: Any) -> bool:
        val = self._extract(other)
        if val is NotImplemented: return NotImplemented
        return self._val > val

    def __ge__(self, other: Any) -> bool:
        val = self._extract(other)
        if val is NotImplemented: return NotImplemented
        return self._val >= val

    def __hash__(self): return hash(self._val)

def U(n: int) -> FastInteger:
    if n < 0: raise ValueError("U() is for non-negative integers only")
    return FastInteger(n)

def S(n: int) -> FastInteger:
    if n < 0: raise ValueError("S() magnitude must be positive")
    return FastInteger(-n)