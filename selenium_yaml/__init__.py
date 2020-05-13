"""
Core Module for validating, parsing and automating YAML Selenium Bots

Basic Usage:
    # Todo
"""
from selenium_yaml import exceptions
from selenium_yaml.parsers import YAMLParser
from selenium import webdriver
from loguru import logger
import os


__title__ = 'SeleniumYAML'
__version__ = '1.0.0'
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
                 save_screenshots=False):
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
        """
        # TODO: Improve cases if the path to the file doesn't exist since at the
        # moment it just returns ""
        self._steps = None
        assert yaml_file, "YAML not provided"
        if isinstance(yaml_file, str) and os.path.exists(yaml_file):
            with open(yaml_file) as inf:
                yaml_file = inf.read()

        self.save_screenshots = save_screenshots

        parser = YAMLParser(yaml_file, self)
        if parser.is_valid():
            self._steps = parser.validated_steps
        else:
            raise exceptions.ValidationError(parser.errors)

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

    def perform(self):
        """ Iterates over and performs each step individually """
        logger.debug("Starting step performance sequence...")
        assert self.driver, "Driver must be initialized prior to performance."
        for step_title, step in self.steps.items():
            try:
                step.run_step(save_screenshot=self.save_screenshots)
            except exceptions.StepPerformanceError:
                logger.exception(
                    "Ran into an exception while performing {step_title}",
                    step_title=step_title
                )
                break
        logger.debug("Step performance sequence finished.")
        self.__quit_driver()

    @property
    def steps(self):
        assert self._steps, (
            "Steps must be validated prior to being accessible"
        )
        return self._steps
