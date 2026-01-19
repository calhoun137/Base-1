from typing import Any, Tuple, Union
import science_mode as science
from science_mode import U, S, FastInteger

class GaussianInteger:
    """
    Represents a complex number a + bi.
    Implements Matter Protocol for Mass checks.
    """
    __slots__ = ('real', 'imag')

    def __init__(self, real: Any, imag: Any):
        self.real = self._ensure_physical(real)
        self.imag = self._ensure_physical(imag)

    def _ensure_physical(self, val: Any):
        if isinstance(val, int):
            return U(val) if val >= 0 else S(abs(val))
        return val

    # [PROTOCOL] Mass is sum of component masses
    @property
    def mass(self) -> int:
        return self.real.mass + self.imag.mass

    @property
    def is_vacuum(self) -> bool:
        return self.mass == 0

    # Legacy support: safe_mag is now just mass access
    def __len__(self) -> int:
        return self.mass

    def __repr__(self) -> str: return f"({self.real}+{self.imag}i)"
    def __str__(self) -> str: return f"{self.real}+{self.imag}i"
    def norm_sq(self): return (self.real * self.real) + (self.imag * self.imag)

    # --- Type Promotion ---
    
    def _promote(self, other: Any) -> "GaussianInteger":
        if isinstance(other, GaussianInteger): return other
        return GaussianInteger(other, 0)

    # --- Arithmetic ---

    def __add__(self, other: Any) -> "GaussianInteger":
        other = self._promote(other)
        return GaussianInteger(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other: Any) -> "GaussianInteger":
        other = self._promote(other)
        return GaussianInteger(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other: Any) -> "GaussianInteger":
        other = self._promote(other)
        r = (self.real * other.real) - (self.imag * other.imag)
        i = (self.real * other.imag) + (self.imag * other.real)
        return GaussianInteger(r, i)

    def __truediv__(self, other: Any) -> Tuple["GaussianInteger", "GaussianInteger"]:
        other = self._promote(other)
        denom_val = other.norm_sq()
        
        # Use Protocol for zero check
        if denom_val.is_vacuum:
            raise ZeroDivisionError("Complex Division by Zero")

        ZERO = self.real - self.real 
        other_conj_imag = ZERO - other.imag
        
        num_r = (self.real * other.real) - (self.imag * other_conj_imag)
        num_i = (self.real * other_conj_imag) + (self.imag * other.real)

        q_real = self._div_nearest(num_r, denom_val)
        q_imag = self._div_nearest(num_i, denom_val)
        
        quotient = GaussianInteger(q_real, q_imag)
        remainder = self - (other * quotient)
        return quotient, remainder

    def __radd__(self, other: Any) -> "GaussianInteger": return self.__add__(other)
    def __rmul__(self, other: Any) -> "GaussianInteger": return self.__mul__(other)
    def __rsub__(self, other: Any) -> "GaussianInteger":
        other_complex = self._promote(other)
        return other_complex - self
    def __rtruediv__(self, other: Any) -> Tuple["GaussianInteger", "GaussianInteger"]:
        other_complex = self._promote(other)
        return other_complex / self

    def _div_nearest(self, n: Any, d: Any) -> Any:
        q, r = n / d
        
        # [FIX] Use Protocol for magnitude comparison
        # 2 * |r| > |d|
        if 2 * r.mass > d.mass:
            ZERO = d - d
            ONE = science.U(1)
            if q >= ZERO: return q + ONE
            else: return q - ONE
        return q
    
    def __eq__(self, other: Any) -> bool:
        other = self._promote(other)
        return (self.real == other.real) and (self.imag == other.imag)

def C(r: Any, i: Any) -> GaussianInteger:
    return GaussianInteger(r, i)