# Bumper tests
Bumper uses nosetests for the majority of test cases.  Install requirements using `pipenv install --dev`

## Testing
Enter pipenv shell `pipenv shell`

### Run tests
`nosetests`

### Run tests with coverage
`nosetests --cover-package bumper --with-coverage`

### Run tests with coverage html report
`nosetests --cover-package bumper --with-coverage --cover-html-dir="tests/report" --cover-html`

The report will be output into tests/report/index.html for further analysis.