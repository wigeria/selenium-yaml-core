# Steps

This is a reference for the steps included with the library. For details on creating your own custom steps, refer to [this page](quickstart/customization.md).

Notes:
  - Details about Resolved Variables mentioned herein can be found [here](reference/resolved-variables.md)
  - The fields that are required are highlighted in bold

## Base Fields

All steps must have the following two fields in the YAML, so that they can be identified and validated by the parser.

```
title
```

The `title` field is used as a unique namespace for a step within a bot. This name is used for storing and accessing `performance_context` for the step as well as for a few other tasks that require namespacing such as screenshots, passing back validation errors, etc.

```
action
```

This field is used to identify the class of the Step that needs to be performed. Each of the core steps have their own identifier that they're registered using, and any custom steps must also be registered with their own unique identifier through the `selenium_yaml.steps.registered_steps.selenium_step` decorator as described [here](/quickstart/customization/#registering-a-step).

# Core Steps

## NavigateStep

```yaml
  - title: Navigate to URL
    action: navigate
    url: <URL to navigate to>
```

- **`url`** - `CharField` for the URL that the driver should be navigated to

This step performs a `driver.get` action with the provided URL.

## WaitStep

```yaml
  - title: Wait for a fixed amount of time
    action: wait
    seconds: <Seconds to wait for>
```

- **`seconds`** - `IntegerField` for the number of steps to wait for

This step performs a wait for the given number of `seconds` using `time.sleep()`.

## WaitForElementStep

```yaml
  - title: Wait for the element to be clickable
    action: wait_for_element
    element: <Xpath selector for the element>
    seconds: <Seconds to wait for>
```

- **`element`** - `CharField` for the XPath selector for the element to wait for
- **`seconds`** - `IntegerField` for the number of seconds to wait for

This step performs waits for the presence of the given `element` for the given number of `seconds`.

## ClickElementStep

```yaml
  - title: Click on an element
    action: click
    element: <Xpath Selector for the Element>
```

- **`element`** - `CharField` for the XPath selector for the element to click on

This step clicks on the `element` identified by the XPath using `driver.click()`.

## TypeTextStep

```yaml
  - title: Type text into an element
    action: type
    element: <Xpath Selector for the Element>
    text: Text to type into the element
    clear: True|False
```

- **`element`** - `CharField` for the XPath selector for the element to send text to
- **`text`** - `CharField` for the text to send to the element
- `clear` - `BooleanField`; if True, clears the field prior to sending any text

This step sends the given `text` to the given `element` using `driver.send_keys()`.

## SelectOptionStep

```yaml
  - title: Select an option from a `select` element
    action: select
    element: <Xpath selector for the Select element>
    option: <Value of the option that should be selected>
```

- **`element`** - `CharField` for the XPath selector for the select element
- **`option`** - `CharField` for the value of the option in the select element that should be selected

This step selects the given `option` in the given select `element`.

## RunBotStep

```yaml
  - title: Run another bot with it's file path
    action: run_bot
    path: /path/to/the/bot
    save_screenshots: True|False
    parse_template: True|False
    template_context:
      - Key: Value
```

- **`path`** - `FilePathField` to the path of the both that should be run
- `save_screenshots` - `BooleanField` for whether this bot should have screenshots' saved or not
- `parse_template` - `BooleanField`; if True, the `template_context` field will be used for rendering the Bot's YAML as a Jinja Template prior to execution
- `template_context` - `ResolvedVariableField(required_type=dict)` field that can either be a resolved variable or a dictionary, and will be used for rendering the Bot's YAML if `parse_template` is True

This step is used for running another bot with the current performance context available in the bot.

## CallAPIStep

```yaml
  - title: Call an API and store it's response and status code
    action: make_request
    method: GET
    url: https://url-to-request.com/?queryParams=value
    body: 
      Key: Value
    headers:
      Key: Value
```

- **`url`** - `CharField` for the URL that should be requested
- **`method`** - `CharField(options=["GET", "PUT", "POST"])` for the request method that should be used
- `body` - `DictField` for the request body
- `headers` - `DictField` for the request headers

This step is used for sending a request with the given details and storing the response's body in the `context` and `status_code` performance context variables under the step's namespace

## IteratorStep

```yaml
  - title: Iterate over an array (resolved/directly provided)
    action: iterate_over
    iterator:
      - Array
    steps:
      - title: Array of steps (step-1)
        action: navigate
        url: navigate-url
      ...
```

- **`iterator`** - `ResolvedVariableField(required_type=list)` field for the array to iterate over
- **`steps`** - `NestedStepsField` containing an array of steps that should be performed for each element in the `iterator`

This step is used to perform all of the steps in the `steps` array for each element in the `iterator`. The context for each iteration is stored under the `step_title__iter_index__sub_step_title` namespace. The `iterator` could also be a resolved variable if required. In the steps in the iterator, a performance context variable for the current element being iterated over is available at `${current_iterator}` (and indices at `${current_index_zero}` and `${current_index_one}`.

## ConditionalStep

```yaml
  - title: Conditionally run a step
    action: conditional
    value: Value to be checked
    equals: This is what `value` needs to equal
    negate: True|False
    steps:
      - title: Array of steps (step-1)
        action: navigate
        url: navigate-url
        ...
```

- **`value`** - `CharField` that can be an XPath selector to a value (**not an element**), or a string, or a resolved variable of any other type
- **`equals`** - `CharField` that the `value` is check against
- `negate` - `BooleanField`; if True, the `value` must equal `equals` for the condition to pass - otherwise, the `value` must **not** equal `equals` for the condition to pass
- **`steps`** - `NestedStepsField` containing an array of steps that should be performed if the condition passes

This step is used for conditionally running a set of steps.

## StoreXpathStep

```yaml
  - title: Store the result of a given xpath selector in the performance context
    action: store_xpath
    selector: "//xpath/selector/@attribute"
    variable: Variable To Store Result In
    select_first: True|False
```

- **`selector`** - `CharField` for the selector to the attribute/prop that should be stored
- **`variable`** - `CharField` for the variable name that the `selector`'s result will be stored in under the step's namespace
- `select_first` - `BooleanField`; if True, will store only the first match for the selector - otherwise, stores all of the matches in the `variable` as an array

This step is used for storing something in the page in the performance context for later use.

## StorePageUrlStep

```yaml
  - title: Store the current page's URL in a <Step Title>__url variable for later use
    action: store_page_url
```

This step is used for storing the current page URL in a `url` variable under the step's namespace.
