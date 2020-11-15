from appium.webdriver.appium_connection import AppiumConnection
from selenium.webdriver.remote.command import Command

from testRunner.library.reporting_command_executor import ReportingCommandExecutor
from testRunner.library import MateClient


class CustomAppiumCommandExecutor(AppiumConnection, ReportingCommandExecutor):
    """Extension of the Appium AppiumConnection (command_executor) class
    Args:
        mate_client (MateClient): Client used to communicate with the Mate Server
        remote_server_addr (str): Remote server address
    """

    def __init__(self, mate_client: MateClient, remote_server_addr: str):
        AppiumConnection.__init__(self, remote_server_addr=remote_server_addr)
        ReportingCommandExecutor.__init__(
            self, mate_client=mate_client, command_executor=self
        )

    def execute(self, command: str, params: dict, skip_reporting: bool = False):
        """Execute an Appium command
        Args:
            command (str): A string specifying the command to execute
            params (dict): A dictionary of named parameters to send with the command as its JSON payload
            skip_reporting (bool): True if command should not be reported to Mate Server, False otherwise
        Returns:
            response: Response returned by the Selenium remote webdriver server
        """
        self.update_known_test_name()

        response = {}

        # Preserve mobile sessions
        if not command == Command.QUIT:
            response = super().execute(command=command, params=params)

        result = response.get("value")

        passed = self.is_command_passed(response=response)

        if not skip_reporting:
            self._report_command(command, params, result, passed)

        return response
