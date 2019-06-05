# Bumper tests
Bumper uses pytest for the majority of test cases.  Install requirements using `pipenv install --dev`

## Testing
Enter pipenv shell `pipenv shell`

### Run tests
`python -m pytest`

### Run tests with coverage
`python -m pytest --cov=bumper tests/`

### Run tests with coverage html report
`python -m pytest --cov=bumper tests/ --cov-report html:tests/report`

The report will be output into tests/report/index.html for further analysis.