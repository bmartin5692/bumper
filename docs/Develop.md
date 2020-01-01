# Developing
To start developing and contributing, install in dev mode.

`pipenv install --dev`

Review the [How It Works](How_It_Works.md) doc to understand the basics and then dive into the code.

As features and functions are added, be sure to add tests to keep the test coverage high.

# Testing
Bumper uses pytest for the majority of test cases, review current tests in the /tests directory.

### Running tests
Enter pipenv shell `pipenv shell`

**Run tests**

- `python -m pytest tests`


**Run tests with coverage**

- `python -m pytest --cov=./ tests`

**Run tests with coverage html report**

- `python -m pytest --cov=./ tests --cov-report html:tests/report`
    - The report will be output into tests/report/index.html for further analysis.