"""
Module containing all basic fields that can be used by steps for validation

Each field must derive from the ``Field`` class included in this module and
may overwrite the validate methods to add custom validation

For the discerning ones among us, yes, this is somewhat similar to what DRF
does with it's serializers and fields

Basic Example:
    # Todo
"""
from selenium_yaml import exceptions
from selenium_yaml import validators as field_validators


class Field:
    """ The Base Field class that all other fields must inherit from

        It specifies basic attributes and validation requirements that are
        used commonly among most field types
    """
    def __init__(self, required=False, default=None, validators=None):
        """ Initializes the field with the provided parameters;

            A ``required`` field must be provided in the step's data, otherwise
            it will raise a Validation error

            A ``default`` for a field, if provided, will be used to populate
            the field if the field is either not in the step's data or if it is
            Null

            The ``validators`` for a field are iterated over during validation
            and are used to make sure that the field is Valid
                All ``validators`` must be derived from the
                ``validators.Validator`` object
        """
        validators = validators or []
        self.required = required
        self.default = default

        if self.required:
            validators.insert(0, field_validators.RequiredValidator())
        self.validators = validators


        # This is set after a successful validation by the ``validate`` method
        self._value = None
        self._errors = None

    def validate(self, value):
        """ Validates the given ``value`` based on the active attributes on the
            class
        """
        errors = []
        for validator in self.validators:
            if not validator.is_valid(value):
                error = validator.error
                if isinstance(error, list):
                    errors += error
                else:
                    errors.append(error)

        if errors:
            self._errors = errors
            raise exceptions.ValidationError(self._errors)
        self._value = value
        self._errors = []

        return value

    @property
    def value(self):
        assert self._value is not None, (
            "The field's ``validate`` method must get called before the value "
            "is accessible."
        )
        return self._value

    @property
    def errors(self):
        assert self._errors is not None, (
            "The field's ``validate`` method must get called before the "
            "errors are accessible."
        )
        return self._errors


class CharField(Field):
    """ Field defining validation used commonly for character fields """
    def __init__(self, *args, max_length=None, validators=None, options=None,
                 **kwargs):
        """ Creates an instance of a CharacterField and adds a max-length
            validator to it if the ``max_length`` attribute is specified and
            also adds a ``validators.TypeValidator(field_type=str)`` validator

            ``max_length``, if specified, adds a
            ``validators.MaxLengthValidator(length=max_length)`` validator to
            the field
        """
        validators = validators or []
        validators.append(field_validators.TypeValidator(field_type=str))

        self.max_length = max_length
        if self.max_length:
            validators.append(
                field_validators.MaxLengthValidator(length=self.max_length))

        self.options = options
        if self.options:
            validators.append(
                field_validators.OptionsValidator(options=self.options))

        super().__init__(*args, validators=validators, **kwargs)


class IntegerField(Field):
    """ Field defining validation used commonly for integer fields """
    def __init__(self, *args, validators=None, **kwargs):
        """ Creates an instance of a IntegerField and adds a
            ``validators.TypeValidator(field_type=int)`` validator
        """
        validators = validators or []
        validators.append(field_validators.TypeValidator(field_type=int))

        super().__init__(*args, validators=validators, **kwargs)


class BooleanField(Field):
    """ Field defining validation used commonly for boolean fields """
    def __init__(self, *args, validators=None, **kwargs):
        """ Creates an instance of a BooleanField and adds a
            ``validators.TypeValidator(field_type=bool)`` validator
        """
        validators = validators or []
        validators.append(field_validators.TypeValidator(field_type=bool))

        super().__init__(*args, validators=validators, **kwargs)


class DictField(Field):
    """ Field defining validation used commonly for dictionary fields """
    def __init__(self, *args, validators=None, **kwargs):
        """ Creates an instance of a DictField and adds a
            ``validators.TypeValidator(field_type=dict)`` validator
        """
        validators = validators or []
        validators.append(field_validators.TypeValidator(field_type=dict))

        super().__init__(*args, validators=validators, **kwargs)


class FilePathField(Field):
    """ Field that adds a ``validators.FilePathValidator`` which confirms that
        the given value is a valid file path
    """
    def __init__(self, *args, validators=None, **kwargs):
        """ Creates an instance of a FilePathField and adds a
            ``validators.FilePathValidator`` validator
        """
        validators = validators or []
        validators.append(field_validators.FilePathValidator())

        super().__init__(*args, validators=validators, **kwargs)


class ResolvedVariableField(Field):
    """ Field that adds a ``validators.ResolvedVariableValidator`` which
        confirms that the field's value is in the format of `${VARIABLE}` or
        is of the required type already
    """
    def __init__(self, *args, required_type=None, validators=None, **kwargs):
        """ Creates an instance of a ResolvedVariableField and adds a
            ``validators.ResolvedVariableValidator`` validator
        """
        validators = validators or []
        validators.append(
            field_validators.ResolvedVariableValidator(
                required_type=required_type
            )
        )

        super().__init__(*args, validators=validators, **kwargs)


class NestedStepsField(Field):
    """ Field that resolves the given data as registered steps """

    def validate(self, value):
        """ Validates each step individually through
            validators.StepValidator

            This has been overwritten since each validator acts on a specific
            item in the list - which is out of the scope of the base method
        """
        if not isinstance(value, list):
            value = [value]
        validated_steps = {}
        for sub_step in value:
            validator = field_validators.StepValidator()
            # This will raise a ValidationError if there's an error anywhere
            step_cls = validator.validate(sub_step)
            validated_steps[step_cls.title] = step_cls
        return super().validate(validated_steps)
