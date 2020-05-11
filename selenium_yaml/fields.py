"""
Module containing all basic fields that can be used by steps for validation

Each field must derive from the ``Field`` class included in this module and
may overwrite the validate methods to add custom validation

For the discerning ones among us, yes, this is somewhat similar to what DRF
does with it's serializers and fields

Basic Example:
    # Todo
"""
from selenium_yaml import validators as field_validators
from selenium_yaml import exceptions


class Field:
    """ The Base Field class that all other fields must inherit from

        It specifies basic attributes and validation requirements that are
        used commonly among most field types
    """
    def __init__(self, required=False, default=None, validators=[]):
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
        self.required = required
        self.default = default
        self.validators = validators

        if self.required:
            self.validators.insert(0, field_validators.RequiredValidator())

        # This is set after a successful validation by the ``validate`` method
        self._value = None
        self._errors = None

    def validate(self, value):
        """ Validates the given value based on the active attributes on the
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
    def __init__(self, max_length=None, validators=[], *args, **kwargs):
        """ Creates an instance of a CharacterField and adds a max-length
            validator to it if the ``max_length`` attribute is specified and
            also adds a ``validators.TypeValidator(field_type=str)`` validator

            ``max_length``, if specified, adds a
            ``validators.MaxLengthValidator(length=max_length)`` validator to
            the field
        """
        validators.append(field_validators.TypeValidator(field_type=str))
        self.max_length = max_length
        if self.max_length:
            validators.append(
                field_validators.MaxLengthValidator(length=self.max_length))

        return super().__init__(*args, validators=validators, **kwargs)


class IntegerField(Field):
    """ Field defining validation used commonly for character fields """
    def __init__(self, validators=[], *args, **kwargs):
        """ Creates an instance of a CharacterField and adds a max-length
            validator to it if the ``max_length`` attribute is specified and
            also adds a ``validators.TypeValidator(field_type=str)`` validator

            ``max_length``, if specified, adds a
            ``validators.MaxLengthValidator(length=max_length)`` validator to
            the field
        """
        validators.append(field_validators.TypeValidator(field_type=int))

        return super().__init__(*args, validators=validators, **kwargs)
