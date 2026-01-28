import sys
import os
import math
from typing import Iterator, Tuple, Any

from core.science_mode import U as ScienceU

class RationalState:
    """
    Helper to perform exact rational arithmetic (a/b) using 
    abstract Matter objects (Unary or FastInteger).
    Includes automatic GCD simplification to prevent Mass Explosion.
    """
    def __init__(self, num, den, U):
        self.num = num
        self.den = den
        self.U = U # Backend Factory

    def simplify(self):
        """
        Reduces the fraction by dividing num and den by GCD.
        Essential for PhysicsMode to prevent OOM errors.
        """
        # 1. Extract Integer Values (Observation)
        # We peek at the mass to calculate the GCD.
        try:
            n_val = int(self.num)
            d_val = int(self.den)
        except Exception:
            # If cast fails, we can't simplify easily. Return as is.
            return self

        # 2. Compute GCD
        # Note: math.gcd works on integers.
        common = math.gcd(n_val, d_val)

        if common <= 1:
            return self

        # 3. Reduce (Operation)
        # We use the backend's division operator to scale down the objects.
        # Logic: val / common -> (quotient, remainder)
        # We trust remainder is 0 because 'common' is a factor.
        
        divisor = self.U(common)
        
        # Division in Base-1 returns (Quotient, Remainder)
        new_num, _ = self.num / divisor
        new_den, _ = self.den / divisor
        
        return RationalState(new_num, new_den, self.U)

    def __sub__(self, other):
        # a/b - c/d = (ad - bc) / bd
        ad = self.num * other.den
        bc = self.den * other.num
        
        # Backend handles signed subtraction (e.g. Unary -> NegativeInteger)
        new_num = ad - bc
        new_den = self.den * other.den
        
        # Simplify immediately to keep mass low
        return RationalState(new_num, new_den, self.U).simplify()

    def __mul__(self, other):
        # a/b * c/d = ac / bd
        new_num = self.num * other.num
        new_den = self.den * other.den
        
        return RationalState(new_num, new_den, self.U).simplify()

def akiyama_tanigawa_generator(backend_factory=ScienceU) -> Iterator[Tuple[Any, Any]]:
    """
    Generates the sequence of Bernoulli Numbers B_k using the Akiyama-Tanigawa algorithm.
    Yields pairs (numerator, denominator).
    
    Output Sequence:
    B_0 = 1
    B_1 = 1/2 
    B_2 = 1/6
    B_3 = 0
    B_4 = -1/30
    ...
    """
    U = backend_factory
    
    # Start with 0-th row element: 1/1
    # B_0 = 1
    root = RationalState(U(1), U(1), U)
    yield (root.num, root.den)
    
    k = 1
    while True:
        # Akiyama-Tanigawa Algorithm
        # To compute B_k, we construct the 0-th row of length k+1:
        # 1, 1/2, 1/3, ..., 1/(k+1)
        
        row = []
        for m in range(k + 1):
            # Term: 1 / (m+1)
            # We simplify just in case, though 1/(m+1) is usually irreducible
            r = RationalState(U(1), U(m + 1), U).simplify()
            row.append(r)
            
        # Reduce k times
        # Recurrence: a[j] = (j+1) * (a[j] - a[j+1])
        for depth in range(1, k + 1):
            new_row = []
            for j in range(k - depth + 1):
                # Factor (j+1)
                factor_val = U(j + 1)
                factor = RationalState(factor_val, U(1), U)
                
                # Difference
                diff = row[j] - row[j+1]
                
                # Update
                val = factor * diff
                new_row.append(val)
            row = new_row
            
        # The head of the list is B_k
        b_k = row[0]
        
        yield (b_k.num, b_k.den)
        
        k += 1