import logging
import socket
import requests
import threading
import queue
import uuid
import testRunner.configs.framework_config as config
from testRunner.library.reporters import StepReport, CustomTestReport, DriverCommandReport

from urllib.parse import urljoin
from enum import Enum, unique
from requests import HTTPError


class MateClient:
    """Client used to communicate with the MATE Server
    Args:

    Attributes:
        _remote_address (str): The mate-server endpoint
        _queue (queue.Queue): queue holding reports to be sent to Mate Server in separate thread
    """

    REPORTS_QUEUE_TIMEOUT = 10

    def __init__(self, execution_id):
        self._remote_address = config.MATE_SERVER_ENDPOINT
        self._queue = queue.Queue()
        self._running = True
        self._session_id = None
        self._execution_id = execution_id
        self._reporting_thread = threading.Thread(target=self.__report_worker, daemon=True)
        self._reporting_thread.start()

    @property
    def session_id(self):
        """Getter for the Appium session ID"""
        return self._session_id

    def update_session_id(self, session_id):
        self._session_id = session_id

    def report_driver_command(self, driver_command_report: DriverCommandReport):
        """Sends command report to the Mate Server
        Args:
            driver_command_report: object containing the driver command to be reported
        """

        queue_item = QueueItem(
            report_as_json=driver_command_report.to_json(),
            url=urljoin(self._remote_address, Endpoint.ReportDriverLog.value),execution_id=self._execution_id)

        self._queue.put(queue_item, block=False)

    def report_step(self, step_report: StepReport):
        """Sends step report to the Mate Server
        Args:
            step_report (StepReport): object containing the step to be reported
        """

        queue_item = QueueItem(
            report_as_json=step_report.to_json(),
            url=urljoin(self._remote_address, Endpoint.ReportStep.value),execution_id=self._execution_id)

        self._queue.put(queue_item, block=False)

    def report_test(self, test_report: CustomTestReport):
        """Sends test report to the Mate Server
        Args:
            test_report (CustomTestReport): object containing the test to be reported
        """

        queue_item = QueueItem(
            report_as_json=test_report.to_json(),
            url=urljoin(self._remote_address, Endpoint.ReportTest.value),execution_id=self._execution_id)

        self._queue.put(queue_item, block=False)

    def stop(self):
        """Send all remaining report items in the queue to Mate Server"""
        # Send a stop signal to the thread worker
        self._running = False

        # Send a final, empty, report to the queue to ensure that
        # the 'running' condition is evaluated one last time
        self._queue.put(
            QueueItem(report_as_json=None, url=None, execution_id=self._execution_id), block=False)

        # Wait until all items have been reported or timeout passes
        self._reporting_thread.join(timeout=self.REPORTS_QUEUE_TIMEOUT)
        if self._reporting_thread.is_alive():
            # Thread is still alive, so there are unreported items
            logging.warning(f"There are {self._queue.qsize()} unreported items in the queue")

    def __report_worker(self):
        """Worker method that is polling the queue for items to report"""
        while self._running or self._queue.qsize() > 0:

            item = self._queue.get()
            if isinstance(item, QueueItem):
                item.send()
            else:
                logging.warning(
                    f"Unknown object of type {type(item)} found on queue, ignoring it.."
                )
            self._queue.task_done()


class QueueItem:
    """Helper class representing an item to be reported
    Args:
        report_as_json (dict): JSON payload representing the item to be reported
        url (str): Mate-Server endpoint the payload should be POSTed to
    Attributes:
        _report_as_json (dict): JSON payload representing the item to be reported
        _url (str): Mate Server endpoint the payload should be POSTed to
    """

    def __init__(self, report_as_json: dict, url: str, execution_id: str):
        self._report_as_json = report_as_json
        self._url = url
        self._execution_id = execution_id

    def send(self):
        """Send a report item to the Mate Server"""
        if self._report_as_json is None and self._url is None:
            # Skip empty queue items put in the queue on stop()
            return

        with requests.Session() as session:
            response = session.post(
                self._url,
                headers={"Content-Type": "application/json", "execution_id": self._execution_id},
                json=self._report_as_json,
            )
            try:
                response.raise_for_status()
            except HTTPError:
                logging.error(
                    f"Reporting to Mate-Server returned an HTTP {response.status_code}"
                )
                logging.error(f"Response from Mate-Server: {response.text}")


@unique
class Endpoint(Enum):
    ReportTest = "mate/api/execution/report_test"
    ReportStep = "mate/api/execution/report_execution_step"
    ReportDriverLog = "mate/api/execution/report_driver_log"