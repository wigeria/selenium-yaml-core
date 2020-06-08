""""
Module containing serialization and validation required for Bot Steps aquired
as YAML Dicts

Basic Usage:
    # Todo
"""
from selenium_yaml import exceptions
from selenium_yaml.steps.registered_steps import get_registered_step
from collections import OrderedDict
import yaml
import os


DUPLICATE_ERROR = "Step titles must be unique"
MISSING_TITLE_ERROR = "A step doesn't have a ``title`` attribute."


class YAMLParser:
    """ Parser that expects a file-like object containing Steps data in a
        YAML format

        Each step in the YAML is validated individually and the data is only
        accessible if each step is valid

        # TODO: Refactor off of a base Parser class
    """
    def __init__(self, yaml_file):
        """ Parses the given ``yaml_file`` and validates and initializes the
            included steps
        """
        self.yaml_data = yaml.load(yaml_file)

        assert isinstance(self.yaml_data, dict), (
            "Invalid YAML Schema. The data must be in a format of "
            "{title, steps: [...]}"
        ) 
        assert "title" in self.yaml_data, (
            "The YAML doesn't have a ``title`` key for the bot."
        )
        assert "steps" in self.yaml_data and \
            isinstance(self.yaml_data["steps"], list), (
                "The ``steps`` in the YAML are not in a list format."
            )
        self.bot_title = self.yaml_data["title"]
        self.screenshots_path = os.path.join(
            os.getcwd(), "screenshots", self.bot_title
        )

    def validate(self):
        """ Validates the ``yaml_data`` attribute and initializes the steps
            that are valid

            Sets the ``_validated_steps`` and ``_errors`` properties
        """
        self._validated_steps = OrderedDict()
        self._errors = {}
        for step in self.yaml_data["steps"]:
            # Validates that the step has a unique title first of all so
            # that errors can be assigned to the correct step title
            step_title = step.pop("title", None)
            if not step_title:
                self._errors = {"<unknown>": MISSING_TITLE_ERROR}
                self._validated_steps = OrderedDict()
                raise ValueError(MISSING_TITLE_ERROR)
            elif step_title in self._validated_steps:
                self._errors[step_title] = [DUPLICATE_ERROR]
            elif step_title in self._errors:
                self._errors[step_title].append(DUPLICATE_ERROR)
            # Then validates that the step's action is registered
            try:
                step_cls = get_registered_step(step.pop("action", None))
            except KeyError:
                self._errors[step_title] = f"{step_title}'s ``step_cls`` " + \
                    f"not found."
                continue
            # Then validates that the step has a valid set of data
            step_cls = step_cls(step_data=step, title=step_title,
                                screenshots_path=self.screenshots_path)
            if not step_cls.is_valid():
                self._errors[step_title] = step_cls.errors
            else:
                self._validated_steps[step_title] = step_cls

        if self._errors:
            self._validated_steps = OrderedDict()
            return False
        return True

    def is_valid(self):
        """ Validates the ``yaml_data`` attribute using the ``validate``
            method

            Either return ``True`` or raises a ValidationError with the
            issues
        """
        is_valid = self.validate()
        if not is_valid:
            raise exceptions.ValidationError(self.errors)
        return True

    @property
    def validated_steps(self):
        assert self._validated_steps is not None, (
            "``is_valid`` must be called successfully prior to accessing the "
            "validated steps"
        )
        return self._validated_steps

    @property
    def errors(self):
        """ Property for the ``_errors`` member - only available if the
            ``is_valid`` method has been called
        """
        assert self._errors is not None, (
            "``is_valid`` must be called prior to accessing the errors"
        )
        return self._errors
