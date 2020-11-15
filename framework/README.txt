Setup instructions for MAC/Linux
#########################################################

#########################################################
#Python packages required                               #
#########################################################
command: python3 -m pip install py4web --no-cache-dir
command: python3 -m pip install Appium-Python-Client
command: python3 -m pip install requests
command: python3 -m pip install pytest
command: python3 -m pip install pytest-xdist
#########################################################

#########################################################
#Initial steps                                          #
#########################################################
#Setup Python virtual env (Required to be done only once during initial project setup)
command: python3 -m venv <path to framework dir>
command: source <path to framework dir>/bin/activate

#Setup PYTHONPATH
command: export PYTHONPATH=<path to framework>:<path to framework>/testRunner:
example: export PYTHONPATH=:~/Downloads/framework:~/Downloads/framework/testRunner:
#########################################################

#########################################################
#Initialise the py4web server                           #
#########################################################
Step1:
command: py4web set_password
<Enter a password for accessing py4web development interface. Need to be done only once>

Step2:
command: py4web run apps
<This will start the py4web server and our MATE Application. Keep this terminal running>

# Make sure Appium Server is running and accessible (This could be the cloud one or local instance)
# Appium URL should be configured in testRunner/configs/execution_config.py: APPIUM_SERVER
# Devices can be configured in testRunner/configs/execution_config.py: DEVICE_LIST

#########################################################

#########################################################
#Running test - From Command Line                       #
#########################################################
Step1:
#Navigate to the testRunner directory and open a new Terminal
command: cd testRunner

#Trigger tests
command: python3 run.py [options]
  -h, --help       show this help message and exit
  --fetch_markers  Get list of available testsuites
  --fetch_tests    Get list of available tests
  --marker MARKER  Marker for the tests to run/collect
  --run            Run tests

command: python3 run.py --fetch_markers
Output: Prints list of test suites based on markers

command: python3 run.py --fetc_tests --marker <suite-name>
Output: Prints list of test cases for given marker (suite)

command: python3 run.py --run --marker <suite-name>

#########################################################

#########################################################
#Running test - From UI                                 #
#########################################################
Step1: Start the XMLRPC Server
command: python run.py (from framework/run.py)
Note: Keep this open as the Mate Server will communicate with this XMLRPC-Server to query test suite information and run
 tests

Step1:
#Navigate to the Mate Server Dashboard
http://127.0.0.1:8000/mate

# Dashboard will populate the test suites fetched from TestRunner XMLRPC end-point based on Markers
# Select the suite to run -> Click Run

#########################################################