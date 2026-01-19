```markdown
# Base-1 Test Style Guide: The "Visual Parametrization" Pattern
**Filename:** `AI_TEST_STYLE_GUIDE.md`
**Context:** Python / Pytest / Constructivist Mathematics

## 1. The Core Philosophy
Tests in the Base-1 Universe are not just code checks; they are **Scientific Experiments**.
We do not test if "functions return values." We test if "Mathematical Truths" hold up across different "Physical Universes" (Backends).

* **Separation of Truth & Matter:** The mathematical facts (e.g., $1/2 + 1/3 = 5/6$) are immutable. The substrate (Unary vs. Science Mode) changes.
* **The "Lab Report":** Tests must print visible, human-readable logs (`[LAB] ...`) so the user can verify the *behavior* of the engine, not just the boolean pass/fail.
* **Universal Compliance:** Every algebraic test must run in both `Physics Mode` (Unary Strings) and `Science Mode` (Integers).

---

## 2. The Structural Pattern

### A. The Setup (Factories)
Do not hardcode backend instantiation inside the test loop. Use a helper factory to "Materialize" numbers.

```python
# [HELPER] Factory to switch universes
def make_cf(value, mode):
    if mode == "physics": ...
    elif mode == "science": ...
    # Materialize Number -> Create Process -> Return Object

```

### B. The Math (Data-Driven)

Define the mathematical truths *outside* the test function. Use a list of tuples with clear comments explaining the math.

```python
# --- Define The Math (Universal Truths) ---
identity_cases = [
    # (Op, Input, Parameter, Expected_Result)
    ("add", (1, 2), 0, [0, 2]),      # 1/2 + 0 = 1/2
    ("mul", (2, 3), 1, [0, 1, 2]),   # 2/3 * 1 = 2/3
]
case_ids = ["x+0=x", "x*1=x"]

```

### C. The Experiment (Test Function)

The test function acts as the "Observer." It parametrizes the **Universe** (`mode`) against the **Math** (`cases`).

```python
@pytest.mark.parametrize("mode", ["physics", "science"])
@pytest.mark.parametrize("op, val, param, expected", identity_cases, ids=case_ids)
def test_algebraic_laws(self, mode, op, val, param, expected):
    
    # 1. Logging (The "Lab Report")
    print(f"\n[LAB] Testing {op} in {mode.upper()}...")
    
    # 2. Setup
    obj = make_cf(val, mode)
    
    # 3. Execution
    result = obj + param
    
    # 4. Observation (Stream Consumption)
    # ALWAYS obey the Iterator Protocol: iter(obj) -> next(it)
    seq = []
    iterator = iter(result)
    for _ in range(len(expected) + 2): # Buffer for safety
        try:
            term = next(iterator)
            seq.append(int(term))
        except StopIteration:
            break
            
    # 5. Verification
    print(f"       Got: {seq}")
    assert seq == expected

```

---

## 3. Critical Rules

### Rule 1: Respect the Protocol

* **Never** use `len()` to check for zero/vacuum. Use the `.is_vacuum` property.
* **Never** assume mass is `len()`. Use the `.mass` property.
* **Always** explicitly call `iter()` on a `ContinuedFraction` before looping or calling `next()`.

### Rule 2: Thermodynamic Safety

* Infinite loops are possible in stream processing. Always wrap consumption loops in a `range(limit)` safety brake.
* Allow for "Buffer" steps. The engine often needs 1-2 extra cycles to realize it is empty and close the stream.

### Rule 3: Mathematical Tolerance

* Be aware of **Uncompressed Unity**.
*  is the canonical form of 1.
*  is the "Historical" form of 1 ().
* Tests should accept  as valid where appropriate, representing the path the engine took.

### Rule 4: Visual Feedback

* Use `pytest -s` compatible print statements.
* Prefix logs with `[LAB]` or `[OBSERVER]` to make them distinct from system errors.
* Print the "Expected" vs "Got" values *before* the assertion fails, to aid in debugging without reading the stack trace.
