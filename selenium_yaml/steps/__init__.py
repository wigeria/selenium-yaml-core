"""
Steps Package containing all of the in-built selenium-yaml Steps along with
a BaseStep that can be used for building customized Steps

Basic Example:
    # Todo
"""
import os
import types

from loguru import logger

import selenium_yaml.exceptions as exceptions
from selenium_yaml.steps import resolvers


class BaseStep:
    """ A Base class that all selenium-yaml Steps should derive from

        All classes that derive from this are resolved as valid steps by the
        steps_parser.SeleniumStepsParser class

        The methods that must be overridden include the following:
            - ``validate`` : Should raise exceptions.ValidationError with a
                meaningful message in case of any validation issues

            - ``perform`` : Perform the actual step on the selenium webdriver
                instance

        Each derived step must be registered using
        ``steps.registered_steps.register_step`` with a friendly name that will
        be used by the parsers

        Each derived step must also have a Meta class that has a `fields`
        attribute containing an iterable of attribute names on the step
        which will point to the fields that need to be validated
    """
    def __init__(self, step_data=None, title=None):
        """ Creates a new instance of the step and sets attributes that will
            be modified during validation so that the step can be performed

            Parameters
            ----------

            ``step_data`` : The data that will be passed forwards to the
                ``perform`` method after validation

            ``title`` : A unique identifier for this step that is used
                for logging
        """
        self.step_data = step_data
        self.title = title
        # This should get set to the validated in ``is_valid`` if it's
        # validated successfully
        self._validated_data = None
        self._errors = None

    def validate(self):
        """ Validates the step's ``step_data`` prior to ``run_step``

            Should return the True/False and set the ``_errors`` and
            ``_validated_data`` attributes

            Must be overridden in derived steps
        """
        self._errors = {}
        self._validated_data = {}
        for field in self.Meta.fields:
            if not hasattr(self, field) or not \
                    isinstance(getattr(getattr(self, field), "validate", None),
                               types.MethodType):
                raise ValueError(f"`{field}` is not a valid field")
            field_instance = getattr(self, field)
            field_default = field_instance.default

            try:
                self._validated_data[field] = field_instance.validate(
                    self.step_data.get(field, field_default)
                )
            except exceptions.ValidationError as exc:
                # Passing the error if the validation field seems like it
                # is something that will use the `performance_data` resolvers
                if resolvers.VariableResolver.find_variables(
                        self.step_data.get(field, field_default)):
                    self._validated_data[field] = self.step_data.get(
                        field, field_default)
                else:
                    self._errors[field] = field_instance.errors

        if self._errors:
            self._validated_data = None
            return False
        return True

    def is_valid(self, raise_exception=False):
        """ Calls the validate method and sets the ``_validated_data`` property
            with the returned data
        """
        assert self.step_data is not None, (
            "There is no data to validate. The ``step_data`` parameter must "
            "be passed into the step for it to get validated."
        )

        if self.validate():
            return True
        else:
            if raise_exception:
                raise exceptions.ValidationError(self.errors)
            return False

    def save_screenshot(self, driver, screenshots_path):
        """ Debug method for taking a full-screen screenshot of the driver
            and saving it to the ``screenshots_path`` directory
        """
        if not os.path.exists(screenshots_path):
            os.makedirs(screenshots_path)

        fname = os.path.join(screenshots_path, f"{self.title}.png")
        with open(fname, 'wb') as outf:
            el = driver.find_element_by_tag_name('body')
            outf.write(el.screenshot_as_png)
        return fname

    def run_step(self, driver, performance_context,
                 save_screenshots=False, screenshots_path=None):
        """ Performs the step using the ``perform`` method and logs any details
            through the ``step_title`` attribute

            Parameters
            ----------

            ``driver`` : Driver that the step will be executed on

            ``performance_context`` : Context for the step that will be used for
                resolving context variables in the step-fields
                (see ``resolve_step_data()``)

            ``save_screenshots`` : Boolean for whether screenshots should be
                saved for this step or not

            ``screenshots_path`` : Path to the directory where the screenshots
                for this step should be saved (if enabled)
        """
        logger.debug("Performing step {title}.", title=self.title)

        # Resolving performance data
        performance_data = self.resolve_step_data(performance_context)

        try:
            step_data = self.perform(
                driver, performance_data, performance_context) or {}
        except exceptions.StepPerformanceError:
            if save_screenshots:
                logger.debug("Screenshot saved at " +
                             self.save_screenshot(driver, screenshots_path))
            raise
        except:
            error_msg = f"Uncaught error while performing {self.title}."
            if save_screenshots:
                error_msg += f" Screenshot saved at " + \
                    self.save_screenshot(driver, screenshots_path)
            raise exceptions.StepPerformanceError(error_msg)

        if not isinstance(step_data, dict):
            step_data = {}

        logger.debug("Successfully performed step {title}.", title=self.title)
        logger.debug(f"Added step data {self.internal_title}: {step_data}.")
        if save_screenshots:
            logger.debug(f"Screenshot saved at " +
                         self.save_screenshot(driver, screenshots_path))

        return step_data

    def perform(self, driver, performance_data, performance_context):
        """ Performs the step's action with the validated data on the given
            driver

            Any returned data is logged by the SeleniumYAML engine for
            debugging and stored in the engine's ``performance_context``
            dict attribute under the step's ``internal_title`` key for
            later usage

            Must be overridden in derived steps

            Make sure this method returns either None or a Dict
        """
        raise NotImplementedError("The ``perform`` method must be overridden "
                                  "by the derived Step classes.")

    @property
    def validated_data(self):
        """ Property for the ``_validated_data`` member - only available if the
            ``is_valid`` method has been called
        """
        assert self._validated_data is not None, (
            "``is_valid`` must be called successfully prior to accessing the "
            "validated data"
        )
        return self._validated_data

    @property
    def errors(self):
        """ Property for the ``_errors`` member - only available if the
            ``is_valid`` method has been called
        """
        assert self._errors is not None, (
            "``is_valid`` must be called prior to accessing the errors"
        )
        return self._errors

    @property
    def internal_title(self):
        """ Returns the title in a format usable as an engine variable that can
            be resolved through `resolvers.resolve_variable`
            Just replaces all double underscores with `\\_` and all pipes
            with `\\\\`
        """
        return self.title.replace("__", "\\_").replace("|", "\\\\")

    def resolve_step_data(self, performance_context):
        """ Uses the validated data and formats all fields with the engine's
            performance context to fill any placeholders
        """
        data = {}

        for key, value in self.validated_data.items():
            resolver = resolvers.VariableResolver(value)
            data[key] = resolver.render(performance_context)
        return data
