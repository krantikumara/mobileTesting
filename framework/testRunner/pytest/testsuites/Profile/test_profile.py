import os
import pytest
import time

from testRunner.pageobjects.android import LoginPage


@pytest.mark.Sanity
@pytest.mark.Login
def test_login(driver, data):
    LoginPage(driver).login_as(data["profileData"]["username"], data["profileData"]["password"])


@pytest.mark.Login
def test_login_with_username(driver, data):
    LoginPage(driver).login_as(data["profileData"]["username"], data["profileData"]["password"])


@pytest.mark.Login
def test_login_with_valid_username(driver, data):
    LoginPage(driver).login_as(data["profileData"]["username"], data["profileData"]["password"])
