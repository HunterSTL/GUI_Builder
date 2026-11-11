from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter

#terminal colors
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[39m"


@dataclass
class UnitTest:
    name: str
    case: Callable[[], None]


@dataclass
class UnitTestResult:
    test_name: str
    passed: bool
    details: str

def assert_equal(
    actual: object,
    expected: object,
    message: str
) -> None:
    if actual != expected:
        raise AssertionError(f"{message} (expected: {expected}, actual: {actual})")

def run_unit_tests(
    tests: tuple[UnitTest, ...]
) -> tuple[list[UnitTestResult], int]:
    """Run all unit tests and return both a list of their results and the execution time in ms."""
    start_time = perf_counter()
    test_results: list[UnitTestResult] = []

    for test in tests:
        try:
            test.case()
        except AssertionError as error:
            passed = False
            details = f"Invariant broken: {error}"
        except Exception as error:
            passed = False
            details = f"Unexpected error: {error}"
        else:
            passed = True
            details = "Test successful"

        test_results.append(
            UnitTestResult(
                test_name=test.name,
                passed=passed,
                details=details
            )
        )

    execution_time_ms = int((perf_counter() - start_time) * 1000)
    return test_results, execution_time_ms

def print_unit_test_results(
    test_results: list[UnitTestResult],
    execution_time_ms: int
) -> None:
    """Format and print the results."""
    def separator() -> None:
        print("-" * 200)

    if not test_results:
        print("No unit tests registered")
        return

    #determine max test name length for formatting
    max_test_name_length = max(len(test_result.test_name) for test_result in test_results)

    #header
    separator()
    header_spacing = " " * (max_test_name_length - len("TEST CASE"))
    print(f"STATUS\tTEST CASE{header_spacing}\tDETAILS")
    separator()

    #body
    for test_result in test_results:
        if test_result.passed:
            verdict = GREEN + "[PASS]" + RESET
        else:
            verdict = RED + "[FAIL]" + RESET

        name_spacing = " " * (max_test_name_length - len(test_result.test_name))
        print(f"{verdict}\t{test_result.test_name + name_spacing}\t{test_result.details}")

    #footer
    pass_count = sum(test_result.passed for test_result in test_results)
    total_count = len(test_results)
    pass_summary = f"{pass_count}/{total_count}"

    if pass_count == total_count:
        overall_verdict = GREEN + "[PASS]" + RESET
    else:
        overall_verdict = RED + "[FAIL]" + RESET

    separator()
    print(f"VERDICT:\t\t{overall_verdict}")
    print(f"PASSED:\t\t\t{pass_summary}")
    print(f"EXECUTION TIME:\t{execution_time_ms} ms")
    separator()
