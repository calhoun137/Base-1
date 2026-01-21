import math
from typing import List, Tuple, Any
from polynomial import Polynomial
import science_mode as science
from science_mode import U

class CollatzLab:
    """
    The Experimental Apparatus.
    Treats Collatz trajectories as fluid dynamics of coefficients.
    """
    
    @staticmethod
    def inject(n: int) -> Polynomial:
        """
        Converts an integer N into a Binary Polynomial P(x).
        Example: 6 (110) -> 0*x^0 + 1*x^1 + 1*x^2
        """
        if n == 0: return Polynomial([U(0)])
        
        coeffs = []
        temp_n = n
        while temp_n > 0:
            bit = temp_n % 2
            coeffs.append(U(bit))
            temp_n //= 2
            
        return Polynomial(coeffs)

    @staticmethod
    def measure_entropy(poly: Polynomial) -> float:
        """
        Calculates the Shannon Entropy of the coefficient distribution.
        Measures the 'Disorder' of the matter spread.
        """
        # 1. Extract Mass from Science Mode objects
        masses = []
        total_mass = 0
        for c in poly.coeffs:
            m = c.mass if hasattr(c, 'mass') else int(c)
            if m > 0:
                masses.append(m)
                total_mass += m
                
        if total_mass == 0: return 0.0

        # 2. Calculate H = -sum(p * log2(p))
        entropy = 0.0
        for m in masses:
            p = m / total_mass
            entropy -= p * math.log2(p)
            
        return entropy

    @staticmethod
    def normalize_and_measure(poly: Polynomial) -> Tuple[Polynomial, int]:
        """
        The Avalanche Engine.
        Resolves 'Overloaded' coefficients (>= 2) by propagating carries.
        Returns:
            1. The Relaxed Polynomial (Binary coefficients)
            2. The Avalanche Energy (Total carries generated)
        """
        # Extract raw integers for mutable processing
        raw_coeffs = [c.mass if hasattr(c, 'mass') else int(c) for c in poly.coeffs]
        
        avalanche_energy = 0
        i = 0
        
        # The Ripple Effect (LSB -> MSB)
        while i < len(raw_coeffs):
            current_val = raw_coeffs[i]
            
            if current_val >= 2:
                carry = current_val // 2
                remainder = current_val % 2
                
                # Update current site
                raw_coeffs[i] = remainder
                
                # Propagate Energy
                avalanche_energy += carry
                
                # Check next site
                if i + 1 >= len(raw_coeffs):
                    raw_coeffs.append(0)
                
                raw_coeffs[i+1] += carry
                
                # Note: We do NOT reset 'i'. 
                # The carry moves to i+1, which will be processed in the next iteration.
                
            i += 1
            
        # Re-materialize into Science Mode Matter
        new_coeffs = [U(c) for c in raw_coeffs]
        return Polynomial(new_coeffs), avalanche_energy

    @staticmethod
    def run_experiment(start_n: int, max_steps: int = 1000):
        """
        Runs the simulation and logs 'Thermodynamic' metrics.
        """
        current_poly = CollatzLab.inject(start_n)
        
        print(f"=== COLLATZ LAB REPORT: N={start_n} ===")
        print(f"{'Step':<6} | {'Val':<15} | {'Entropy':<8} | {'Avalanche':<10} | {'Poly State (Low->High)'}")
        print("-" * 80)

        step = 0
        while step < max_steps:
            # 1. Measure Pre-Flux State
            entropy = CollatzLab.measure_entropy(current_poly)
            val = current_poly.evaluate(U(2)).mass
            
            # 2. Normalize (The Avalanche) to check Parity
            # Note: We normalize *before* deciding the move to ensure LSB is valid.
            relaxed_poly, energy = CollatzLab.normalize_and_measure(current_poly)
            
            # Print Stat Line
            # Truncate poly string for display
            poly_str = str(relaxed_poly)
            if len(poly_str) > 30: poly_str = poly_str[:27] + "..."
            
            print(f"{step:<6} | {val:<15} | {entropy:.4f}   | {energy:<10} | {poly_str}")
            
            # Check for Stopping Condition (Vacuum or Unit)
            if val <= 1:
                print(">>> CONVERGENCE ACHIEVED <<<")
                break
                
            # 3. Apply Dynamics (Map)
            # Check LSB of the RELAXED polynomial
            lsb = relaxed_poly.coeffs[0].mass
            
            if lsb % 2 == 0:
                # Even: Descent (Shift Right / Divide by x)
                # In polynomial terms: P_next = P / x
                # Since we are normalized, dividing by x is just dropping c_0
                next_coeffs = relaxed_poly.coeffs[1:]
                if not next_coeffs: next_coeffs = [U(0)]
                current_poly = Polynomial(next_coeffs)
            else:
                # Odd: Ascent (3n + 1)
                # P_next = (x + 1) * P + 1
                # We perform this on the RELAXED polynomial to start the cycle fresh
                
                # (x + 1)
                x_plus_1 = Polynomial([U(1), U(1)]) 
                
                # (x + 1) * P
                product = relaxed_poly * x_plus_1
                
                # + 1
                current_poly = product + Polynomial([U(1)])
                
            step += 1

if __name__ == "__main__":
    # Test Case 1: The Classic 27 (Grows to 9232 before falling)
    CollatzLab.run_experiment(27, max_steps=120)
    
    print("\n" + "="*40 + "\n")
    
    # Test Case 2: 19 (Rapid fluctuations)
    CollatzLab.run_experiment(19, max_steps=25)