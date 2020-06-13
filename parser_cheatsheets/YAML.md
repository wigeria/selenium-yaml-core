
# YAML Parser Cheatsheet

Contains schema for the base steps in a YAML format


## Base YAML Schema

```yaml
title: Bot Title
steps:
  - An array item for each step
```


## Steps

Each step, at minimum, must have a `title` and an `action` key. The `title` will be used for naming the step, while the `action` should be the identifier the step is registered with. Each step should have a unique `title` (*this may change*).

- **Navigate**

     ```yaml
    - title: Navigate to URL
      action: navigate
      url: <URL to navigate to>
    ```

- **Wait**

     ```yaml
    - title: Wait for a fixed amount of time
      action: wait
      seconds: 10
    ```

- **Wait For Element**

     ```yaml
    - title: Wait for the element to be clickable
      action: wait_for_element
      element: <Xpath Selector for the Element>
      seconds: 10
    ```

- **Click**

     ```yaml
    - title: Click on an element
      action: click
      element: <Xpath Selector for the Element>
    ```

- **Type**

     ```yaml
    - title: Type text into an element
      action: type
      element: <Xpath Selector for the Element>
      text: Text to type into the element
      clear: True|False <-- If True, clears the element before typing anything
    ```

- **Select**

     ```yaml
    - title: Select an option from a `select` element
      action: select
      element: <Xpath selector for the Select element>
      option: <Value of the option that should be selected>
    ```

- **Make Request**

     ```yaml
    - title: Call an API and store it's response and status code
      action: make_request
      method: GET
      url: https://url-to-request.com/?queryParams=value
      body: 
        Key: <NOT REQUIRED; Request Body (currently restricted to JSON Request data)>
        Key2: <Value2>...
      headers:
        Key: <NOT REQUIRED; Headers that should be sent with the request>
        Key2: <Value2>...
    ```

- **Iterator**

     ```yaml
    - title: Iterate over an array (resolved/directly provided)
      action: iterate_over
      iterator:
        - Query1
        - Query2
      steps:
        - title: Navigate to Google
          action: navigate
          url: https://google.com
        - title: Add Query
          action: type
          element: //input[@name='q']
          text: "`current_iterator` here refers to the current element in the loop: ${current_iterator}"
    ```
  - This can also be used with the **Make Request** Step:

  ```yaml
    - title: Loop step
      action: iterate_over
      iterator: ${Call API__content}
      steps:
      - title: Navigate to Google
        action: navigate
        url: https://google.com
      - title: Add Query
        action: type
        element: //input[@name='q']
        text: "TEXT HERE: ${current_iterator__id} ${current_iterator__title}"
  ```
  
- **Run Bot**

  ```yaml
  - title: Run another bot with it's file path
      action: run_bot
      path: /path/to/bot's/yaml
  ```

- **Store Page URL**

  ```yaml
  - title: Store the current page's URL in a <Step Title>__url variable for later use
      action: store_page_url
  ```

- **Store Xpath Nodes**

  ```yaml
  - title: Store the result of a given xpath selector as a variable for later use (attributes/props only!)
      action: store_xpath
      selector: "//img[@id='img-id']/@src" <-- Note that this is an xpath selector to an attribute, not an element!
      variable: Variable To Store Result In
      select_first: True|False <-- If False, the result is stored as an array; if True, only the first result is stored
  ```

- **Conditional**

  ```yaml
  - title: Conditionally run a step
      action: conditional
      value: //span/text() <-- Value to be checked; this could be a resolved variable or an xpath selector
      equals: The Value must equal this; could be a resolved variable or any other type
      negate: True|False <-- If True, condition is set to `value != equals`, otherwise it's `value == equals`
      steps:
        - title: These Steps only run if the condition evaluates to True
          action: navigate
          url: https://google.com
        - title: Add Query
          action: type
          element: //input[@name='q']
          text: "Query"
  ```

## Resolved Variables

Inside certain fields inside of steps (mainly all excluding `title` and `action`), variables collected/stored during the runtime of the bot can be used by enclosing them in `${...}` brackets. The variables collected by a certain step is ALWAYS stored in a dictionary named after the step-title; essentially namespacing it (so variables are accessible as `${StepTitle__<variable path>`; see [1]). These variables have certain unique features.

1. Assume we have a variable `x` that is a dictionary containing a key `a`. We can refer to `a` using `${x__a}`. This can be nested - if `a` is another dictionary, and `b` is a key inside `a`, `b` can be referenced as `${x__a__b}`.

2. Lists can be indexed by their zero-index. If `a` is a list inside a dictionary `x`, we can get the first value in the list `a` as `${x__a__0}`. These indices use the python-syntax; `-1` is the last element, `2` is the third element and so on.

3. Certain functions can be called on variables based on their type using the `|` symbol. For example, if we wanted to `split` a string variable `x` by commas and get the first value, we could use `${x|split(',')__0}`. The same logic in [1] and [2] can be used alongside these.
  1. Note that all "Steps" by themselves are treated as dictionaries as a whole. So if you wanted to get all of the variables stored by a step split by commas, you could use `${step_title|join(',')}`.

### Resolved Variable Functions

Here's the list of all functions available for resolved variables split by their type.

1. String
  - `split(delim, maxsplit=None)` - Splits the string by the given delimiter.
  - `upper()` - Uppercases the entire string
  - `lower()` - Lowercasess the entire string
  - `capitalize()` - Capitalizes the first letter of the string
  - `zfill(width)` - Adds zeroes before the string so that it reaches the required width
  - `strip()` - Strips spaces from before and after the string
  - `len()` - Gives back the length of the string as an integer
  - `startswith(prefix)` - Returns a boolean based on whether a string starts with a value or not
  - `endswith(prefix)` - Returns a boolean based on whether a string ends with a value or not

2. List
  - `len()` - Returns the length of the string as an integer
  - `index(value)` - Returns the index of the given value in the list
  - `reverse()` - Returns the list in reverse
  - `sort()` - Returns the sorted list
  - `join(delim)` - Returns the list joined by the delimiter as a string

3. Dict
  - `get(key, default=None)` - Returns the key if it exists in the dict, otherwise returns the default if provided
  - `keys()` - Returns a list of all keys in the dictionary
  - `items()` - Returns a list of tuples of all (key, value) pairs in the dictionary