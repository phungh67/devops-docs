"""
Example usage of the Differential Privacy DSL with Adult Census Dataset

This module demonstrates how to use the DP_DSL class with real census data,
showing practical differential privacy applications.
"""

from typing import List, Tuple, Any
from dp import DP_DSL, Dataset, create_dataset, Adult, Income, Occupation, load_adult_dataset


def basic_count_example(adult_data: Dataset[Adult]) -> None:
    """Basic example: counting high earners with different epsilon values"""
    print("=== High Earners Count Example ===")

    # Calculate true high earner count
    true_high_earner_count = len([a for a in adult_data if a.income == Income.HIGH_INCOME])
    print(f"True high earners count: {true_high_earner_count}")

    # Create DSL instance with total budget for all queries
    dsl = DP_DSL(budget=6.1)  # 0.1 + 1.0 + 5.0

    # Filter to high earners (budget-free transformation)
    high_earners = dsl.filter(lambda person: person.income == Income.HIGH_INCOME, adult_data)

    # Run three count queries with different epsilon values
    print("DP Count with different epsilon values:")

    result1 = dsl.count(high_earners, epsilon=0.1)
    print(f"  ε=0.1: {result1.dp_value:.2f}")
    print(f"  Budget status: {dsl}")

    result2 = dsl.count(high_earners, epsilon=1.0)
    print(f"  ε=1.0: {result2.dp_value:.2f}")
    print(f"  Budget status: {dsl}")

    result3 = dsl.count(high_earners, epsilon=5.0)
    print(f"  ε=5.0: {result3.dp_value:.2f}")
    print(f"  Final budget status: {dsl}")


def union_stability_example(adult_data: Dataset[Adult]) -> None:
    """Example showing union and stability amplification"""
    print("=== Union with Overlapping Groups Example ===")

    # Calculate true counts
    high_earners_count = len([a for a in adult_data if a.income == Income.HIGH_INCOME])

    white_collar_occupations = {
        Occupation.EXEC_MANAGERIAL,
        Occupation.PROF_SPECIALTY,
        Occupation.TECH_SUPPORT,
        Occupation.ADM_CLERICAL
    }
    white_collar_count = len([
        a for a in adult_data
        if a.occupation in white_collar_occupations
    ])

    overlap_count = high_earners_count + white_collar_count

    print(f"True high earners count: {high_earners_count}")
    print(f"True white-collar workers count: {white_collar_count}")
    print(f"Expected union count: {overlap_count}")

    # Create DSL instance
    dsl = DP_DSL(budget=6.1)

    # Create groups (budget-free transformations)
    high_earners = dsl.filter(lambda person: person.income == Income.HIGH_INCOME, adult_data)
    white_collar = dsl.filter(
        lambda person: person.occupation in white_collar_occupations,
        adult_data
    )

    # Union creates stability amplification (budget-free)
    combined = dsl.union(high_earners, white_collar)
    print(f"Combined dataset stability: {combined.stability}")

    # Run union count queries with different epsilon values
    print("DP Union count with different epsilon values:")

    result1 = dsl.count(combined, epsilon=0.1)
    print(f"  ε=0.1: {result1.dp_value:.2f}")

    result2 = dsl.count(combined, epsilon=1.0)
    print(f"  ε=1.0: {result2.dp_value:.2f}")

    result3 = dsl.count(combined, epsilon=5.0)
    print(f"  ε=5.0: {result3.dp_value:.2f}")

    print(f"Final budget status: {dsl}")


def occupation_analysis_example(adult_data: Dataset[Adult]) -> None:
    """Example using groupBy to analyze occupations"""
    print("=== Occupation GroupBy Example ===")

    # Calculate true average hours per occupation
    from collections import defaultdict
    occupation_groups = defaultdict(list)
    for person in adult_data:
        occupation_groups[person.occupation].append(person)

    occupation_avgs = []
    for occ, people in occupation_groups.items():
        if people:
            avg_hours = sum(p.hours_per_week for p in people) / len(people)
            occupation_avgs.append((occ, avg_hours))

    true_high_avg_occupations = len([(occ, avg) for occ, avg in occupation_avgs if avg > 40])

    print("True average hours per occupation:")
    for occ, avg in occupation_avgs[:10]:  # Show first 10
        print(f"  {occ.name}: {avg:.2f}")
    print(f"True count of occupations with avg hours > 40: {true_high_avg_occupations}")

    # Create DSL instance
    dsl = DP_DSL(budget=15.5)  # 1.0 + 1.5 + 2.0 + 11.0

    # Group by occupation (budget-free, but doubles stability)
    occ_groups = dsl.group_by(lambda person: person.occupation, adult_data)
    print(f"Grouped dataset stability: {occ_groups.stability}")

    # Calculate average hours per occupation (budget-free)
    def calc_avg_hours(occ_people_tuple):
        occ, people = occ_people_tuple
        if people:
            total_hours = sum(p.hours_per_week for p in people)
            return total_hours / len(people)
        return 0.0

    avg_hours = dsl.map(calc_avg_hours, occ_groups)

    # Filter to occupations with high average hours (budget-free)
    hard_working_occs = dsl.filter(lambda avg: avg > 40, avg_hours)

    # Run count queries with different epsilon values
    print("DP count of occupations with avg hours > 40:")

    result1 = dsl.count(hard_working_occs, epsilon=1.0)
    print(f"  ε=1.0: {result1.dp_value:.2f}")

    result2 = dsl.count(hard_working_occs, epsilon=1.5)
    print(f"  ε=1.5: {result2.dp_value:.2f}")

    result3 = dsl.count(hard_working_occs, epsilon=2.0)
    print(f"  ε=2.0: {result3.dp_value:.2f}")

    result4 = dsl.count(hard_working_occs, epsilon=11.0)
    print(f"  ε=11.0: {result4.dp_value:.2f}")

    print(f"Final budget status: {dsl}")


def partition_example(adult_data: Dataset[Adult]) -> None:
    """Demonstrate partition with age-based analysis"""
    print("=== Age Group Partition Example ===")

    # Calculate true high earner counts by age group
    young_count = len([a for a in adult_data
                      if a.age < 30 and a.income == Income.HIGH_INCOME])
    middle_count = len([a for a in adult_data
                       if 30 <= a.age < 50 and a.income == Income.HIGH_INCOME])
    senior_count = len([a for a in adult_data
                       if a.age >= 50 and a.income == Income.HIGH_INCOME])

    print("True high earner counts by age group:")
    print(f"  Young (<30): {young_count}")
    print(f"  Middle (30-49): {middle_count}")
    print(f"  Senior (50+): {senior_count}")

    # Create DSL instance for each partition query
    results = []

    for epsilon in [0.1, 1.0, 10.0]:
        # Create fresh DSL instance for each epsilon test
        dsl = DP_DSL(budget=epsilon + 0.1)  # Small buffer for partition overhead

        def classify_age(person: Adult) -> str:
            if person.age < 30:
                return "Young"
            elif person.age < 50:
                return "Middle"
            else:
                return "Senior"

        def count_high_earners(age_group: str, age_group_data: Dataset[Adult]) -> Any:
            high_earners = dsl.filter(
                lambda person: person.income == Income.HIGH_INCOME,
                age_group_data
            )
            return dsl.count(high_earners, epsilon=epsilon)

        # Use partition (which consumes epsilon for the operation)
        partition_results = dsl.partition(
            keys=["Young", "Middle", "Senior"],
            classifier=classify_age,
            dataset=adult_data,
            computation=count_high_earners,
            epsilon=epsilon
        )

        results.append((epsilon, partition_results))

    print("DP high earner counts by age group with different epsilon values:")
    for epsilon, age_group_results in results:
        print(f"  ε={epsilon}:")
        for age_group, result in age_group_results:
            print(f"    {age_group}: {result.dp_value:.2f}")


def budget_management_example() -> None:
    """Example showing advanced budget management features"""
    print("=== Budget Management Example ===")

    # Create a small test dataset
    test_data = create_dataset([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Create DSL instance
    dsl = DP_DSL(budget=3.0)
    print(f"Initial: {dsl}")

    # Apply transformations (budget-free)
    filtered = dsl.filter(lambda x: x > 5, test_data)
    print(f"After filter: {dsl}")

    # First measurement
    result1 = dsl.count(filtered, epsilon=1.0)
    print(f"After first count (ε=1.0): {dsl}")
    print(f"Result 1: {result1.dp_value:.2f}")

    # Check budget status
    status = dsl.budget_status()
    print(f"Budget status: {status}")

    # Second measurement
    doubled = dsl.map(lambda x: x * 2.0, filtered)
    result2 = dsl.sum(doubled, epsilon=1.5, lower_bound=0.0, upper_bound=20.0)
    print(f"After sum (ε=1.5): {dsl}")
    print(f"Result 2: {result2.dp_value:.2f}")

    # Try to exceed budget (should fail)
    print("\nTrying to exceed budget...")
    try:
        result3 = dsl.count(filtered, epsilon=1.0)  # Would exceed budget
        print("ERROR: Should have failed!")
    except Exception as e:
        print(f"Correctly caught error: {e}")

    print(f"Final: {dsl}")


def main() -> None:
    """Run all examples with the Adult Census dataset"""
    print("Differential Privacy DSL - Examples")
    print("=" * 50)

    print("Loading Adult Census dataset...")
    adult_data = load_adult_dataset("adult.csv")

    print(f"Loaded {len(adult_data)} records")
    print()

    # Run all examples with the loaded dataset
    basic_count_example(adult_data)
    print()

    union_stability_example(adult_data)
    print()

    occupation_analysis_example(adult_data)
    print()

    partition_example(adult_data)
    print()

    budget_management_example()
    print()

    print("All examples completed!")


if __name__ == "__main__":
    main()