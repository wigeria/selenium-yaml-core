"""
Contains tests for the steps included in steps.core_steps
"""
from selenium_yaml import SeleniumYAML
from selenium_yaml.steps import core_steps as steps
from selenium import webdriver
import pytest
import os
import time
import requests_mock
import json


HTML_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "html_files")


def get_html_furl(fname):
    """ Returns the file url to the given html file's name in the
        tests/html_files dir
    """
    return "file:///" + os.path.join(HTML_DIR, fname).replace("\\", "/")


def setup_driver():
    """ Returns a Chrome webdriver instance for use in steps """
    return webdriver.Chrome()


class TestCoreSteps:
    """ Contains tests for all steps in steps.core_steps """
    def test_navigate_step(self):
        """ Tests that the navigate step successfully navigates the user to a
            given URL
        """
        step_data = {
            "url": get_html_furl("test_form.html")
        }
        step = steps.NavigateStep(step_data, "Navigate To File")
        assert step.is_valid() is True

        driver = setup_driver()
        step.run_step(driver, {})
        assert driver.current_url == step_data["url"]
        driver.quit()

    def test_type_step(self):
        """ Tests that the value of an input element changes after being typed
            into
        """
        url = get_html_furl("test_form.html")
        step_data = {
            "text": "test@email.com",
            "element": "//input[@name='email']",
            "clear": True
        }
        step = steps.TypeTextStep(step_data, "Type Email")
        assert step.is_valid() is True

        driver = setup_driver()
        driver.get(url)
        step.run_step(driver, {})
        assert (
            driver.find_element_by_name("email").get_attribute("value") ==
            step_data["text"]
        )
        driver.quit()

    def test_click_step(self):
        """ Tests that an element can be clicked successfully through the
            Click step
        """
        url = get_html_furl("test_form.html")
        step_data = {
            "element": "//button[@id='submit']"
        }
        step = steps.ClickElementStep(step_data, "Click Submit")
        assert step.is_valid() is True

        driver = setup_driver()
        driver.get(url)
        step.run_step(driver, {})
        assert driver.find_element_by_id("clicked-successfully")
        driver.quit()

    def test_select_step(self):
        """ Tests that the value of a select element changes correctly after
            an option is selected
        """
        url = get_html_furl("test_form.html")
        option = "opt2"
        step_data = {
            "element": "//select",
            "option": option
        }
        step = steps.SelectOptionStep(step_data, "Select Option")
        assert step.is_valid() is True

        driver = setup_driver()
        driver.get(url)
        step.run_step(driver, {})
        assert (
            driver.find_element_by_id("select").get_attribute("value") ==
            option
        )
        driver.quit()

    def test_make_request_step(self, requests_mock):
        """ Tests that the make-request step correctly makes a request with the
            given data and returns the status-code and content
        """
        url = "http://test.com/1/"
        requests_mock.get(url, text=json.dumps({"id": 100}))
        step_data = {
            "method": "GET",
            "url": url,
            "body": {},
            "headers": {}
        }
        step = steps.CallAPIStep(step_data, "Make Request")
        assert step.is_valid() is True

        driver = setup_driver()
        step_data = step.run_step(driver, {})
        assert step_data["status_code"] == 200
        assert step_data["content"] == {"id": 100}

    def test_iterator_step(self):
        """ Tests that the iterator step iterates over given steps and runs
            each sequentially
        """
        url = get_html_furl("test_form.html")
        step_data = {
            "iterator": ["1", "2", "3"],
            "steps": [
                {
                    "title": "Nav1",
                    "action": "navigate",
                    "url": url + "?email=Test1"
                },
                {
                    "title": "Nav2",
                    "action": "navigate",
                    "url": url + "?email=Test2"
                }
            ]
        }
        step = steps.IteratorStep(step_data, "Iterator Step")
        assert step.is_valid() is True

        driver = setup_driver()
        driver.get(url)
        step.run_step(driver, {})
        assert driver.current_url == url + "?email=Test2"
        driver.quit()

    def test_conditional_step(self):
        """ Tests that the conditional step only runs the sub-steps when a
            condition is passed
        """
        url = get_html_furl("test_form.html")
        step_data = {
            "value": "5",
            "equals": "5",
            "steps": [
                {
                    "title": "Nav1",
                    "action": "navigate",
                    "url": url
                }
            ]
        }
        step = steps.ConditionalStep(step_data, "Conditional Step")
        assert step.is_valid() is True, step.errors

        driver = setup_driver()
        driver.get(url)
        step.run_step(driver, {})
        assert driver.current_url == url
        driver.quit()

        step_data["equals"] = "3"
        driver = setup_driver()
        driver.get(url)
        step.run_step(driver, {})
        assert driver.current_url == url
        driver.quit()
