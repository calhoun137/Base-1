from typing import List, Any
from dataclasses import dataclass
from .unary import Algebraic

@dataclass
class Polynomial(Algebraic):
    """
    Represents a polynomial P(x).
    Implements Matter Protocol.
    """
    coeffs: List[Any] 

    def __post_init__(self):
        while len(self.coeffs) > 1:
            last = self.coeffs[-1]
            # [FIX] Use Protocol for Vacuum check
            if hasattr(last, 'is_vacuum') and last.is_vacuum:
                self.coeffs.pop()
            else:
                break

    # [PROTOCOL]
    @property
    def mass(self) -> int:
        return sum(c.mass for c in self.coeffs)

    @property
    def is_vacuum(self) -> bool:
        return self.mass == 0

    def __len__(self) -> int: return len(self.coeffs)

    def __repr__(self) -> str:
        if not self.coeffs: return "0"
        terms = []
        first_term = True
        for i in range(len(self.coeffs) - 1, -1, -1):
            c = self.coeffs[i]
            # Use Protocol check
            if hasattr(c, 'is_vacuum') and c.is_vacuum: continue
            
            try:
                val = int(c)
                is_scalar = True
                is_negative = (val < 0)
                mag = abs(val)
            except (TypeError, ValueError):
                is_scalar = False
                val = c
                is_negative = False
                mag = c

            if is_scalar:
                str_mag = "" if (mag == 1 and i > 0) else str(mag)
            else:
                str_mag = str(mag)

            if i == 0: str_var = ""
            elif i == 1: str_var = "x"
            else: str_var = f"x^{i}"

            if first_term:
                term = f"-{str_mag}{str_var}" if (is_scalar and is_negative) else f"{str_mag}{str_var}"
            else:
                if is_scalar:
                    term = f" - {str_mag}{str_var}" if is_negative else f" + {str_mag}{str_var}"
                else:
                    term = f" + {str_mag}{str_var}"
            terms.append(term)
            first_term = False
        return "".join(terms) if terms else "0"

    def evaluate(self, x: Any) -> Any:
        result = self.coeffs[-1]
        for i in range(len(self.coeffs) - 2, -1, -1):
            result = result * x + self.coeffs[i]
        return result

    def __add__(self, other: Any) -> "Polynomial":
        if not isinstance(other, Polynomial): return NotImplemented
        len_self = len(self.coeffs)
        len_other = len(other.coeffs)
        max_len = max(len_self, len_other)
        
        sample = self.coeffs[0]
        if hasattr(sample, '_val'): from .science_mode import U
        else: from .unary import U
        ZERO = U(0)

        new_coeffs = []
        for i in range(max_len):
            c1 = self.coeffs[i] if i < len_self else ZERO
            c2 = other.coeffs[i] if i < len_other else ZERO
            new_coeffs.append(c1 + c2)
        return Polynomial(new_coeffs)

    def __mul__(self, other: Any) -> "Polynomial":
        if not isinstance(other, Polynomial):
            return NotImplemented

        # --- [HARDENED KERNEL START] ---
        # 1. The Vacuum Check
        # In a Constructivist Universe, "Nothing times Something is Nothing."
        # If either polynomial has no coefficients (True Vacuum), 
        # the result is immediately the Vacuum.
        if not self.coeffs or not other.coeffs:
            return self.__class__([])
        # --- [HARDENED KERNEL END] ---

        # 2. Standard Arithmetic (Safe to proceed)
        n = len(self.coeffs)
        m = len(other.coeffs)

        # This line previously crashed because self.coeffs was empty.
        # Now, we are guaranteed at least one element exists.
        sample = self.coeffs[0]

        # Determine the Universe (Physics vs Science) for the zero element
        # (This logic infers the type of zero to use for the accumulator)
        if hasattr(sample, '_val'):
            # Science Mode (Integers)
            from . import science_mode
            zero_val = science_mode.U(0)
        else:
            # Physics Mode (Unary)
            from . import unary
            zero_val = unary.U(0)

        # Convolve
        result = [zero_val for _ in range(n + m - 1)]
        for i in range(n):
            for j in range(m):
                # result[i+j] += self[i] * other[j]
                term = self.coeffs[i] * other.coeffs[j]
                result[i + j] = result[i + j] + term

        return self.__class__(result)
    def __truediv__(self, other: Any) -> tuple["Polynomial", "Polynomial"]:
        if not isinstance(other, Polynomial): return NotImplemented
        sample = self.coeffs[0]
        if hasattr(sample, '_val'): from .science_mode import U
        else: from .unary import U
        ZERO = U(0)

        dividend_coeffs = list(self.coeffs)
        divisor_coeffs = other.coeffs
        
        # Use Protocol for zero check on divisor
        if len(divisor_coeffs) == 0 or divisor_coeffs[-1].is_vacuum:
             raise ZeroDivisionError("Polynomial Division by Zero")

        quotient_coeffs = [ZERO] * len(dividend_coeffs)
        deg_divisor = len(divisor_coeffs) - 1
        lead_divisor = divisor_coeffs[-1]

        while len(dividend_coeffs) >= len(divisor_coeffs):
            deg_rem = len(dividend_coeffs) - 1
            lead_rem = dividend_coeffs[-1]
            factor, _ = lead_rem / lead_divisor
            
            if factor.is_vacuum: break

            deg_diff = deg_rem - deg_divisor
            quotient_coeffs[deg_diff] = quotient_coeffs[deg_diff] + factor
            
            for i in range(len(divisor_coeffs)):
                target_idx = i + deg_diff
                to_subtract = divisor_coeffs[i] * factor
                dividend_coeffs[target_idx] = dividend_coeffs[target_idx] - to_subtract
            
            while len(dividend_coeffs) > 0:
                if dividend_coeffs[-1].is_vacuum: dividend_coeffs.pop()
                else: break
        
        if not dividend_coeffs: dividend_coeffs = [ZERO]
        return Polynomial(quotient_coeffs), Polynomial(dividend_coeffs)

    def shift(self, c: Any) -> "Polynomial":
        new_coeffs = list(self.coeffs)
        n = len(new_coeffs) - 1
        for i in range(n):
            for j in range(n - 1, i - 1, -1):
                term = new_coeffs[j+1] * c
                new_coeffs[j] = new_coeffs[j] + term
        return Polynomial(new_coeffs)

    def reverse(self) -> "Polynomial":
        return Polynomial(list(reversed(self.coeffs)))