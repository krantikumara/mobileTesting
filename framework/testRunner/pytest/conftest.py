import pytest
import json
import os

from testRunner.library import RemoteDriver
import testRunner.configs.execution_config as config
from testRunner.library import LoggingHelper
import uuid


def pytest_addoption(parser):
    parser.addoption("--session", action="store", help="Mate Server Session ID")


@pytest.fixture(scope='session')
def data():
    # To-DO: Keep this path as a config property
    test_data_dir = "testsuites/testData"

    data = {}
    json_files = [file_name for file_name in os.listdir(test_data_dir) if file_name.endswith('.json')]

    for json_file in json_files:
        with open(os.path.join(test_data_dir, json_file)) as config_file:
            data[json_file.replace(".json", "")] = json.load(config_file)

    return data


@pytest.fixture
def driver(request):
    # Mate session ID:
    mate_session_id = request.config.getoption("--session")

    # Initialise logging
    LoggingHelper.configure_logging()

    # Get Desired Caps
    desired_capabilities = config.DESIRED_CAPS[config.PLATFORM]

    # Initialise the Customer Driver Object
    driver = RemoteDriver(config.APPIUM_SERVER, desired_capabilities, mate_session_id)

    yield driver

    driver.close_app()
    # This step is important, Also marks the end of TC
    driver.quit()
