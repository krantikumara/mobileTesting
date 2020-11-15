import logging

from appium.webdriver.webdriver import WebDriver as AppiumWebDriver
from testRunner.library import LoggingHelper, ReportHelper, MateClient, CustomAppiumCommandExecutor, Reporter
import testRunner.library.assertions as assertions


class RemoteDriver(AppiumWebDriver):
    """Used to create a new Appium Driver instance
    Args:
        desired_capabilities (dict): Automation session desired capabilities and options
    Attributes:
        _desired_capabilities (dict): Automation session desired capabilities and options
        _mate_client (MateClient): client responsible for communicating with the Mate Server
        command_executor (CustomAppiumCommandExecutor): the HTTP command executor used to send commands
    """

    __instance = None

    def __init__(
            self,
            remote_address: str,
            desired_capabilities: dict = None,
            execution_id: str = None
    ):

        if RemoteDriver.__instance is not None:
            raise Exception("A driver session already exists")

        LoggingHelper.configure_logging()

        self._desired_capabilities = desired_capabilities

        self._mate_client: MateClient = MateClient(execution_id)

        AppiumWebDriver.__init__(
            self,
            command_executor=remote_address,
            desired_capabilities=self._desired_capabilities,
        )

        self._mate_client.update_session_id(self.session_id)

        self.command_executor = CustomAppiumCommandExecutor(
            mate_client=self._mate_client,
            remote_server_addr=remote_address,
        )

        # this ensures that mobile-specific commands are also available for our command executor
        self._addCommands()
        RemoteDriver.__instance = self

    @classmethod
    def instance(cls):
        """Returns the singleton instance of the driver object"""
        return RemoteDriver.__instance

    def report(self) -> Reporter:
        """Enables access to the reporting actions from the driver object"""
        return Reporter(self.command_executor)

    @property
    def assertion(self) -> assertions.Assertions:
        """Enables access to the Assertions from the driver object"""
        return assertions.Assertions(self)

    def quit(self):
        """Quits the driver and stops the session with the Mate Server, cleaning up after itself."""
        # Report any left over driver command reports
        self.command_executor.clear_stash()

        # Make instance available again
        RemoteDriver.__instance = None

        try:
            AppiumWebDriver.quit(self)
        except Exception:
            pass

        # Stop the Mate client
        self.command_executor.mate_client.stop()
