"""
Module containing all of the basic steps required for common Selenium use-cases

All of the steps contained here are derived from the BaseStep class and build
their own ``perform`` and ``validate`` methods
"""
import selenium_yaml
from selenium_yaml import exceptions
from selenium_yaml import fields
from selenium_yaml.steps import BaseStep
import selenium_yaml.driver_utils as utils
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import selenium.common.exceptions as sel_exceptions
import time
import json


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
        data = self.performance_data

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
        time.sleep(self.performance_data["seconds"])

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
        data = self.performance_data

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
        data = self.performance_data
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
        data = self.performance_data
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
        data = self.performance_data
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


class RunBotStep(BaseStep):
    """ Step that takes a path to another Bot's YAML file and runs said
        bot with the same data given to the current bot
    """
    path = fields.FilePathField(required=True)

    def perform(self):
        """ Runs the Bot through the ``path`` YAML File """
        data = self.performance_data
        engine = selenium_yaml.SeleniumYAML(
            yaml_file=data["path"],
            driver=self.engine.driver,
            save_screenshots=self.engine.save_screenshots,
            parse_template=self.engine.parse_template,
            template_context=self.engine.template_context
        )
        engine.perform(quit=False)

    class Meta:
        fields = ["path"]


class CallAPIStep(BaseStep):
    """ Step that calls a given API Url with the given method and data
        and returns the response and status code for the Engine to store
    """
    url = fields.CharField(required=True)
    method = fields.CharField(required=True, default="GET",
                              options=["GET", "PUT", "POST"])
    body = fields.DictField(required=False, default={})
    headers = fields.DictField(required=False, default={})

    def perform(self):
        """ Calls the given URL with the given method and body """
        data = self.performance_data
        req = requests.Request(
            url=data["url"],
            method=data["method"],
            data=data["body"],
            headers=data["headers"]
        )
        r = req.prepare()
        session = requests.Session()
        response = session.send(r)

        status_code = response.status_code
        try:
            content = response.json()
        except json.decoder.JSONDecodeError:
            content = response.content

        return {
            "status_code": status_code,
            "content": content
        }

    class Meta:
        fields = ["url", "method", "body", "headers"]
