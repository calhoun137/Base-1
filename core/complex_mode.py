from typing import Any, Tuple, Union
from . import science_mode as science
from .science_mode import U, S, FastInteger

class GaussianInteger:
    """
    Represents a complex number a + bi in the Gaussian Lattice Z[i].
    Implements Matter Protocol.
    """
    __slots__ = ('real', 'imag')

    def __init__(self, real: Any, imag: Any):
        self.real = self._ensure_physical(real)
        self.imag = self._ensure_physical(imag)

    def _ensure_physical(self, val: Any):
        if isinstance(val, int):
            return U(val) if val >= 0 else S(abs(val))
        return val

    # [PROTOCOL] Mass is sum of component masses (Manhattan Magnitude)
    @property
    def mass(self) -> int:
        return self.real.mass + self.imag.mass

    @property
    def is_vacuum(self) -> bool:
        return self.mass == 0

    # Euclidean Norm Squared (N(z) = a^2 + b^2)
    # Critical for Hurwitz Division
    def norm_sq(self) -> "FastInteger":
        return (self.real * self.real) + (self.imag * self.imag)

    def __repr__(self) -> str: return f"({self.real}+{self.imag}i)"
    def __str__(self) -> str: return f"{self.real}+{self.imag}i"

    # --- Type Promotion ---
    def _promote(self, other: Any) -> "GaussianInteger":
        if isinstance(other, GaussianInteger): return other
        # If other is int or FastInteger, promote to Complex
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
        denom_norm = other.norm_sq()
        
        if denom_norm.is_vacuum:
            raise ZeroDivisionError("Complex Division by Zero")

        # Multiply by conjugate to clear denominator
        # (a+bi)/(c+di) = (a+bi)(c-di) / (c^2+d^2)
        ZERO = self.real - self.real 
        other_conj_imag = ZERO - other.imag
        
        num_r = (self.real * other.real) - (self.imag * other_conj_imag)
        num_i = (self.real * other_conj_imag) + (self.imag * other.real)

        # Divide Real and Imag parts separately using Nearest Integer logic
        q_real = self._div_nearest(num_r, denom_norm)
        q_imag = self._div_nearest(num_i, denom_norm)
        
        quotient = GaussianInteger(q_real, q_imag)
        remainder = self - (other * quotient)
        return quotient, remainder

    def _div_nearest(self, n: Any, d: Any) -> Any:
        """
        Rounds n/d to the nearest integer.
        Tie-breaking logic is determined by the underlying integer division.
        """
        # 1. Standard Truncated Division
        q, r = n / d
        
        # 2. Check Rounding Condition: |r| > |d|/2
        # We use strict Euclidean Norm logic here to ensure minimal remainder.
        # Since these are scalars, Norm = Square.
        
        # Optimization: We can check 2*|r| > |d| directly on magnitudes
        # But for 'science_mode' objects, we must be careful.
        
        # Let's map to Python ints for the logic check to avoid infinite recursion
        # or expensive object creation, then apply result to the objects.
        r_mag = r.mass # absolute value for scalars
        d_mag = d.mass
        
        if 2 * r_mag > d_mag:
            # We need to round away from zero
            # If q is positive, q+1. If q is negative, q-1.
            ZERO = d - d
            ONE = science.U(1)
            
            # Check sign of quotient
            if q >= ZERO: return q + ONE
            else: return q - ONE
            
        return q
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GaussianInteger):
            # Attempt promotion for comparison
            if isinstance(other, (int, FastInteger)):
                return self.imag.is_vacuum and self.real == other
            return False
        return (self.real == other.real) and (self.imag == other.imag)
    
    def __hash__(self):
        return hash((self.real, self.imag))

    # Right-side operations
    def __radd__(self, other: Any) -> "GaussianInteger": return self.__add__(other)
    def __rmul__(self, other: Any) -> "GaussianInteger": return self.__mul__(other)
    def __rsub__(self, other: Any) -> "GaussianInteger":
        other = self._promote(other)
        return other - self
    def __rtruediv__(self, other: Any) -> Tuple["GaussianInteger", "GaussianInteger"]:
        other = self._promote(other)
        return other / self

def C(r: Any, i: Any) -> GaussianInteger:
    return GaussianInteger(r, i)