from inspect import getframeinfo, stack


class Assertions:
    def __init__(self, driver):
        self.driver = driver

    def assert_equal(self, description, actual, expected, screenshot=True):
        message = f"Actual: {actual} \nExpected: {expected} \n"
        caller = getframeinfo(stack()[1][0])
        message += "%s:%d" % (caller.filename.split("testRunner")[1], caller.lineno)

        if actual == expected:

            self.driver.report().step(description=description,
                                      message=message,
                                      screenshot=True, passed=True)
            return True
        else:
            self.driver.report().step(description=description,
                                      message=message,
                                      screenshot=True, passed=False)
            return False

    def assert_true(self, description, expression, screenshot=True):
        caller = getframeinfo(stack()[1][0])
        message = "%s:%d" % (caller.filename.split("testRunner")[1], caller.lineno)
        if expression:
            self.driver.report().step(description=description,
                                      screenshot=True,
                                      message=message,
                                      passed=True)
            return True
        else:
            self.driver.report().step(description=description,
                                      screenshot=True,
                                      message=message,
                                      passed=False)
            return False