"""
Contains methods for resolving variables stored in the SeleniumYAML engine
through a string value

The methods should support reading of Nested variables in dictionaries,
as well as first level values

Basic Usage:
    # TODO
"""
import re


def resolve_variable(data, key):
    """ A recursive function that takes the "first level" of the ``key``
        and checks if the ``data`` dictionary contains it. If so, it
        recursively calls itself on the dictionary if the value of that
        key is a dictionary, or returns the value if it's either not
        present/is not a dictionary
    """
    if not isinstance(key, list):
        key = key.split("__")

    if key:
        current_level = key.pop(0)
        if isinstance(data, dict):
            if current_level in data:
                return resolve_variable(data[current_level], key)
            return None
        else:
            raise ValueError(
                f"Can't query non-dict for value ``{current_level}``."
            )
    return data


def find_placeholders(value):
    """ Returns a list of all placeholders in ``${...}`` in the given value """
    if isinstance(value, str):
        r = re.compile(r"\$\{(.*?)\}")
        return r.findall(value)


def substitute_placeholders(value, context):
    """ Replaces any words enclosed in `${...}` in the ``value`` with their
        resolved values in the ``context`` if any
    """
    if isinstance(value, str):
        placeholders = find_placeholders(value)
        for placeholder in placeholders:
            # Only replaces the placeholder if the resolution is valid
            resolved_value = resolve_variable(context, placeholder)
            if resolved_value:
                value = value.replace(
                    "${" + placeholder + "}",
                    str(resolve_variable(context, placeholder))
                )
    return value