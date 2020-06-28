# Installation

The bot is relatively simple to install, but you'll need to install a few core dependencies before you can use it.

## Installing Python 3

SeleniumYAML doesn't support Python 2, considering that it's been discontinued for quite a while now. You can confirm that you have Python 3.6+ using `python --version` and make sure you get an output higher than `Python 3.6`. If you have 3.6 or higher, feel free to skip this. Otherwise, refer to [this page](https://wiki.python.org/moin/BeginnersGuide/Download) to install Python 3.6 or higher.

## Installing PIP

PIP is the most widely used package manager for Python. If you don't already have it installed (if you installed using a binary, it should've come prepackaged), refer to [this page](https://pip.pypa.io/en/stable/installing/) to install it.

## Installing Selenium and a Webdriver

Selenium is the automation library used by SeleniumYAML bots (duh). Installing it is rather straight forward for most systems; simply run the following:

```
pip install selenium
```

If you run into any issues, refer to Selenium's [installation page](https://selenium-python.readthedocs.io/installation.html).

Now, you need to install a Webdriver. There are a lot of these out there, but you need to install one for whichever WebBrowser you're looking to automate tasks on with SeleniumYAML. Make sure you install one that supports the version of the browser you have installed. Here's some of the popular ones.

| Browser: | Download Link                                                          |
|----------|------------------------------------------------------------------------|
| Chrome:  | <https://sites.google.com/a/chromium.org/chromedriver/downloads>       |
| Firefox: | <https://github.com/mozilla/geckodriver/releases>                      |
| Edge:    | <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>|
| Safari:  | <https://webkit.org/blog/6900/webdriver-support-in-safari-10/>         |

After you've downloaded the one you're interested in, it's recommended that you add it to your PATH environment variable. Instructions on doing this can vary based on your OS, so it's suggested that you do a Google search.

## Installing SeleniumYAML

Finally done with the dependencies. Installing SeleniumYAML is simple; just run this:

```
pip install selenium-yaml
```

You can confirm that you've installed it successfully by running `run_sally.py --version`.
