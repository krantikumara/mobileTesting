from selenium.webdriver.common.by import By
from testRunner.pageobjects.android.base_page import BasePage


class SettingsPage(BasePage):
    # Define Locators Here
    button_wifi = (By.XPATH, "//*[@text='Wi-Fi']")
    label_wifi_heading = (By.XPATH, "//*[@text='Wi-Fi' and @class='UIAView']")

    # Contants
    label_wifi_title = "Wi-Fi"

    def __init__(self, driver):
        super().__init__(driver)

    def navigate_to_wifi_screen(self):

        if self.driver.assertion.assert_true("Verify if the Wifi option is displayed in Settings screen",
                                             self.is_element_visible(self.button_wifi)):
            self.click(self.button_wifi)

        self.driver.assertion.assert_equal("Verify if the screen title displayed in as expected",
                                             self.get_element(self.label_wifi_heading).text, self.label_wifi_title)