import uuid
import logging
from datetime import datetime

from testRunner.library import ReportHelper


class DriverCommandReport:
    """Payload object sent to the Mate Server when reporting a driver command.
    Args:
        command (str): The name of the command that was executed
        command_params (dict): Parameters associated with the command
        result (dict): The result of the command that was executed
        passed (bool): Indication whether or not command execution was performed successfully
        screenshot (str): Screenshot as base64 encoded string
    Attributes:
        _command (str): The name of the command that was executed
        _command_params (dict): Parameters associated with the command
        _result (dict): The result of the command that was executed
        _passed (bool): Indication whether or not command execution was performed successfully
        _screenshot (str): Screenshot as base64 encoded string
    """

    def __init__(
            self,
            command: str,
            command_params: dict,
            result: dict,
            passed: bool,
            screenshot: str = None,
    ):
        self._command = command
        self._command_params = command_params
        self._result = result
        self._passed = passed
        self._screenshot = screenshot
        self._timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self._testcase_id = ReportHelper.infer_test_name()

    @property
    def command(self) -> str:
        """Getter for the command property"""
        return self._command

    @property
    def command_params(self) -> dict:
        """Getter for the command_params property"""
        return self._command_params

    @property
    def result(self) -> dict:
        """Getter for the result property"""
        return self._result

    @property
    def passed(self) -> bool:
        """Getter for the passed property"""
        return self._passed

    @property
    def screenshot(self) -> str:
        """Getter for the screenshot property"""
        return self._screenshot

    @screenshot.setter
    def screenshot(self, value: str):
        """Setter for the screenshot property"""
        self._screenshot = value

    def to_json(self):
        """Creates a JSON representation of the current DriverCommandReport instance
            Returns:
                dict: JSON representation of the current instance
        """
        payload = {
            "testcase_id": self._testcase_id,
            "timestamp":self._timestamp,
            "commandName": self._command,
            "commandParameters": self._command_params,
            "result": self._result,
            "passed": self._passed,
        }

        # Add screenshot to report if it is provided
        if self._screenshot is not None:
            payload["screenshot"] = self._screenshot

        return payload

    def __eq__(self, other):
        """Custom equality function, used in report stashing"""
        if not isinstance(other, DriverCommandReport):
            return NotImplemented

        return (
                self._command == other._command
                and self._command_params == other._command_params
                and self._result == other._result
                and self._passed == other._passed
        )

    def __hash__(self):
        """Implement hash to allow objects to be used in sets and dicts"""
        return hash(
            (
                self.command,
                self.command_params,
                self.result,
                self.passed,
                self.screenshot,
            )
        )


class StepReport:
    """Payload object sent to the MATE Server when reporting a test step.
        Args:
            description (str): The step description
            message (str): A message that goes with the step
            passed (bool): True if the step should be marked as passed, False otherwise
            screenshot (str): A base64 encoded screenshot that is associated with the step
        Attributes:
            _description (str): The step description
            _message (str): A message that goes with the step
            _passed (bool): True if the step should be marked as passed, False otherwise
            _screenshot (str): A base64 encoded screenshot that is associated with the step
    """

    def __init__(self, description: str, message: str, passed: bool, screenshot: str = None):
        self._timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self._testcase_id = ReportHelper.infer_test_name()
        self._description = description
        self._message = message
        self._passed = passed
        self._screenshot = screenshot

    def to_json(self) -> dict:
        """Generates a dict containing the JSON representation of the step payload"""
        json = {
            "testcase_id": self._testcase_id,
            "timestamp":self._timestamp,
            "guid": str(uuid.uuid4()),
            "description": self._description,
            "message": self._message,
            "passed": self._passed,
        }
        if self._screenshot is not None:
            json["screenshot"] = self._screenshot

        return json


class CustomTestReport:
    """Payload object sent to the Mate Server when reporting a test.

    Attributes:
        _timestamp (str): Current timestamp
        _testcase_id (str): Unique id of the testcase
    """

    def __init__(self):
        self._timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self._testcase_id = ReportHelper.infer_test_name()

    def to_json(self):
        """Generates a dict containing the JSON representation of the test payload"""
        return {"timestamp":self._timestamp, "testcase_id": self._testcase_id}


class Reporter:
    """Exposes reporting actions to the WebDriver object
    Args:
        command_executor: the command executor associated with the driver
    Attributes:
        _command_executor: the command executor associated with the driver
    """

    def __init__(self, command_executor):
        self._command_executor = command_executor

    def step(self, description: str, message: str, passed: bool, screenshot: bool = False):
        """Sends a step report to the MATE Server
        Args:
            description (str): The step description
            message (str): A message that goes with the step
            passed (bool): True if the step should be marked as passed, False otherwise
            screenshot (bool): True if a screenshot should be made, False otherwise
        """

        # First update the current test name and report a test if necessary
        self._command_executor.update_known_test_name()

        step_report = StepReport(
            description, message, passed, self._command_executor.create_screenshot() if screenshot else None,
        )
        self._command_executor.mate_client.report_step(step_report)

        logging.debug(f"Step '{description}' {'passed' if passed else 'failed'}")
