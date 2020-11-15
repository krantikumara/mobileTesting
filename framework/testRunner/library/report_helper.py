import logging
import os


class ReportHelper:
    """Provides helper functions used in reporting command, tests and steps"""

    @classmethod
    def infer_test_name(cls) -> str:
        """Tries to infer the test name from pytest
        Returns:
            str: The inferred test name
        """
        known_phases = [" (teardown)", " (call)", " (setup)"]
        current_test_info = os.environ.get("PYTEST_CURRENT_TEST")
        for phase in known_phases:
            current_test_info = current_test_info.replace(phase, "")

        return current_test_info if current_test_info is not None else "Unnamed Test"
