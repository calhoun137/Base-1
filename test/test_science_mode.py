import unary as physics
import science_mode as science

def run_comparison(test_name, operation_lambda, expected_val_int, expected_len):
    """
    Executes an operation on both backends and verifies they match the expected physics.
    """
    print(f"\n--- {test_name} ---")
    
    # 1. Physics Mode (The Truth)
    p_res = operation_lambda(physics)
    print(f"Physics: {p_res} (Type: {type(p_res).__name__})")
    
    # 2. Science Mode (The Optimization)
    s_res = operation_lambda(science)
    print(f"Science: {s_res} (Type: {type(s_res).__name__})")
    
    # 3. Verification
    # Check Integer Value
    if int(s_res) != expected_val_int:
        print(f"FAIL: Value mismatch. Science={int(s_res)}, Expected={expected_val_int}")
        return False
        
    # Check 'Mass' (Length) - Critical for cost simulation
    if len(s_res) != expected_len:
        print(f"FAIL: Mass mismatch. Science Len={len(s_res)}, Expected={expected_len}")
        return False

    # Check Parity with Physics
    if int(p_res) != int(s_res):
        print(f"FAIL: Backend Divergence! Physics={int(p_res)} vs Science={int(s_res)}")
        return False

    print("STATUS: PASS")
    return True

def verify_division_logic():
    """
    The critical test for Truncated vs Floor division.
    """
    print("\n--- Critical Test: Negative Division (S(7) / U(2)) ---")
    
    # Physics Mode
    p_div = physics.S(7)
    p_divisor = physics.U(2)
    p_q, p_r = p_div / p_divisor
    
    # Science Mode
    s_div = science.S(7)
    s_divisor = science.U(2)
    s_q, s_r = s_div / s_divisor
    
    print(f"Physics Result: Q={p_q}, R={p_r}")
    print(f"Science Result: Q={s_q}, R={s_r}")
    
    # Verification Logic
    # Expected: -3, Remainder -1 (Truncated)
    # Python Native would give: -4, Remainder 1 (Floor)
    
    if int(s_q) == -3 and int(s_r) == -1:
        print("STATUS: PASS (Science Mode correctly implements Truncated Division)")
    else:
        print("STATUS: FAIL (Science Mode drifted to Python Native behavior)")

def test_run_suite():
    print("=== Backend Isomorphism Verification ===")
    
    # Test 1: Addition (Annihilation)
    # 5 + (-3) = 2
    run_comparison(
        "Addition (5 + -3)",
        lambda lib: lib.U(5) + lib.S(3),
        expected_val_int=2,
        expected_len=2
    )

    # Test 2: Multiplication (Scaling)
    # -3 * 5 = -15
    run_comparison(
        "Multiplication (-3 * 5)",
        lambda lib: lib.S(3) * lib.U(5),
        expected_val_int=-15,
        expected_len=15
    )
    
    # Test 3: Division
    verify_division_logic()
