from selenium.webdriver.common.by import By
from testRunner.pageobjects.android.base_page import BasePage


class LoginPage(BasePage):
    # Define Locators Here
    textfield_username = (By.ID, "usernameTextField")
    textfield_password = (By.ID, "passwordTextField")
    button_dologin = (By.ID, "loginButton")

    def __init__(self, driver):
        super().__init__(driver)

    def login_as(self, username: str, password: str):

        if self.driver.assertion.assert_true("Verify if the username field is displayed",
                                             self.is_element_visible(self.textfield_username), True):
            self.get_element(self.textfield_username).send_keys(username)

        if self.driver.assertion.assert_true("Verify if the password field is displayed",
                                             self.is_element_visible(self.textfield_password), True):
            self.get_element(self.textfield_password).send_keys(password)

        if self.driver.assertion.assert_true("Verify if the login button is displayed",
                                             self.is_element_visible(self.button_dologin), True):
            self.click(self.button_dologin)
