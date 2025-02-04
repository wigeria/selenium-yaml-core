"""
Module containing all of the basic steps required for common Selenium use-cases

All of the steps contained here are derived from the BaseStep class and build
their own ``perform`` and ``validate`` methods
"""
import json
import time

import requests
import selenium.common.exceptions as sel_exceptions
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

import selenium_yaml
import selenium_yaml.driver_utils as utils
from selenium_yaml import exceptions, fields, validators
from selenium_yaml.steps import BaseStep


class NavigateStep(BaseStep):
    """ Step that performs a ``driver.get`` action with the given
        ``target_url``

        The input must contain the following members:
            - ``url`` : The URL that the driver should be navigated to
    """
    url = fields.CharField(required=True)

    def perform(self, driver, performance_data, performance_context):
        """ Navigates the engine to the provided ``url`` """
        driver.get(performance_data["url"])

    class Meta:
        fields = ["url"]


class WaitStep(BaseStep):
    """ Step that explicitly waits for a given amounts of ``seconds``

        The input must contain the following members:
            - ``seconds`` : The number of seconds the driver should wait for
    """
    seconds = fields.IntegerField(required=True)

    def perform(self, driver, performance_data, performance_context):
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

    def perform(self, driver, performance_data, performance_context):
        """ Adds an explicit wait for the given ``seconds`` until the given
            ``element`` is visible
        """
        try:
            WebDriverWait(driver, performance_data["seconds"]).until(
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

    def perform(self, driver, performance_data, performance_context):
        """ Clicks on the given ``element`` """
        elem = utils.wait_for_element(driver, performance_data["element"])
        elem.click()

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
    clear = fields.BooleanField(required=True, default=False)

    def perform(self, driver, performance_data, performance_context):
        """ Clicks on the given ``element`` """
        elem = utils.wait_for_element(driver, performance_data["element"])
        if performance_data["clear"]:
            elem.clear()
        elem.send_keys(performance_data["text"])

    class Meta:
        fields = ["element", "text", "clear"]


class SelectOptionStep(BaseStep):
    """ Step that selects the given ``option`` in the given ``select`` element

        The input must contain the following members:
             - ``element`` : XPATH Selector for the select element
             - ``option`` : The option that should be selected
    """
    option = fields.CharField(required=True)
    element = fields.CharField(required=True)

    def perform(self, driver, performance_data, performance_context):
        """ Selects the given ``option`` in the given ``element`` """
        elem = utils.wait_for_element(driver, performance_data["element"])
        select_el = Select(elem)
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
    save_screenshots = fields.BooleanField(required=True, default=False)
    parse_template = fields.BooleanField(required=True, default=False)
    template_context = fields.ResolvedVariableField(
        required=False, required_type=dict)

    def perform(self, driver, performance_data, performance_context):
        """ Runs the Bot through the ``path`` YAML File """
        engine = selenium_yaml.SeleniumYAML(
            yaml_file=performance_data["path"],
            driver=driver,
            save_screenshots=performance_data["save_screenshots"],
            parse_template=performance_data["parse_template"],
            template_context=performance_data["template_context"]
        )
        engine.performance_context = performance_context
        engine.perform(quit_driver=False)

    class Meta:
        fields = ["path", "save_screenshots", "parse_template",
                  "template_context"]


class CallAPIStep(BaseStep):
    """ Step that calls a given API Url with the given method and data
        and returns the response and status code for the Engine to store
    """
    url = fields.CharField(required=True)
    method = fields.CharField(required=True, default="GET",
                              options=["GET", "PUT", "POST"])
    body = fields.DictField(required=False, default={})
    headers = fields.DictField(required=False, default={})

    def perform(self, driver, performance_data, performance_context):
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

    def perform(self, driver, performance_data, performance_context):
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

        step_context = {}
        # TODO: Make each step in the iteration be stored in
        # the `__iter_index__step_title` namespace under this step
        for index, item in enumerate(iterator):
            performance_context["current_iterator"] = item
            performance_context["current_index_zero"] = index
            performance_context["current_index_one"] = index+1
            index = str(index)
            step_context[index] = {}
            for step_title, step in steps.items():
                try:
                    step_context[index][step_title] = step.run_step(
                        driver=driver,
                        performance_context=performance_context,
                        save_screenshots=False
                    )
                except exceptions.StepPerformanceError:
                    logger.exception(
                        "Ran into an exception while performing {step_title}",
                        step_title=step_title
                    )
                    raise
            performance_context.pop("current_iterator")
        return step_context

    class Meta:
        fields = ["iterator", "steps"]


class ConditionalStep(BaseStep):
    """ Conditionally executes the ``steps`` if the xpath ``value`` or stored
        variables matches the ``equals`` field
        Note that the resolved xpath value is ALWAYS a list
        ``negate`` is used to decide whether to use `==` as the operator
        or `!=`
    """
    # The value field could be provided as an xpath selector or as a
    # resolved variable
    value = fields.ResolvedVariableField(required=True, required_type=str)
    equals = fields.ResolvedVariableField(required=True)
    negate = fields.BooleanField(required=True, default=False)
    steps = fields.NestedStepsField()

    def perform(self, driver, performance_data, performance_context):
        """ Executes all of the nested steps if the given ``value``
            (resolved/xpath) is equal to the given ``equals`` field
        """
        value = performance_data["value"]
        equals = performance_data["equals"]
        steps = performance_data["steps"]

        # Checking if value is a resolved variable - if not, it's resolved
        # as xpath; we know that it isn't resolved if it's the same as the
        # value in ``validated_data`` since the value is resolved through
        # ``get_performance_data()`` in ``run_step()``
        if value == self.validated_data["value"]:
            logger.debug(f"Value: {value}, Equals: {equals}")
            try:
                xpath_result = utils.execute_xpath(driver, value)
                # Converting the ``equals`` value to a list, since
                # resolved xpath is always a list
                if xpath_result:
                    value = xpath_result
                    if not isinstance(equals, list):
                        equals = [equals]
            except sel_exceptions.JavascriptException:
                pass
        # Converting both ``value`` and ``equals`` to sets if they're arrays
        if isinstance(value, list) and isinstance(equals, list):
            value = set(value)
            equals = set(equals)

        if performance_data["negate"]:
            condition = value != equals
            operator = "!="
        else:
            condition = value == equals
            operator = "=="

        if condition:
            logger.debug(f"{value} {operator} {equals}; executing sub-steps.")
            step_context = {"success": True}
            for step_title, step in steps.items():
                try:
                    step_context[step_title] = step.run_step(
                        driver=driver,
                        performance_context=performance_context,
                        save_screenshots=False
                    )
                except exceptions.StepPerformanceError:
                    logger.exception(
                        "Ran into an exception while performing {step_title}",
                        step_title=step_title
                    )
                    break
            return step_context
        else:
            logger.debug(f"{value} {operator} {equals}; skipping sub-steps.")
            return {"success": False}

    class Meta:
        fields = ["value", "equals", "steps", "negate"]


class StoreXpathStep(BaseStep):
    """ Step for storing the nodes returned by a given xpath ``selector``
        into the engine's performance data in a given ``variable`` so that
        it can later be accessed as ``Step Name__<variable>``

        Note that the ``selector`` is not validated as Xpath at the moment,
        so it should be used with care

        If ``select_first`` is provided as True, only the first xpath return
        value is stored - otherwise the full return value is stored as an array
    """
    selector = fields.CharField(required=True)
    select_first = fields.BooleanField(required=True, default=False)
    variable = fields.CharField(required=True)

    def perform(self, driver, performance_data, performance_context):
        """ Returns the xpath selector's value so that it gets stored in
            the engine performance data
        """
        selector = performance_data["selector"]
        variable = performance_data["variable"]
        select_first = performance_data["select_first"]

        value = utils.execute_xpath(driver, selector)

        if select_first:
            value = value[0] if value else None

        return {
            variable: value
        }

    class Meta:
        fields = ["selector", "select_first", "variable"]


class StorePageUrlStep(BaseStep):
    """ Step for storing the current page url into a ``Step Title__url``
        variable so that it can be accessed later on
    """
    def perform(self, driver, performance_data, performance_context):
        """ Returns the current driver URL for later access """
        return {
            "url": driver.current_url
        }

    class Meta:
        fields = []
