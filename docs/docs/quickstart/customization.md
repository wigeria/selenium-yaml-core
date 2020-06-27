# Customization

Most of the functionality provided by SeleniumYAML can be customized and added to for suiting your own needs. This page aims to explain how to modify and add new Steps, Fields and Validators.

## The Structure of a Step

A Step is defined as a derivative of the `selenium_yaml.steps.BaseStep` class. There are 3 main things that *must* be added to each new step.

- `selenium_yaml.fields.Field` Attributes for each field that the step needs to receive as input in the YAML structure of the step
- A Meta class containing a `fields` list that should have a list of each defined field in the step
- A `perform` function that will be responsible for performing the actual functionality of the step

With that taken into account, here's what the core `NavigateStep` looks like:

```python
class NavigateStep(BaseStep):
    """ Step that performs a ``driver.get`` action with the given
        ``target_url``
    """
    url = fields.CharField(required=True)

    def perform(self, driver, performance_data, performance_context):
        """ Navigates the driver to the provided ``url`` """
        driver.get(performance_data["url"])

    class Meta:
        fields = ["url"]
```

Let's go over each part:

```python
url = fields.CharField(required=True)
```

This is what is going to be used to receive the `url` field as input from the YAML. The `CharField` implements it's own set of validators, which is validated prior to the bot execution. Here's what the step might look like in the YAML:

```yaml
- title: Step Title
  action: Step Identifier // This is explained in the Step Registration section
  url: https://google.com
```

Now, so that the step-parser can actually recognize the existence of that field, it must be added to the Meta class.

```python
class Meta:
    fields = ["url"]
```

And finally, the actual performance method for the step:

```python
def perform(self, driver, performance_data, performance_context):
    """ Navigates the driver to the provided ``url`` """
    driver.get(performance_data["url"])
```

The `performance_data` variable contains the data provided to the step in the YAML rendered with the `performance_context`. If you would like to access the raw data as provided in the YAML, you could access it from the `step_data` attribute on the class (through `self.step_data` in the `perform` method). If you would like to access the data after validation, but prior to being rendered, you could access it through the `validated_data` property on the class.

## Registering a Step

Before a step can be used in the YAML, it needs to be registered. This can be done through the provided class decorator:

```python
from selenium_yaml.steps.registered_steps import selenium_step


@selenium_step("step identifier")
class NavigateStep(BaseStep):
    ...
```

The Identifier passed into the `selenium_step` decorator is what is going to be used as the "action" identifier for the step in the YAML. This must be unique; using duplicates will result in an error.

## Custom Validators

Custom validators can be created to be used in fields for providing custom validation. All validators should derive from the `validators.Validator` class. The `validate()` method can be overwritten to provide custom validation for values, and the `__init__` method can be overwritten for adding new arguments. Here's an example of a `RegexValidator` that raises an exception if a value doesn't match the given regex:

```python
import re
from selenium_yaml.validators import Validator

class RegexValidator(Validator):
    """ Validator which checks to make sure that the given value is matches
        the given regex
    """
    def __init__(self, regex, *args, **kwargs):
        """ Adds a ``options`` attribute to the validator prior to init """
        self.regex = regex
        super().__init__(*args, **kwargs)

    def validate(self, value):
        """ Validates that the value matches the regex """
        if not re.match(self.regex, value):
            raise exceptions.ValidationError(
                f"The `{value}` does not match `{self.regex}`.")
```

In case of any validation errors, the validators should raise `exceptions.ValidationError` exceptions so that they can be handled correctly by the parser.

## Custom Fields

A Field class can provide it's own methods for Validation (`validate`) and overwrite the `__init__` method to add any validators. It is suggested to use `validators` for validation, instead of just directly validating everything in the `validate` method.

Here's a very basic example of a field that adds a custom "RegexValidator" to validate phone numbers:

```python
from selenium_yaml.fields import Field


class PhoneNumberField(Field):
    """ Field defining regex validation for phone numbers """
    def __init__(self, *args, validators=None, **kwargs):
        """ Creates an instance of a PhoneNumberField and adds a
            ``RegexValidator`` validator
        """
        validators = validators or []
        validators.append(field_validators.RegexValidator(r"\d{3}-\d{3}-\d{4}"))

        super().__init__(*args, validators=validators, **kwargs)
```

These fields can then be used in Steps as required.

## Running the Customized Bot

After all of the customization, you need to execute SeleniumYAML's engine:

```python
from selenium_yaml import SeleniumYAML

# Define/Import/Register any custom steps here

if __name__ == "__main__":
    engine = SeleniumYAML(
        yaml_file="path to the yaml file/a file-like object",
        save_screenshots=False,  # If true, a screenshot of the driver will be saved after each step
        template_context={},  # The template context used for rendering the YAML through Jinja
        parse_template=False  # If true, the template_context will be used to render the YAML through Jinja
    )
    engine.perform()
```
