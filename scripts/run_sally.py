"""
CLI For the SeleniumYAML library

Basic Usage:
    # TODO
"""
import argparse
from selenium_yaml import SeleniumYAML


def setup_parser():
    """ Returns an instance of argparse.ArgumentParser with all of the
        arguments required for the script set up
    """
    parser = argparse.ArgumentParser(description="Run SeleniumYAML Bots~")
    parser.add_argument("--yaml-file", type=str, help="Path to the YAML Bot")

    parser.add_argument('--screenshots', dest='save_screenshots',
                        action='store_true')
    parser.add_argument('--no-screenshots', dest='save_screenshots',
                        action='store_false')
    parser.set_defaults(save_screenshots=True)
    return parser


def main(yaml_file, save_screenshots=False):
    """ Runs the SeleniumYAML bot over the given ``yaml_file`` """
    engine = SeleniumYAML(yaml_file=yaml_file,
                          save_screenshots=save_screenshots)
    engine.perform()


if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    main(args.yaml_file, save_screenshots=args.save_screenshots)


