import configparser
import subprocess
import os
import re

# To-Do -> Add proper logging and error handling throughout

REGEX_MARKERS = {"TEST": "<Module (.+?)>",
                 "FUNCTION": "<Function (.+?)>"
                 }


class PyTestHelper:
    def __init__(self, pytest_root):
        self.pytest_root = pytest_root

    def parse_tests_from_pytest(self, output):
        tests = output.stdout.splitlines()
        tests = [test.decode("utf-8") for test in tests if test]
        collected_tests = []
        test_file_path = ""
        for test in tests:
            if "Module" in test:
                test_file_path = re.search(REGEX_MARKERS["TEST"], test).group(1)
            if "Function" in test:
                test_function_name = re.search(REGEX_MARKERS["FUNCTION"], test).group(1)
                collected_tests.append(test_file_path + "::" + test_function_name)
        return collected_tests

    def get_markers(self):
        try:
            config = configparser.ConfigParser()
            if os.path.exists(os.path.join(self.pytest_root, "pytest.ini")):
                config.read(os.path.join(self.pytest_root, "pytest.ini"))
                tests = config["pytest"]["markers"].split("\n")
                tests = [test for test in tests if test]
                return tests
            else:
                return []
        except Exception as exp:
            return []

    def get_tests(self, marker=None):
        if marker:
            cmd = ["pytest", "-m", marker, "--collect-only"]
        else:
            cmd = ["pytest", "--collect-only"]

        try:
            output = subprocess.run(cmd, cwd=self.pytest_root,
                                    capture_output=True)

            return self.parse_tests_from_pytest(output)
        except Exception as exp:
            return []

    def run_tests(self, execution_id, marker=None, test=None):
        if marker:
            # Run tests with specific marker
            cmd = ["pytest", "-m", marker, "--session", execution_id]
        elif test:
            # Run specific test
            cmd = ["pytest", "--session", execution_id, test]
        else:
            # Run all tests
            cmd = ["pytest", "--session", execution_id]

        output = subprocess.run(cmd, cwd=self.pytest_root, capture_output=True)
        return output.stdout, output.stderr
