from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from subprocess import Popen
import os
from testRunner.library.pytest_helper import PyTestHelper
import time


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class TestRunner:
    def __init__(self):
        self.helper = PyTestHelper(os.path.join(os.getcwd(), "testRunner", "pytest"))
        self.execution_proc = []

    def get_tests(self, suite):
        suite = suite.split(":")[0]
        print(f"get_tests() called with arg {suite}")
        return self.helper.get_tests(suite)

    def get_test_suites(self):
        print(f"get_test_suites() called")
        return self.helper.get_markers()

    def run_test(self, test):
        # To-Do - We need to track tests being triggered. And should block user from running tests when there are
        # already tests running (on the same device). device specific locks maybe.
        # We also need to a add a is_alive mechanism such that execution states are reported to Mate Client

        cmd = None
        # To-Do - Currently using a check for .py extension in arg to identify if the request is to run a specific
        # test, we need to improve this by implementing a dedicated method for independent tests
        if ".py" in test:
            cmd = ["python", "run.py", "--run", "--test", test]
        else:
            # if the arg does not have .py in it then it is assumed to be a suite -> Improve this by having a
            # dedicated method for test suites
            if test in self.get_test_suites():
                cmd = ["python", "run.py", "--run", "--marker", test.split(":")[0]]
        if cmd:
            proc = Popen(cmd, cwd=os.path.join(os.getcwd(), "testRunner"))
            self.execution_proc.append(proc)
            return True
        else:
            return False


# Create server
print("Starting XMLRPC Server at localhost:8001/RPC2")
with SimpleXMLRPCServer(('localhost', 8001),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    # Register an instance; all the methods of the instance are
    # published as XML-RPC methods

    server.register_instance(TestRunner())

    # Run the server's main loop
    server.serve_forever()
