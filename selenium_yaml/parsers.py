""""
Module containing serialization and validation required for Bot Steps aquired
as YAML Dicts

Basic Usage:
    # Todo
"""
from collections import OrderedDict

import yaml
from selenium_yaml import exceptions
from selenium_yaml.steps.registered_steps import get_registered_step

DUPLICATE_ERROR = "Step titles must be unique"
MISSING_TITLE_ERROR = "A step doesn't have a ``title`` attribute."


class YAMLParser:
    """ Parser that expects a file-like object containing Steps data in a
        YAML format

        The YAML can optionally also include ``exception_steps`` which are
        triggered by the engine for any exceptions encountered during
        performance

        Each step in the YAML is validated individually and the data is only
        accessible if each step is valid

        # TODO: Refactor off of a base Parser class
    """
    def __init__(self, yaml_file):
        """ Parses the given ``yaml_file`` and validates and initializes the
            included steps
        """
        self.yaml_data = yaml.safe_load(yaml_file)

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
        # Defaulting the exception steps to a list if not present, otherwise
        # validating that they're provided as a list
        if "exception_steps" not in self.yaml_data:
            self.yaml_data["exception_steps"] = []
        else:
            assert isinstance(self.yaml_data["exception_steps"], list), (
                "``exception_steps`` must be provided in a list format."
            )
        self.bot_title = self.yaml_data["title"]

        self._validated_steps = None
        self._errors = None

    def validate(self):
        """ Validates the ``yaml_data`` attribute and initializes the steps
            and exception_steps that are valid

            Sets the ``_validated_steps``, ``_validated_exception_steps``
            and ``_errors`` properties
        """
        self._validated_steps = OrderedDict()
        self._validated_exception_steps = OrderedDict()
        self._errors = {}
        for step in self.yaml_data["steps"]:
            self.validate_step(step, self._validated_steps)
        for exception_step in self.yaml_data["exception_steps"]:
            self.validate_step(exception_step, self._validated_exception_steps)

        if self._errors:
            self._validated_steps = OrderedDict()
            self._validated_exception_steps = OrderedDict()
            return False
        return True

    def validate_step(self, step, validated_array):
        """ Validates the given ``step`` dictionary through a provided
            set of rules;
            The validated step is then stored in the ``validated_array``
            array; this is specified since some steps may be
            destined for different locations:
                ``validated_steps`` and ``validated_exception_steps``

            The ``title`` is required, and must be unique.
            The ``action`` must point to a registered Step class
            The other data provided in the step must be validated successfullly
            against the Step class identified by ``action``
        """
        # Validates that the step has a unique title first of all so
        # that errors can be assigned to the correct step title
        step_title = step.pop("title", None)
        if not step_title:
            self._errors = {"<unknown>": MISSING_TITLE_ERROR}
            validated_array = OrderedDict()
            raise ValueError(MISSING_TITLE_ERROR)
        elif step_title in validated_array:
            self._errors[step_title] = [DUPLICATE_ERROR]
        elif step_title in self._errors:
            self._errors[step_title].append(DUPLICATE_ERROR)
        # Then validates that the step's action is registered
        try:
            step_cls = get_registered_step(step.pop("action", None))
        except KeyError:
            self._errors[step_title] = f"{step_title}'s ``step_cls`` " + \
                "not found."
            return
        # Then validates that the step has a valid set of data
        step_cls = step_cls(step_data=step, title=step_title)
        if not step_cls.is_valid():
            self._errors[step_title] = step_cls.errors
        else:
            validated_array[step_title] = step_cls

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
    def validated_exception_steps(self):
        assert self._validated_exception_steps is not None, (
            "``is_valid`` must be called successfully prior to accessing the "
            "validated exception steps"
        )
        return self._validated_exception_steps

    @property
    def errors(self):
        """ Property for the ``_errors`` member - only available if the
            ``is_valid`` method has been called
        """
        assert self._errors is not None, (
            "``is_valid`` must be called prior to accessing the errors"
        )
        return self._errors
