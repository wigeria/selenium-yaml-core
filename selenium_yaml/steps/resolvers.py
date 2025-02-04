"""
Contains methods for resolving variables stored in the SeleniumYAML engine
through a string value

The methods should support reading of Nested variables in dictionaries,
as well as first level values

Basic Usage:
    # TODO
"""
import re
import collections
import ast


len_function = lambda resolved_value=None: len(resolved_value)
FUNCTIONS = {
    "str": {
        "split": lambda delim, maxsplit=-1, resolved_value=None: (
            resolved_value.split(delim, maxsplit)),
        "upper": lambda resolved_value=None: resolved_value.upper(),
        "lower": lambda resolved_value=None: resolved_value.lower(),
        "capitalize": lambda resolved_value=None: resolved_value.capitalize(),
        "zfill": lambda width, resolved_value=None: resolved_value.zfill(width),
        "strip": lambda resolved_value=None: resolved_value.strip(),
        "len": len_function,
        "startswith": lambda prefix, resolved_value=None: (
            resolved_value.startswith(prefix)),
        "endswith": lambda suffix, resolved_value=None: (
            resolved_value.endswith(suffix)),
    },
    "dict": {
        "get": lambda key, default=None, resolved_value=None: (
            resolved_value.get(key, default)),
        "keys": lambda resolved_value=None: dict(resolved_value.keys()),
        "items": lambda resolved_value=None: list(resolved_value.items()),
    },
    "list": {
        "len": len_function,
        "index": lambda key, resolved_value=None: resolved_value.index(key),
        "reverse": lambda resolved_value=None: list(reversed(resolved_value)),
        "sort": lambda resolved_value=None: sorted(resolved_value),
        "join": lambda delim, resolved_value=None: delim.join(resolved_value)
    }
}


class VariableResolver:
    """ Resolver class that receives a value containing variables in the form
        of ``${name__sub_var|func(param1, param2=...)...}`` and resolves all of
        those variables through a provided ``context`` dictionary
    """
    def __init__(self, value):
        """ Creates a new instance of ``VariableResolver`` as sets the value
            as a class attribute

            Parameters
            ----------

            ``value`` : String/List/Dict containing variables that needs
                to be resolved
        """
        self.value = value

    @staticmethod
    def find_variables(value):
        """ Returns a list of all variables in ``${...}`` in the given
            value
        """
        if isinstance(value, str):
            r = re.compile(r"\$\{(.*?)\}")
            return r.findall(value)

    @staticmethod
    def parse_functions(value):
        """ Receives a string as input and parses out all of the functions
            in the format of `string|func1(...)|func2(...)` into an ordered
            dict in the format of `{func1: {param: ...}, func2: {}}`
        """
        functions = re.split(r'(?<!\\)\|', value)
        value = functions.pop(0)

        parsed_functions = collections.OrderedDict()
        for function in functions:
            call = ast.parse(function).body[0].value
            if isinstance(call, ast.Call):
                fname = call.func.id
                parsed_functions[fname] = {}
                parsed_functions[fname]["args"] = [
                    ast.literal_eval(arg) for arg in call.args]
                parsed_functions[fname]["kwargs"] = {
                    arg.arg: ast.literal_eval(arg.value) for arg in call.keywords}
        return value, parsed_functions

    @classmethod
    def resolve_functions(cls, value, functions):
        """ Executes all of the given ``functions`` on the provided
            ``value``
        """
        value_type = type(value).__name__
        assert value_type in FUNCTIONS, (
            "Value type must be str, list or dict!")
        methods = FUNCTIONS[value_type]

        for function, params in functions.items():
            value = methods[function](
                *params["args"], resolved_value=value, **params["kwargs"])
        return value

    @classmethod
    def resolve_variable(cls, data, key):
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
            current_level, functions = cls.parse_functions(current_level)
            # raise ValueError(functions)
            if isinstance(data, dict):
                # If data is a dictionary, try to get the key from the dictionary
                if current_level in data:
                    value = cls.resolve_functions(
                        data[current_level], functions)
                    return cls.resolve_variable(value, key)
                return None
            elif isinstance(data, list):
                # If data is a list, try to get the index for the list
                try:
                    value = data[int(current_level)]
                except IndexError:
                    return None
                except ValueError:
                    raise ValueError(f"`{current_level}` must be an integer since "
                                     f"`{data}` is an array.")
                value = cls.resolve_functions(value, functions)
                return cls.resolve_variable(value, key)
            else:
                raise ValueError(
                    f"Can't query non-dict for value ``{current_level}``."
                )
        return data

    @classmethod
    def substitute_variables(cls, value, context):
        """ Substitutes all variables in the given ``value`` through the
            given ``context``
        """
        if isinstance(value, str):
            placeholders = cls.find_variables(value)
            placeholder_count = len(placeholders)
            for placeholder in placeholders:
                # Only replaces the placeholder if the resolution is valid
                resolved_value = cls.resolve_variable(
                    context, placeholder)
                placeholder_string = "${" + placeholder + "}"
                if placeholder_count == 1 and value == placeholder_string:
                    # This is for cases where we need the placeholder to be
                    # replaced as is; steps should handle their own conversions
                    return resolved_value
                else:
                    if resolved_value is not None:
                        value = value.replace(
                            placeholder_string,
                            str(resolved_value)
                        )
            return value
        elif isinstance(value, dict):
            return {k: cls.substitute_variables(v, context)
                    for k, v in value.items()}
        elif isinstance(value, list):
            return [cls.substitute_variables(i, context) for i in value]
        return value

    def render(self, context):
        """ Renders and resolves the variables contained in the ``value``
            attribute through the context dictionary

            Parameters
            ----------

            ``context`` : Dictionary containing context required for resolving
                variables in the value
        """
        assert isinstance(context, dict)
        return self.substitute_variables(self.value, context)
