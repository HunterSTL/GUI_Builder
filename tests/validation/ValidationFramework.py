from dataclasses import dataclass
from collections.abc import Callable
from typing import Any
from time import perf_counter

#terminal colors
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[39m"


@dataclass
class ValidationTest:
    name: str
    expected_error_message: str
    action: Callable[..., None]
    setup: Callable[[], dict[str, Any]] | None = None
    teardown: Callable[..., None] | None = None


@dataclass
class ValidationTestResult:
    test_name: str
    passed: bool
    details: str

def run_validation_tests(
    tests: tuple[ValidationTest, ...]
) -> tuple[list[ValidationTestResult], int]:
    """Run all validation tests and return both a list of their results and the execution time in ms."""
    start_time = perf_counter()
    test_results: list[ValidationTestResult] = []

    for test in tests:
        context = test.setup() if test.setup is not None else {}

        try:
            test.action(**context)
        except ValueError as error:
            actual_error_message = str(error)
            if actual_error_message == test.expected_error_message:
                passed = True
                details = actual_error_message
            else:
                passed = False
                details = f"Wrong error message: {actual_error_message}"
        except Exception as error:
            passed = False
            details = f"Wrong exception type: {type(error).__name__}: {error}"
        else:
            passed = False
            details = "No error raised"
        finally:
            if test.teardown is not None:
                test.teardown(**context)

        test_results.append(
            ValidationTestResult(
                test_name=test.name,
                passed=passed,
                details=details
            )
        )

    execution_time_ms = int((perf_counter() - start_time) * 1000)
    return test_results, execution_time_ms

def print_validation_test_results(
    test_results: list[ValidationTestResult],
    execution_time_ms: int
) -> None:
    """Format and print the results."""
    def separator() -> None:
        print("-" * 200)

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
