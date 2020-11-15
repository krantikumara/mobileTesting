from urllib.parse import urljoin
import uuid
import argparse
from requests import HTTPError, Session
import subprocess
import sys, os
from testRunner.configs import framework_config
from testRunner.library.pytest_helper import PyTestHelper

# MATE Server end point for registering execution
REGISTER_EXECUTION_PATH = urljoin(framework_config.MATE_SERVER_ENDPOINT, 'mate/api/execution/get_execution_id')

sys.path.append(os.path.abspath(os.getcwd()))


def register_execution_id(path, id):
    with Session() as session:
        response = session.post(
            REGISTER_EXECUTION_PATH,
            headers={"Content-Type": "application/json"},
            json={"execution_id": str(id)})
        try:
            response.raise_for_status()
        except HTTPError:
            print(f"Registering to Mate-Server returned an HTTP {response.status_code}")

    return response.json()["execution_id"]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pytest wrapper!')
    parser.add_argument('--fetch_markers', action='store_true', help='Get list of available testsuites')
    parser.add_argument('--fetch_tests', action='store_true', help='Get list of available tests')
    parser.add_argument('--marker', help='Marker for the tests to run/collect')
    parser.add_argument('--run', action='store_true', help='Run tests')
    parser.add_argument('--test', help='Specific test to run')
    args = parser.parse_args()

    helper = PyTestHelper(os.path.join(os.getcwd(), "pytest"))

    if args.fetch_markers:
        print(*helper.get_markers(), sep="\n")
        sys.exit(0)

    if args.fetch_tests:
        # If marker is provided - get only tests with the specific marker
        if args.marker:
            print(*helper.get_tests(args.marker), sep="\n")
            sys.exit(0)
        print(*helper.get_tests(), sep="\n")
        sys.exit(0)

    if args.run:
        print("Generating execution-id...")
        EXECUTION_ID = str(uuid.uuid4())
        print(f"Initializing session with MATE Server with Execution ID : {EXECUTION_ID}")
        if not register_execution_id(REGISTER_EXECUTION_PATH, EXECUTION_ID):
            print("Error Registering Execution...Exit!")
            sys.exit(1)
        # If marker is provided - run only tests with the specific marker
        if args.marker:
            output, error = helper.run_tests(EXECUTION_ID, marker=args.marker)
        elif args.test:
            output, error = helper.run_tests(EXECUTION_ID, test=args.test)
        else:
            output, error = helper.run_tests(EXECUTION_ID)

        print("Execution Output:")
        print(output)
        if error:
            print("Execution Errors:")
            print(error)
        print("Execution Completed!!!")
        print("Check results at : http://127.0.0.1:8000/mate")
        sys.exit(0)








