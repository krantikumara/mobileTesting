import os
import pytest
import time

from testRunner.pageobjects.ios import SettingsPage


@pytest.mark.Sanity
@pytest.mark.Network
def test_wifi_navigation(driver):
    SettingsPage(driver).navigate_to_wifi_screen()


@pytest.mark.Network
def test_wifi_enable(driver):
    SettingsPage(driver).navigate_to_wifi_screen()
