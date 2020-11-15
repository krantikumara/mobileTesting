import logging
import inspect
import uuid

from selenium.webdriver.remote.command import Command
from testRunner.library import ReportHelper
from testRunner.library.reporters import DriverCommandReport, CustomTestReport
from testRunner.library import MateClient


class ReportingCommandExecutor:
    """Class responsible for executing commands and reporting them
    Args:
        mate_client (MateClient): Client used to communicate with the Mate Server
        command_executor: The command executor used to send WebDriver commands (Selenium or Appium)
    Attributes:
        _mate_client (MateClient): Client used to communicate with the Mate Server
        _command_executor: The command executor used to send WebDriver commands (Selenium or Appium)
        _stashed_command (DriverCommandReport): contains stashed driver command for preventing duplicates
        inside WebDriverWait
        _latest_known_test_name (str): contains latest known test name
    """

    def __init__(self, mate_client: MateClient, command_executor):
        self._mate_client = mate_client
        self._command_executor = command_executor
        self._stashed_command = None
        self._latest_known_test_name = ReportHelper.infer_test_name()

    @property
    def mate_client(self):
        """Getter for the Mate client associated with this connection"""
        return self._mate_client

    def _report_command(self, command: str, params: dict, result: dict, passed: bool):
        """Reports a driver command to the MateServer
        Args:
            command (str): The driver command to execute
            params (dict): Named parameters to send with the command as its JSON payload
            result (dict): The response returned by the Selenium remote webdriver server
            passed (bool): True if the command execution was successful, False otherwise
        """

        if command == Command.QUIT:
            self.report_test()
            return  # This ensures that the actual driver.quit() command is not included in the report

        # If the command is executed as part of a wait loop, we don't want to report it every time
        self._is_webdriverwait = False

        # See if the command is executed inside a wait loop
        for frame in inspect.stack().__reversed__():
            if str(frame.filename).find("wait.py") > 0:
                self._is_webdriverwait = True
                break

        driver_command_report = DriverCommandReport(command, params, result, passed)

        if not passed:
            driver_command_report.screenshot = self.create_screenshot()

        if self._is_webdriverwait:
            # Only stash the command for reporting later when driver command reporting is enabled
            self._stashed_command = driver_command_report
            return  # Do not report the command right away

        if self._stashed_command is not None:
            # report the stashed command and clear it
            self.mate_client.report_driver_command(self._stashed_command)
            self._stashed_command = None
        # report the current command
        self.mate_client.report_driver_command(driver_command_report)

    def update_known_test_name(self):
        """Infers the current test name and if different from the latest known test name, reports a test"""
        current_test_name = ReportHelper.infer_test_name()

        if (
                current_test_name not in [self._latest_known_test_name, "Unnamed Test"]

        ):
            # update the latest known test name for future reports
            self._latest_known_test_name = current_test_name

    def report_test(self):
        """Sends a test report to the Mate if this option is not explicitly disabled
        """

        if not self._latest_known_test_name == "Unnamed Test":
            # only report those tests that have been identified as one when their names were inferred

            self.mate_client.report_test(CustomTestReport())

    def create_screenshot(self) -> str:
        """Creates a screenshot (PNG) and returns it as a base64 encoded string
        Returns:
            str: The base64 encoded screenshot in PNG format (or None if screenshot taking fails)
        """
        create_screenshot_params = {
            "sessionId": self.mate_client.session_id
        }
        create_screenshot_response = self._command_executor.execute(
            Command.SCREENSHOT, create_screenshot_params, True
        )
        try:
            return create_screenshot_response["value"]
        except KeyError as ke:
            logging.error(f"Error occurred creating a screenshot: {ke}")
            logging.error(
                f"Response from RemoteWebDriver: {create_screenshot_response}"
            )
            return None

    def clear_stash(self):
        """Reports stashed command if there is one left. Should be called when session ends to prevent
           wait-related commands from not being reported.
        """

        if self._stashed_command is not None:
            # report the stashed command and clear it
            self.mate_client.report_driver_command(self._stashed_command)
            self._stashed_command = None

    def is_command_passed(self, response: dict) -> bool:
        """Determine command result based on response using state and status.
        Args:
            response (dict): The response returned by the Selenium remote webdriver server
        Returns:
            bool: True if passed, otherwise False.
        """
        # Both None and 0 response status values indicate command execution was OK
        return True if response.get("status") in [None, 0] else False
