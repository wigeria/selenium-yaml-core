# Resolved Variables

Resolved Variables are template variables that can be added to steps in bots that are rendered right before the execution of the step using all of the context stored prior to it's execution. Note that these variables are **not** rendered in the `title` and `action` fields for the steps, since those are used prior to the actual execution.

All of the data returned by a Step's `perform()` method (note that this should always be None or a Dict) is stored in the performance context under that Step's Namespace (it's `title`).

Resolved Variables allow for nested access using double underscores (`__`).

# Schema

Resolved Variables can be added to the bots using by enclosing variables in `${...}` brackets. Spaces are allowed inside the brackets, as well as certain functions defined [here](#functions)

## Accessing Nested Fields

Context data can be nested infinitely and can be accessed by passing through levels using `__`.

For example, if we had a [CallAPIStep](/reference/steps/#CallAPIStep) step titled `Call an API` (which stores the response body in the `context` variable) which received a JSON response of `{key1: {key2: value}}`, we could access `value` using the following in any of the following steps:

```
${Call an API__content__key1__key2}
```

If we received a response of `{key1: [value1, value2, value3]}` however, and we wanted to access `value3`, we could retreive that through it's zero-index as follows:

```
${Call an API__content__key1__2}
```

These two formats can be used as required to traverse through dictionaries and lists.

## Using Functions

Certain functions can be used for modifying resolved variables for more complex use cases. The functions available depend on the type of variable they're being used against.

These can be used through the `|` (pipe) symbol. For example, if we wanted to us the split function to separate a string by `,` and get the first value, we could do the following:

```
${Step Title__string_variable|split(',')__0}
```

### Strings

- `split(delim, maxsplit=None)` - Splits the string by the given delimiter.
- `upper()` - Uppercases the entire string
- `lower()` - Lowercasess the entire string
- `capitalize()` - Capitalizes the first letter of the string
- `zfill(width)` - Adds zeroes before the string so that it reaches the required width
- `strip()` - Strips spaces from before and after the string
- `len()` - Gives back the length of the string as an integer
- `startswith(prefix)` - Returns a boolean based on whether a string starts with a value or not
- `endswith(prefix)` - Returns a boolean based on whether a string ends with a value or not

### List

- `len()` - Returns the length of the string as an integer
- `index(value)` - Returns the index of the given value in the list
- `reverse()` - Returns the list in reverse
- `sort()` - Returns the sorted list
- `join(delim)` - Returns the list joined by the delimiter as a string

### Dict

- `get(key, default=None)` - Returns the key if it exists in the dict, otherwise returns the default if provided
- `keys()` - Returns a list of all keys in the dictionary
- `items()` - Returns a list of tuples of all (key, value) pairs in the dictionary
