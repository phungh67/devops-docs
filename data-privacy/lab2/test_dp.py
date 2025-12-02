"""
Test suite for the unified DP_DSL class

This module tests the object-oriented DP_DSL class that encapsulates
budget management, transformations, and measurements in a single interface.
"""

import sys
sys.path.append('.')

from dp import DP_DSL, Dataset, create_dataset, InsufficientBudget, InvalidParameter
import math
import numpy as np


def test_dsl_basic_functionality():
    """Test basic DP_DSL functionality"""
    print("Testing DP_DSL basic functionality...")

    # Create test dataset and DSL instance
    data = create_dataset([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], stability=1)
    dsl = DP_DSL(budget=3.0)

    # Test initial state
    assert dsl.get_remaining_budget() == 3.0
    assert dsl.get_used_budget() == 0.0

    # Apply transformations (budget-free)
    filtered = dsl.filter(lambda x: x > 5, data)
    assert len(filtered) == 5
    assert dsl.get_used_budget() == 0.0  # No budget consumed

    # Apply measurements (budget-consuming)
    count_result = dsl.count(filtered, epsilon=1.0)
    assert abs(count_result.dp_value - 5.0) < 5.0  # Allow for noise
    assert dsl.get_used_budget() == 1.0

    # Apply more transformations and measurements
    doubled = dsl.map(lambda x: x * 2.0, filtered)
    sum_result = dsl.sum(doubled, epsilon=1.5, lower_bound=0.0, upper_bound=20.0)
    assert dsl.get_used_budget() == 2.5

    print("  ✓ Basic functionality test passed!")


def test_dsl_budget_management():
    """Test DP_DSL budget management"""
    print("Testing DP_DSL budget management...")

    data = create_dataset([1, 2, 3], stability=1)
    dsl = DP_DSL(budget=2.0)

    # Test normal budget consumption
    result1 = dsl.count(data, epsilon=0.5)
    assert dsl.get_used_budget() == 0.5
    assert result1.epsilon_spent == 0.5

    # Test budget status
    status = dsl.budget_status()
    assert status['total_budget'] == 2.0
    assert status['used_budget'] == 0.5
    assert status['remaining_budget'] == 1.5
    assert status['usage_percentage'] == 25.0

    # Test remaining budget consumption
    result2 = dsl.count(data, epsilon=1.0)
    assert dsl.get_used_budget() == 1.5

    # Test budget violation
    try:
        dsl.count(data, epsilon=1.0)  # Would exceed budget
        assert False, "Should have failed with insufficient budget"
    except InsufficientBudget as e:
        assert e.requested == 1.0
        assert e.available == 0.5

    print("  ✓ Budget management test passed!")


def test_dsl_transformations():
    """Test DP_DSL transformations and stability tracking"""
    print("Testing DP_DSL transformations...")

    data1 = create_dataset([1, 2, 3], stability=1)
    data2 = create_dataset([4, 5, 6], stability=2)
    dsl = DP_DSL(budget=5.0)

    # Test filter (preserves stability)
    filtered = dsl.filter(lambda x: x > 2, data1)
    assert filtered.stability == 1
    assert list(filtered) == [3]  # Test via iteration

    # Test map (preserves stability)
    mapped = dsl.map(lambda x: x * 2, data1)
    assert mapped.stability == 1
    assert list(mapped) == [2, 4, 6]  # Test via iteration

    # Test union (adds stabilities)
    union_data = dsl.union(data1, data2)
    assert union_data.stability == 3
    assert list(union_data) == [1, 2, 3, 4, 5, 6]  # Test via iteration

    # Test intersect (adds stabilities)
    intersect_data = dsl.intersect(data1, union_data)
    assert intersect_data.stability == 4  # 1 + 3

    # Test group_by (doubles stability)
    grouped = dsl.group_by(lambda x: x % 2, data1)
    assert grouped.stability == 2
    assert len(grouped) == 2  # Even and odd groups

    print("  ✓ Transformations test passed!")


def test_dsl_stability_noise_scaling():
    """Test that higher stability produces proportionally more noise"""
    print("Testing DP_DSL stability noise scaling...")

    epsilon = 1.0
    trials = 20

    # Test with stability 1
    dsl1 = DP_DSL(budget=trials * epsilon)
    data1 = create_dataset([1] * 50, stability=1)

    errors1 = []
    for _ in range(trials):
        result = dsl1.count(data1, epsilon)
        error = abs(result.dp_value - 50)
        errors1.append(error)

    avg_error1 = sum(errors1) / len(errors1)

    # Test with stability 2 (should have ~2x more noise)
    dsl2 = DP_DSL(budget=trials * epsilon)
    data2 = create_dataset([1] * 50, stability=2)

    errors2 = []
    for _ in range(trials):
        result = dsl2.count(data2, epsilon)
        error = abs(result.dp_value - 50)
        errors2.append(error)

    avg_error2 = sum(errors2) / len(errors2)

    print(f"  Stability 1 avg error: {avg_error1:.2f}")
    print(f"  Stability 2 avg error: {avg_error2:.2f}")
    print(f"  Error ratio: {avg_error2 / avg_error1:.2f}")

    # Higher stability should produce more noise (allow some tolerance)
    assert avg_error2 > avg_error1 * 0.8, "Higher stability should produce more noise"

    print("  ✓ Stability noise scaling test passed!")


def test_dsl_epsilon_comparison():
    """Test that smaller epsilon values produce more noise"""
    print("Testing DP_DSL epsilon comparison...")

    data = create_dataset([10, 20, 30, 40, 50], stability=1)
    true_count = 5
    trials = 30

    # Test low epsilon (high privacy, more noise)
    epsilon_low = 0.5
    dsl_low = DP_DSL(budget=trials * epsilon_low)

    low_errors = []
    for _ in range(trials):
        result = dsl_low.count(data, epsilon_low)
        error = abs(result.dp_value - true_count)
        low_errors.append(error)

    avg_low_error = sum(low_errors) / len(low_errors)

    # Test high epsilon (low privacy, less noise)
    epsilon_high = 2.0
    dsl_high = DP_DSL(budget=trials * epsilon_high)

    high_errors = []
    for _ in range(trials):
        result = dsl_high.count(data, epsilon_high)
        error = abs(result.dp_value - true_count)
        high_errors.append(error)

    avg_high_error = sum(high_errors) / len(high_errors)

    print(f"  Low ε={epsilon_low} avg error: {avg_low_error:.2f}")
    print(f"  High ε={epsilon_high} avg error: {avg_high_error:.2f}")

    # Lower epsilon should produce higher average error (more noise)
    assert avg_low_error > avg_high_error, \
        f"Expected low ε to have more error, but got low={avg_low_error:.2f}, high={avg_high_error:.2f}"

    print("  ✓ Epsilon comparison test passed!")


def test_dsl_error_handling():
    """Test DP_DSL error handling"""
    print("Testing DP_DSL error handling...")

    # Test invalid budget
    try:
        DP_DSL(budget=0.0)
        assert False, "Should have failed with zero budget"
    except InvalidParameter:
        pass

    try:
        DP_DSL(budget=-1.0)
        assert False, "Should have failed with negative budget"
    except InvalidParameter:
        pass

    # Test invalid epsilon
    dsl = DP_DSL(budget=2.0)
    data = create_dataset([1, 2, 3], stability=1)

    try:
        dsl.count(data, epsilon=-1.0)
        assert False, "Should have failed with negative epsilon"
    except InvalidParameter:
        pass

    try:
        dsl.count(data, epsilon=0.0)
        assert False, "Should have failed with zero epsilon"
    except InvalidParameter:
        pass

    print("  ✓ Error handling test passed!")


def test_dsl_budget_utilities():
    """Test DP_DSL budget utility methods"""
    print("Testing DP_DSL budget utilities...")

    dsl = DP_DSL(budget=5.0)
    data = create_dataset([1, 2, 3], stability=1)

    # Test initial status
    status = dsl.budget_status()
    assert status['total_budget'] == 5.0
    assert status['used_budget'] == 0.0
    assert status['remaining_budget'] == 5.0
    assert status['usage_percentage'] == 0.0

    # Consume some budget
    dsl.count(data, epsilon=2.0)

    # Test updated status
    status = dsl.budget_status()
    assert status['used_budget'] == 2.0
    assert status['remaining_budget'] == 3.0
    assert status['usage_percentage'] == 40.0

    # Test string representation
    str_repr = str(dsl)
    assert "2.000/5.000" in str_repr
    assert "40.0%" in str_repr

    # Test budget reset
    dsl.reset_budget(10.0)
    assert dsl.get_total_budget() == 10.0
    assert dsl.get_used_budget() == 0.0

    print("  ✓ Budget utilities test passed!")


# ============================================================================
# (α,β)-Accuracy Tests (Based on Haskell Implementation)
# ============================================================================

def test_laplace_accuracy():
    """Test Laplace mechanism using (α,β)-accuracy bounds"""
    print("Testing Laplace mechanism (α,β)-accuracy...")

    # Test dpCount with (α,β)-accuracy
    count_test = _test_count_accuracy()

    # Test dpSum with (α,β)-accuracy
    sum_test = _test_sum_accuracy()

    all_passed = count_test and sum_test
    print(f"  Laplace accuracy tests: {'PASSED' if all_passed else 'FAILED'}")

    assert all_passed

# These functions are named with an underscore so that `pytest` won't consider them standalone test cases

def _test_count_accuracy():
    """Test dpCount accuracy using (α,β) bounds with multiple epsilon values"""
    print("  Testing dpCount (α,β)-accuracy with multiple epsilons:")

    epsilons = [0.1, 1.0, 10.0]
    beta = 0.05  # 95% confidence
    sensitivity = 1.0  # Count has sensitivity 1
    true_count = 0  # Empty dataset
    num_samples = 10000

    print(f"    β = {beta} (95% confidence)")
    print(f"    Sensitivity = {sensitivity}")

    # Test each epsilon value
    results = []
    for epsilon in epsilons:
        result = _test_count_for_epsilon(beta, sensitivity, true_count, num_samples, epsilon)
        results.append(result)

    all_passed = all(results)
    print(f"    Overall dpCount accuracy test: {all_passed}")

    return all_passed


def _test_count_for_epsilon(beta, sensitivity, true_count, num_samples, epsilon):
    """Test dpCount for a specific epsilon value"""
    alpha = math.log(1.0 / beta) * (sensitivity / epsilon)  # Theoretical error bound
    print(f"    ε = {epsilon}:")
    print(f"      Theoretical α bound = {alpha}")

    # Generate samples using empty dataset (matching Haskell approach)
    empty_data = create_dataset([], stability=1)
    dsl = DP_DSL(budget=num_samples * epsilon + 1.0)  # Large budget for samples

    samples = []
    for _ in range(num_samples):
        result = dsl.count(empty_data, epsilon)
        samples.append(result.dp_value)

    # Check how many samples violate the α bound
    errors = [abs(sample - true_count) for sample in samples]
    violations = len([e for e in errors if e > alpha])
    violation_rate = violations / num_samples

    print(f"      Violations: {violations}/{num_samples} ({violation_rate * 100:.1f}%)")
    print(f"      Expected violation rate: ≤ {beta * 100:.1f}%")

    test_passed = violation_rate <= beta * 1.1  # Allow 10% tolerance for finite sample variation
    print(f"      Test result: {'PASSED' if test_passed else 'FAILED'}")

    return test_passed


def _test_sum_accuracy():
    """Test dpSum accuracy using (α,β) bounds with multiple epsilon values"""
    print("  Testing dpSum (α,β)-accuracy with multiple epsilons and sensitivities:")

    epsilons = [0.1, 1.0, 10.0]
    beta = 0.05  # 95% confidence
    num_samples = 10000
    # Test different bounds to verify sensitivity calculation
    bounds_list = [(0.0, 1.0), (0.0, 10.0), (-5.0, 5.0), (-10.0, 20.0)]

    print(f"    β = {beta} (95% confidence)")

    # Test each bounds configuration
    results = []
    for bounds in bounds_list:
        result = _test_sum_for_bounds(beta, num_samples, epsilons, bounds)
        results.append(result)

    all_passed = all(results)
    print(f"    Overall dpSum accuracy test: {all_passed}")

    return all_passed


def _test_sum_for_bounds(beta, num_samples, epsilons, bounds):
    """Test dpSum for a specific bounds configuration across multiple epsilons"""
    lower_bound, upper_bound = bounds
    sensitivity = max(abs(lower_bound), abs(upper_bound))
    print(f"    Bounds: [{lower_bound}, {upper_bound}] (sensitivity = {sensitivity})")

    # Test each epsilon value for this bounds configuration
    results = []
    for epsilon in epsilons:
        result = _test_sum_for_epsilon(beta, sensitivity, num_samples, lower_bound, upper_bound, epsilon)
        results.append(result)

    all_passed = all(results)
    print(f"      Bounds test result: {'PASSED' if all_passed else 'FAILED'}")
    return all_passed


def _test_sum_for_epsilon(beta, sensitivity, num_samples, lower_bound, upper_bound, epsilon):
    """Test dpSum for a specific epsilon value"""
    alpha = math.log(1.0 / beta) * (sensitivity / epsilon)  # Theoretical error bound
    print(f"      ε = {epsilon}:")
    print(f"        Theoretical α bound = {alpha}")

    # Generate samples using empty dataset (matching Haskell approach)
    empty_data = create_dataset([], stability=1)
    dsl = DP_DSL(budget=num_samples * epsilon + 1.0)  # Large budget for samples

    samples = []
    for _ in range(num_samples):
        result = dsl.sum(empty_data, epsilon, lower_bound, upper_bound)
        samples.append(result.dp_value)

    # Check how many samples violate the α bound (true sum is 0 for empty dataset)
    errors = [abs(sample) for sample in samples]
    violations = len([e for e in errors if e > alpha])
    violation_rate = violations / num_samples

    print(f"        Violations: {violations}/{num_samples} ({violation_rate * 100:.1f}%)")
    print(f"        Expected violation rate: ≤ {beta * 100:.1f}%")

    test_passed = violation_rate <= beta * 1.1  # Allow 10% tolerance for finite sample variation
    print(f"        Test result: {'PASSED' if test_passed else 'FAILED'}")

    return test_passed


def test_stability_tracking_accuracy():
    """Test that stability is correctly tracked through transformations using (α,β)-accuracy"""
    print("Testing stability tracking with (α,β)-accuracy...")

    # Test 1: Union amplifies stability
    stability_test1 = _test_union_stability_accuracy()

    # Test 2: GroupBy doubles stability
    stability_test2 = _test_groupby_stability_accuracy()

    all_passed = stability_test1 and stability_test2
    print(f"  Union stability amplification: {stability_test1}")
    print(f"  GroupBy stability doubling: {stability_test2}")
    print(f"  Stability tracking tests: {'PASSED' if all_passed else 'FAILED'}")

    assert all_passed


def _test_union_stability_accuracy():
    """Test union amplifies stability correctly using (α,β)-accuracy"""
    print("    Testing union stability amplification with (α,β)-accuracy...")

    epsilon = 1.0
    num_samples = 10000
    beta = 0.05  # 95% confidence

    # Test stability=1 (baseline)
    baseline_dsl = DP_DSL(budget=num_samples * epsilon + 1.0)
    baseline_data = create_dataset([], stability=1)
    baseline_samples = []
    for _ in range(num_samples):
        result = baseline_dsl.count(baseline_data, epsilon)
        baseline_samples.append(result.dp_value)

    # Test stability=2 (after union)
    union_dsl = DP_DSL(budget=num_samples * epsilon + 1.0)
    data1 = create_dataset([], stability=1)
    data2 = create_dataset([], stability=1)
    union_data = union_dsl.union(data1, data2)  # Should have stability=2
    union_samples = []
    for _ in range(num_samples):
        result = union_dsl.count(union_data, epsilon)
        union_samples.append(result.dp_value)

    # Calculate α bounds for each stability level
    baseline_alpha = math.log(1.0 / beta) * (1.0 / epsilon)  # stability=1, sensitivity=1
    union_alpha = math.log(1.0 / beta) * (2.0 / epsilon)  # stability=2, sensitivity=1

    # Check violations for baseline (stability=1)
    baseline_errors = [abs(sample) for sample in baseline_samples]
    baseline_violations = len([e for e in baseline_errors if e > baseline_alpha])
    baseline_violation_rate = baseline_violations / num_samples

    # Check violations for union (stability=2)
    union_errors = [abs(sample) for sample in union_samples]
    union_violations = len([e for e in union_errors if e > union_alpha])
    union_violation_rate = union_violations / num_samples

    print(f"      Baseline (stability=1) α bound: {baseline_alpha}")
    print(f"      Baseline violations: {baseline_violations}/{num_samples} ({baseline_violation_rate * 100:.1f}%)")
    print(f"      Union (stability=2) α bound: {union_alpha}")
    print(f"      Union violations: {union_violations}/{num_samples} ({union_violation_rate * 100:.1f}%)")

    # Both should satisfy (α,β)-accuracy, and union should have larger α bound (less accurate)
    baseline_test = baseline_violation_rate <= beta * 1.1
    union_test = union_violation_rate <= beta * 1.1
    test_passed = baseline_test and union_test

    print(f"      Baseline accuracy test: {'PASSED' if baseline_test else 'FAILED'}")
    print(f"      Union accuracy test: {'PASSED' if union_test else 'FAILED'}")
    return test_passed


def _test_groupby_stability_accuracy():
    """Test groupBy doubles stability using (α,β)-accuracy"""
    print("    Testing groupBy stability doubling with (α,β)-accuracy...")

    epsilon = 1.0
    num_samples = 10000
    beta = 0.05  # 95% confidence

    # Test stability=1 (baseline)
    baseline_dsl = DP_DSL(budget=num_samples * epsilon + 1.0)
    baseline_data = create_dataset([], stability=1)
    baseline_samples = []
    for _ in range(num_samples):
        result = baseline_dsl.count(baseline_data, epsilon)
        baseline_samples.append(result.dp_value)

    # Test stability=2 (after groupBy)
    groupby_dsl = DP_DSL(budget=num_samples * epsilon + 1.0)
    data = create_dataset([], stability=1)
    grouped_data = groupby_dsl.group_by(lambda x: x % 2, data)  # Group by even/odd on empty dataset
    grouped_samples = []
    for _ in range(num_samples):
        result = groupby_dsl.count(grouped_data, epsilon)
        grouped_samples.append(result.dp_value)

    # Calculate α bounds for each stability level
    baseline_alpha = math.log(1.0 / beta) * (1.0 / epsilon)  # stability=1, sensitivity=1
    grouped_alpha = math.log(1.0 / beta) * (2.0 / epsilon)  # stability=2, sensitivity=1

    # Check violations for baseline (stability=1)
    baseline_errors = [abs(sample) for sample in baseline_samples]
    baseline_violations = len([e for e in baseline_errors if e > baseline_alpha])
    baseline_violation_rate = baseline_violations / num_samples

    # Check violations for groupBy (stability=2)
    grouped_errors = [abs(sample) for sample in grouped_samples]
    grouped_violations = len([e for e in grouped_errors if e > grouped_alpha])
    grouped_violation_rate = grouped_violations / num_samples

    print(f"      Baseline (stability=1) α bound: {baseline_alpha}")
    print(f"      Baseline violations: {baseline_violations}/{num_samples} ({baseline_violation_rate * 100:.1f}%)")
    print(f"      GroupBy (stability=2) α bound: {grouped_alpha}")
    print(f"      GroupBy violations: {grouped_violations}/{num_samples} ({grouped_violation_rate * 100:.1f}%)")

    # Both should satisfy (α,β)-accuracy, and groupBy should have larger α bound (less accurate)
    baseline_test = baseline_violation_rate <= beta * 1.1
    grouped_test = grouped_violation_rate <= beta * 1.1
    test_passed = baseline_test and grouped_test

    print(f"      Baseline accuracy test: {'PASSED' if baseline_test else 'FAILED'}")
    print(f"      GroupBy accuracy test: {'PASSED' if grouped_test else 'FAILED'}")

    return test_passed
