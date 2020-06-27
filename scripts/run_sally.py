"""
CLI For the SeleniumYAML library

Basic Usage:
    # TODO
"""
import argparse
import selenium_yaml
from loguru import logger
import os


class TemplateContextAction(argparse.Action):
    """ Custom argparse action to add a string value in the format of
        ``key1=var1,key2=var2,key3=var3`` to a dictionary named
        after the dest (template_context) in the NameSpace as {
            key1: var1,
            key2: var2,
            key3: var3
        }
    """
    def __call__(self, parser, namespace, values, option_string=None):
        template_context = {}
        for item in values.split(","):
            k, v = item.split("=")
            template_context[k] = v
        setattr(namespace, self.dest, template_context)


def setup_parser():
    """ Returns an instance of argparse.ArgumentParser with all of the
        arguments required for the script set up
    """
    parser = argparse.ArgumentParser(description="Run SeleniumYAML Bots~")
    parser.add_argument('-v', '--version', action='version',
                        version=selenium_yaml.__title__ + ' ' +
                        selenium_yaml.__version__)
    parser.add_argument("--yaml-file", type=str, help="Path to the YAML Bot")

    parser.add_argument('--screenshots', dest='save_screenshots',
                        action='store_true')
    parser.add_argument('--no-screenshots', dest='save_screenshots',
                        action='store_false')
    parser.set_defaults(save_screenshots=True)

    parser.add_argument('--logs', dest='save_logs',
                        action='store_true')
    parser.add_argument('--no-logs', dest='save_logs',
                        action='store_false')

    parser.add_argument('--context', dest="template_context",
                        action=TemplateContextAction, type=str,
                        default=argparse.SUPPRESS)
    parser.set_defaults(save_logs=True, template_context={})
    return parser


def main(yaml_file, save_screenshots=False, save_logs=False,
         template_context=None):
    """ Runs the SeleniumYAML bot over the given ``yaml_file`` """
    if save_logs:
        logger.add(os.path.join("logs", "sally_{time}.log"))

    parse_template = True if template_context else False
    engine = selenium_yaml.SeleniumYAML(yaml_file=yaml_file,
                                        save_screenshots=save_screenshots,
                                        template_context=template_context,
                                        parse_template=parse_template)
    engine.perform()


if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    main(args.yaml_file,
         save_screenshots=args.save_screenshots,
         save_logs=args.save_logs,
         template_context=args.template_context)
