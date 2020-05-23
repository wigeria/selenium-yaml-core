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

- **Run Bot**

      ```yaml
  - title: Run another bot with it's file path
    action: run_bot
    path: /path/to/bot's/yaml
      ```
  