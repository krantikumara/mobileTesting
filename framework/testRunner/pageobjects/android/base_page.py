from selenium.webdriver.common.by import By
from testRunner.library import RemoteDriver


class BasePage:

    def __init__(self, driver:RemoteDriver):
        self.driver = driver

    def is_element_visible(self, locator):
        try:
            element = self.driver.find_element(*locator)
            return element.is_displayed()
        except Exception as exp:
            print("Error in is_element_visible()")
            return False

    def get_element(self, locator):
        try:
            return self.driver.find_element(*locator)
        except Exception as exp:
            print("Error in get_element()")
            return False

    def click(self, locator):
        try:
            return self.get_element(locator).click()
        except Exception as exp:
            print("Error in click()")
            return False
