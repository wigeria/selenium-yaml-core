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
import json
from loguru import logger
import requests
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

    def perform(self, performance_data):
        """ Navigates the engine to the provided ``url`` """
        driver = self.engine.driver
        driver.get(performance_data["url"])

    class Meta:
        fields = ["url"]


class WaitStep(BaseStep):
    """ Step that explicitly waits for a given amounts of ``seconds``

        The input must contain the following members:
            - ``seconds`` : The number of seconds the driver should wait for
    """
    seconds = fields.IntegerField(required=True)

    def perform(self, performance_data):
        """ Adds an explicit wait for the given ``seconds`` """
        time.sleep(performance_data["seconds"])

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

    def perform(self, performance_data):
        """ Adds an explicit wait for the given ``seconds`` until the given
            ``element`` is visible
        """
        driver = self.engine.driver

        try:
            WebDriverWait(driver, data["seconds"]).until(
                EC.presence_of_element_located(
                    (By.XPATH, performance_data["element"])
                )
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

    def perform(self, performance_data):
        """ Clicks on the given ``element`` """
        driver = self.engine.driver
        el = utils.wait_for_element(driver, performance_data["element"])
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

    def perform(self, performance_data):
        """ Clicks on the given ``element`` """
        driver = self.engine.driver
        el = utils.wait_for_element(driver, performance_data["element"])
        el.send_keys(performance_data["text"])

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

    def perform(self, performance_data):
        """ Selects the given ``option`` in the given ``element`` """
        driver = self.engine.driver
        el = utils.wait_for_element(driver, performance_data["element"])
        select_el = Select(el)
        try:
            select_el.select_by_value(performance_data["option"])
        except sel_exceptions.NoSuchElementException:
            raise exceptions.StepPerformanceError(
                f"The option `{performance_data['option']}` could not be found."
            )

    class Meta:
        fields = ["element", "option"]


class RunBotStep(BaseStep):
    """ Step that takes a path to another Bot's YAML file and runs said
        bot with the same data given to the current bot
    """
    path = fields.FilePathField(required=True)

    def perform(self, performance_data):
        """ Runs the Bot through the ``path`` YAML File """
        engine = selenium_yaml.SeleniumYAML(
            yaml_file=performance_data["path"],
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

    def perform(self, performance_data):
        """ Calls the given URL with the given method and body """
        req = requests.Request(
            url=performance_data["url"],
            method=performance_data["method"],
            data=performance_data["body"],
            headers=performance_data["headers"]
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


class IteratorStep(BaseStep):
    """ Step that takes an ``iterator`` as input and performs all of the given
        ``steps`` for each iterator

        The iterator MUST be an array variable resolved through the
        ``resolvers``
    """
    iterator = fields.ResolvedVariableField(required=True, required_type=list)
    steps = fields.NestedStepsField()

    def perform(self, performance_data):
        """ Iterates over the ``iterator`` array (which should be a list -
            either resolved or by default) and performs each step once per item
        """
        iterator = performance_data["iterator"]
        steps = performance_data["steps"]

        if not isinstance(iterator, list):
            raise exceptions.StepPerformanceError(
                f"The iterator `{iterator}` is not an array can not be "
                "iterated over"
            )

        for item in iterator:
            extra_context = {"current_iterator": item}
            for step_title, step in steps.items():
                try:
                    step.run_step(
                        save_screenshot=self.engine.save_screenshots,
                        extra_context=extra_context
                    )
                except exceptions.StepPerformanceError:
                    logger.exception(
                        "Ran into an exception while performing {step_title}",
                        step_title=step_title
                    )
                    break

    class Meta:
        fields = ["iterator", "steps"]
