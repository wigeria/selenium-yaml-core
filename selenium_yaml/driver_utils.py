"""
Module containing some common methods used in Selenium bots
"""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from selenium_yaml import exceptions
from selenium_yaml.exceptions import StepPerformanceError


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


def execute_xpath(driver, xpath_sel):
    """ Returns the value of the given ``xpath_sel`` selector through a script
        execution in the ``driver``
    """
    script = """
        var nodes = document.evaluate("%s", document, null, XPathResult.ANY_TYPE, null); 
        var currentNode = nodes.iterateNext();
        var returnValues = [];
        while (currentNode) {
            returnValues.push(currentNode.nodeValue);
            currentNode = nodes.iterateNext();
        };
        return returnValues;
    """ % xpath_sel
    nodes = driver.execute_script(script)
    return nodes
