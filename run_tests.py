"""
Runs the tests with the general arguments required; including but not
limited to `coverage` and driver settings
"""
import pytest
import sys

if __name__ == "__main__":
    try:
        sys.argv.remove('--coverage')
    except ValueError:
        run_cov = True
    else:
        run_cov = False

    pytest_args = []

    if run_cov:
        pytest_args += ["--cov-report=html", "--cov=selenium_yaml"]

    pytest.main(pytest_args)
