from typing import Any, List, Iterator
from polynomial import Polynomial
import unary
import science_mode

class GaloisField:
    """
    A Factory, Physics Engine, and Territory Map for Finite Fields F_p^n.
    """
    def __init__(self, p: Any, n: int, mod_poly_coeffs: List[Any]):
        self.p = p
        self.n = n
        self.mod_poly = Polynomial(mod_poly_coeffs)
        
        # Calculate Total Order (q = p^n) for Fermat's Little Theorem
        # We need the scalar mass of p
        if hasattr(p, 'mass'): self.p_mass = p.mass
        elif hasattr(p, '__len__'): self.p_mass = len(p)
        else: self.p_mass = int(p)
            
        self.order = self.p_mass ** n

    def _get_unit_matter(self):
        if hasattr(self.p, '_val'): return science_mode.U(1)
        return unary.U(1)

    def _get_zero_matter(self):
        if hasattr(self.p, '_val'): return science_mode.U(0)
        return unary.U(0)

    def zero(self):
        """Returns the additive identity (Vacuum)."""
        return self.Element([self._get_zero_matter()])

    def one(self):
        """Returns the multiplicative identity."""
        return self.Element([self._get_unit_matter()])

    def __call__(self, coeffs: List[Any]):
        """Factory: Create element from coefficients."""
        return self.Element(coeffs)

    def __repr__(self):
        """The Title of the Map."""
        return f"<GaloisField: F_{self.p_mass}^{self.n} | Mod: {self.mod_poly}>"

    def __iter__(self) -> Iterator["GaloisElement"]:
        """
        Cartography: Iterates through ALL elements of the field.
        Order: Lexicographical (Counter).
        """
        for i in range(self.order):
            coeffs = []
            val = i
            for _ in range(self.n):
                digit = val % self.p_mass
                if hasattr(self.p, '_val'): mat = science_mode.U(digit)
                else: mat = unary.U(digit)
                coeffs.append(mat)
                val //= self.p_mass
            yield self.Element(coeffs)

    def atlas(self) -> str:
        """
        Generates the Reference Book (Cayley Tables) for the Field.
        Safe for printing.
        """
        elements = list(self)
        
        # 1. Determine Column Width (Padding)
        # We find the longest string representation in the field
        labels = [str(e) for e in elements]
        max_len = max(len(s) for s in labels)
        width = max(max_len, 3) + 2  # Minimum 3 chars, plus padding
        
        fmt = f"{{:>{width}}}" # Right-aligned format string
        
        out = []
        out.append(f"=== FIELD ATLAS: F_{self.p_mass}^{self.n} ===")
        out.append(f"Modulus: {self.mod_poly}")
        out.append("")

        def build_table(title, op_symbol, op_func):
            out.append(f"[{title}]")
            
            # Header Row
            header = f"{op_symbol:>{width}} |" + "".join([fmt.format(l) + " |" for l in labels])
            out.append(header)
            
            # Separator
            sep = "-" * len(header)
            out.append(sep)
            
            # Data Rows
            for i, row_elem in enumerate(elements):
                row_str = f"{labels[i]:>{width}} |"
                for col_elem in elements:
                    try:
                        res = op_func(row_elem, col_elem)
                        res_str = str(res)
                    except ZeroDivisionError:
                        res_str = "ERR"
                    row_str += fmt.format(res_str) + " |"
                out.append(row_str)
            out.append("")

        # Addition Table
        build_table("ADDITION TABLE", "(+)", lambda a, b: a + b)

        # Multiplication Table
        build_table("MULTIPLICATION TABLE", "(*)", lambda a, b: a * b)
        
        return "\n".join(out)

    @property
    def Element(self):
        field_context = self

        class GaloisElement(Polynomial):
            def __repr__(self):
                return f"GF<{super().__repr__()}>"

            def _enforce_physics(self, poly: Polynomial) -> "GaloisElement":
                """Physics Engine: Mod p and Mod P(x) with Normalization."""
                
                # 1. Modulo p + Normalization
                reduced_coeffs = []
                for c in poly.coeffs:
                    reduced_c = c % field_context.p
                    
                    # Normalize Anti-Matter to Positive Matter
                    is_negative = False
                    if hasattr(reduced_c, '_val'): 
                        if reduced_c._val < 0: is_negative = True
                    elif isinstance(reduced_c, unary.NegativeInteger): 
                        is_negative = True
                    
                    # [FIX] Do NOT lift Vacuum (0), even if it's S(0)
                    if is_negative and not reduced_c.is_vacuum:
                        reduced_c = reduced_c + field_context.p
                    reduced_coeffs.append(reduced_c)

                temp_poly = Polynomial(reduced_coeffs)

                # 2. Modulo P(x)
                if len(temp_poly) > field_context.n:
                    _, remainder = temp_poly / field_context.mod_poly
                    
                    final_coeffs = []
                    for c in remainder.coeffs:
                        r_c = c % field_context.p
                        
                        is_negative = False
                        if hasattr(r_c, '_val'): 
                            if r_c._val < 0: is_negative = True
                        elif isinstance(r_c, unary.NegativeInteger): 
                            is_negative = True
                        
                        # [FIX] Do NOT lift Vacuum (0)
                        if is_negative and not r_c.is_vacuum:
                            r_c = r_c + field_context.p
                        final_coeffs.append(r_c)
                    
                    return GaloisElement(final_coeffs)
                
                return GaloisElement(temp_poly.coeffs)

            # --- The Frobenius Stream ---
            def __iter__(self):
                """
                Returns an iterator that traverses the Frobenius Orbit.
                Yields: self, self^p, self^p^2, ...
                """
                current = self
                while True:
                    yield current
                    current = current ** field_context.p_mass

            # --- Field Arithmetic ---

            def trace(self) -> "GaloisElement":
                """
                The Spectral Projector.
                Sums the entire Frobenius Orbit of the element.
                result = self + self^p + self^p^2 + ...
                """
                # Start with Vacuum (0)
                orbit_sum = field_context.zero()
                
                # Consume the stream of the element's orbit
                # strictly for 'n' steps (the degree of the field)
                iterator = iter(self)
                for _ in range(field_context.n):
                    conjugate = next(iterator)
                    orbit_sum = orbit_sum + conjugate
                    
                return orbit_sum
            
            def inverse(self):
                """Multiplicative Inverse via Fermat's Little Theorem."""
                if self.is_vacuum:
                    raise ZeroDivisionError("Cannot invert Vacuum (Zero).")
                # Exponent = Order - 2
                exp = field_context.order - 2
                return self ** exp

            def __truediv__(self, other: Any) -> "GaloisElement":
                """Field Division (Exact)."""
                if not isinstance(other, GaloisElement):
                    return NotImplemented
                inv = other.inverse()
                return self * inv

            # Standard ops wrap the physics engine
            def __add__(self, other: Any) -> "GaloisElement":
                res = super().__add__(other); return self._enforce_physics(res) if res is not NotImplemented else NotImplemented
            def __mul__(self, other: Any) -> "GaloisElement":
                res = super().__mul__(other); return self._enforce_physics(res) if res is not NotImplemented else NotImplemented
            def __sub__(self, other: Any) -> "GaloisElement":
                res = super().__sub__(other); return self._enforce_physics(res) if res is not NotImplemented else NotImplemented
            
            def __pow__(self, exponent: int) -> "GaloisElement":
                if exponent == 0: return field_context.one()
                if exponent == 1: return self
                base = self
                result = field_context.one()
                while exponent > 0:
                    if exponent % 2 == 1:
                        result = result * base
                    base = base * base
                    exponent //= 2
                return result

        return GaloisElement