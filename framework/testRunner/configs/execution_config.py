import os

# List of devices to be used for execution
# Value - device-id from command 'adb devices' for Android
# Value - device-udid from command 'instruments -s devices' for iOS
#
# Note: Keep this is as empty [] for cloud devices as device allocations will be dynamic

DEVICE_LIST_ANDROID = ["RFCM700KEPM"]
DEVICE_LIST_IOS = ["00008020-000C15E11188002E"]

PLATFORM = "Android"

# Appium End point
# Appium Host + Port
# If Cloud Devices then corresponding endpoint
APPIUM_SERVER = "http://localhost:4723/wd/hub"

# Desired capabilities
# Dict of desired capabilities for different platforms.
# Platform will be passed as argument to the test-runner and test-runner will refer this Dict for the mapping

DESIRED_CAPS = {
                "iOS": {
                    "udid": DEVICE_LIST_IOS[0],
                    "platformName": "iOS",
                    "platformVersion": "13.4",
                    "automationName": "xcuitest",
                    "newCommandTimeout": 60,
                    "bundleId": "com.apple.Preferences"
                },

                "Android": {
                    "udid": DEVICE_LIST_ANDROID[0],
                    "platformName": "Android",
                    "platformVersion": "9",
                    "automationName": "uiautomator2",
                    "appActivity": "com.experitest.ExperiBank.LoginActivity",
                    "appPackage": "com.experitest.ExperiBank",
                    "app": os.path.join(os.getcwd().split("testRunner")[0], "testRunner", "builds", "EriBank.apk")
                }
            }