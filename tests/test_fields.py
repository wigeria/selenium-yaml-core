"""
Contains tests for the fields included in selenium_yaml.fields
"""
from selenium_yaml import fields
from selenium_yaml import exceptions
import pytest
import os


class FieldTestMixin:
    """ Contains common methods for testing field validation successs or
        failure
    """
    def is_successful_validation(self, field, value, step=None):
        """ Uses basic assertions to test that the validation was a success

            Parameters
            ----------
            field : An instance of a field derived from
                        selenium_yaml.fields.Field

            value : The value that should be passed on to the field
        """
        assert field.validate(value) == value
        assert isinstance(field.errors, list)
        assert len(field.errors) == 0
        assert field.value == value

    def is_unsuccessful_validation(self, field, value, step=None):
        """ Uses basic assertions to test that the validation was a failure

            Parameters
            ----------
            field : An instance of a field derived from
                        selenium_yaml.fields.Field

            value : The value that should be passed on to the field
        """
        with pytest.raises(exceptions.ValidationError) as _:
            field.validate(value)
        assert isinstance(field.errors, list)
        assert len(field.errors) > 0


class TestCharField(FieldTestMixin):
    """ Contains tests for the char field for required, default,
        max_length. options and type
    """
    def test_char_field_type(self):
        """ Tests that the char field fails with a non-string value """
        field = fields.CharField()
        self.is_unsuccessful_validation(field, 0)

    def test_required_char_field_without_default_on_null(self):
        """ Tests that a required char field fails without a default on
            a null value
        """
        field = fields.CharField(required=True)
        self.is_unsuccessful_validation(field, None)

    def test_required_char_field_with_default_on_null(self):
        """ Tests that a required char field succeeds with a valid string
            default on a null value
        """
        field = fields.CharField(required=True, default="Test")
        self.is_successful_validation(field, field.default)

    def test_char_field_max_length_exceeded(self):
        """ Tests that the char field validation fails if the value is longer
            than the max length
        """
        field = fields.CharField(max_length=3)
        self.is_unsuccessful_validation(field, "Test")

    def test_char_field_max_length_valid(self):
        """ Tests that the char field validation succeeds if the value is not
            longer than the max length
        """
        field = fields.CharField(max_length=6)
        self.is_successful_validation(field, "Test")

    def test_char_field_fails_on_non_option_member(self):
        """ Tests that the char field validation fails if a non-option is
            passed in
        """
        options = ["Test", "4"]
        field = fields.CharField(max_length=6, options=options)
        self.is_unsuccessful_validation(field, "Fail")

    def test_char_field_succeeds_onoption_member(self):
        """ Tests that the char field validation succeeds if a valid option is
            passed in
        """
        options = ["Test", "4"]
        field = fields.CharField(max_length=6, options=options)
        self.is_successful_validation(field, "Test")


class TestIntegerField(FieldTestMixin):
    """ Contains tests for the integer field for required, default and type """
    def test_integer_field_type(self):
        """ Tests that the integer field fails with a non-integer value """
        field = fields.IntegerField()
        self.is_unsuccessful_validation(field, "Test")

    def test_required_integer_field_without_default_on_null(self):
        """ Tests that a required integer field fails without a default """
        field = fields.IntegerField(required=True)
        self.is_unsuccessful_validation(field, None)

    def test_required_integer_field_with_default_on_null(self):
        """ Tests that a required integer field succeeds with a valid int
            default on a null value
        """
        field = fields.IntegerField(required=True, default=10)
        self.is_successful_validation(field, field.default)


class TestBooleanField(FieldTestMixin):
    """ Contains tests for the Boolean field for required, default and type """
    def test_boolean_field_type(self):
        """ Tests that the Boolean field fails with a non-boolean value """
        field = fields.BooleanField()
        self.is_unsuccessful_validation(field, "Test")

    def test_required_boolean_field_without_default_on_null(self):
        """ Tests that a required Boolean field fails without a default """
        field = fields.BooleanField(required=True)
        self.is_unsuccessful_validation(field, None)

    def test_required_boolean_field_with_default_on_null(self):
        """ Tests that a required boolean field succeeds with a valid bool
            default on a null value
        """
        field = fields.BooleanField(required=True, default=True)
        self.is_successful_validation(field, field.default)


class TestDictField(FieldTestMixin):
    """ Contains tests for the dict field for required, default and type """
    def test_dict_field_type(self):
        """ Tests that the dict field fails with a non-dict value """
        field = fields.DictField()
        self.is_unsuccessful_validation(field, "Test")

    def test_required_dict_field_without_default_on_null(self):
        """ Tests that a required dict field fails without a default """
        field = fields.DictField(required=True)
        self.is_unsuccessful_validation(field, None)

    def test_required_dict_field_with_default_on_null(self):
        """ Tests that a required dict field succeeds with a valid dict
            default on a null value
        """
        field = fields.DictField(required=True, default={"test": 1})
        self.is_successful_validation(field, field.default)


class TestFilePathField(FieldTestMixin):
    """ Contains tests for the FilePathField """
    def test_invalid_on_invalid_filepath(self):
        """ Tests that the validation fails on non-existent fpaths """
        value = os.path.join(os.getcwd(), "thispathshouldnotexist.txt")
        field = fields.FilePathField()
        self.is_unsuccessful_validation(field, value)

    def test_validator_on_valid_filepath(self):
        """ Tests that the validation succeeds on valid fpaths """
        value = os.path.join(os.getcwd(), ".gitignore")
        field = fields.FilePathField()
        self.is_successful_validation(field, value)
