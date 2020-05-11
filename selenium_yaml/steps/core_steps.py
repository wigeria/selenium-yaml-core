"""
Module containing all of the basic steps required for common Selenium use-cases

All of the steps contained here are derived from the BaseStep class and build
their own ``perform`` and ``validate`` methods
"""
from selenium_yaml import exceptions
from selenium_yaml import fields
from selenium_yaml.steps import BaseStep
import selenium_yaml.driver_utils as utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import selenium.common.exceptions as sel_exceptions
import time


class NavigateStep(BaseStep):
    """ Step that performs a ``driver.get`` action with the given
        ``target_url``

        The input must contain the following members:
            - ``url`` : The URL that the driver should be navigated to
    """
    url = fields.CharField(required=True)

    def perform(self):
        """ Navigates the engine to the provided ``url`` """
        driver = self.engine.driver
        data = self.validated_data

        driver.get(data["url"])

    class Meta:
        fields = ["url"]


class WaitStep(BaseStep):
    """ Step that explicitly waits for a given amounts of ``seconds``

        The input must contain the following members:
            - ``seconds`` : The number of seconds the driver should wait for
    """
    seconds = fields.IntegerField(required=True)

    def perform(self):
        """ Adds an explicit wait for the given ``seconds`` """
        time.sleep(self.validated_data["seconds"])

    class Meta:
        fields = ["seconds"]


class WaitForElementStep(BaseStep):
    """ Step that explicitly waits for a given amounts of ``seconds`` until
        the given ``element`` is clickable

        The input must contain the following members:
             - ``seconds`` : The number of seconds the driver should wait for
             - ``element`` : XPATH Selector for the element to wait for
    """
    seconds = fields.IntegerField(required=True)
    element = fields.CharField(required=True)

    def perform(self):
        """ Adds an explicit wait for the given ``seconds`` until the given
            ``element`` is visible
        """
        driver = self.engine.driver
        data = self.validated_data

        try:
            WebDriverWait(driver, data["seconds"]).until(
                EC.presence_of_element_located((By.XPATH, data["element"]))
            )
        except sel_exceptions.TimeoutException:
            raise exceptions.StepPerformanceError(
                "Could not find element in time."
            )

    class Meta:
        fields = ["seconds", "element"]


class ClickElementStep(BaseStep):
    """ Step that clicks on the given ``element``

        The input must contain the following members:
             - ``element`` : XPATH Selector for the element to click on
    """
    element = fields.CharField(required=True)

    def perform(self):
        """ Clicks on the given ``element`` """
        driver = self.engine.driver
        data = self.validated_data
        el = utils.wait_for_element(driver, data["element"])
        el.click()

    class Meta:
        fields = ["element"]


class TypeTextStep(BaseStep):
    """ Step that adds the given ``text`` to the given ``element``

        The input must contain the following members:
             - ``element`` : XPATH Selector for the element to add text to
             - ``text`` : The text that should be entered into the element
    """
    text = fields.CharField(required=True)
    element = fields.CharField(required=True)

    def perform(self):
        """ Clicks on the given ``element`` """
        driver = self.engine.driver
        data = self.validated_data
        el = utils.wait_for_element(driver, data["element"])
        el.send_keys(data["text"])

    class Meta:
        fields = ["element", "text"]


class SelectOptionStep(BaseStep):
    """ Step that selects the given ``option`` in the given ``select`` element

        The input must contain the following members:
             - ``element`` : XPATH Selector for the select element
             - ``option`` : The option that should be selected
    """
    option = fields.CharField(required=True)
    element = fields.CharField(required=True)

    def perform(self):
        """ Selects the given ``option`` in the given ``element`` """
        driver = self.engine.driver
        data = self.validated_data
        el = utils.wait_for_element(driver, data["element"])
        select_el = Select(el)
        try:
            select_el.select_by_value(data["option"])
        except sel_exceptions.NoSuchElementException:
            raise exceptions.StepPerformanceError(
                f"The option `{data['option']}` could not be found."
            )

    class Meta:
        fields = ["element", "option"]
