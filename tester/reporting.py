import datetime
import os

from jinja2 import Environment, FileSystemLoader


class TestReport:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.env.get_template("report.html")
        self.tests = []

    def add_test_result(self, name, testbench, status, duration, seed, details=None):
        """Add a test result to the report."""
        self.tests.append(
            {"name": name, "testbench": testbench, "status": status, "duration": duration, "seed": seed, "details": details}
        )

    def generate(self, output_path):
        """Generate HTML report at the specified path."""
        passed = sum(1 for t in self.tests if t["status"] == "passed")
        failed = sum(1 for t in self.tests if t["status"] == "failed")
        skipped = sum(1 for t in self.tests if t["status"] == "skipped")

        report_data = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.tests),
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "tests": self.tests,
        }

        html = self.template.render(**report_data)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(html)
