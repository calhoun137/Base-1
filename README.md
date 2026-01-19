# Base-1: A Thermodynamic Computational Universe

**"Simulating the Physics of Number Theory"**

This project is a constructivist computational laboratory. Instead of treating numbers as abstract floating-point values, this system forces the computer to treat numbers as **Physical Matter**. The integer `n` is represented by allocating memory for a string of length n(Unary).

## 🌌 Core Philosophy

1. **Constructivism:** No floating-point approximations. All numbers are constructed from integers, rationals, or algebraic processes.
2. **Unary Physics:** The fundamental unit is `|`. To represent the number 5, the machine must carry the string `|||||`.
3. **Thermodynamics of Computation:**
* **Mass ():** The total magnitude of coefficients in the system (RAM usage).
* **Entropy ():** Defined as . This measures the information density required to describe the state.
4. **Isomorphism:** We maintain two parallel backends. **Physics Mode** (Strings) proves the concept. **Science Mode** (Ints) runs the same logic efficiently.

---

## 🏗 System Architecture

### 1. The Substrate (Backends)

The system relies on "Duck Typing" to allow seamless interaction between physical matter and simulated matter.

* **`unary.py` (Physics Mode):** Implements `NonNegativeInteger` and `NegativeInteger` as string containers. Arithmetic is string concatenation ().
* **`science_mode.py` (Science Mode):** Implements `FastInteger`. Wraps Python's arbitrary-precision `int`.
* *Key Feature:* Implements **"Safe Physics"** (Magnitude checks that avoid `len()` overflows) and **"Universal Duck Typing"** (can absorb Unary strings).



### 2. The Geometry (Complex Plane)

* **`complex_mode.py`:** Implements `GaussianInteger`.
* **Crucial Logic:** Implements **Hurwitz Division** (Rounding to the Nearest Gaussian Integer). This is required for the Euclidean Algorithm to converge in the complex plane (Voronoi tiling).
* **Reflective Arithmetic:** Handles operations between Scalars and Complex numbers via `__rmul__`, etc.



### 3. The Engines

We do not compute numbers; we build machines that generate them.

* **`stream.py`:** A physical register. Wraps iterators to allow "Peeking" (Observation, 0 Mass cost) and "Consuming" (Action, Irreversible entropy increase).
* **`gosper.py` (The Reactor):** Implements the **Bihomographic Gosper Engine**.
* Maintains a state cube of 8 coefficients.
* Ingests two streams (addition, multiplication, division).
* Emits a single stream of Continued Fraction terms.
* Includes a **Thermodynamic Observer** (`state.entropy`) and a **Drain Cycle** to flush finite rational tails.


* **`transcendental.py` (The Matrix Pump):**
* Converts **Generalized Continued Fractions (GCF)** (matrix streams) into **Simple Continued Fractions (SCF)** (integer streams).
* Generates , , and handles fractional linear transformations.


* **`algorithms.py`:**
* **`Euclid`:** Rational tiling generator ().
* **`AlgebraicStream`:** Solves  (e.g., ) using the "Accordion Method" (Sign Scan  Shift  Reverse).



---

## 📁 File Structure & Key Modules

| File | Responsibility | Key Insight/Status |
| --- | --- | --- |
| **`core/unary.py`** | The Unary "Matter" implementation. | String-based integers. |
| **`core/science_mode.py`** | High-performance integer wrapper. | Implements "Safe Mass" checks to prevent `OverflowError`. |
| **`core/complex_mode.py`** | Gaussian Integer logic. | Implements `_safe_mag` and Reflection. |
| **`core/continued_fraction.py`** | High-level API wrapper. | Overloads `+`, `-`, `*`, `/` to spawn Gosper Engines. |
| **`core/gosper.py`** | The arithmetic engine. | Handles state consensus and finite stream termination. |
| **`core/transcendental.py`** | Transcendental functions. | Generates ,  via Matrix Pumping. |
constructible Euler-Mascheroni constant. |
| **`core/polynomial.py`** | Polynomial manipulation. | Implements Horner's Method for efficient Taylor Shifting. |

---

## 🚀 Usage Examples

**1. Basic Arithmetic (Gosper Engine)**

```python
from continued_fraction import ContinuedFraction
from algorithms import Euclid
from stream import Stream
import science_mode as N

# Create 1/2
s1 = Stream(Euclid(N.U(1), N.U(2)))
cf1 = ContinuedFraction(s1)

# Create 1/3
s2 = Stream(Euclid(N.U(1), N.U(3)))
cf2 = ContinuedFraction(s2)

# Compute 1/2 + 1/3 = 5/6 -> [0; 1, 5]
result = cf1 + cf2 

```

**2. Transcendental Generation ()**

```python
from transcendental import ln_generator, gcf_to_scf
from stream import Stream

# Generate GCF for ln(1+1)
gcf = ln_generator(1)
# Pump to SCF
scf = gcf_to_scf(gcf)
# Stream: [0, 1, 2, 3, 1...]

```

---

## ⚠️ "Safe Physics" Warning

When using `ScienceMode`, the integers can grow larger than the addressable memory space.

* **Never use `len(obj)**` in logic checks. It will raise `OverflowError`.
* **Use `_safe_mag(obj)**` or check `if int(obj) == 0`.