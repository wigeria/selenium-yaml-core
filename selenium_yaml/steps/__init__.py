"""
Steps Package containing all of the in-built selenium-yaml Steps along with
a BaseStep that can be used for building customized Steps

Basic Example:
    # Todo
"""
from selenium_yaml import exceptions
from selenium_yaml import fields as step_fields
from loguru import logger
import os


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
    def __init__(self, engine, step_data=None, title=None):
        """ Creates a new instance of the step and sets attributes that will
            be modified during validation so that the step can be performed

            Parameters
            ----------

            ``engine`` : The selenium_yaml.SeleniumYAML instance that's
                going to be performing this step; this instance will also have
                the webdriver attribute in ``engine.driver`` if all steps get
                validated successfully

            ``step_data`` : The data that will be passed forwards to the
                ``perform`` method after validation

            ``title`` : A unique identifier for this step that is used
                for logging
        """
        self.engine = engine
        self.step_data = step_data
        self.title = title
        # This should get set to the validated in ``is_valid`` if it's
        # validated successfully
        self._validated_data = None
        self._errors = None

    def validate(self):
        """ Validates the step's ``step_data`` prior to ``perform``

            Should return the True/False and set the ``_errors`` and
            ``_validated_data`` attributes

            Must be overridden in derived steps
        """
        self._errors = {}
        self._validated_data = {}
        for field in self.Meta.fields:
            if not hasattr(self, field) or not \
                    isinstance(getattr(self, field), step_fields.Field):
                raise ValueError(f"`{field}` is not a valid field")
            field_instance = getattr(self, field)
            field_default = field_instance.default

            try:
                self._validated_data[field] = field_instance.validate(
                    self.step_data.get(field, field_default))
            except exceptions.ValidationError as exc:
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
        is_valid = self.validate()

        if is_valid:
            return True
        else:
            if raise_exception:
                raise exceptions.ValidationError(self.errors)
            return False

    def save_screenshot(self,
                        dir_path=os.path.join(os.getcwd(), "screenshots")):
        """ Debug method for taking a full-screen screenshot of the driver
            and saving it to the given ``dir_path`` directory
        """
        assert self.engine.driver, "Driver is not initialized."
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        fname = os.path.join(dir_path, f"{self.title}.png")
        with open(fname, 'wb') as outf:
            el = self.engine.driver.find_element_by_tag_name('body')
            outf.write(el.screenshot_as_png)
        return fname

    def run_step(self, save_screenshot=False):
        """ Performs the step using the ``perform`` method and logs any details
            through the ``step_title`` attribute
        """
        logger.debug("Performing step {title}.", title=self.title)
        try:
            self.perform()
        except exceptions.StepPerformanceError:
            if save_screenshot:
                logger.debug(f"Screenshot saved at {self.save_screenshot()}")
            raise
        except:
            error_msg = f"Uncaught error while performing {self.title}."
            if save_screenshot:
                error_msg += \
                    f" Screenshot saved at {self.save_screenshot()}"
            raise exceptions.StepPerformanceError(error_msg)
        logger.debug("Successfully performed step {title}.", title=self.title)
        if save_screenshot:
            logger.debug(f"Screenshot saved at {self.save_screenshot()}")

    def perform(self):
        """ Performs the step's action with the validated data

            Any returned data is logged by the SeleniumYAML engine for
            debugging

            Must be overridden in derived steps
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
