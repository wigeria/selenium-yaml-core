"""
Contains tests for the field resolvers used for replacing variables with
context data
"""

from selenium_yaml.steps import resolvers


class TestResolvers:
    """ Contains tests that check the resolvers against different types
        of variables and context data
    """
    def test_resolver_against_dict(self):
        """ Tests the resolver to get a string value from a nested dict """
        placeholder = "Value is: ${data__dict1__dict2__key}"
        key = "Value"
        expected_value = f"Value is: {key}"
        context = {
            "data": {
                "dict1": {
                    "dict2": {"key": key}
                }
            }
        }
        resolver = resolvers.VariableResolver(placeholder)
        assert (
            resolver.render(context) == expected_value
        )

    def test_resolver_against_invalid_resolver(self):
        """ Tests the resolver against a value that doesn't exist """
        placeholder = "Value is: ${data__dict1__dict2__invalid_key}"
        context = {
            "data": {
                "dict1": {
                    "dict2": {"key": "random-key"}
                }
            }
        }
        resolver = resolvers.VariableResolver(placeholder)
        assert (
            resolver.render(context) == placeholder
        )

    def test_resolver_against_array_index(self):
        """ Tests that the resolver can be used for indexing into arrays """
        placeholder = "Value is: ${data__dict1__arr1__0__dict2__key}"
        key = "ArrayResult"
        expected_value = f"Value is: {key}"
        context = {
            "data": {
                "dict1": {
                    "arr1": [{
                        "dict2": {"key": key}
                    }]
                }
            }
        }
        resolver = resolvers.VariableResolver(placeholder)
        assert (
            resolver.render(context) == expected_value
        )

    def test_resolver_with_complex_value(self):
        """ Tests that a resolver can handle resolving all keys inside a
            complex value formed of dicts and arrays
        """
        placeholder_dict = {
            "key1": "${var1}",
            "key2": "${var2}",
            "key3": {
                "key4": {
                    "key5": "${var3}"
                },
                "key5": ["${var4}", "${var5}"]
            }
        }
        context = {
            "var1": "Val1",
            "var2": "Val2",
            "var3": "Val3",
            "var4": "Val4",
            "var5": "Val5"
        }
        expected_result = {
            "key1": context["var1"],
            "key2": context["var2"],
            "key3": {
                "key4": {
                    "key5": context["var3"]
                },
                "key5": [context["var4"], context["var5"]]
            }
        }
        resolver = resolvers.VariableResolver(placeholder_dict)
        assert (
            resolver.render(context) == expected_result
        )

    def test_functions_in_variable(self):
        """ Tests cases where variables have functions called on them inside
            a resolved variable
        """
        placeholder = "Value is: ${key|lower()|capitalize()|split(',')__0}"
        key = "ArrayResult,Value"
        expected_value = f"Value is: Arrayresult"
        context = {"key": key}
        resolver = resolvers.VariableResolver(placeholder)
        assert (
            resolver.render(context) ==
            expected_value
        )
