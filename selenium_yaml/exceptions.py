"""
Module containing all of the exceptions used within the framework

Yep, the validation error idea is very similar to what DRF's doing, just in a
smaller scope
"""


def get_error_display(detail):
    """ Iterates over the detail and parses each ValidationError into
        it's own message
    """
    if isinstance(detail, list):
        return [get_error_display(exc) for exc in detail]
    elif isinstance(detail, dict):
        return {
            key: get_error_display(value) for key, value in detail.items()
        }
    elif isinstance(detail, ValidationError):
        return get_error_display(detail.detail)
    elif isinstance(detail, str):
        return detail
    return None


class ValidationError(Exception):
    """ Exception that should be raised by the step parsers and fields in case
        of any validation issues

        The ``detail`` attribute must be a list/dict at all times
    """
    def __init__(self, detail):
        """ Creates a new instance of the exception

            ``detail`` is always expected to be a non-empty list or dict
                If ``detail`` is a list, it must be a list of ValidationErrors
                    or a list of strings
                Elif ``detail`` is a dict, it must a dict with the field
                    names as keys and a validation errors or strings as values
        """
        if not isinstance(detail, list) and not isinstance(detail, dict):
            detail = [detail]
        self.detail = detail

    @property
    def error(self):
        """ Parses the detail into a human-readable syntax and returns the
            user-friendly dict
        """
        return get_error_display(self.detail)


class StepPerformanceError(Exception):
    """ Exception that should be raised if there are any issues encountered
        while performing a step
    """
    def __init__(self, detail):
        """ Creates a new instance of the exception

            ``detail`` should be a descriptive message of what went wrong
        """
        self.detail = detail
