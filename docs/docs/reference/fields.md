# Fields

This is a reference of the fields included with the library. Any custom fields can added as required by following the instructions available [here](/quickstart/customization/#custom-fields).

Fields are used in steps for the main purpose of providing collective validation for input to a common group of data.

## CharField

- `max_length` - The maximum length allowed for the input
- `options` - An array of options that the input could be allowed to be

This field implements the following validators:

- `TypeValidator(field_type=str)`
- `MaxLengthValidator` if the max length is provided
- `OptionsValidator` if any options are provided

## IntegerField

This field implements the following validators:

- `TypeValidator(field_type=int)`

## BooleanField

This field implements the following validators:

- `TypeValidator(field_type=bool)`

## DictField

This field implements the following validators:

- `TypeValidator(field_type=dict)`

## FilePathField

This field implements the following validators:

- `FilePathValidator`

Used to receive the path of a file in the system as input.

## ResolvedVariableField

- `required_type` - The type the input is allowed to be if it isn't a resolved variable

This field implements the following validators:

- `ResolvedVariableValidator`

## NestedStepsField

This field implements the following validators individuallly for each element in the input:

- `StepValidator`

A rather specific step that is used for parsing and validating sub-steps.
