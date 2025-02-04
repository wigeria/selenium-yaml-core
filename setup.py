import os
import setuptools


def get_file_contents(fpath):
    contents = ""
    with open(fpath, "r") as inf:
        contents = inf.read()
    return contents

conf_files = {
    "README": "README.md",
}
requirements = [
    "selenium>=3.141.0",
    "Jinja2==2.11.3",
    "loguru",
    "PyYAML==5.4",
    "requests"
]


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="selenium-yaml",
    version="1.0.97",
    author="Abhishek Verma",
    author_email="wigeriaaeriag@gmail.com",
    description="Selenium bots using YAML",
    long_description=get_file_contents(conf_files["README"]),
    long_description_content_type="text/markdown",
    url="https://github.com/wigeria/selenium-yaml-core",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
    ],
    python_requires='>=3.6',
    scripts=["scripts/run_sally.py"],
    install_requires=requirements
)
