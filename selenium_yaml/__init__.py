"""
Core Module for validating, parsing and automating YAML Selenium Bots

Basic Usage:
    # Todo
"""
import os

from collections import OrderedDict
from jinja2 import Template
from loguru import logger
from random import uniform
from selenium import webdriver
import time

from selenium_yaml import exceptions
from selenium_yaml.parsers import YAMLParser

__title__ = 'SeleniumYAML'
__version__ = '1.0.97'
__author__ = 'Abhishek Verma'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2020 Abhishek Verma'


class SeleniumYAML:
    """ Backend for converting YAML into Selenium Bots by converting each
        item in the `steps` array into an individual "Step"
    """
    @logger.catch(reraise=True)
    def __init__(self, yaml_file=None, driver_class=webdriver.Chrome,
                 driver_options=None, driver_executable_path='chromedriver',
                 save_screenshots=False, parse_template=False,
                 template_context=None, driver=None):
        """ Creates a new instance of the SeleniumYAML parser and validates the
            provided yaml as well as initializes the driver (if not provided)

            ``yaml_file``, if specified, must be an open File-like object or a
            string path to a YAML file with valid YAML containing the steps
            that will be used for creating the automation; one of either
            ``yaml_file`` or ``yaml_string`` must be provided

            ``driver_class``, if specified, must be a valid Selenium webdriver
            class (either a driver class in selenium.webdriver or a subclass of
            the same) - defaults to selenium.webdriver.Chrome

            ``driver_options``, if specified, must be a set of Selenium options
            compatible with the active ``driver_class``

            ``driver_executable_path``, if specified, must be the path to the
            driver for the active ``driver_class``

            ``save_screenshots``, if specified, is used to take screenshots of
            each step after it's executed or if it runs into an exception

            ``parse_template``, if True, parses the given YAML File as a Jinja2
            template prior to parsing it through the YAMLParser

            ``template_context`` is passed to Jinja2's Template.render method
            as context if ``parse_template`` is True

            ``driver``, if present, is used as the driver class for the engine;
            this is used in case you want the bot to act on an already running
            driver
        """
        # TODO: Improve cases if the path to the file doesn't exist since at
        # the moment it just returns ""
        assert yaml_file, "YAML not provided"
        if isinstance(yaml_file, str) and os.path.exists(yaml_file):
            with open(yaml_file, encoding="UTF-8") as inf:
                yaml_file = inf.read()

        # These are set as class attributes so that they can be passed to any
        # bots connected via `run_bot` steps
        self.parse_template = parse_template
        self.template_context = template_context
        if parse_template:
            template_context = template_context or {}
            template = Template(yaml_file)
            yaml_file = template.render(template_context)

        parser = YAMLParser(yaml_file)
        if parser.is_valid():
            self.steps = parser.validated_steps
            self.title = parser.bot_title
            self.exception_steps = parser.validated_exception_steps
        else:
            raise exceptions.ValidationError(parser.errors)

        self.save_screenshots = save_screenshots
        self.performance_context = OrderedDict()

        if isinstance(driver, webdriver.remote.webdriver.WebDriver):
            self.driver = driver
        else:
            self.driver_class = driver_class
            self.driver_options = driver_options
            self.driver_executable_path = driver_executable_path
            self.driver = self.__initialize_driver()

    def __initialize_driver(self):
        """ Initializes a Selenium Webdriver with the given class

            ``driver_class`` is a driver class in selenium.webdriver, or
            is derived from the same

            ``driver_options`` is a a driver options class that's compatible
            with the provided ``driver_class``

            ``driver_executable_path`` is the path to the driver executable
            compatible with the provided driver classs
        """
        return self.driver_class(options=self.driver_options,
                                 executable_path=self.driver_executable_path)

    def __quit_driver(self):
        """ Quits the driver on the instance, and sets the attribute to
            Null
        """
        assert self.driver, "Driver is not initialized."
        self.driver.quit()
        self.driver = None

    @logger.catch(reraise=True)
    def run_exception_steps(self):
        """ Runs the exception steps in order with the provided step data

            Note that any exceptions on these are simply logged and otherwise
            ignored. For that reason, any exception tests must be tested
            carefully themselves

        """
        for step_title, exception_step in self.exception_steps.items():
            try:
                step_data = exception_step.run_step(
                    self.driver,
                    self.performance_context,
                    save_screenshots=False)
            except:
                logger.exception(
                    "Ran into an exception while performing exception " +
                    "step: {step_title}",
                    step_title=step_title
                )
            else:
                self.performance_context[step_title] = step_data

    def perform(self, quit_driver=True, dynamic_delay_range=None):
        """ Iterates over and performs each step individually
            If ``quit_driver`` is False, it doesn't quit the driver after
            performance

            If ``dynamic_delay_range`` is provided as a tuple of
            `(min, max)` seconds, a random delay between that range is added
            between each step's execution
        """
        logger.debug("Starting step performance sequence...")
        assert self.driver, "Driver must be initialized prior to performance."
        screenshots_path = os.path.join(os.getcwd(), "screenshots", self.title)
        for step_title, step in self.steps.items():
            try:
                step_data = step.run_step(
                    self.driver,
                    self.performance_context,
                    save_screenshots=self.save_screenshots,
                    screenshots_path=screenshots_path)
            except exceptions.StepPerformanceError:
                logger.exception(
                    "Ran into an exception while performing {step_title}",
                    step_title=step_title
                )
                self.run_exception_steps()
                break
            except:
                self.run_exception_steps()
                raise
            self.performance_context[step_title] = step_data
            if dynamic_delay_range:
                time.sleep(uniform(*dynamic_delay_range))
        logger.debug("Step performance sequence finished.")
        if quit_driver:
            self.__quit_driver()
