import datetime
import os
import time

from .reporting import TestReport


class TestRunner:
    def __init__(self):
        self.report = TestReport()

    def run_test(self, testbench, test, **kwargs):
        """Run a single test and collect results."""
        start_time = time.time()
        details = None
        result = None  # Initialize result variable
        try:
            # Existing test execution code...
            # The actual implementation should set the result variable
            # For now, we'll just initialize it to avoid the undefined name error
            # Assuming result should be defined in the commented out code
            # If it's passed as a parameter, we could use:
            # result = kwargs.get("result")
            status = "passed" if result and hasattr(result, "success") and result.success else "failed"
        except Exception as e:
            status = "failed"
            details = str(e)

        duration = time.time() - start_time

        self.report.add_test_result(
            name=test,
            testbench=testbench,
            status=status,
            duration=round(duration, 2),
            seed=kwargs.get("seed", "random"),
            details=details if status == "failed" else None,
        )

    def run_regression(self, tests, **kwargs):
        """Run multiple tests and generate report."""
        for testbench, test in tests:
            self.run_test(testbench, test, **kwargs)

        report_path = os.path.join("reports", f'report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        self.report.generate(report_path)
        return report_path
