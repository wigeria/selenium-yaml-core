"""
Module containing all of the commonly used validators for the Fields

Any new validators created must inherit from the ``Validator`` class provided
in this module

Basic Example:
    # TODO
"""
import os

from selenium_yaml import exceptions, steps


class Validator:
    """ Base Validator class that all field validators must inherit from

        All new validators must overwrite the ``validate`` method to adjust the
        validation functionality. All validators must be limited in scope and
        should only validate a single feature of the value provided

        The derived validators must also overwrite the ERROR_MESSAGE attribute
        to provide a customized error message

        The ``is_valid`` method must be used before the validation errors can
        be accessed
    """
    def __init__(self):
        """ Creates a new instance of the validator and sets the ``_value`` and
            ``_error`` attributes to their default values
        """
        self._error = None

    def validate(self, value):
        """ This method should be overridden and raise an
            exceptions.ValidationError exception for any error encountered
            with a meaningful message
        """
        raise NotImplementedError(
            "The ``validate`` method must be overwritten by all derived "
            "classes"
        )

    def is_valid(self, value):
        """ Calls the validate method with the ``value`` and return a boolean
            describing whether the ``value`` was validated successfully or not

            Also populates the ``_error`` attribute with the validation error's
            ``error`` in case of an unsuccessful validation
        """
        try:
            self.validate(value)
        except exceptions.ValidationError as exc:
            self._error = exc.error
            return False

        self._error = ""
        return True

    @property
    def error(self):
        assert self._error is not None, (
            "The ``is_valid`` must be called before accessing the error"
        )
        return self._error


class StepValidator:
    """ Validator for step fields - checks to make sure that the step data can
        be resolved into a valid registered step

        This validator doesn't need to derive from the base validator, as it's
        used in a very different manner
    """
    def validate(self, step_data):
        """ Receives the step-data as input and validates through the
            ``action`` key in the given dictionary

            Returns a validated instance of the step
        """
        errors = {}
        # Title/Action validation must be done prior to the actual step
        # validation
        if "title" not in step_data:
            step_title = "<unknown>"
            raise exceptions.ValidationError({
                step_title: "``title`` attribute is not provided on step."
            })
        step_title = step_data.pop("title")
        errors[step_title] = []
        if "action" not in step_data:
            errors[step_title].append(
                "``action`` is attribute not provided on step.")
            raise exceptions.ValidationError(errors)
        action = step_data.pop("action")

        try:
            step_cls = steps.registered_steps.get_registered_step(action)
        except KeyError:
            raise exceptions.ValidationError(
                f"{step_title}'s ``step_cls`` "
                "not found."
            )
        # TODO: Since the sub-steps aren't initialized with a screenshots path,
        # their screenshots CAN NOT BE SAVED at the moment!
        step_cls = step_cls(
            step_data=step_data,
            title=step_title)
        if not step_cls.is_valid():
            errors[step_title] = step_cls.errors
            raise exceptions.ValidationError(errors)

        return step_cls


class RequiredValidator(Validator):
    """ Validator which checks to make sure that the value is not None """
    def validate(self, value):
        """ Validates that the value isn't Null """
        if value is None:
            raise exceptions.ValidationError(
                "Value is required but not provided")


class MaxLengthValidator(Validator):
    """ Validator which checks to make sure that the length of the value is
        smaller than the ``maximum_length`` provided
    """
    def __init__(self, *args, length=100, **kwargs):
        """ Adds a length attribute to the validator prior to init """
        self.length = length
        super().__init__(*args, **kwargs)

    def validate(self, value):
        """ Validates that the value has a smaller length than self.length """
        try:
            len(value)
        except TypeError:
            raise exceptions.ValidationError("Value has no attribute len()")
        if len(value) > self.length:
            raise exceptions.ValidationError(
                f"Length greater than {self.length}")


class TypeValidator(Validator):
    """ Validator which checks to make sure that the type of the value matches
        the given ``field_type``
    """
    def __init__(self, *args, field_type=str, **kwargs):
        """ Adds a ``field_type`` attribute to the validator prior to init """
        self.field_type = field_type
        super().__init__(*args, **kwargs)

    def validate(self, value):
        """ Validates that the value is an instance of ``self.field_type`` """
        if not isinstance(value, self.field_type):
            raise exceptions.ValidationError(
                f"Value is not an instance of {self.field_type.__name__}.")


class OptionsValidator(Validator):
    """ Validator which checks to make sure that the given ``value`` is a
        part of the given ``options`` array
    """
    def __init__(self, *args, options=None, **kwargs):
        """ Adds a ``options`` attribute to the validator prior to init """
        self.options = options or []
        super().__init__(*args, **kwargs)

    def validate(self, value):
        """ Validates that the value is in the ``options`` array """
        if value not in self.options:
            raise exceptions.ValidationError(
                f"Value is not one of {self.options}.")


class FilePathValidator(Validator):
    """ Validator which checks to make sure that the given value is a valid
        file path
    """
    def validate(self, value):
        """ Validates that the value is an existing file path """
        if not os.path.exists(value):
            raise exceptions.ValidationError(
                f"The `{value}` file path does not exist.")


class ResolvedVariableValidator(Validator):
    """ Validator which checks to make sure that the given value is either
        a performance variable that can be resolved (in the format of
        ``${VARIABLE}``) or is already of the required type
    """
    def __init__(self, *args, required_type=None, **kwargs):
        """ Adds a ``required_type`` attribute to the validator prior to
            init
            If ``required_type`` is None, the value will be considered valid
            if it is **not null**
        """
        self.required_type = required_type
        super().__init__(*args, **kwargs)

    def validate(self, value):
        """ Validates that the value is either a resolved variable or of the
            given ``required_type``
        """
        placeholders = steps.resolvers.VariableResolver.find_variables(
            value)
        no_placeholders = placeholders is None or len(placeholders) != 1

        if self.required_type is not None:
            if no_placeholders and not isinstance(value, self.required_type):
                raise exceptions.ValidationError(
                    f"The `{value}` is not a resolved variable, and is not of "
                    "the required type either.")
        else:
            if no_placeholders and value is None:
                raise exceptions.ValidationError(
                    f"The `{value}` is not a resolved variable, and is not of "
                    "the required type either.")
