"""
Module containing a mapping of steps that are useable by the parsers

Each custom created step must be registered using the included
``register_step`` method
"""
from selenium_yaml import steps
from selenium_yaml.steps import core_steps

REGISTERED_STEPS = {
    "navigate": core_steps.NavigateStep,
    "wait": core_steps.WaitStep,
    "wait_for_element": core_steps.WaitForElementStep,
    "click": core_steps.ClickElementStep,
    "type": core_steps.TypeTextStep,
    "select": core_steps.SelectOptionStep,
    "make_request": core_steps.CallAPIStep,
    "iterate_over": core_steps.IteratorStep,
    "run_bot": core_steps.RunBotStep,
    "conditional": core_steps.ConditionalStep,
    "store_xpath": core_steps.StoreXpathStep,
    "store_page_url": core_steps.StorePageUrlStep
}


def get_registered_step(friendly_name):
    """ Returns the registered step from the mapping if it exists, otherwise
        raises a KeyError exception
    """
    return REGISTERED_STEPS[friendly_name]


def register_step(friendly_name, step_cls):
    """ Registers a new step with the given ``friendly_name`` and the
        ``step_cls``

        The ``step_cls`` is expected to be an instance of ``steps.BaseStep``
    """
    global REGISTERED_STEPS
    if friendly_name in REGISTERED_STEPS:
        raise ValueError(f"The name `{friendly_name}` is already registered.")
    REGISTERED_STEPS[friendly_name] = step_cls


def selenium_step(friendly_name):
    """ Decorator for registering a step with a given name """
    class StepWrapper:
        def __init__(self, step_cls):
            self.step_cls = step_cls
            print(self.step_cls, type(self.step_cls))
            register_step(friendly_name, self.step_cls)

        def __call__(self, *args, **kwargs):
            return self.step_cls

    return StepWrapper
