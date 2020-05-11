"""
Module containing some common methods used in Selenium bots
"""
from selenium_yaml.exceptions import StepPerformanceError
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


def wait_for_element(driver, xpath_sel, timeout=10):
    """ Waits for the element identified by the given ``xpath_sel`` for
        ``timeout`` seconds
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath_sel))
        )
    except TimeoutException:
        raise exceptions.StepPerformanceError(
            "Could not find the element identified by " +
            f"`{xpath_sel}` within `{timeout}` seconds."
        )
