# Validators

This is a reference for all of the base validators included with the library. Any custom validators can be added as required by following the instructions mentioned [here](/quickstart/customization/#custom-validators).

Validators are used in the [Fields](reference/fields.md) for validating the data used in the bots.

## RequiredValidator

Validates that the given value isn't Null. Generally used to make sure that the field either has a default set or has a value passed into the step.

## MaxLengthValidator

- `length` - Maximum length allowed for the value

Validates that the given value doesn't exceed the provided length, and that the value HAS a length in the first place.

## TypeValidator

- `field_type` - The type the value must be of

Validates that the given value is an instance of the given `field_type`.

## OptionsValidator

- `options` - A list of the options that the value must be a part of

Validates that the given value matches one of the options in the `options` array.

## FilePathValidator

Validates that the given value is a path to an existing file on the system.

## ResolvedVariableValidator

- `required_type` - The type the value must be of if it isn't a resolved variable

Validates that the variable is either a correctly formatted resolved variable, or that it matches the given `required_type`. Note that this doesn't validate if the resolved variable is going to be in the context during the step's execution since the validation is done prior to any execution.
