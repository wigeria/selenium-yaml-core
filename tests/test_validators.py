"""
Contains tests for the base Validators included in selenium_yaml.validators
"""


from selenium_yaml import validators
import os


class ValidationTestMixin:
    """ Contains basic methods for checking whether a validation was
        a success or a failure
    """
    def is_successful_validation(self, validator, value):
        """ Uses basic assertions to test that the validation was a success

            Parameters
            ----------
            validator : An instance of a validator derived from
                        selenium_yaml.validators.Validator

            value : The value that should be passed on to the validator
        """
        assert validator.is_valid(value) is True
        assert isinstance(validator.error, str)
        assert len(validator.error) == 0

    def is_unsuccessful_validation(self, validator, value):
        """ Uses basic assertions to test that the validation was a failure

            Parameters
            ----------
            validator : An instance of a validator derived from
                        selenium_yaml.validators.Validator

            value : The value that should be passed on to the validator
        """
        assert validator.is_valid(value) is False
        assert isinstance(validator.error, list)
        assert len(validator.error) > 0


class TestRequiredValidation(ValidationTestMixin):
    """ Tests the RequiredValidator on null and non-null values """
    def test_required_on_null(self):
        """ Tests that the required validator raises an exception on a Null
            value and that the error attribute gets populated
        """
        validator = validators.RequiredValidator()
        self.is_unsuccessful_validation(validator, None)

    def test_required_on_non_null_values(self):
        """ Tests that the required validator doesn't raise an exception for
            valid (non-null) values and that the error attribute is set to a
            blank string
        """
        validator = validators.RequiredValidator()
        valid_values = ["Valid Value", 100, True, [], ["Crazy"]]
        for value in valid_values:
            self.is_successful_validation(validator, value)


class TestMaxLengthValidation(ValidationTestMixin):
    """ Tests the MaxLengthValidator on values that don't have a len, values
        that exceed a max length and values that fall within the max length
    """
    def test_max_length_on_no_len(self):
        """ Tests that the max-length validator fails on values that don't have
            a len attribute
        """
        validator = validators.MaxLengthValidator(length=3)
        self.is_unsuccessful_validation(validator, 0)

    def test_max_length_on_greater_len(self):
        """ Tests that the max-length validator fails on values that have a len
            greater than the specified max-length
        """
        invalid_values = ["Test", [1, 2, 3, 4]]
        validator = validators.MaxLengthValidator(length=3)
        for value in invalid_values:
            self.is_unsuccessful_validation(validator, value)

    def test_max_length_on_valid_len(self):
        """ Tests that the max-length validator succeeds on values that have a
            len within the given threshold
        """
        valid_values = ["XYZ", [1, 2]]
        validator = validators.MaxLengthValidator(length=3)
        for value in valid_values:
            self.is_successful_validation(validator, value)


class TestTypeValidation(ValidationTestMixin):
    """ Tests that the TypeValidator only succeeds on values that are
        instances of the given type
    """
    def test_validator_on_non_matching_type(self):
        """ Tests that the validation fails for values that aren't of a
            matching type
        """
        invalid_values = [1, False]
        validator = validators.TypeValidator(field_type=str)
        for value in invalid_values:
            self.is_unsuccessful_validation(validator, value)

    def test_validator_on_matching_type(self):
        """ Tests that the validation succeeds on values that are of a
            matching type
        """
        valid_values = ["This", "Is", "Valid"]
        validator = validators.TypeValidator(field_type=str)
        for value in valid_values:
            self.is_successful_validation(validator, value)


class TestOptionsValidation(ValidationTestMixin):
    """ Tests that the options validator only succeeds if the value is a
        part of the given options array
    """
    def test_validator_on_non_member(self):
        """ Tests that the validation fails on non-members """
        options = [1, 2]
        validator = validators.OptionsValidator(options=options)
        self.is_unsuccessful_validation(validator, 3)

    def test_validator_on_member(self):
        """ Tests that the validation succeeds on a member """
        options = [1, 2]
        validator = validators.OptionsValidator(options=options)
        self.is_successful_validation(validator, 1)


class TestFilePathValidation(ValidationTestMixin):
    """ Tests that the FilePath validator is only valid when the given
        value is a valid file path
    """
    def test_validator_on_invalid_filepath(self):
        """ Tests that the validation fails on non-existent fpaths """
        value = os.path.join(os.getcwd(), "thispathshouldnotexist.txt")
        validator = validators.FilePathValidator()
        self.is_unsuccessful_validation(validator, value)

    def test_validator_on_valid_filepath(self):
        """ Tests that the validation succeeds on valid fpaths """
        value = os.path.join(os.getcwd(), ".gitignore")
        validator = validators.FilePathValidator()
        self.is_successful_validation(validator, value)


class TestResolvedVariableValidation(ValidationTestMixin):
    """ Tests that the ResolvedVariable validation is only valid on a resolved
        variable or an instance of the given type
    """
    def test_validator_on_resolved_var(self):
        """ Tests that the validation succeeds on a valid resolved var """
        value = "${resolved_var}"
        validator = validators.ResolvedVariableValidator()
        self.is_successful_validation(validator, value)
