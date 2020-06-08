"""
Contains tests for the steps included in steps.core_steps
"""
from selenium_yaml import SeleniumYAML
from selenium_yaml.steps import core_steps as steps
from selenium_yaml.steps.registered_steps import REGISTERED_STEPS
import pytest
import os
import yaml


class TestCoreSteps:
    """ Contains tests for all steps in steps.core_steps """
    HTML_DIR = None

    @classmethod
    def setup_class(cls):
        """ Sets the path to the tests/html_files directory as a class
            attribute prior to the test-sequence
        """
        cls.HTML_DIR = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "html_files")

    def test_navigate_step(self):
        """ Tests that the navigate step successfully navigates the user to a
            given URL
        """
        step_data = {
            "title": "Navigate Step Test",
            "steps": [{
                "title": "Navigate to file",
                "action": "navigate",
                "url": "file:///" + os.path.join(
                    self.HTML_DIR, "test_form.html")
            }]
        }
        engine = None
